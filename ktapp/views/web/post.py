# -*- coding: utf-8 -*-

import datetime
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
    try:
        film = get_object_or_404(models.Film, pk=request.POST['film_id'])
    except Http404:
        if request.POST.get('ajax', '') == '1':
            return HttpResponse(json.dumps({'success': False}), content_type='application/json')
        raise
    if not film.is_open_for_vote_from():
        if request.POST.get('ajax', '') == '1':
            return HttpResponse(json.dumps({'success': False}), content_type='application/json')
        raise
    try:
        rating = int(request.POST['rating'])
    except ValueError:
        rating = 0
    if rating < 0 or rating > 5:
        rating = 0
    fb = request.POST.get('fb', '0')
    if rating == 0:
        models.Vote.objects.filter(film=film, user=request.user).delete()
    elif 1 <= rating <= 5:
        vote, created = models.Vote.objects.get_or_create(film=film, user=request.user, defaults={
            'rating': rating,
            'shared_on_facebook': fb == '1',
        })
        vote.rating = rating
        if not created:  # don't reset shared_on_facebook once a vote has been shared
            if fb == '1':
                vote.shared_on_facebook = True
        vote.save()
    if request.POST.get('ajax', '') == '1':
        special_users = {request.user.id}
        for friend in request.user.get_follows():
            special_users.add(friend.id)
        votes = {}
        for idx, r in enumerate(range(5, 0, -1)):
            votes[r] = []
            for u in film.vote_set.filter(rating=r).select_related('user').order_by('user__username'):
                if u.user.id in special_users:
                    votes[r].append({
                        'username': u.user.username,
                        'url': reverse('user_profile', args=(u.user.id, u.user.slug_cache)),
                    })
        return HttpResponse(json.dumps({
            'success': True,
            'votes': votes,
            'rating': rating,
        }), content_type='application/json')
    return HttpResponseRedirect(reverse('film_main', args=(film.pk, film.slug_cache)))


@require_POST
@login_required
def edit_share_on_facebook(request):
    share_on_facebook = request.POST.get('share_on_facebook', '0')
    request.user.facebook_rating_share = (share_on_facebook == '1')
    request.user.save(update_fields=['facebook_rating_share'])
    return HttpResponse(json.dumps({'success': True}), content_type='application/json')


@require_POST
@login_required
def wish(request):
    try:
        film = get_object_or_404(models.Film, pk=request.POST['film_id'])
    except Http404:
        if request.POST.get('ajax', '') == '1':
            return HttpResponse(json.dumps({'success': False}), content_type='application/json')
        raise
    wish_type = request.POST.get('wish_type', '')
    action = request.POST.get('action', '')
    if wish_type in [type_code for type_code, type_name in models.Wishlist.WISH_TYPES] and action in {'+', '-'}:
        if action == '+':
            models.Wishlist.objects.get_or_create(film=film, wished_by=request.user, wish_type=wish_type)
        else:
            models.Wishlist.objects.filter(film=film, wished_by=request.user, wish_type=wish_type).delete()
    if request.POST.get('ajax', '') == '1':
        return HttpResponse(json.dumps({'success': True}), content_type='application/json')
    return HttpResponseRedirect(reverse('film_main', args=(film.pk, film.slug_cache)))


@require_POST
@login_required
def new_comment(request):
    domain_type = request.POST['domain']
    if domain_type == models.Comment.DOMAIN_FILM:
        domain = get_object_or_404(models.Film, pk=request.POST['film'])
    elif domain_type == models.Comment.DOMAIN_TOPIC:
        domain = get_object_or_404(models.Topic, pk=request.POST['topic'])
    elif domain_type == models.Comment.DOMAIN_POLL:
        domain = get_object_or_404(models.Poll, pk=request.POST['poll'])
    else:
        raise Http404
    if domain_type == models.Comment.DOMAIN_TOPIC:
        if domain.closed_until and domain.closed_until > datetime.datetime.now() and not request.user.is_game_master:
            return HttpResponseForbidden()
    comment_form = kt_forms.CommentForm(data=request.POST)
    if comment_form.is_valid():
        comment = comment_form.save(commit=False)
        comment.created_by = request.user
        comment.save(domain=domain)  # Comment model updates domain object
    if domain_type == models.Comment.DOMAIN_FILM:
        return HttpResponseRedirect(reverse('film_comments', args=(domain.pk, domain.slug_cache)))
    elif domain_type == models.Comment.DOMAIN_TOPIC:
        return HttpResponseRedirect(reverse('forum', args=(domain.pk, domain.slug_cache)))
    elif domain_type == models.Comment.DOMAIN_POLL:
        return HttpResponseRedirect(reverse('poll', args=(domain.pk, domain.slug_cache)))
    else:
        raise Http404


