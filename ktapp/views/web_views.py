# -*- coding: utf-8 -*-

import datetime
import math

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django import forms
from django.db.models import Sum, Q
from django.utils.html import strip_tags
from django.utils.crypto import get_random_string

from ktapp import models
from ktapp import forms as kt_forms
from ktapp import utils as kt_utils
from ktapp import texts


COMMENTS_PER_PAGE = 100
MESSAGES_PER_PAGE = 50


def index(request):
    today = datetime.date.today()
    today = datetime.datetime.strptime('2014-11-10', '%Y-%m-%d')  # HACK
    offset = (today.weekday() - 3) % 7  # last Thursday=premier day
    from_date = today - datetime.timedelta(days=offset+7)
    until_date = today - datetime.timedelta(days=offset-7)
    premier_list = []
    # TODO: add alternative premier dates
    for film in models.Film.objects.filter(main_premier__gte=from_date, main_premier__lte=until_date).order_by('-main_premier', 'orig_title'):
        if premier_list:
            if premier_list[-1][0] != film.main_premier:
                premier_list.append([film.main_premier, []])
        else:
            premier_list.append([film.main_premier, []])
        premier_list[-1][1].append(film)
    return render(request, "ktapp/index.html", {
        "premier_list": premier_list,
        "comments": models.Comment.objects.select_related('film', 'created_by', 'reply_to').filter(domain=models.Comment.DOMAIN_FILM)[:20],
    })


def search(request):
    q = request.GET.get('q')
    if not q:
        return HttpResponseRedirect(reverse('index'))
    results = []
    for result in models.Film.objects.filter(
            Q(orig_title__icontains=q)
            | Q(other_titles__icontains=q)
    ):
        results.append({
            'rank': 1000 + result.num_rating(),
            'type': 'film',
            'title': '%s (%s)' % (result.orig_title, result.year),
            'url': reverse('film_main', args=(result.id, result.slug_cache)),
            'object': result,
        })
    for result in models.Artist.objects.filter(name__icontains=q):
        results.append({
            'rank': 1000  + result.num_rating(),
            'type': 'artist',
            'title': result.name,
            'url': reverse('artist', args=(result.id, result.slug_cache)),
            'object': result,
        })
    for result in models.FilmArtistRelationship.objects.filter(role_name__icontains=q, role_type=models.FilmArtistRelationship.ROLE_TYPE_ACTOR):
        results.append({
            'rank': 900,
            'type': 'role',
            'title': result.role_name,
            'url': reverse('role', args=(result.id, result.slug_cache)),
            'object': result,
        })
    for result in models.Sequel.objects.filter(name__icontains=q):
        results.append({
            'rank': 850,
            'type': 'sequel/%s' % result.sequel_type,
            'title': result.name,
            'url': '',  # TODO
            'object': result,
        })
    for result in models.Keyword.objects.filter(name__icontains=q):
        results.append({
            'rank': 800,
            'type': 'keyword/%s' % result.keyword_type,
            'title': result.name,
            'url': '',  # TODO
            'object': result,
        })
    for result in models.Topic.objects.filter(title__icontains=q):
        results.append({
            'rank': 750,
            'type': 'topic',
            'title': result.title,
            'url': reverse('forum', args=(result.id, result.slug_cache)),
            'object': result,
        })
    for result in models.Poll.objects.filter(title__icontains=q):
        results.append({
            'rank': 700,
            'type': 'poll',
            'title': result.title,
            'url': '',  # TODO
            'object': result,
        })
    for result in models.KTUser.objects.filter(username__icontains=q):
        results.append({
            'rank': 500,
            'type': 'user',
            'title': result.username,
            'url': reverse('user_profile', args=(result.id, result.slug_cache)),
            'object': result,
        })
    # content searches (should be separate?):
    # | Q(plot_summary__icontains=q)
    # for result in models.Comment.objects.filter(content__icontains=q):
    #     if result.domain == models.Comment.DOMAIN_FILM:
    #         title = '%s (%s)' % (result.film.orig_title, result.film.year)
    #         url = reverse('film_comments', args=(result.film.id, result.film.slug_cache))
    #     elif result.domain == models.Comment.DOMAIN_TOPIC:
    #         title = result.topic.title
    #         url = reverse('forum', args=(result.topic.id, result.topic.slug_cache))
    #     else:
    #         title = result.poll.title
    #         url = ''  # TODO
    #     results.append({
    #         'rank': 750,
    #         'type': 'comment',
    #         'title': title,
    #         'url': url,
    #         'object': result,
    #     })
    # Quote
    # Trivia
    # Review
    return render(request, 'ktapp/search.html', {
        'q': q,
        'result_count': len(results),
        'results': sorted(results, key=lambda r: (-r['rank'], r['title']))[:100],
    })


