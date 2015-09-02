# -*- coding: utf-8 -*-

import json

from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from ktapp import models
from ktapp import forms as kt_forms
from ktapp import utils as kt_utils


@require_POST
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


@require_POST
@login_required
def wish(request):
    film = get_object_or_404(models.Film, pk=request.POST['film_id'])
    wish_type = request.POST.get('wish_type', '')
    action = request.POST.get('action', '')
    if wish_type in [type_code for type_code, type_name in models.Wishlist.WISH_TYPES] and action in ['+', '-']:
        if action == '+':
            models.Wishlist.objects.get_or_create(film=film, wished_by=request.user, wish_type=wish_type)
        else:
            models.Wishlist.objects.filter(film=film, wished_by=request.user, wish_type=wish_type).delete()
    return HttpResponseRedirect(reverse('film_main', args=(film.pk, film.slug_cache)))


@require_POST
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


@require_POST
@login_required
@kt_utils.kt_permission_required('new_quote')
def new_quote(request):
    film = get_object_or_404(models.Film, pk=request.POST["film"])
    if request.POST:
        quote_form = kt_forms.QuoteForm(data=request.POST)
        if quote_form.is_valid():
            quote = quote_form.save(commit=False)
            quote.created_by = request.user
            quote.save()
    return HttpResponseRedirect(reverse("film_quotes", args=(film.pk, film.slug_cache)))


@require_POST
@login_required
@kt_utils.kt_permission_required('new_trivia')
def new_trivia(request):
    film = get_object_or_404(models.Film, pk=request.POST["film"])
    if request.POST:
        trivia_form = kt_forms.TriviaForm(data=request.POST)
        if trivia_form.is_valid():
            trivia = trivia_form.save(commit=False)
            trivia.created_by = request.user
            trivia.save()
    return HttpResponseRedirect(reverse("film_trivias", args=(film.pk, film.slug_cache)))