@require_POST
@login_required
def edit_comment(request):
    next_url = request.GET.get('next', request.POST.get('next', request.META.get('HTTP_REFERER')))
    comment = get_object_or_404(models.Comment, id=request.POST.get('comment_id', 0))
    if request.user.is_staff or (comment.created_by.id == request.user.id and comment.editable()):
        content = request.POST.get('content', '').strip()
        if content != '':
            comment.content = content
            comment.save()
        return HttpResponseRedirect(next_url)
    return HttpResponseForbidden()


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
            'open_for_vote_from': film.open_for_vote_from.strftime('%Y-%m-%d') if film.open_for_vote_from else None,
            'main_premier': film.main_premier.strftime('%Y-%m-%d') if film.main_premier else None,
            'main_premier_year': film.main_premier_year,
        }
        open_for_vote_from = kt_utils.strip_whitespace(request.POST.get('open_for_vote_from', ''))
        if len(open_for_vote_from) == 10 and kt_utils.is_date(open_for_vote_from):
            film.open_for_vote_from = open_for_vote_from
            film.save()
        elif open_for_vote_from == '':
            film.open_for_vote_from = None
            film.save()
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
            'open_for_vote_from': film.open_for_vote_from,
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
        film.fix_keywords()
    return HttpResponseRedirect(reverse('film_keywords', args=(film.id, film.slug_cache)))


@require_POST
@login_required
@kt_utils.kt_permission_required('edit_film')
def edit_sequels(request):
    film = get_object_or_404(models.Film, id=request.POST.get('film_id', 0))
    sequel_names_before = set(['(%s) %s' % (s.sequel_type, s.name) for s in film.all_sequels()])
    sequel_names_after = set()
    sequels_before = set([s.id for s in film.all_sequels()])
    sequels_after = set()
    for raw_sequel in request.POST.getlist('sequel', []):
        raw_sequel = kt_utils.strip_whitespace(raw_sequel)
        if raw_sequel == '':
            continue
        if raw_sequel[:3] in {'(A)', '(S)', '(R)'}:
            sequel_type = raw_sequel[1]
            sequel_name = raw_sequel[3:].strip()
        else:
            sequel_type = 'S'
            sequel_name = raw_sequel
        sequel, created = models.Sequel.objects.get_or_create(
            sequel_type=sequel_type,
            name=sequel_name,
        )
        if created:
            sequel.created_by = request.user
            sequel.save()
        sequels_after.add(sequel.id)
        sequel_names_after.add('(%s) %s' % (sequel.sequel_type, sequel.name))
    for sequel_id in sequels_before - sequels_after:
        models.FilmSequelRelationship.objects.filter(film=film, sequel_id=sequel_id).delete()
        if models.FilmSequelRelationship.objects.filter(sequel_id=sequel_id).count() == 0:
            models.Sequel.objects.get(id=sequel_id).delete()
    for sequel_id in sequels_after - sequels_before:
        models.FilmSequelRelationship.objects.create(
            film=film,
            sequel=models.Sequel.objects.get(id=sequel_id),
            created_by=request.user,
        )
    kt_utils.changelog(
        models.Change,
        request.user,
        'edit_sequels',
        'film:%s' % film.id,
        {'sequels': sorted(list(sequel_names_before))},
        {'sequels': sorted(list(sequel_names_after))},
    )
    return HttpResponseRedirect(reverse('film_main', args=(film.id, film.slug_cache)))


@require_POST
@login_required
@kt_utils.kt_permission_required('edit_film')
def new_award(request):
    film = get_object_or_404(models.Film, id=request.POST.get('film_id', 0))
    name = kt_utils.strip_whitespace(request.POST.get('name', ''))
    year = kt_utils.strip_whitespace(request.POST.get('year', ''))
    category = kt_utils.strip_whitespace(request.POST.get('category', ''))
    if name == '' or year == '' or category == '':
        return HttpResponseRedirect(reverse('film_awards', args=(film.id, film.slug_cache)))
    artist_name = kt_utils.strip_whitespace(request.POST.get('artist', ''))
    note = kt_utils.strip_whitespace(request.POST.get('note', ''))
    if artist_name:
        artist = models.Artist.get_artist_by_name(artist_name)
    else:
        artist = None
    if artist_name != '' and artist is None and note == '':
        note = artist_name
    models.Award.objects.create(
        film=film,
        name=name,
        year=year,
        category=category,
        artist=artist,
        note=note,
        created_by_id=request.user.id,
    )
    return HttpResponseRedirect(reverse('film_awards', args=(film.id, film.slug_cache)))