def film_main(request, id, film_slug):
    film = get_object_or_404(models.Film, pk=id)
    rating = 0
    if request.user.is_authenticated():
        try:
            vote = models.Vote.objects.get(film=film, user=request.user)
            rating = vote.rating
        except models.Vote.DoesNotExist:
            pass
    return render(request, 'ktapp/film_subpages/film_main.html', {
        'active_tab': 'main',
        'film': film,
        'rating': rating,
        'ratings': range(1, 6),
        'roles': film.filmartistrelationship_set.filter(role_type=models.FilmArtistRelationship.ROLE_TYPE_ACTOR),
        'votes': zip(
            [film.num_specific_rating(r) for r in range(5, 0, -1)],
            [film.vote_set.filter(rating=r).select_related('user').order_by('user__username') for r in range(5, 0, -1)]
        ),
    })


def film_comments(request, id, film_slug):
    film = get_object_or_404(models.Film, pk=id)
    p = int(request.GET.get('p', 0))
    if p == 1:
        return HttpResponseRedirect(reverse('film_comments', args=(film.id, film.slug_cache)))
    max_pages = int(math.ceil(1.0 * film.number_of_comments / COMMENTS_PER_PAGE))
    if max_pages == 0:
        max_pages = 1
    if p == 0:
        p = 1
    if p > max_pages:
        return HttpResponseRedirect(reverse('film_comments', args=(film.id, film.slug_cache)) + '?p=' + str(max_pages))
    if max_pages > 1:
        first_comment = film.number_of_comments - COMMENTS_PER_PAGE * (p - 1) - (COMMENTS_PER_PAGE - 1)
        last_comment = film.number_of_comments - COMMENTS_PER_PAGE * (p - 1)
        comments = film.comment_set.filter(serial_number__lte=last_comment, serial_number__gte=first_comment)
    else:
        comments = film.comment_set.all()
    try:
        reply_to_comment = models.Comment.objects.get(id=request.GET.get('valasz'))
        reply_to_id = reply_to_comment.id
    except models.Comment.DoesNotExist:
        reply_to_comment = None
        reply_to_id = None
    comment_form = kt_forms.CommentForm(initial={
        'domain': models.Comment.DOMAIN_FILM,
        'film': film,
        'topic': None,
        'poll': None,
        'reply_to': reply_to_id,
    })
    comment_form.fields['domain'].widget = forms.HiddenInput()
    comment_form.fields['film'].widget = forms.HiddenInput()
    comment_form.fields['topic'].widget = forms.HiddenInput()
    comment_form.fields['poll'].widget = forms.HiddenInput()
    comment_form.fields['reply_to'].widget = forms.HiddenInput()
    return render(request, 'ktapp/film_subpages/film_comments.html', {
        'active_tab': 'comments',
        'film': film,
        'comments': comments,
        'comment_form': comment_form,
        'reply_to_comment': reply_to_comment,
        'p': p,
        'max_pages': max_pages,
    })


def film_quotes(request, id, film_slug):
    film = get_object_or_404(models.Film, pk=id)
    quote_form = kt_forms.QuoteForm(initial={
        "film": film,
    })
    quote_form.fields["film"].widget = forms.HiddenInput()
    return render(request, "ktapp/film_subpages/film_quotes.html", {
        "active_tab": "quotes",
        "film": film,
        "quotes": film.quote_set.all(),
        "quote_form": quote_form,
    })


def film_trivias(request, id, film_slug):
    film = get_object_or_404(models.Film, pk=id)
    trivia_form = kt_forms.TriviaForm(initial={
        "film": film,
    })
    trivia_form.fields["film"].widget = forms.HiddenInput()
    return render(request, "ktapp/film_subpages/film_trivias.html", {
        "active_tab": "trivias",
        "film": film,
        "trivias": film.trivia_set.all(),
        "trivia_form": trivia_form,
    })