@require_POST
@login_required
@kt_utils.kt_permission_required('new_review')
def new_review(request):
    film = get_object_or_404(models.Film, pk=request.POST.get('film', 0))
    if request.POST:
        review_form = kt_forms.ReviewForm(data=request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.created_by = request.user
            review.save()
    return HttpResponseRedirect(reverse('film_reviews', args=(film.pk, film.slug_cache)))


@require_POST
@login_required
@kt_utils.kt_permission_required('approve_review')
def approve_review(request):
    film = get_object_or_404(models.Film, pk=request.POST.get('film_id', 0))
    if request.POST:
        review = get_object_or_404(models.Review, pk=request.POST.get('review_id', 0))
        if review.film == film:
            review.approved = True
            review.save()
    return HttpResponseRedirect(reverse('film_reviews', args=(film.pk, film.slug_cache)))


@require_POST
@login_required
@kt_utils.kt_permission_required('approve_review')
def disapprove_review(request):
    film = get_object_or_404(models.Film, pk=request.POST.get('film_id', 0))
    if request.POST:
        review = get_object_or_404(models.Review, pk=request.POST.get('review_id', 0))
        if review.film == film:
            comment = models.Comment(
                domain=models.Comment.DOMAIN_FILM,
                film=film,
                created_by=review.created_by,
                content=review.content,
            )
            comment.save(domain=film)
            review.film = film  # NOTE: this is needed, otherwise review.delete() will save the original values of the film (e.g. old number_of_comments)
            review.delete()
    return HttpResponseRedirect(reverse('film_comments', args=(film.pk, film.slug_cache)))


@require_POST
@login_required
@kt_utils.kt_permission_required('new_picture')
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


@require_POST
@login_required
@kt_utils.kt_permission_required('edit_picture')
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


@require_POST
@login_required
@kt_utils.kt_permission_required('delete_picture')
def delete_picture(request):
    picture = get_object_or_404(models.Picture, pk=request.POST['picture'])
    if request.POST:
        picture.delete()
    return HttpResponseRedirect(reverse('film_pictures', args=(picture.film.pk, picture.film.slug_cache)))


@require_POST
@login_required
@kt_utils.kt_permission_required('edit_film')
def edit_film(request):
    film = get_object_or_404(models.Film, id=request.POST.get('film_id', 0))
    if request.POST:
        state_before = {
            'orig_title': film.orig_title,
            'second_title': film.second_title,
            'third_title': film.third_title,
            'year': film.year,
            'imdb_link': film.imdb_link,
            'porthu_link': int(film.porthu_link) if film.porthu_link else None,
            'wikipedia_link_en': film.wikipedia_link_en,
            'wikipedia_link_hu': film.wikipedia_link_hu,
        }
        film_orig_title = kt_utils.strip_whitespace(request.POST.get('film_orig_title', ''))
        if film_orig_title:
            film.orig_title = film_orig_title
        film.second_title = kt_utils.strip_whitespace(request.POST.get('film_second_title', ''))
        film.third_title = kt_utils.strip_whitespace(request.POST.get('film_third_title', ''))
        try:
            film_year = int(request.POST.get('film_year', None))
        except ValueError:
            film_year = None
        if film_year == 0:
            film_year = None
        film.year = film_year
        directors = set()
        for director_name in kt_utils.strip_whitespace(request.POST.get('film_directors', '')).split(','):
            director_name = kt_utils.strip_whitespace_and_separator(director_name)
            if director_name == '':
                continue
            director = models.Artist.get_artist_by_name(director_name)
            if director is None:
                director = models.Artist.objects.create(name=director_name)
            directors.add(director)
        models.FilmArtistRelationship.objects.filter(film=film, role_type=models.FilmArtistRelationship.ROLE_TYPE_DIRECTOR).delete()
        for director in directors:
            models.FilmArtistRelationship.objects.create(
                film=film,
                artist=director,
                role_type=models.FilmArtistRelationship.ROLE_TYPE_DIRECTOR,
                created_by=request.user,
            )
        film_imdb_link = kt_utils.strip_whitespace(request.POST.get('film_imdb_link', ''))
        if film_imdb_link.startswith('tt'):
            film.imdb_link = film_imdb_link
        elif 'imdb.com' in film_imdb_link and '/tt' in film_imdb_link:
            film.imdb_link = film_imdb_link[film_imdb_link.index('/tt')+1:].split('/')[0]
        else:
            film.imdb_link = ''
        film_porthu_link = kt_utils.strip_whitespace(request.POST.get('film_porthu_link', ''))
        if film_porthu_link.isdigit():
            film.porthu_link = film_porthu_link
        elif 'i_film_id' in film_porthu_link:
            try:
                film.porthu_link = int(film_porthu_link[film_porthu_link.index('i_film_id')+10:].split('&')[0])
            except ValueError:
                film.porthu_link = None
        else:
            film.porthu_link = None
        film.wikipedia_link_en = kt_utils.strip_whitespace(request.POST.get('film_wikipedia_link_en', ''))
        film.wikipedia_link_hu = kt_utils.strip_whitespace(request.POST.get('film_wikipedia_link_hu', ''))
        film.save()
        state_after = {
            'orig_title': film.orig_title,
            'second_title': film.second_title,
            'third_title': film.third_title,
            'year': film.year,
            'imdb_link': film.imdb_link,
            'porthu_link': int(film.porthu_link) if film.porthu_link else None,
            'wikipedia_link_en': film.wikipedia_link_en,
            'wikipedia_link_hu': film.wikipedia_link_hu,
        }
        kt_utils.changelog(
            models.Change,
            request.user,
            'edit_film',
            'film:%s' % film.id,
            state_before, state_after
        )
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@require_POST
@login_required
@kt_utils.kt_permission_required('edit_film')
def edit_plot(request):
    film = get_object_or_404(models.Film, id=request.POST.get('film_id', 0))
    if request.POST:
        state_before = {
            'plot_summary': film.plot_summary,
        }
        plot = request.POST.get('plot', '').strip()
        film.plot_summary = plot
        film.save()
        state_after = {
            'plot_summary': film.plot_summary,
        }
        kt_utils.changelog(
            models.Change,
            request.user,
            'edit_film',
            'film:%s' % film.id,
            state_before, state_after
        )
    return HttpResponseRedirect(reverse('film_main', args=(film.id, film.slug_cache)))


@require_POST
@login_required
@kt_utils.kt_permission_required('edit_premiers')
def edit_premiers(request):
    film = get_object_or_404(models.Film, id=request.POST.get('film_id', 0))
    if request.POST:
        state_before = {
            'main_premier': film.main_premier.strftime('%Y-%m-%d') if film.main_premier else None,
            'main_premier_year': film.main_premier_year,
        }
        main_premier = kt_utils.strip_whitespace(request.POST.get('main_premier', ''))
        if len(main_premier) == 4 and main_premier.isdigit():
            film.main_premier = None
            film.main_premier_year = main_premier
            film.save()
        elif len(main_premier) == 10 and kt_utils.is_date(main_premier):
            film.main_premier = main_premier
            film.main_premier_year = int(main_premier[:4])
            film.save()
        elif main_premier == '':
            film.main_premier = None
            film.main_premier_year = None
            film.save()
        state_after = {
            'main_premier': film.main_premier,
            'main_premier_year': film.main_premier_year,
        }
        kt_utils.changelog(
            models.Change,
            request.user,
            'edit_premiers',
            'film:%s' % film.id,
            state_before, state_after
        )

        for p in film.other_premiers():
            premier_when = kt_utils.strip_whitespace(request.POST.get('other_premier_when_%s' % p.id, ''))
            try:
                premier_type = int(kt_utils.strip_whitespace(request.POST.get('other_premier_type_%s' % p.id, '0')))
            except ValueError:
                continue
            if premier_when == '':
                state_before = {
                    'premier_type': unicode(p.premier_type),
                    'when': p.when,
                }
                p.delete()
                state_after = {}
                kt_utils.changelog(
                    models.Change,
                    request.user,
                    'edit_premiers',
                    'film:%s' % film.id,
                    state_before, state_after
                )
            elif len(premier_when) == 10 and kt_utils.is_date(premier_when):
                try:
                    pt = models.PremierType.objects.get(id=premier_type)
                except models.PremierType.DoesNotExist:
                    pt = None
                if pt:
                    state_before = {
                        'premier_type': unicode(p.premier_type),
                        'when': p.when.strftime('%Y-%m-%d') if p.when else None,
                    }
                    p.when = premier_when
                    p.premier_type = pt
                    p.save()
                    state_after = {
                        'premier_type': unicode(p.premier_type),
                        'when': p.when,
                    }
                    kt_utils.changelog(
                        models.Change,
                        request.user,
                        'edit_premiers',
                        'film:%s' % film.id,
                        state_before, state_after
                    )
        for idx in xrange(1, 2):
            premier_when = kt_utils.strip_whitespace(request.POST.get('new_other_premier_when_%s' % idx, ''))
            try:
                premier_type = int(kt_utils.strip_whitespace(request.POST.get('new_other_premier_type_%s' % idx, '0')))
            except ValueError:
                continue
            if premier_when == '':
                continue
            elif len(premier_when) == 10 and kt_utils.is_date(premier_when):
                try:
                    pt = models.PremierType.objects.get(id=premier_type)
                except models.PremierType.DoesNotExist:
                    pt = None
                if pt:
                    state_before = {}
                    models.Premier.objects.create(
                        film=film,
                        when=premier_when,
                        premier_type=pt,
                    )
                    state_after = {
                        'premier_type': unicode(pt),
                        'when': premier_when,
                    }
                    kt_utils.changelog(
                        models.Change,
                        request.user,
                        'edit_premiers',
                        'film:%s' % film.id,
                        state_before, state_after
                    )
    return HttpResponseRedirect(reverse('film_main', args=(film.id, film.slug_cache)))


@require_POST
@login_required
@kt_utils.kt_permission_required('edit_film')
def edit_keywords(request):
    film = get_object_or_404(models.Film, id=request.POST.get('film_id', 0))
    if request.POST:
        for type_name, type_code in [('countries', 'C'), ('genres', 'G')]:
            old_keywords = set()
            for keyword in models.FilmKeywordRelationship.objects.filter(film=film, keyword__keyword_type=type_code):
                old_keywords.add(keyword.keyword.id)
            new_keywords = set()
            for keyword_name in kt_utils.strip_whitespace(request.POST.get(type_name, '')).split(','):
                keyword_name = kt_utils.strip_whitespace_and_separator(keyword_name)
                if keyword_name.endswith('*'):
                    keyword_name = keyword_name[:-1]
                if not keyword_name:
                    continue
                keyword = models.Keyword.get_keyword_by_name(keyword_name, type_code)
                if keyword:
                    new_keywords.add(keyword.id)
            for keyword_id in old_keywords - new_keywords:
                models.FilmKeywordRelationship.objects.filter(film=film, keyword__id=keyword_id).delete()
            for keyword_id in new_keywords - old_keywords:
                models.FilmKeywordRelationship.objects.create(
                    film=film,
                    keyword=models.Keyword.objects.get(id=keyword_id),
                    created_by=request.user,
                    spoiler=False,
                )
            for keyword_id in new_keywords & old_keywords:
                keyword = models.FilmKeywordRelationship.objects.filter(film=film, keyword__id=keyword_id)[0]
                keyword.spoiler = False
                keyword.save()
        # major and other keywords
        old_keywords = set()
        for keyword in models.FilmKeywordRelationship.objects.filter(film=film, keyword__keyword_type__in=(models.Keyword.KEYWORD_TYPE_MAJOR, models.Keyword.KEYWORD_TYPE_OTHER)):
            old_keywords.add(keyword.keyword.id)
        new_keywords = set()
        new_keyword_spoiler = {}
        for keyword_name in kt_utils.strip_whitespace(request.POST.get('keywords', '')).split(','):
            keyword_name = kt_utils.strip_whitespace_and_separator(keyword_name)
            if keyword_name.endswith('*'):
                spoiler = True
                keyword_name = keyword_name[:-1]
            else:
                spoiler = False
            if not keyword_name:
                continue
            keyword = models.Keyword.get_keyword_by_name(keyword_name, 'K')
            if keyword is None:
                keyword, created = models.Keyword.objects.get_or_create(
                    name=keyword_name,
                    keyword_type=models.Keyword.KEYWORD_TYPE_OTHER,
                )
                if created:
                    keyword.created_by = request.user
                    keyword.save()
            if keyword:
                new_keywords.add(keyword.id)
                new_keyword_spoiler[keyword.id] = spoiler
        for keyword_id in old_keywords - new_keywords:
            models.FilmKeywordRelationship.objects.filter(film=film, keyword__id=keyword_id).delete()
        for keyword_id in new_keywords - old_keywords:
            models.FilmKeywordRelationship.objects.create(
                film=film,
                keyword=models.Keyword.objects.get(id=keyword_id),
                created_by=request.user,
                spoiler=new_keyword_spoiler[keyword_id],
            )
        for keyword_id in new_keywords & old_keywords:
            keyword = models.FilmKeywordRelationship.objects.filter(film=film, keyword__id=keyword_id)[0]
            keyword.spoiler = new_keyword_spoiler[keyword_id]
            keyword.save()
    return HttpResponseRedirect(reverse('film_keywords', args=(film.id, film.slug_cache)))


@require_POST
@login_required
@kt_utils.kt_permission_required('merge_artist')
def merge_artist(request):
    artist_1 = get_object_or_404(models.Artist, id=request.POST.get('artist_1', 0))
    artist_2 = get_object_or_404(models.Artist, id=request.POST.get('artist_2', 0))
    if request.POST:
        if artist_1.id < artist_2.id:
            artist_to_delete = artist_2
            artist_to_leave = artist_1
        else:
            artist_to_delete = artist_1
            artist_to_leave = artist_2
        for role in artist_to_delete.filmartistrelationship_set.all():
            role.artist = artist_to_leave
            role.save()
        for bio in models.Biography.objects.filter(artist=artist_to_delete):
            bio.artist = artist_to_leave
            bio.save()
        for aw in models.Award.objects.filter(artist=artist_to_delete):
            aw.artist = artist_to_leave
            aw.save()
        for utli in models.UserToplistItem.objects.filter(director=artist_to_delete):
            utli.director = artist_to_leave
            utli.save()
        for utli in models.UserToplistItem.objects.filter(actor=artist_to_delete):
            utli.actor = artist_to_leave
            utli.save()
        if artist_to_leave.name != artist_to_delete.name:
            artist_to_leave.name = '%s / %s' % (artist_to_leave.name, artist_to_delete.name)
            artist_to_leave.save()
        artist_to_delete.delete()
        return HttpResponseRedirect(reverse('artist', args=(artist_to_leave.id, artist_to_leave.slug_cache)))
    return HttpResponseRedirect(reverse('artist', args=(artist_1.id, artist_1.slug_cache)))


@require_POST
@login_required
@kt_utils.kt_permission_required('new_role')
def new_role(request):
    if request.POST:
        role_name = kt_utils.strip_whitespace(request.POST.get('role_name', ''))  # NOTE: role name *can* contain , or ;
        role_type = kt_utils.strip_whitespace(request.POST.get('role_type', ''))
        role_artist = kt_utils.strip_whitespace_and_separator(request.POST.get('role_artist', ''))
        role_gender = kt_utils.strip_whitespace(request.POST.get('role_gender', ''))
        try:
            film = models.Film.objects.get(id=request.POST.get('film_id', 0))
        except models.Film.DoesNotExist:
            film = None
        if film and role_name != '' and role_type in ['F', 'V'] and role_artist != '' and ',' not in role_artist and role_gender in ['M', 'F']:
            artist = models.Artist.get_artist_by_name(role_artist)
            if artist is None:
                artist = models.Artist.objects.create(
                    name=role_artist,
                    gender=role_gender,
                )
            if artist.gender != role_gender:
                artist.gender = role_gender
                artist.save()
            models.FilmArtistRelationship.objects.create(
                film=film,
                artist=artist,
                role_type=models.FilmArtistRelationship.ROLE_TYPE_ACTOR,
                actor_subtype=role_type,
                role_name=role_name,
                created_by=request.user,
            )
            return HttpResponse(json.dumps({'success': True}), content_type='application/json')
    return HttpResponse(json.dumps({'success': False}), content_type='application/json')


@require_POST
@login_required
@kt_utils.kt_permission_required('delete_role')
def delete_role(request):
    role = get_object_or_404(models.FilmArtistRelationship, id=request.POST.get('role', 0))
    if request.POST:
        role.delete()
    return HttpResponseRedirect(reverse('film_main', args=(role.film.id, role.film.slug_cache)))


@require_POST
@login_required
@kt_utils.kt_permission_required('new_topic')
def new_topic(request):
    if request.POST:
        topic_form = kt_forms.TopicForm(data=request.POST)
        if topic_form.is_valid():
            topic = topic_form.save(commit=False)
            topic.created_by = request.user
            topic.save()
            return HttpResponseRedirect(reverse("forum", args=(topic.pk, topic.slug_cache)))
    return HttpResponseRedirect(reverse("list_of_topics"))


@require_POST
@login_required
def follow(request):
    next_url = request.GET.get('next', request.POST.get('next', request.META.get('HTTP_REFERER')))
    try:
        other_user = models.KTUser.objects.get(id=request.POST.get('whom', 0))
    except models.KTUser.DoesNotExist:
        return HttpResponseRedirect(next_url)
    models.Follow.objects.get_or_create(who=request.user, whom=other_user)
    return HttpResponseRedirect(next_url)


@require_POST
@login_required
def unfollow(request):
    next_url = request.GET.get('next', request.POST.get('next', request.META.get('HTTP_REFERER')))
    try:
        other_user = models.KTUser.objects.get(id=request.POST.get('whom', 0))
    except models.KTUser.DoesNotExist:
        return HttpResponseRedirect(next_url)
    models.Follow.objects.filter(who=request.user, whom=other_user).delete()
    return HttpResponseRedirect(next_url)


@require_POST
@login_required
def delete_message(request):
    next_url = request.GET.get('next', request.POST.get('next', request.META.get('HTTP_REFERER')))
    if request.user.validated_email:
        try:
            message = models.Message.objects.get(id=request.POST.get('message_id', 0), owned_by=request.user)
        except models.Message.DoesNotExist:
            return HttpResponseRedirect(next_url)
        is_private = message.private
        owned_by = message.owned_by
        other = message.recipients()[0]
        message.delete()
        if is_private:
            models.MessageCountCache.update_cache(owned_by=owned_by, partner=other)
            models.MessageCountCache.update_cache(owned_by=other, partner=owned_by)
    return HttpResponseRedirect(next_url)


@require_POST
@login_required
def poll_vote(request):
    poll = get_object_or_404(models.Poll, id=request.POST.get('poll', 0))
    if poll.state != models.Poll.STATE_OPEN:
        return HttpResponseForbidden()
    pollchoice = get_object_or_404(models.PollChoice, id=request.POST.get('pollchoice', 0))
    if request.POST.get('vote', 0) == '1':
        models.PollVote.objects.get_or_create(user=request.user, pollchoice=pollchoice)
    else:
        models.PollVote.objects.filter(user=request.user, pollchoice=pollchoice).delete()
    return HttpResponseRedirect(reverse('poll', args=(poll.id, poll.slug_cache)))