@require_POST
@login_required
@kt_utils.kt_permission_required('new_link')
def new_link(request):
    film_id = request.POST.get('film_id', 0)
    if film_id:
        film = get_object_or_404(models.Film, id=film_id)
    else:
        film = None
    name = kt_utils.strip_whitespace(request.POST.get('name', ''))
    url = kt_utils.strip_whitespace(request.POST.get('url', ''))
    if name == '' or url == '':
        if film:
            return HttpResponseRedirect(reverse('film_links', args=(film.id, film.slug_cache)))
        else:
            return HttpResponseRedirect(reverse('links'))
    link_type = kt_utils.strip_whitespace(request.POST.get('link_type', ''))
    if link_type not in {'R', 'I', 'O', '-'}:
        link_type = '-'
    lead = request.POST.get('lead', '').strip()
    author_name = kt_utils.strip_whitespace(request.POST.get('author', ''))
    author = models.KTUser.get_user_by_name(author_name)
    models.Link.objects.create(
        name=name,
        url=url,
        link_type=link_type,
        lead=lead,
        author=author,
        film=film,
        created_by_id=request.user.id,
        featured=True,
    )
    if film:
        return HttpResponseRedirect(reverse('film_links', args=(film.id, film.slug_cache)))
    else:
        return HttpResponseRedirect(reverse('links'))


@require_POST
@login_required
@kt_utils.kt_permission_required('suggest_link')
def suggest_link(request):
    film_id = request.POST.get('film_id', 0)
    if film_id:
        film = get_object_or_404(models.Film, id=film_id)
    else:
        film = None
    name = kt_utils.strip_whitespace(request.POST.get('name', ''))
    url = kt_utils.strip_whitespace(request.POST.get('url', ''))
    if name == '' or url == '':
        if film:
            return HttpResponseRedirect(reverse('film_links', args=(film.id, film.slug_cache)))
        else:
            return HttpResponseRedirect(reverse('links'))
    link_type = kt_utils.strip_whitespace(request.POST.get('link_type', ''))
    if link_type not in {'R', 'I', 'O', '-'}:
        link_type = '-'
    lead = request.POST.get('lead', '').strip()
    author_name = kt_utils.strip_whitespace(request.POST.get('author', ''))
    author = models.KTUser.get_user_by_name(author_name)

    models.SuggestedContent.objects.create(
        created_by=request.user,
        domain=models.SuggestedContent.DOMAIN_LINK,
        content=json.dumps({
            'name': name,
            'url': url,
            'link_type': link_type,
            'lead': lead,
            'author': {
                'id': author.id,
                'slug_cache': author.slug_cache,
                'username': author.username,
            } if author else None,
            'film': {
                'id': film.id,
                'slug_cache': film.slug_cache,
                'orig_title': film.orig_title,
                'year': film.year,
            } if film else None,
        }),
    )
    return HttpResponseRedirect(reverse('suggested_links'))


@require_POST
@login_required
@kt_utils.kt_permission_required('new_link')
def accept_link(request):
    suggested_content = get_object_or_404(models.SuggestedContent, id=request.POST.get('id', 0), domain=models.SuggestedContent.DOMAIN_LINK)
    content = json.loads(suggested_content.content)
    author = None
    if content['author']:
        try:
            author = models.KTUser.objects.get(id=content['author']['id'])
        except models.KTUser.DoesNotExist:
            pass
    film = None
    if content['film']:
        try:
            film = models.Film.objects.get(id=content['film']['id'])
        except models.Film.DoesNotExist:
            pass
    models.Link.objects.create(
        name=content['name'],
        url=content['url'],
        link_type=content['link_type'],
        lead=content['lead'],
        author=author,
        film=film,
        created_by=suggested_content.created_by,
        featured=request.POST.get('f', '0') == '1'
    )
    suggested_content.delete()
    return HttpResponseRedirect(reverse('suggested_links'))


@require_POST
@login_required
@kt_utils.kt_permission_required('new_link')
def reject_link(request):
    suggested_content = get_object_or_404(models.SuggestedContent, id=request.POST.get('id', 0), domain=models.SuggestedContent.DOMAIN_LINK)
    suggested_content.delete()
    return HttpResponseRedirect(reverse('suggested_links'))