def film_reviews(request, id, film_slug):
    film = get_object_or_404(models.Film, pk=id)
    review_form = kt_forms.ReviewForm(initial={
        "film": film,
    })
    review_form.fields["film"].widget = forms.HiddenInput()
    return render(request, "ktapp/film_subpages/film_reviews.html", {
        "active_tab": "reviews",
        "film": film,
        "reviews": film.review_set.all(),
        "review_form": review_form,
    })


def film_review(request, id, film_slug, review_id):
    film = get_object_or_404(models.Film, pk=id)
    review = get_object_or_404(models.Review, pk=review_id)
    if review.film != film:
        raise Http404
    return render(request, "ktapp/film_subpages/film_review.html", {
        "active_tab": "reviews",
        "film": film,
        "review": review,
    })


def film_awards(request, id, film_slug):
    film = get_object_or_404(models.Film, pk=id)
    return render(request, "ktapp/film_subpages/film_awards.html", {
        "active_tab": "awards",
        "film": film,
        "awards": film.award_set.all().order_by('name', 'year', 'category'),
    })


def film_links(request, id, film_slug):
    film = get_object_or_404(models.Film, pk=id)
    return render(request, "ktapp/film_subpages/film_links.html", {
        "active_tab": "links",
        "film": film,
        "links": film.link_set.all(),
    })


def _get_next_picture(pictures, picture):
    found_this = False
    next_picture = None
    for pic in pictures:
        if found_this:
            next_picture = pic
            break
        if pic == picture:
            found_this = True
    if next_picture is None:
        next_picture = pictures[0]
    return next_picture


def _get_selected_picture_details(film, picture, next_picture):
    return {
        "picture": picture,
        "next_picture": next_picture,
        "pic_height": models.Picture.THUMBNAIL_SIZES["mid"][1],
        "artists": picture.artists.all(),
        "film_title_article": "az" if film.orig_title[:1].lower() in u"aáeéiíoóöőuúüű" else "a",
    }


def film_pictures(request, id, film_slug):
    film = get_object_or_404(models.Film, pk=id)
    pictures = sorted(film.picture_set.all(), key=lambda pic: (pic.order_key, pic.id))
    upload_form = kt_forms.PictureUploadForm(initial={
        "film": film,
    })
    upload_form.fields["film"].widget = forms.HiddenInput()
    context = {
        "active_tab": "pictures",
        "film": film,
        "pictures": pictures,
        "upload_form": upload_form,
        'all_artists_in_film': film.artists.all(),
    }
    if len(pictures) == 1:
        next_picture = _get_next_picture(pictures, pictures[0])
        context.update(_get_selected_picture_details(film, pictures[0], next_picture))
    return render(request, "ktapp/film_subpages/film_pictures.html", context)


def film_picture(request, id, film_slug, picture_id):
    film = get_object_or_404(models.Film, pk=id)
    picture = get_object_or_404(models.Picture, pk=picture_id)
    if picture.film != film:
        raise Http404
    pictures = sorted(film.picture_set.all(), key=lambda pic: (pic.order_key, pic.id))
    next_picture = _get_next_picture(pictures, picture)
    upload_form = kt_forms.PictureUploadForm(initial={
        "film": film,
    })
    upload_form.fields["film"].widget = forms.HiddenInput()
    context = {
        "active_tab": "pictures",
        "film": film,
        "pictures": pictures,
        "upload_form": upload_form,
        'all_artists_in_film': film.artists.all(),
    }
    context.update(_get_selected_picture_details(film, picture, next_picture))
    return render(request, "ktapp/film_subpages/film_pictures.html", context)


def film_keywords(request, id, film_slug):
    film = get_object_or_404(models.Film, pk=id)
    return render(request, "ktapp/film_subpages/film_keywords.html", {
        "active_tab": "keywords",
        "film": film,
        "major_keywords": film.keyword_set.filter(keyword_type=models.Keyword.KEYWORD_TYPE_MAJOR),
        "other_keywords": film.keyword_set.filter(keyword_type=models.Keyword.KEYWORD_TYPE_OTHER),
    })


