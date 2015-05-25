# -*- coding: utf-8 -*-

import datetime

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django import forms
from django.template.defaultfilters import slugify
from django.db.models import Sum

from ktapp import models
from ktapp import forms as kt_forms


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
        "comments": models.Comment.objects.filter(domain=models.Comment.DOMAIN_FILM)[:20],
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
    return render(request, "ktapp/film_subpages/film_main.html", {
        "active_tab": "main",
        "film": film,
        "rating": rating,
        "ratings": range(1, 6),
        "roles": film.filmartistrelationship_set.filter(role_type=models.FilmArtistRelationship.ROLE_TYPE_ACTOR),
        "votes": [film.vote_set.filter(rating=r) for r in range(1, 6)],
    })


def film_comments(request, id, film_slug):
    film = get_object_or_404(models.Film, pk=id)
    comment_form = kt_forms.CommentForm(initial={
        "domain": models.Comment.DOMAIN_FILM,
        "film": film,
        "topic": None,
        "poll": None,
        "reply_to": None,
    })
    comment_form.fields["domain"].widget = forms.HiddenInput()
    comment_form.fields["film"].widget = forms.HiddenInput()
    comment_form.fields["topic"].widget = forms.HiddenInput()
    comment_form.fields["poll"].widget = forms.HiddenInput()
    comment_form.fields["reply_to"].widget = forms.HiddenInput()
    return render(request, "ktapp/film_subpages/film_comments.html", {
        "active_tab": "comments",
        "film": film,
        "comments": film.comment_set.all(),
        "comment_form": comment_form,
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
        "awards": film.award_set.all(),
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
    pictures = film.picture_set.all()
    upload_form = kt_forms.PictureUploadForm(initial={
        "film": film,
    })
    upload_form.fields["film"].widget = forms.HiddenInput()
    context = {
        "active_tab": "pictures",
        "film": film,
        "pictures": pictures,
        "upload_form": upload_form,
    }
    if pictures.count() == 1:
        next_picture = _get_next_picture(pictures, pictures[0])
        context.update(_get_selected_picture_details(film, pictures[0], next_picture))
    return render(request, "ktapp/film_subpages/film_pictures.html", context)


def film_picture(request, id, film_slug, picture_id):
    film = get_object_or_404(models.Film, pk=id)
    picture = get_object_or_404(models.Picture, pk=picture_id)
    if picture.film != film:
        raise Http404
    pictures = film.picture_set.all()
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
    return HttpResponseRedirect(reverse("film_main", args=(film.pk, film.film_slug)))


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
        return HttpResponseRedirect(reverse("film_comments", args=(domain.pk, domain.film_slug)))
    elif domain_type == models.Comment.DOMAIN_TOPIC:
        return HttpResponseRedirect(reverse("forum", args=(domain.pk, slugify(domain.title))))
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
    return HttpResponseRedirect(reverse("film_quotes", args=(film.pk, film.film_slug)))


@login_required
def new_trivia(request):
    film = get_object_or_404(models.Film, pk=request.POST["film"])
    if request.POST:
        trivia_form = kt_forms.TriviaForm(data=request.POST)
        if trivia_form.is_valid():
            trivia = trivia_form.save(commit=False)
            trivia.created_by = request.user
            trivia.save()
    return HttpResponseRedirect(reverse("film_trivias", args=(film.pk, film.film_slug)))


@login_required
def new_review(request):
    film = get_object_or_404(models.Film, pk=request.POST["film"])
    if request.POST:
        review_form = kt_forms.ReviewForm(data=request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.created_by = request.user
            review.save()
    return HttpResponseRedirect(reverse("film_reviews", args=(film.pk, film.film_slug)))


@login_required
def new_picture(request):
    film = get_object_or_404(models.Film, pk=request.POST["film"])
    if request.POST:
        upload_form = kt_forms.PictureUploadForm(request.POST, request.FILES)
        if upload_form.is_valid():
            picture = upload_form.save(commit=False)
            picture.created_by = request.user
            picture.save()
    return HttpResponseRedirect(reverse("film_pictures", args=(film.pk, film.film_slug)))


def artist(request, id, name_slug):
    artist = get_object_or_404(models.Artist, pk=id)
    directions = artist.filmartistrelationship_set.filter(role_type=models.FilmArtistRelationship.ROLE_TYPE_DIRECTOR).order_by('-film__year', 'film__orig_title')
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
            director_vote_avg = 0
    else:
        director_vote_count = 0
    roles = artist.filmartistrelationship_set.filter(role_type=models.FilmArtistRelationship.ROLE_TYPE_ACTOR)
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
            actor_vote_avg = 0
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
        "awards": models.Award.objects.filter(artist=artist),
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
        return HttpResponseRedirect(reverse("list_of_topics"))
    comment_form = kt_forms.CommentForm(initial={
        "domain": models.Comment.DOMAIN_TOPIC,
        "film": None,
        "topic": topic,
        "poll": None,
        "reply_to": None,
    })
    comment_form.fields["domain"].widget = forms.HiddenInput()
    comment_form.fields["film"].widget = forms.HiddenInput()
    comment_form.fields["topic"].widget = forms.HiddenInput()
    comment_form.fields["poll"].widget = forms.HiddenInput()
    comment_form.fields["reply_to"].widget = forms.HiddenInput()
    return render(request, "ktapp/forum.html", {
        "topic": topic,
        "comments": topic.comment_set.all()[:100],
        "comment_form": comment_form,
    })


def latest_comments(request):
    return render(request, "ktapp/latest_comments.html", {
        "comments": models.Comment.objects.all()[:100],
    })


@login_required
def new_topic(request):
    if request.POST:
        topic_form = kt_forms.TopicForm(data=request.POST)
        if topic_form.is_valid():
            topic = topic_form.save(commit=False)
            topic.created_by = request.user
            topic.save()
            return HttpResponseRedirect(reverse("forum", args=(topic.pk, slugify(topic.title))))
    return HttpResponseRedirect(reverse("list_of_topics"))


def registration(request):
    if request.method == 'POST':
        form = kt_forms.UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            return HttpResponseRedirect(reverse("index"))
    else:
        form = kt_forms.UserCreationForm()
    return render(request, "ktapp/registration.html", {
        'form': form,
    })


def user_profile(request, id, name_slug):
    selected_user = get_object_or_404(models.KTUser, pk=id)
    if selected_user == request.user:
        return HttpResponseRedirect(reverse('user_profile_own'))
    return render(request, 'ktapp/user_profile.html', {
        'selected_user': selected_user,
        'last_votes': selected_user.votes().order_by('-when', '-id')[:20],
    })