@require_POST
@login_required
@kt_utils.kt_permission_required('new_film')
def accept_film(request):
    suggested_content = get_object_or_404(models.SuggestedContent, id=request.POST.get('id', 0), domain=models.SuggestedContent.DOMAIN_FILM)
    content = json.loads(suggested_content.content)
    film = models.Film.objects.create(
        created_by=suggested_content.created_by,
        orig_title=content['orig_title'],
        second_title=content['second_title'],
        third_title=content['third_title'],
        year=content['year'],
        main_premier=content['main_premier'],
        main_premier_year=content['main_premier_year'],
        plot_summary=content['plot_summary'],
        imdb_link=content['imdb_link'],
        porthu_link=content['porthu_link'],
        wikipedia_link_en=content['wikipedia_link_en'],
        wikipedia_link_hu=content['wikipedia_link_hu'],
    )

    directors = set()
    for director_name in content['directors'].split(','):
        director_name = kt_utils.strip_whitespace_and_separator(director_name)
        if director_name == '':
            continue
        director = models.Artist.get_artist_by_name(director_name)
        if director is None:
            director = models.Artist.objects.create(name=director_name)
        directors.add(director)
    for director in directors:
        models.FilmArtistRelationship.objects.create(
            film=film,
            artist=director,
            role_type=models.FilmArtistRelationship.ROLE_TYPE_DIRECTOR,
            created_by=suggested_content.created_by,
        )

    for keyword_str, type_code in [(content['countries'], 'C'), (content['genres'], 'G')]:
        new_keywords = set()
        for keyword_name in keyword_str.split(','):
            keyword_name = kt_utils.strip_whitespace_and_separator(keyword_name)
            if keyword_name.endswith('*'):
                keyword_name = keyword_name[:-1]
            if not keyword_name:
                continue
            keyword = models.Keyword.get_keyword_by_name(keyword_name, type_code)
            if keyword:
                new_keywords.add(keyword.id)
        for keyword_id in new_keywords:
            models.FilmKeywordRelationship.objects.create(
                film=film,
                keyword=models.Keyword.objects.get(id=keyword_id),
                created_by=suggested_content.created_by,
                spoiler=False,
            )
    film.fix_keywords()

    state_before = {}
    state_after = {
        'orig_title': film.orig_title,
        'second_title': film.second_title,
        'third_title': film.third_title,
        'year': film.year,
        'main_premier': film.main_premier,
        'main_premier_year': film.main_premier_year,
        'plot_summary': film.plot_summary,
        'imdb_link': film.imdb_link,
        'porthu_link': film.porthu_link,
        'wikipedia_link_en': film.wikipedia_link_en,
        'wikipedia_link_hu': film.wikipedia_link_hu,
    }
    kt_utils.changelog(
        models.Change,
        suggested_content.created_by,
        'new_film',
        'film:%s' % film.id,
        state_before, state_after
    )
    suggested_content.delete()
    return HttpResponseRedirect(reverse('film_main', args=(film.id, film.slug_cache)))


@require_POST
@login_required
@kt_utils.kt_permission_required('new_film')
def reject_film(request):
    suggested_content = get_object_or_404(models.SuggestedContent, id=request.POST.get('id', 0), domain=models.SuggestedContent.DOMAIN_FILM)
    suggested_content.delete()
    return HttpResponseRedirect(reverse('suggested_films'))


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
            role.save(update_fields=['artist'])
        for pic in models.Picture.objects.filter(artist=artist_to_delete):
            pic.artist = artist_to_leave
            pic.save(update_fields=['artist'])
        for bio in models.Biography.objects.filter(artist=artist_to_delete):
            bio.artist = artist_to_leave
            bio.save(update_fields=['artist'])
        for aw in models.Award.objects.filter(artist=artist_to_delete):
            aw.artist = artist_to_leave
            aw.save(update_fields=['artist'])
        for utli in models.UserToplistItem.objects.filter(director=artist_to_delete):
            utli.director = artist_to_leave
            utli.save(update_fields=['director'])
        for utli in models.UserToplistItem.objects.filter(actor=artist_to_delete):
            utli.actor = artist_to_leave
            utli.save(update_fields=['actor'])
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
    if request.user.id != other_user.id:
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


@require_POST
@login_required
@kt_utils.kt_permission_required('poll_admin')
def poll_archive(request):
    poll = get_object_or_404(models.Poll, id=request.POST.get('poll', 0))
    if poll.state != models.Poll.STATE_OPEN:
        return HttpResponseForbidden()
    poll.state = models.Poll.STATE_CLOSED
    poll.open_until = datetime.datetime.now()
    poll.save()
    return HttpResponseRedirect(reverse('poll', args=(poll.id, poll.slug_cache)))