@login_required
def vote(request):
    film = get_object_or_404(models.Film, pk=request.POST["film_id"])
    try:
        rating = int(request.POST["rating"])
    except ValueError:
        rating = 0
    if rating == 0:
        models.Vote.objects.filter(film=film, user=request.user).delete()
    elif 1 <= rating <= 5:
        vote, created = models.Vote.objects.get_or_create(film=film, user=request.user, defaults={"rating": rating})
        vote.rating = rating
        vote.save()
    return HttpResponseRedirect(reverse("film_main", args=(film.pk, film.slug_cache)))


@login_required
def new_comment(request):  # TODO: extend with poll comments
    domain_type = request.POST["domain"]
    if domain_type == models.Comment.DOMAIN_FILM:
        domain = get_object_or_404(models.Film, pk=request.POST["film"])
    elif domain_type == models.Comment.DOMAIN_TOPIC:
        domain = get_object_or_404(models.Topic, pk=request.POST["topic"])
    elif domain_type == models.Comment.DOMAIN_POLL:
        domain = get_object_or_404(models.Poll, pk=request.POST["poll"])
    else:
        raise Http404
    if request.POST:
        comment_form = kt_forms.CommentForm(data=request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.created_by = request.user
            comment.save(domain=domain)  # Comment model updates domain object
    if domain_type == models.Comment.DOMAIN_FILM:
        return HttpResponseRedirect(reverse("film_comments", args=(domain.pk, domain.slug_cache)))
    elif domain_type == models.Comment.DOMAIN_TOPIC:
        return HttpResponseRedirect(reverse("forum", args=(domain.pk, domain.slug_cache)))
    elif domain_type == models.Comment.DOMAIN_POLL:
        return HttpResponseRedirect(reverse("index"))
    else:
        raise Http404


@login_required
def new_quote(request):
    film = get_object_or_404(models.Film, pk=request.POST["film"])
    if request.POST:
        quote_form = kt_forms.QuoteForm(data=request.POST)
        if quote_form.is_valid():
            quote = quote_form.save(commit=False)
            quote.created_by = request.user
            quote.save()
    return HttpResponseRedirect(reverse("film_quotes", args=(film.pk, film.slug_cache)))


@login_required
def new_trivia(request):
    film = get_object_or_404(models.Film, pk=request.POST["film"])
    if request.POST:
        trivia_form = kt_forms.TriviaForm(data=request.POST)
        if trivia_form.is_valid():
            trivia = trivia_form.save(commit=False)
            trivia.created_by = request.user
            trivia.save()
    return HttpResponseRedirect(reverse("film_trivias", args=(film.pk, film.slug_cache)))


@login_required
def new_review(request):
    film = get_object_or_404(models.Film, pk=request.POST["film"])
    if request.POST:
        review_form = kt_forms.ReviewForm(data=request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.created_by = request.user
            review.save()
    return HttpResponseRedirect(reverse("film_reviews", args=(film.pk, film.slug_cache)))


@login_required
def new_picture(request):
    film = get_object_or_404(models.Film, pk=request.POST['film'])
    if request.POST:
        upload_form = kt_forms.PictureUploadForm(request.POST, request.FILES)
        if upload_form.is_valid():
            picture = upload_form.save(commit=False)
            picture.created_by = request.user
            picture.save()
            possible_artists = {
                unicode(artist.id): artist for artist in film.artists.all()
            }
            for artist_id in request.POST.getlist('picture_artist_cb'):
                if artist_id in possible_artists:
                    picture.artists.add(possible_artists[artist_id])
    return HttpResponseRedirect(reverse('film_pictures', args=(film.pk, film.slug_cache)))


@login_required
def edit_picture(request):
    picture = get_object_or_404(models.Picture, pk=request.POST['picture'])
    if request.POST:
        picture.picture_type = request.POST.get('picture_type', 'O')
        picture.source_url = request.POST.get('source_url', '')
        picture.save()
        picture.artists.clear()
        possible_artists = {
            unicode(artist.id): artist for artist in picture.film.artists.all()
        }
        for artist_id in request.POST.getlist('picture_artist_cb_edit'):
            if artist_id in possible_artists:
                picture.artists.add(possible_artists[artist_id])
    return HttpResponseRedirect(reverse('film_picture', args=(picture.film.pk, picture.film.slug_cache, picture.id)) + '#pix')


@login_required
def delete_picture(request):
    picture = get_object_or_404(models.Picture, pk=request.POST['picture'])
    if request.POST:
        picture.delete()
    return HttpResponseRedirect(reverse('film_pictures', args=(picture.film.pk, picture.film.slug_cache)))


def artist(request, id, name_slug):
    artist = get_object_or_404(models.Artist, pk=id)
    directions = artist.filmartistrelationship_set.filter(role_type=models.FilmArtistRelationship.ROLE_TYPE_DIRECTOR).order_by('-film__year', 'film__orig_title')
    director_vote_avg = 0
    if directions:
        director_votes = directions.aggregate(nr1=Sum('film__number_of_ratings_1'),
                                              nr2=Sum('film__number_of_ratings_2'),
                                              nr3=Sum('film__number_of_ratings_3'),
                                              nr4=Sum('film__number_of_ratings_4'),
                                              nr5=Sum('film__number_of_ratings_5'))
        director_vote_count = director_votes.get('nr1', 0) + director_votes.get('nr2', 0) + director_votes.get('nr3', 0) + director_votes.get('nr4', 0) + director_votes.get('nr5', 0)
        if director_vote_count:
            director_vote_avg = 1.0 * (director_votes.get('nr1', 0) + 2*director_votes.get('nr2', 0) + 3*director_votes.get('nr3', 0) + 4*director_votes.get('nr4', 0) + 5*director_votes.get('nr5', 0)) / director_vote_count
    else:
        director_vote_count = 0
    roles = artist.filmartistrelationship_set.filter(role_type=models.FilmArtistRelationship.ROLE_TYPE_ACTOR).order_by('-film__year', 'film__orig_title')
    actor_vote_avg = 0
    if roles:
        actor_votes = roles.aggregate(nr1=Sum('film__number_of_ratings_1'),
                                      nr2=Sum('film__number_of_ratings_2'),
                                      nr3=Sum('film__number_of_ratings_3'),
                                      nr4=Sum('film__number_of_ratings_4'),
                                      nr5=Sum('film__number_of_ratings_5'))
        actor_vote_count = actor_votes.get('nr1', 0) + actor_votes.get('nr2', 0) + actor_votes.get('nr3', 0) + actor_votes.get('nr4', 0) + actor_votes.get('nr5', 0)
        if actor_vote_count:
            actor_vote_avg = 1.0 * (actor_votes.get('nr1', 0) + 2*actor_votes.get('nr2', 0) + 3*actor_votes.get('nr3', 0) + 4*actor_votes.get('nr4', 0) + 5*actor_votes.get('nr5', 0)) / actor_vote_count
    else:
        actor_vote_count = 0
    return render(request, "ktapp/artist.html", {
        "artist": artist,
        "directions": directions,
        "roles": roles,
        "director_vote_count": director_vote_count,
        "actor_vote_count": actor_vote_count,
        "director_vote_avg": director_vote_avg,
        "actor_vote_avg": actor_vote_avg,
        "awards": models.Award.objects.filter(artist=artist).order_by('name', 'year', 'category'),
        'biographies': models.Biography.objects.filter(artist=artist),
    })


def role(request, id, name_slug):
    role = get_object_or_404(models.FilmArtistRelationship, pk=id)
    return render(request, "ktapp/role.html", {
        "role": role,
    })


def list_of_topics(request):
    return render(request, "ktapp/list_of_topics.html", {
        "topics": models.Topic.objects.all(),
        "topic_form": kt_forms.TopicForm(),
    })


def forum(request, id, title_slug):
    try:
        topic = models.Topic.objects.get(pk=id)
    except models.Topic.DoesNotExist:
        return HttpResponseRedirect(reverse('list_of_topics'))
    p = int(request.GET.get('p', 0))
    if p == 1:
        return HttpResponseRedirect(reverse('forum', args=(topic.id, topic.slug_cache)))
    max_pages = int(math.ceil(1.0 * topic.number_of_comments / COMMENTS_PER_PAGE))
    if max_pages == 0:
        max_pages = 1
    if p == 0:
        p = 1
    if p > max_pages:
        return HttpResponseRedirect(reverse('forum', args=(topic.id, topic.slug_cache)) + '?p=' + str(max_pages))
    if max_pages > 1:
        first_comment = topic.number_of_comments - COMMENTS_PER_PAGE * (p - 1) - (COMMENTS_PER_PAGE - 1)
        last_comment = topic.number_of_comments - COMMENTS_PER_PAGE * (p - 1)
        comments = topic.comment_set.filter(serial_number__lte=last_comment, serial_number__gte=first_comment)
    else:
        comments = topic.comment_set.all()
    try:
        reply_to_comment = models.Comment.objects.get(id=request.GET.get('valasz'))
        reply_to_id = reply_to_comment.id
    except models.Comment.DoesNotExist:
        reply_to_comment = None
        reply_to_id = None
    comment_form = kt_forms.CommentForm(initial={
        'domain': models.Comment.DOMAIN_TOPIC,
        'film': None,
        'topic': topic,
        'poll': None,
        'reply_to': reply_to_id,
    })
    comment_form.fields['domain'].widget = forms.HiddenInput()
    comment_form.fields['film'].widget = forms.HiddenInput()
    comment_form.fields['topic'].widget = forms.HiddenInput()
    comment_form.fields['poll'].widget = forms.HiddenInput()
    comment_form.fields['reply_to'].widget = forms.HiddenInput()
    return render(request, 'ktapp/forum.html', {
        'topic': topic,
        'comments': comments,
        'comment_form': comment_form,
        'reply_to_comment': reply_to_comment,
        'p': p,
        'max_pages': max_pages,
    })


def latest_comments(request):
    return render(request, "ktapp/latest_comments.html", {
        "comments": models.Comment.objects.select_related('film', 'topic', 'created_by', 'reply_to').all()[:100],
    })


@login_required
def new_topic(request):
    if request.POST:
        topic_form = kt_forms.TopicForm(data=request.POST)
        if topic_form.is_valid():
            topic = topic_form.save(commit=False)
            topic.created_by = request.user
            topic.save()
            return HttpResponseRedirect(reverse("forum", args=(topic.pk, topic.slug_cache)))
    return HttpResponseRedirect(reverse("list_of_topics"))


def registration(request):

    def is_valid_email(email):
        try:
            validate_email(email)
        except ValidationError:
            return False
        return True

    next_url = request.GET.get('next', request.POST.get('next', request.META.get('HTTP_REFERER')))
    error_type = ''
    username = request.POST.get('username', '')
    email = request.POST.get('email', '')
    nickname = request.POST.get('nickname', '')
    if request.method == 'POST':
        if nickname != '':
            error_type = 'robot'
        elif username == '':
            error_type = 'name_empty'
        elif email == '':
            error_type = 'email_empty'
        elif not is_valid_email(email):
            error_type = 'email_invalid'
        elif models.KTUser.objects.filter(email=email).count():
            error_type = 'email_taken'
        elif models.KTUser.objects.filter(username=username).count():
            error_type = 'name_taken'
        else:
            password = get_random_string(32)
            user = models.KTUser.objects.create_user(username, email, password)
            token = get_random_string(64)
            models.PasswordToken.objects.create(
                token=token,
                belongs_to=user,
                valid_until=datetime.datetime.now() + datetime.timedelta(days=30),
            )
            user.email_user(
                texts.WELCOME_EMAIL_SUBJECT,
                texts.WELCOME_EMAIL_BODY.format(
                    username=user.username,
                    verification_url=request.build_absolute_uri(reverse('verify_email', args=(token,))),
                )
            )
            login(request, kt_utils.custom_authenticate(models.KTUser, username, password))
            welcome_message = models.Message.objects.create(
                sent_by=None,
                content=texts.WELCOME_PM_BODY.format(
                    username=user.username,
                    email=user.email,
                    reset_password_url=reverse('reset_password', args=('',)),  # important: don't send the token via pm
                ),
                owned_by=user,
                private=True,
            )
            welcome_message.sent_to.add(user)
            welcome_message.save()
            return HttpResponseRedirect(next_url)
    return render(request, 'ktapp/registration.html', {
        'next': next_url,
        'username': username,
        'email': email,
        'error_type': error_type,
    })


def custom_login(request):
    next_url = request.GET.get('next', request.POST.get('next', request.META.get('HTTP_REFERER')))
    if request.method == 'POST':
        username_or_email = request.POST.get('username', '')
        password = request.POST.get('password', '')
        nickname = request.POST.get('nickname', '')
        error_type = ''
        if nickname != '':
            error_type = 'robot'
            username_or_email = ''
        elif not username_or_email:
            error_type = 'name_empty'
            username_or_email = ''
        elif not password:
            error_type = 'password_empty'
        else:
            user = kt_utils.custom_authenticate(models.KTUser, username_or_email, password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(next_url)
                else:
                    error_type = 'ban'
            else:
                error_type = 'fail'
        return render(request, 'ktapp/login.html', {
            'next': next_url,
            'error_type': error_type,
            'username': username_or_email,
        })
    return render(request, 'ktapp/login.html', {
        'next': next_url,
    })


def user_profile(request, id, name_slug):
    selected_user = get_object_or_404(models.KTUser, pk=id)
    return render(request, 'ktapp/user_profile.html', {
        'selected_user': selected_user,
        'latest_votes': selected_user.votes().order_by('-when', '-id')[:50],
        'latest_comments': models.Comment.objects.select_related('film', 'topic', 'created_by', 'reply_to').filter(created_by=selected_user)[:20],
    })


def verify_email(request, token):
    error_type = ''
    new_password1 = request.POST.get('new_password1', '')
    new_password2 = request.POST.get('new_password2', '')
    nickname = request.POST.get('nickname', '')
    token_object = None
    if len(token) != 64:
        error_type = 'short_token'
    else:
        try:
            token_object = models.PasswordToken.objects.get(token=token)
        except models.PasswordToken.DoesNotExist:
            error_type = 'invalid_token'
        if token_object:
            if token_object.valid_until < datetime.datetime.now():
                error_type = 'invalid_token'
            else:
                if request.user.id:
                    if request.user.id != token_object.belongs_to.id:
                        logout(request)
                if not token_object.belongs_to.is_active:
                    error_type = 'ban'
    if error_type == '':
        if request.method == 'POST':
            if nickname != '':
                error_type = 'robot'
            elif len(new_password1) < 6:
                error_type = 'new_password_short'
            elif new_password1 != new_password2:
                error_type = 'new_password_mismatch'
            else:
                token_object.belongs_to.set_password(new_password1)
                token_object.belongs_to.validated_email = True
                token_object.belongs_to.save()
                if not request.user.id:
                    login(request, kt_utils.custom_authenticate(models.KTUser, token_object.belongs_to.username, new_password1))
                error_type = 'ok'
                token_object.delete()
    return render(request, 'ktapp/verify_email.html', {
        'error_type': error_type,
    })


def reset_password(request, token):
    error_type = ''
    username_or_email = request.POST.get('username', '')
    nickname = request.POST.get('nickname', '')
    if token == '':
        if request.method == 'POST':
            if nickname != '':
                error_type = 'robot'
                username_or_email = ''
            elif not username_or_email:
                error_type = 'name_empty'
                username_or_email = ''
            else:
                user = None
                try:
                    user = models.KTUser.objects.get(username=username_or_email)
                except models.KTUser.DoesNotExist:
                    try:
                        user = models.KTUser.objects.get(email=username_or_email)
                    except models.KTUser.DoesNotExist:
                        pass
                if user is None:
                    error_type = 'no_user'
                elif not user.is_active:
                    error_type = 'ban'
                else:
                    token = get_random_string(64)
                    models.PasswordToken.objects.create(
                        token=token,
                        belongs_to=user,
                        valid_until=datetime.datetime.now() + datetime.timedelta(hours=24),
                    )
                    user.email_user(
                        texts.PASSWORD_RESET_EMAIL_SUBJECT,
                        texts.PASSWORD_RESET_EMAIL_BODY.format(
                            username=user.username,
                            reset_password_url=request.build_absolute_uri(reverse('reset_password', args=(token,))),
                        )
                    )
                    error_type = 'ok'
        return render(request, 'ktapp/reset_password.html', {
            'page_type': 'ask',
            'error_type': error_type,
            'username': username_or_email,
        })
    new_password1 = request.POST.get('new_password1', '')
    new_password2 = request.POST.get('new_password2', '')
    nickname = request.POST.get('nickname', '')
    token_object = None
    if len(token) != 64:
        error_type = 'short_token'
    else:
        try:
            token_object = models.PasswordToken.objects.get(token=token)
        except models.PasswordToken.DoesNotExist:
            error_type = 'invalid_token'
        if token_object:
            if token_object.valid_until < datetime.datetime.now():
                error_type = 'invalid_token'
            else:
                if request.user.id:
                    if request.user.id != token_object.belongs_to.id:
                        logout(request)
                if not token_object.belongs_to.is_active:
                    error_type = 'ban'
    if error_type == '':
        if request.method == 'POST':
            if nickname != '':
                error_type = 'robot'
            elif len(new_password1) < 6:
                error_type = 'new_password_short'
            elif new_password1 != new_password2:
                error_type = 'new_password_mismatch'
            else:
                token_object.belongs_to.set_password(new_password1)
                token_object.belongs_to.validated_email = True
                token_object.belongs_to.save()
                if not request.user.id:
                    login(request, kt_utils.custom_authenticate(models.KTUser, token_object.belongs_to.username, new_password1))
                error_type = 'ok'
                token_object.delete()
    return render(request, 'ktapp/reset_password.html', {
        'error_type': error_type,
    })


@login_required
def change_password(request):
    if not request.user.validated_email:
        return HttpResponseRedirect(reverse('user_profile', args=(request.user.id, request.user.slug_cache)))
    error_type = ''
    old_password = request.POST.get('old_password', '')
    new_password1 = request.POST.get('new_password1', '')
    new_password2 = request.POST.get('new_password2', '')
    nickname = request.POST.get('nickname', '')
    if request.method == 'POST':
        if nickname != '':
            error_type = 'robot'
        elif not request.user.check_password(old_password):
            error_type = 'old_password_invalid'
        elif len(new_password1) < 6:
            error_type = 'new_password_short'
        elif new_password1 != new_password2:
            error_type = 'new_password_mismatch'
        else:
            request.user.set_password(new_password1)
            request.user.save()
            return HttpResponseRedirect(reverse('user_profile', args=(request.user.id, request.user.slug_cache)))
    return render(request, 'ktapp/change_password.html', {
        'error_type': error_type,
    })


@login_required
def messages(request):
    number_of_messages = models.Message.objects.filter(owned_by=request.user).count()
    p = int(request.GET.get('p', 0))
    if p == 1:
        return HttpResponseRedirect(reverse('messages'))
    max_pages = int(math.ceil(1.0 * number_of_messages / MESSAGES_PER_PAGE))
    if max_pages == 0:
        max_pages = 1
    if p == 0:
        p = 1
    if p > max_pages:
        return HttpResponseRedirect(reverse('messages') + '?p=' + str(max_pages))
    return render(request, 'ktapp/messages.html', {
        'messages': models.Message.objects.filter(owned_by=request.user).order_by('-sent_at')[(p-1) * MESSAGES_PER_PAGE:p * MESSAGES_PER_PAGE],
        'p': p,
        'max_pages': max_pages,
    })


@login_required
def new_message(request):
    if not request.user.validated_email:
        return HttpResponseRedirect(reverse('messages'))
    if request.POST:
        raw_content = request.POST['content']
        content = strip_tags(raw_content)
        if len(content) == 0:
            return HttpResponseRedirect(reverse('messages'))
        raw_recipients = request.POST['recipients']
        recipients = []
        for recipient_name in raw_recipients.strip().split(','):
            try:
                recipient = models.KTUser.objects.get(username=recipient_name.strip())
            except models.KTUser.DoesNotExist:
                continue
            recipients.append(recipient)
        recipients = list(set(recipients))
        if len(recipients) == 0:
            return HttpResponseRedirect(reverse('messages'))
        owners = list(set(recipients + [request.user]))
        for owner in owners:
            message = models.Message.objects.create(
                sent_by=request.user,
                content=content,
                owned_by=owner,
                private=len(recipients)==1,
            )
            for recipient in recipients:
                message.sent_to.add(recipient)
            message.save()
        return HttpResponseRedirect(reverse('messages'))
    return render(request, 'ktapp/new_message.html')