@require_POST
@login_required
@kt_utils.kt_permission_required('poll_admin')
def poll_activate(request):
    poll = get_object_or_404(models.Poll, id=request.POST.get('poll', 0))
    if poll.state != models.Poll.STATE_APPROVED:
        return HttpResponseForbidden()
    poll.state = models.Poll.STATE_OPEN
    poll.open_from = datetime.datetime.now()
    poll.save()
    return HttpResponseRedirect(reverse('poll', args=(poll.id, poll.slug_cache)))


@require_POST
@login_required
@kt_utils.kt_permission_required('poll_admin')
def poll_support(request):
    poll = get_object_or_404(models.Poll, id=request.POST.get('poll', 0))
    if poll.state != models.Poll.STATE_WAITING_FOR_APPROVAL:
        return HttpResponseForbidden()
    nominated_by = set([int(id) for id in poll.nominated_by.split(',') if id != ''])
    if request.user.id not in nominated_by:
        poll.nominated_by = poll.nominated_by + unicode(request.user.id) + ','
        if len(nominated_by) + 1 >= 3:
            poll.state = models.Poll.STATE_APPROVED
        poll.save()
    return HttpResponseRedirect(reverse('polls') + '?tipus=leendo')


@require_POST
@login_required
@kt_utils.kt_permission_required('new_poll')
def new_poll(request):
    title = kt_utils.strip_whitespace(request.POST.get('title', ''))
    if title == '':
        return HttpResponseRedirect(reverse('polls') + '?tipus=leendo')
    choices = []
    for choice in request.POST.get('choices', '').strip().split('\n'):
        choice = kt_utils.strip_whitespace(choice)
        if choice == '':
            continue
        choices.append(choice)
    if len(choices) == 0:
        return HttpResponseRedirect(reverse('polls') + '?tipus=leendo')
    poll = models.Poll.objects.create(
        title=title,
        created_by=request.user,
        nominated_by=',%s,' % request.user.id,
        state=models.Poll.STATE_WAITING_FOR_APPROVAL,
    )
    for idx, choice in enumerate(choices):
        models.PollChoice.objects.create(
            poll=poll,
            choice=choice,
            serial_number=idx + 1,
        )
    return HttpResponseRedirect(reverse('polls') + '?tipus=leendo')


@require_POST
@login_required
@kt_utils.kt_permission_required('admin')
def move_to_off(request):
    off_topic = models.Topic.objects.get(id=87)
    domain_object = None
    domain = ''
    for id_str in kt_utils.strip_whitespace(request.POST.get('list_of_ids', '')).split(','):
        id_str = kt_utils.strip_whitespace(id_str)
        if id_str == '':
            continue
        try:
            comment = models.Comment.objects.get(id=id_str)
        except models.Comment.DoesNotExist:
            comment = None
        if comment:
            if domain_object is None:
                domain = comment.domain
                if comment.domain == models.Comment.DOMAIN_FILM:
                    domain_object = comment.film
                    url = request.build_absolute_uri(reverse('film_comments', args=(domain_object.id, domain_object.slug_cache)))
                    link_text = domain_object.orig_title
                elif comment.domain == models.Comment.DOMAIN_TOPIC:
                    domain_object = comment.topic
                    url = request.build_absolute_uri(reverse('topic', args=(domain_object.id, domain_object.slug_cache)))
                    link_text = domain_object.title
                elif comment.domain == models.Comment.DOMAIN_POLL:
                    domain_object = comment.poll
                    url = request.build_absolute_uri(reverse('poll', args=(domain_object.id, domain_object.slug_cache)))
                    link_text = domain_object.title
            if domain_object is None:
                continue
            comment.domain = 'T'
            comment.topic = off_topic
            comment.film_id = None
            comment.poll_id = None
            comment.rating = None
            comment.content += u'\n\n--\nÁthelyezve a(z) [link={url}]{link_text}[/link] topikból.'.format(
                url=url,
                link_text=link_text,
            )
            comment.save()
    if domain_object:
        models.Comment.fix_comments(domain, domain_object)
        models.Comment.fix_comments('T', off_topic)
    return HttpResponse(json.dumps({'success': True}), content_type='application/json')


@require_POST
@login_required
def close_topic(request):
    if not request.user.is_game_master:
        return HttpResponseForbidden()
    topic = get_object_or_404(models.Topic, id=request.POST.get('topic_id', 0))
    closed_until = kt_utils.strip_whitespace(request.POST.get('closed_until'))
    closed_until = closed_until[:16] + ':00'
    if len(closed_until) == 19 and kt_utils.is_datetime(closed_until):
        topic.closed_until = closed_until
    else:
        topic.closed_until = None
    topic.save(update_fields=['closed_until'])
    return HttpResponseRedirect(reverse('forum', args=(topic.id, topic.slug_cache)))
