# -*- coding: utf-8 -*-

import datetime
import hashlib
import math
import json
from ipware.ip import get_ip

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
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
    hash_of_the_day = int(hashlib.md5(datetime.datetime.now().strftime('%Y-%m-%d')).hexdigest(), 16)
    # film of the day
    number_of_films = models.Film.objects.filter(main_poster__isnull=False, number_of_ratings__gte=10).count()
    film_no_of_the_day = hash_of_the_day % number_of_films
    try:
        film_of_the_day = models.Film.objects.filter(main_poster__isnull=False, number_of_ratings__gte=10).order_by('id')[film_no_of_the_day]
    except models.Film.DoesNotExist:
        film_of_the_day = models.Film.objects.get(id=1)
    # toplist of the day
    number_of_toplists = models.UserToplist.objects.filter(quality=True).count()
    toplist_no_of_the_day = hash_of_the_day % number_of_toplists
    try:
        toplist_of_the_day = models.UserToplist.objects.filter(quality=True).order_by('id')[toplist_no_of_the_day]
    except models.Film.DoesNotExist:
        toplist_of_the_day = models.UserToplist.objects.get(id=1)
    # buzz
    buzz_comment_domains = {}
    for comment in models.Comment.objects.all()[:100]:
        key = (comment.domain, comment.film_id, comment.topic_id, comment.poll_id)
        if key not in buzz_comment_domains:
            buzz_comment_domains[key] = (comment.id, comment.created_at)
        else:
            if comment.created_at > buzz_comment_domains[key][1]:
                buzz_comment_domains[key] = (comment.id, comment.created_at)
    buzz_comment_ids = [id for id, _ in sorted(buzz_comment_domains.values(), key=lambda x: x[1], reverse=True)[:10]]
    return render(request, 'ktapp/index.html', {
        'film': film_of_the_day,
        'toplist': toplist_of_the_day,
        'toplist_list': models.UserToplistItem.objects.filter(usertoplist=toplist_of_the_day).select_related('film', 'director', 'actor').order_by('serial_number'),
        'buzz_comments': models.Comment.objects.select_related('film', 'topic', 'poll', 'created_by', 'reply_to', 'reply_to__created_by').filter(id__in=buzz_comment_ids),
    })


def premiers(request):
    today = datetime.date.today()
    this_year = today.year
    offset = today.weekday()  # this Monday
    from_date = today - datetime.timedelta(days=offset+14)
    until_date = today - datetime.timedelta(days=offset-6)
    premier_list = []
    # TODO: add alternative premier dates
    for film in models.Film.objects.filter(main_premier__gte=from_date, main_premier__lte=until_date).order_by('-main_premier', 'orig_title', 'id'):
        if premier_list:
            if premier_list[-1][0] != film.main_premier:
                premier_list.append([film.main_premier, []])
        else:
            premier_list.append([film.main_premier, []])
        premier_list[-1][1].append(film)
    return render(request, 'ktapp/premiers.html', {
        'premier_list': premier_list,
        'premier_list_full': models.Film.objects.filter(main_premier_year=this_year).order_by('main_premier', 'orig_title', 'id'),
    })


def _list_of_films(request):
    qs = models.Film.objects
    no_filter = True

    title = kt_utils.strip_whitespace(request.GET.get('title', ''))
    if title:
        qs = qs.filter(
            Q(orig_title__icontains=title)
            | Q(second_title__icontains=title)
            | Q(third_title__icontains=title)
        )
        no_filter = False

    year = kt_utils.strip_whitespace(request.GET.get('year', ''))
    year_interval = kt_utils.str2interval(year, int)
    if year_interval:
        qs = qs.filter(year__range=year_interval)
        no_filter = False

    directors = kt_utils.strip_whitespace(request.GET.get('directors', '')).strip(',')
    for director_name in directors.split(','):
        if director_name.strip():
            try:
                director = models.Artist.objects.filter(name=director_name.strip())[0]
            except IndexError:
                director = None
            if director:
                qs = qs.filter(artists__id=director.id, filmartistrelationship__role_type=models.FilmArtistRelationship.ROLE_TYPE_DIRECTOR)
                no_filter = False

    actors = kt_utils.strip_whitespace(request.GET.get('actors', '')).strip(',')
    for actor_name in actors.split(','):
        if actor_name.strip():
            try:
                actor = models.Artist.objects.filter(name=actor_name.strip())[0]
            except IndexError:
                actor = None
            if actor:
                qs = qs.filter(artists__id=actor.id, filmartistrelationship__role_type=models.FilmArtistRelationship.ROLE_TYPE_ACTOR)
                no_filter = False

    countries = kt_utils.strip_whitespace(request.GET.get('countries', '')).strip(',')
    for country_name in countries.split(','):
        if country_name.strip():
            try:
                country = models.Keyword.objects.filter(name=country_name.strip(), keyword_type=models.Keyword.KEYWORD_TYPE_COUNTRY)[0]
            except IndexError:
                country = None
            if country:
                qs = qs.filter(keywords__id=country.id)
                no_filter = False

    genres = kt_utils.strip_whitespace(request.GET.get('genres', '')).strip(',')
    for genre_name in genres.split(','):
        if genre_name.strip():
            try:
                genre = models.Keyword.objects.filter(name=genre_name.strip(), keyword_type=models.Keyword.KEYWORD_TYPE_GENRE)[0]
            except IndexError:
                genre = None
            if genre:
                qs = qs.filter(keywords__id=genre.id)
                no_filter = False

    keywords = kt_utils.strip_whitespace(request.GET.get('keywords', '')).strip(',')
    for keyword_name in keywords.split(','):
        if keyword_name.strip():
            try:
                keyword = models.Keyword.objects.filter(name=keyword_name.strip(), keyword_type__in=[models.Keyword.KEYWORD_TYPE_MAJOR, models.Keyword.KEYWORD_TYPE_OTHER])[0]
            except IndexError:
                keyword = None
            if keyword:
                qs = qs.filter(keywords__id=keyword.id)
                no_filter = False

    try:
        avg_rating_min = float(kt_utils.strip_whitespace(request.GET.get('avg_rating_min', '')).replace(',', '.'))
    except ValueError:
        avg_rating_min = None
    try:
        avg_rating_max = float(kt_utils.strip_whitespace(request.GET.get('avg_rating_max', '')).replace(',', '.'))
    except ValueError:
        avg_rating_max = None
    avg_rating_interval = kt_utils.minmax2interval(avg_rating_min, avg_rating_max, 0.0, 5.0)
    if avg_rating_interval:
        qs = qs.filter(average_rating__range=avg_rating_interval)
        no_filter = False

    try:
        num_rating_min = int(kt_utils.strip_whitespace(request.GET.get('num_rating_min', '')))
    except ValueError:
        num_rating_min = None
    try:
        num_rating_max = int(kt_utils.strip_whitespace(request.GET.get('num_rating_max', '')))
    except ValueError:
        num_rating_max = None
    num_rating_interval = kt_utils.minmax2interval(num_rating_min, num_rating_max, 0, 99999)
    if num_rating_interval:
        qs = qs.filter(number_of_ratings__range=num_rating_interval)
        no_filter = False

    return (
        no_filter, qs,
        title, year,
        directors, actors,
        countries, genres, keywords,
        avg_rating_min, avg_rating_max,
        num_rating_min, num_rating_max
    )


def browse(request):
    (
        no_filter, qs,
        title, year,
        directors, actors,
        countries, genres, keywords,
        avg_rating_min, avg_rating_max,
        num_rating_min, num_rating_max
    ) = _list_of_films(request)
    if no_filter:
        error_type = ''
        results = []
        result_count = 0
    else:
        qs = qs.distinct()
        result_count = qs.count()
        if result_count > 1000:
            error_type = 'too_many'
            results = []
        else:
            error_type = 'ok'
            results = qs.order_by('orig_title', 'year', 'id')
    return render(request, 'ktapp/browse.html', {
        'title': title,
        'year': year,
        'directors': directors,
        'actors': actors,
        'countries': countries,
        'genres': genres,
        'keywords': keywords,
        'avg_rating_min': kt_utils.coalesce(avg_rating_min, ''),
        'avg_rating_max': kt_utils.coalesce(avg_rating_max, ''),
        'num_rating_min': kt_utils.coalesce(num_rating_min, ''),
        'num_rating_max': kt_utils.coalesce(num_rating_max, ''),
        'error_type': error_type,
        'result_count': result_count,
        'results': results,
    })


def search(request):
    q = request.GET.get('q')
    if not q:
        return HttpResponseRedirect(reverse('index'))
    results = []
    for result in models.Film.objects.filter(
            Q(orig_title__icontains=q)
            | Q(second_title__icontains=q)
            | Q(third_title__icontains=q)
    ):
        results.append({
            'rank': 1000 + result.number_of_ratings,
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


def _get_type_and_filter(request):
    today = datetime.date.today()
    this_year = today.year
    minimum_year = 1900
    minimum_premier = 1970
    toplist_type = request.GET.get('tipus', '')
    if toplist_type not in {'legjobb', 'ismeretlen', 'legrosszabb', 'legerdekesebb', 'legnezettebb'}:
        toplist_type = 'legjobb'
    try:
        year = int(request.GET.get('ev', '')) / 10 * 10
    except ValueError:
        year = None
    if year:
        if year > this_year / 10 * 10:
            year = this_year / 10 * 10
        if year < minimum_year:
            year = minimum_year - 10
        return toplist_type, 'ev', year
    try:
        premier = int(request.GET.get('bemutato', ''))
    except ValueError:
        premier = None
    if premier:
        if premier > this_year:
            premier = this_year
        if premier < minimum_premier:
            premier = minimum_premier
        return toplist_type, 'bemutato', premier
    try:
        country = models.Keyword.objects.get(slug_cache=request.GET.get('orszag', ''), keyword_type=models.Keyword.KEYWORD_TYPE_COUNTRY)
    except models.Keyword.DoesNotExist:
        country = None
    if country:
        return toplist_type, 'orszag', country
    try:
        genre = models.Keyword.objects.get(slug_cache=request.GET.get('mufaj', ''), keyword_type=models.Keyword.KEYWORD_TYPE_GENRE)
    except models.Keyword.DoesNotExist:
        genre = None
    if genre:
        return toplist_type, 'mufaj', genre
    return toplist_type, '', ''


def _get_film_list(toplist_type, filter_type, filter_value):
    thresholds = {
        'legjobb': 100,
        'ismeretlen': 30,
        'legrosszabb': 100,
        'legerdekesebb': 50,
        'legnezettebb': 100,
    }
    qs = models.Film.objects
    if filter_type == 'ev':
        qs = qs.filter(year__range=(filter_value, filter_value+9))
    elif filter_type == 'bemutato':
        qs = qs.filter(main_premier_year=filter_value)
    elif filter_type in {'orszag', 'mufaj'}:
        qs = models.FilmKeywordRelationship.objects.filter(keyword__id=filter_value.id)

    if filter_type in {'orszag', 'mufaj'}:
        if toplist_type == 'legjobb':
            if qs.filter(film__number_of_ratings__gte=thresholds[toplist_type]).filter(film__average_rating__gte=3.5).count() >= 50:
                qs = qs.filter(film__number_of_ratings__gte=thresholds[toplist_type]).filter(film__average_rating__gte=3.5)
            elif qs.filter(film__number_of_ratings__gte=thresholds[toplist_type]/2).filter(film__average_rating__gte=3.5).count() >= 20:
                qs = qs.filter(film__number_of_ratings__gte=thresholds[toplist_type]/2).filter(film__average_rating__gte=3.5)
            else:
                qs = qs.filter(film__number_of_ratings__gte=10).filter(film__average_rating__gte=3.5)
            qs = qs.order_by('-film__average_rating')
        elif toplist_type == 'ismeretlen':
            qs = qs.filter(film__number_of_ratings__lt=thresholds[toplist_type]).filter(film__number_of_ratings__gte=10)
            qs = qs.order_by('-film__average_rating')
        elif toplist_type == 'legrosszabb':
            if qs.filter(film__number_of_ratings__gte=thresholds[toplist_type]).filter(film__average_rating__lte=2.5).count() >= 50:
                qs = qs.filter(film__number_of_ratings__gte=thresholds[toplist_type]).filter(film__average_rating__lte=2.5)
            elif qs.filter(film__number_of_ratings__gte=thresholds[toplist_type]/2).filter(film__average_rating__lte=2.5).count() >= 20:
                qs = qs.filter(film__number_of_ratings__gte=thresholds[toplist_type]/2).filter(film__average_rating__lte=2.5)
            else:
                qs = qs.filter(film__number_of_ratings__gte=10).filter(film__average_rating__lte=2.5)
            qs = qs.order_by('film__average_rating')
        elif toplist_type == 'legerdekesebb':
            if qs.filter(film__number_of_comments__gte=thresholds[toplist_type]).count() >= 50:
                qs = qs.filter(film__number_of_comments__gte=thresholds[toplist_type])
            elif qs.filter(film__number_of_comments__gte=thresholds[toplist_type]/2).count() >= 20:
                qs = qs.filter(film__number_of_comments__gte=thresholds[toplist_type]/2)
            else:
                qs = qs.filter(film__number_of_comments__gte=10)
            qs = qs.order_by('-film__number_of_comments')
        elif toplist_type == 'legnezettebb':
            if qs.filter(film__number_of_ratings__gte=thresholds[toplist_type]).count() >= 50:
                qs = qs.filter(film__number_of_ratings__gte=thresholds[toplist_type])
            elif qs.filter(film__number_of_ratings__gte=thresholds[toplist_type]/2).count() >= 20:
                qs = qs.filter(film__number_of_ratings__gte=thresholds[toplist_type]/2)
            else:
                qs = qs.filter(film__number_of_ratings__gte=10)
            qs = qs.order_by('-film__number_of_ratings')
    else:
        if toplist_type == 'legjobb':
            if qs.filter(number_of_ratings__gte=thresholds[toplist_type]).filter(average_rating__gte=3.5).count() >= 50:
                qs = qs.filter(number_of_ratings__gte=thresholds[toplist_type]).filter(average_rating__gte=3.5)
            elif qs.filter(number_of_ratings__gte=thresholds[toplist_type]/2).filter(average_rating__gte=3.5).count() >= 20:
                qs = qs.filter(number_of_ratings__gte=thresholds[toplist_type]/2).filter(average_rating__gte=3.5)
            else:
                qs = qs.filter(number_of_ratings__gte=10).filter(average_rating__gte=3.5)
            qs = qs.order_by('-average_rating')
        elif toplist_type == 'ismeretlen':
            qs = qs.filter(number_of_ratings__lt=thresholds[toplist_type]).filter(number_of_ratings__gte=10)
            qs = qs.order_by('-average_rating')
        elif toplist_type == 'legrosszabb':
            if qs.filter(number_of_ratings__gte=thresholds[toplist_type]).filter(average_rating__lte=2.5).count() >= 50:
                qs = qs.filter(number_of_ratings__gte=thresholds[toplist_type]).filter(average_rating__lte=2.5)
            elif qs.filter(number_of_ratings__gte=thresholds[toplist_type]/2).filter(average_rating__lte=2.5).count() >= 20:
                qs = qs.filter(number_of_ratings__gte=thresholds[toplist_type]/2).filter(average_rating__lte=2.5)
            else:
                qs = qs.filter(number_of_ratings__gte=10).filter(average_rating__lte=2.5)
            qs = qs.order_by('average_rating')
        elif toplist_type == 'legerdekesebb':
            if qs.filter(number_of_comments__gte=thresholds[toplist_type]).count() >= 50:
                qs = qs.filter(number_of_comments__gte=thresholds[toplist_type])
            elif qs.filter(number_of_comments__gte=thresholds[toplist_type]/2).count() >= 20:
                qs = qs.filter(number_of_comments__gte=thresholds[toplist_type]/2)
            else:
                qs = qs.filter(number_of_comments__gte=10)
            qs = qs.order_by('-number_of_comments')
        elif toplist_type == 'legnezettebb':
            if qs.filter(number_of_ratings__gte=thresholds[toplist_type]).count() >= 50:
                qs = qs.filter(number_of_ratings__gte=thresholds[toplist_type])
            elif qs.filter(number_of_ratings__gte=thresholds[toplist_type]/2).count() >= 20:
                qs = qs.filter(number_of_ratings__gte=thresholds[toplist_type]/2)
            else:
                qs = qs.filter(number_of_ratings__gte=10)
            qs = qs.order_by('-number_of_ratings')
    return qs


def top_films(request):
    today = datetime.date.today()
    this_year = today.year
    minimum_year = 1900
    minimum_premier = 1970
    toplist_type, filter_type, filter_value = _get_type_and_filter(request)
    qs = _get_film_list(toplist_type, filter_type, filter_value)
    if filter_type in {'orszag', 'mufaj'}:
        films = [x.film for x in qs[:250]]
    else:
        films = qs[:250]
    links = []
    if filter_type == 'ev':
        links.append((1890, '-1899'))
        # links.append((1900, '-1909'))
        # links.append((1910, '-1919'))
        for y in range(minimum_year, this_year, 10):
            links.append((y, '%s-%s' % (y, unicode(y + 9)[2:])))
    elif filter_type == 'bemutato':
        for y in range(minimum_premier, this_year + 1):
            links.append((y, y))
    elif filter_type == 'orszag':
        for c in models.Keyword.objects.filter(keyword_type=models.Keyword.KEYWORD_TYPE_COUNTRY).order_by('name'):
            links.append((c.slug_cache, c.name))
    elif filter_type == 'mufaj':
        for g in models.Keyword.objects.filter(keyword_type=models.Keyword.KEYWORD_TYPE_GENRE).order_by('name'):
            links.append((g.slug_cache, g.name))
    return render(request, 'ktapp/top_films.html', {
        'active_tab': filter_type,
        'type': toplist_type,
        'filter_type': filter_type,
        'filter_value': filter_value.slug_cache if filter_type in {'orszag', 'mufaj'} else filter_value,
        'default_filter_values': {
            'ev': this_year / 10 * 10,
            'bemutato': this_year,
            'orszag': 'magyar',
            'mufaj': 'akciofilm',
        },
        'links': links,
        'films': films,
    })


def film_main(request, id, film_slug):
    film = get_object_or_404(models.Film, pk=id)
    rating = 0
    special_users = set()
    if request.user.is_authenticated():
        special_users.add(request.user.id)
        for friend in request.user.get_follows():
            special_users.add(friend.id)
        try:
            vote = models.Vote.objects.get(film=film, user=request.user)
            rating = vote.rating
        except models.Vote.DoesNotExist:
            pass
    votes = []
    for idx, r in enumerate(range(5, 0, -1)):
        votes.append(([], []))
        for u in film.vote_set.filter(rating=r).select_related('user').order_by('user__username'):
            if u.user.id in special_users:
                votes[idx][0].append(u)
            else:
                votes[idx][1].append(u)
    utls = models.UserToplistItem.objects.filter(film=film).select_related('usertoplist', 'usertoplist__created_by').order_by('-usertoplist__ordered', 'serial_number', 'usertoplist__title', 'usertoplist__id')
    my_wishes = dict((wish_type[0], False) for wish_type in models.Wishlist.WISH_TYPES)
    wish_count = [0, 0]
    for wish in models.Wishlist.objects.filter(film=film):
        if wish.wish_type == models.Wishlist.WISH_TYPE_YES:
            wish_count[0] += 1
        if wish.wish_type == models.Wishlist.WISH_TYPE_NO:
            wish_count[1] += 1
        if wish.wished_by_id == request.user.id:
            my_wishes[wish.wish_type] = True
    return render(request, 'ktapp/film_subpages/film_main.html', {
        'active_tab': 'main',
        'film': film,
        'rating': rating,
        'ratings': range(1, 6),
        'roles': film.filmartistrelationship_set.filter(role_type=models.FilmArtistRelationship.ROLE_TYPE_ACTOR).select_related('artist').order_by('role_name'),
        'votes': zip(
            [film.num_specific_rating(r) for r in range(5, 0, -1)],
            votes,
        ),
        'special_users': special_users,
        'my_wishes': my_wishes,
        'wish_count': wish_count,
        'utls': utls,
        'premier_types': models.PremierType.objects.all().order_by('name'),
        'other_premiers': film.other_premiers(),
        'permission_edit_film': kt_utils.check_permission('edit_film', request.user),
        'permission_edit_premiers': kt_utils.check_permission('edit_premiers', request.user),
        'permission_new_role': kt_utils.check_permission('new_role', request.user),
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
    comments_qs = film.comment_set.select_related('created_by', 'reply_to', 'reply_to__created_by')
    if max_pages > 1:
        first_comment = film.number_of_comments - COMMENTS_PER_PAGE * (p - 1) - (COMMENTS_PER_PAGE - 1)
        last_comment = film.number_of_comments - COMMENTS_PER_PAGE * (p - 1)
        comments = comments_qs.filter(serial_number__lte=last_comment, serial_number__gte=first_comment)
    else:
        comments = comments_qs.all()
    reply_to_comment = None
    reply_to_id = None
    if request.GET.get('valasz'):
        try:
            reply_to_comment = models.Comment.objects.get(id=request.GET.get('valasz'))
            reply_to_id = reply_to_comment.id
        except models.Comment.DoesNotExist:
            pass
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
        'permission_edit_film': kt_utils.check_permission('edit_film', request.user),
    })


def film_quotes(request, id, film_slug):
    film = get_object_or_404(models.Film, pk=id)
    quote_form = kt_forms.QuoteForm(initial={'film': film})
    quote_form.fields['film'].widget = forms.HiddenInput()
    return render(request, 'ktapp/film_subpages/film_quotes.html', {
        'active_tab': 'quotes',
        'film': film,
        'quotes': film.quote_set.all(),
        'quote_form': quote_form,
        'permission_new_quote': kt_utils.check_permission('new_quote', request.user),
        'permission_edit_film': kt_utils.check_permission('edit_film', request.user),
    })


def film_trivias(request, id, film_slug):
    film = get_object_or_404(models.Film, pk=id)
    trivia_form = kt_forms.TriviaForm(initial={'film': film})
    trivia_form.fields['film'].widget = forms.HiddenInput()
    return render(request, 'ktapp/film_subpages/film_trivias.html', {
        'active_tab': 'trivias',
        'film': film,
        'trivias': film.trivia_set.all(),
        'trivia_form': trivia_form,
        'permission_new_trivia': kt_utils.check_permission('new_trivia', request.user),
        'permission_edit_film': kt_utils.check_permission('edit_film', request.user),
    })


def film_reviews(request, id, film_slug):
    film = get_object_or_404(models.Film, pk=id)
    review_form = kt_forms.ReviewForm(initial={'film': film})
    review_form.fields['film'].widget = forms.HiddenInput()
    return render(request, 'ktapp/film_subpages/film_reviews.html', {
        'active_tab': 'reviews',
        'film': film,
        'reviews': film.review_set.filter(approved=True).all(),
        'unapproved_reviews': film.review_set.filter(approved=False).all(),
        'review_form': review_form,
        'permission_new_review': kt_utils.check_permission('new_review', request.user),
        'permission_approve_review': kt_utils.check_permission('approve_review', request.user),
        'permission_edit_film': kt_utils.check_permission('edit_film', request.user),
    })


def film_review(request, id, film_slug, review_id):
    film = get_object_or_404(models.Film, pk=id)
    review = get_object_or_404(models.Review, pk=review_id, approved=True)
    if review.film != film:
        raise Http404
    return render(request, 'ktapp/film_subpages/film_review.html', {
        'active_tab': 'reviews',
        'film': film,
        'review': review,
        'permission_edit_film': kt_utils.check_permission('edit_film', request.user),
    })


def film_awards(request, id, film_slug):
    film = get_object_or_404(models.Film, pk=id)
    return render(request, 'ktapp/film_subpages/film_awards.html', {
        'active_tab': 'awards',
        'film': film,
        'awards': film.award_set.all().order_by('name', 'year', 'category'),
        'permission_edit_film': kt_utils.check_permission('edit_film', request.user),
    })


def film_links(request, id, film_slug):
    film = get_object_or_404(models.Film, pk=id)
    return render(request, 'ktapp/film_subpages/film_links.html', {
        'active_tab': 'links',
        'film': film,
        'links_official': film.link_set.filter(link_type=models.Link.LINK_TYPE_OFFICIAL),
        'links_reviews': film.link_set.filter(link_type=models.Link.LINK_TYPE_REVIEWS),
        'links_interviews': film.link_set.filter(link_type=models.Link.LINK_TYPE_INTERVIEWS),
        'links_other': film.link_set.filter(link_type=models.Link.LINK_TYPE_OTHER),
        'permission_edit_film': kt_utils.check_permission('edit_film', request.user),
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
        'picture': picture,
        'next_picture': next_picture,
        'pic_height': models.Picture.THUMBNAIL_SIZES['max'][1],
        'artists': picture.artists.all(),
        'film_title_article': 'az' if film.orig_title[:1].lower() in u'aáeéiíoóöőuúüű' else 'a',
    }


def film_pictures(request, id, film_slug):
    film = get_object_or_404(models.Film, pk=id)
    pictures = sorted(film.picture_set.all(), key=lambda pic: (pic.order_key, pic.id))
    upload_form = kt_forms.PictureUploadForm(initial={'film': film})
    upload_form.fields['film'].widget = forms.HiddenInput()
    context = {
        'active_tab': 'pictures',
        'film': film,
        'pictures': pictures,
        'upload_form': upload_form,
        'all_artists_in_film': film.artists.all(),
        'permission_new_picture': kt_utils.check_permission('new_picture', request.user),
        'permission_edit_picture': kt_utils.check_permission('edit_picture', request.user),
        'permission_delete_picture': kt_utils.check_permission('delete_picture', request.user),
        'permission_edit_film': kt_utils.check_permission('edit_film', request.user),
    }
    if len(pictures) == 1:
        next_picture = _get_next_picture(pictures, pictures[0])
        context.update(_get_selected_picture_details(film, pictures[0], next_picture))
    return render(request, 'ktapp/film_subpages/film_pictures.html', context)


def film_picture(request, id, film_slug, picture_id):
    film = get_object_or_404(models.Film, pk=id)
    picture = get_object_or_404(models.Picture, pk=picture_id)
    if picture.film != film:
        raise Http404
    pictures = sorted(film.picture_set.all(), key=lambda pic: (pic.order_key, pic.id))
    next_picture = _get_next_picture(pictures, picture)
    upload_form = kt_forms.PictureUploadForm(initial={'film': film})
    upload_form.fields['film'].widget = forms.HiddenInput()
    context = {
        'active_tab': 'pictures',
        'film': film,
        'pictures': pictures,
        'upload_form': upload_form,
        'all_artists_in_film': film.artists.all(),
        'permission_new_picture': kt_utils.check_permission('new_picture', request.user),
        'permission_edit_picture': kt_utils.check_permission('edit_picture', request.user),
        'permission_delete_picture': kt_utils.check_permission('delete_picture', request.user),
        'permission_edit_film': kt_utils.check_permission('edit_film', request.user),
    }
    context.update(_get_selected_picture_details(film, picture, next_picture))
    return render(request, 'ktapp/film_subpages/film_pictures.html', context)


def film_keywords(request, id, film_slug):
    film = get_object_or_404(models.Film, pk=id)
    rating = 0
    if request.user.is_authenticated():
        try:
            vote = models.Vote.objects.get(film=film, user=request.user)
            rating = vote.rating
        except models.Vote.DoesNotExist:
            pass
    major_keywords = models.FilmKeywordRelationship.objects.filter(film=film, keyword__keyword_type=models.Keyword.KEYWORD_TYPE_MAJOR)
    other_keywords = models.FilmKeywordRelationship.objects.filter(film=film, keyword__keyword_type=models.Keyword.KEYWORD_TYPE_OTHER)
    if rating == 0:  # hide spoiler keywords
        major_keywords = major_keywords.exclude(spoiler=True)
        other_keywords = other_keywords.exclude(spoiler=True)
    return render(request, 'ktapp/film_subpages/film_keywords.html', {
        'active_tab': 'keywords',
        'film': film,
        'major_keywords': [(x.keyword, x.spoiler) for x in major_keywords.order_by('keyword__name', 'keyword__id')],
        'other_keywords': [(x.keyword, x.spoiler) for x in other_keywords.order_by('keyword__name', 'keyword__id')],
        'permission_edit_film': kt_utils.check_permission('edit_film', request.user),
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


@login_required
@kt_utils.kt_permission_required('delete_picture')
def delete_picture(request):
    picture = get_object_or_404(models.Picture, pk=request.POST['picture'])
    if request.POST:
        picture.delete()
    return HttpResponseRedirect(reverse('film_pictures', args=(picture.film.pk, picture.film.slug_cache)))


@login_required
@kt_utils.kt_permission_required('new_film')
def new_film(request):
    if request.POST:
        film_orig_title = kt_utils.strip_whitespace(request.POST.get('film_orig_title', ''))
        if film_orig_title == '':
            return render(request, 'ktapp/new_film.html', {
                'permission_edit_premiers': kt_utils.check_permission('edit_premiers', request.user),
            })
        state_before = {}
        film = models.Film.objects.create(
            orig_title=film_orig_title,
            created_by=request.user,
        )
        film.second_title = kt_utils.strip_whitespace(request.POST.get('film_second_title', ''))
        film.third_title = kt_utils.strip_whitespace(request.POST.get('film_third_title', ''))
        try:
            film_year = int(request.POST.get('film_year', None))
        except ValueError:
            film_year = None
        if film_year == 0:
            film_year = None
        film.year = film_year

        if kt_utils.check_permission('edit_premiers', request.user):
            main_premier = kt_utils.strip_whitespace(request.POST.get('main_premier', ''))
            if len(main_premier) == 4 and main_premier.isdigit():
                film.main_premier = None
                film.main_premier_year = int(main_premier)
            elif len(main_premier) == 10 and kt_utils.is_date(main_premier):
                film.main_premier = main_premier
                film.main_premier_year = int(main_premier[:4])

        directors = set()
        for director_name in kt_utils.strip_whitespace(request.POST.get('film_directors', '')).split(','):
            if director_name.strip() == '':
                continue
            director = models.Artist.get_artist_by_name(director_name.strip())
            if director is None:
                director = models.Artist.objects.create(name=director_name.strip())
            directors.add(director)
        for director in directors:
            models.FilmArtistRelationship.objects.create(
                film=film,
                artist=director,
                role_type=models.FilmArtistRelationship.ROLE_TYPE_DIRECTOR,
                created_by=request.user,
            )

        for type_name, type_code in [('countries', 'C'), ('genres', 'G')]:
            new_keywords = set()
            new_keyword_spoiler = {}
            for keyword_name in kt_utils.strip_whitespace(request.POST.get(type_name, '')).split(','):
                keyword_name = keyword_name.strip()
                if keyword_name.endswith('*'):
                    spoiler = True
                    keyword_name = keyword_name[:-1]
                else:
                    spoiler = False
                if not keyword_name:
                    continue
                if type_code not in {'M', 'O'}:
                    spoiler = False
                if request.user.is_staff:
                    keyword, created = models.Keyword.objects.get_or_create(
                        name=keyword_name,
                        keyword_type=type_code,
                    )
                    if created:
                        keyword.created_by = request.user
                        keyword.save()
                else:
                    try:
                        keyword = models.Keyword.objects.get(
                            name=keyword_name,
                            keyword_type=type_code,
                        )
                    except models.Keyword.DoesNotExist:
                        keyword = None
                if keyword:
                    new_keywords.add(keyword.id)
                    new_keyword_spoiler[keyword.id] = spoiler
            for keyword_id in new_keywords:
                models.FilmKeywordRelationship.objects.create(
                    film=film,
                    keyword=models.Keyword.objects.get(id=keyword_id),
                    created_by=request.user,
                    spoiler=new_keyword_spoiler[keyword_id],
                )

        film.plot_summary = request.POST.get('film_plot', '').strip()

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
            request.user,
            'new_film',
            'film:%s' % film.id,
            state_before, state_after
        )
        return HttpResponseRedirect(reverse('film_main', args=(film.id, film.slug_cache)))
    return render(request, 'ktapp/new_film.html', {
        'permission_edit_premiers': kt_utils.check_permission('edit_premiers', request.user),
    })


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
            if director_name.strip() == '':
                continue
            director = models.Artist.get_artist_by_name(director_name.strip())
            if director is None:
                director = models.Artist.objects.create(name=director_name.strip())
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


@login_required
@kt_utils.kt_permission_required('edit_film')
def edit_keywords(request):
    film = get_object_or_404(models.Film, id=request.POST.get('film_id', 0))
    if request.POST:
        for type_name, type_code in [('countries', 'C'), ('genres', 'G'), ('major_keywords', 'M'), ('other_keywords', 'O')]:
            old_keywords = set()
            for keyword in models.FilmKeywordRelationship.objects.filter(film=film, keyword__keyword_type=type_code):
                old_keywords.add(keyword.keyword.id)
            new_keywords = set()
            new_keyword_spoiler = {}
            for keyword_name in kt_utils.strip_whitespace(request.POST.get(type_name, '')).split(','):
                keyword_name = keyword_name.strip()
                if keyword_name.endswith('*'):
                    spoiler = True
                    keyword_name = keyword_name[:-1]
                else:
                    spoiler = False
                if not keyword_name:
                    continue
                if type_code not in {'M', 'O'}:
                    spoiler = False
                if type_code in {'C', 'G'} and not request.user.is_staff:
                    try:
                        keyword = models.Keyword.objects.get(
                            name=keyword_name,
                            keyword_type=type_code,
                        )
                    except models.Keyword.DoesNotExist:
                        keyword = None
                else:
                    keyword, created = models.Keyword.objects.get_or_create(
                        name=keyword_name,
                        keyword_type=type_code,
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


def artist_main(request, id, name_slug):
    artist = get_object_or_404(models.Artist, pk=id)
    try:
        random_picture = artist.picture_set.all().order_by('?')[0]
    except IndexError:
        random_picture = None
    if request.POST:
        if kt_utils.check_permission('edit_artist', request.user):
            artist_name = kt_utils.strip_whitespace(request.POST.get('artist_name', ''))
            artist_gender = kt_utils.strip_whitespace(request.POST.get('artist_gender', ''))
            if artist_gender in ['U', 'M', 'F']:
                artist.name = artist_name
                artist.gender = artist_gender
                artist.save()
            return HttpResponseRedirect(reverse('artist', args=(artist.id, artist.slug_cache)))
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
    normal_name = artist.name
    similar_artists = [a for a in models.Artist.objects.filter(name=normal_name) if a != artist]
    if ' ' in normal_name:
        reversed_name = '%s %s' % (normal_name[normal_name.index(' ')+1:], normal_name[:normal_name.index(' ')])
        similar_artists += [a for a in models.Artist.objects.filter(name=reversed_name)]
        similar_artists = set(similar_artists)
    return render(request, 'ktapp/artist.html', {
        'artist': artist,
        'random_picture': random_picture,
        'directions': directions,
        'roles': roles,
        'director_vote_count': director_vote_count,
        'actor_vote_count': actor_vote_count,
        'director_vote_avg': director_vote_avg,
        'actor_vote_avg': actor_vote_avg,
        'awards': models.Award.objects.filter(artist=artist).order_by('name', 'year', 'category'),
        'biographies': models.Biography.objects.filter(artist=artist, approved=True),
        'unapproved_biographies': models.Biography.objects.filter(artist=artist, approved=False),
        'similar_artists': similar_artists,
        'permission_edit_artist': kt_utils.check_permission('edit_artist', request.user),
        'permission_merge_artist': kt_utils.check_permission('merge_artist', request.user),
        'permission_approve_bio': kt_utils.check_permission('approve_bio', request.user),
    })


def artist_pictures(request, id, name_slug):
    artist = get_object_or_404(models.Artist, pk=id)
    pictures = sorted(artist.picture_set.all(), key=lambda pic: (-pic.film.year, pic.film.orig_title, pic.id))
    context = {
        'artist': artist,
        'pictures': pictures,
    }
    if len(pictures) == 1:
        picture = pictures[0]
        next_picture = _get_next_picture(pictures, picture)
        context.update(_get_selected_picture_details(picture.film, picture, next_picture))
        context.update({'film': picture.film})
    return render(request, 'ktapp/artist_pictures.html', context)


def artist_picture(request, id, name_slug, picture_id):
    artist = get_object_or_404(models.Artist, pk=id)
    picture = get_object_or_404(models.Picture, pk=picture_id)
    pictures = sorted(artist.picture_set.all(), key=lambda pic: (-pic.film.year, pic.film.orig_title, pic.id))
    next_picture = _get_next_picture(pictures, picture)
    context = {
        'artist': artist,
        'film': picture.film,
        'pictures': pictures,
    }
    context.update(_get_selected_picture_details(picture.film, picture, next_picture))
    return render(request, 'ktapp/artist_pictures.html', context)


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


def role(request, id, name_slug):
    role = get_object_or_404(models.FilmArtistRelationship, pk=id)
    if request.POST:
        if kt_utils.check_permission('edit_role', request.user):
            role_name = kt_utils.strip_whitespace(request.POST.get('role_name', ''))
            role_type = kt_utils.strip_whitespace(request.POST.get('role_type', ''))
            if role_name != '' and role_type in ['F', 'V']:
                role.role_name = role_name
                role.actor_subtype = role_type
                role.save()
            return HttpResponseRedirect(reverse('role', args=(role.id, role.slug_cache)))
    return render(request, 'ktapp/role.html', {
        'role': role,
        'permission_edit_role': kt_utils.check_permission('edit_role', request.user),
        'permission_delete_role': kt_utils.check_permission('delete_role', request.user),
    })


@login_required
@kt_utils.kt_permission_required('new_role')
def new_role(request):
    if request.POST:
        role_name = kt_utils.strip_whitespace(request.POST.get('role_name', ''))
        role_type = kt_utils.strip_whitespace(request.POST.get('role_type', ''))
        role_artist = kt_utils.strip_whitespace(request.POST.get('role_artist', ''))
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


@login_required
@kt_utils.kt_permission_required('delete_role')
def delete_role(request):
    role = get_object_or_404(models.FilmArtistRelationship, id=request.POST.get('role', 0))
    if request.POST:
        role.delete()
    return HttpResponseRedirect(reverse('film_main', args=(role.film.id, role.film.slug_cache)))


def list_of_topics(request):
    return render(request, 'ktapp/list_of_topics.html', {
        'topics': models.Topic.objects.all().select_related('last_comment', 'last_comment__created_by'),
        'topic_form': kt_forms.TopicForm(),
        'permission_new_topic': kt_utils.check_permission('new_topic', request.user),
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
    comments_qs = topic.comment_set.select_related('created_by', 'reply_to', 'reply_to__created_by')
    if max_pages > 1:
        first_comment = topic.number_of_comments - COMMENTS_PER_PAGE * (p - 1) - (COMMENTS_PER_PAGE - 1)
        last_comment = topic.number_of_comments - COMMENTS_PER_PAGE * (p - 1)
        comments = comments_qs.filter(serial_number__lte=last_comment, serial_number__gte=first_comment)
    else:
        comments = comments_qs.all()
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
    return render(request, 'ktapp/latest_comments.html', {
        'comments': models.Comment.objects.select_related('film', 'topic', 'poll', 'created_by', 'reply_to', 'reply_to__created_by').all()[:100],
    })


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


@login_required
def favourites(request):
    favourites = []
    favourite_ids = []
    for fav in request.user.get_follows().order_by('username', 'id'):
        favourites.append(fav)
        favourite_ids.append(fav.id)
    return render(request, 'ktapp/favourites.html', {
        'favourites': favourites,
        'latest_votes': models.Vote.objects.filter(user__in=favourite_ids).select_related('user', 'film').order_by('-when', '-id')[:50],
        'latest_comments': models.Comment.objects.filter(created_by__in=favourite_ids).select_related('film', 'topic', 'poll', 'created_by', 'reply_to', 'reply_to__created_by').all()[:20],
    })


def usertoplists(request):
    return render(request, 'ktapp/usertoplists.html', {
        'usertoplists': models.UserToplist.objects.all().select_related('created_by').order_by('-created_at'),
    })


def usertoplist(request, id, title_slug):
    toplist = get_object_or_404(models.UserToplist, pk=id)
    toplist_list = []
    with_comments = False
    for item in models.UserToplistItem.objects.filter(usertoplist=toplist).select_related('film', 'director', 'actor').order_by('serial_number'):
        toplist_list.append(item)
        if item.comment:
            with_comments = True
    return render(request, 'ktapp/usertoplist.html', {
        'toplist': toplist,
        'toplist_list': toplist_list,
        'with_comments': with_comments,
    })


def polls(request):
    poll_type = kt_utils.strip_whitespace(request.GET.get('tipus', ''))
    if poll_type not in {'aktualis', 'regi', 'leendo'}:
        poll_type = 'aktualis'
    polls_qs = models.Poll.objects.select_related('created_by')

    if poll_type == 'leendo':
        polls_w = polls_qs.filter(state=models.Poll.STATE_WAITING_FOR_APPROVAL)
        polls_a = polls_qs.filter(state=models.Poll.STATE_APPROVED)
        return render(request, 'ktapp/polls_admin.html', {
            'polls_w': polls_w.order_by('-created_at'),
            'polls_a': polls_a.order_by('-created_at'),
        })

    if poll_type == 'aktualis':
        polls = polls_qs.filter(state=models.Poll.STATE_OPEN).order_by('-open_from')
    else:
        polls = polls_qs.filter(state=models.Poll.STATE_CLOSED).order_by('-open_until')
    return render(request, 'ktapp/polls.html', {
        'poll_type': poll_type,
        'polls': polls,
    })


def poll(request, id, title_slug):
    selected_poll = get_object_or_404(models.Poll, pk=id, state__in=['O', 'C'])
    pollchoices_qs = models.PollChoice.objects.filter(poll=selected_poll)
    if selected_poll.state == 'O':
        pollchoices_qs = pollchoices_qs.order_by('serial_number')
    else:
        pollchoices_qs = pollchoices_qs.order_by('-number_of_votes', 'choice', 'id')
    pollchoices_raw = []
    sum_number_of_votes = 0
    max_number_of_votes = 0
    for pollchoice in pollchoices_qs:
        pollchoices_raw.append(pollchoice)
        sum_number_of_votes += pollchoice.number_of_votes
        max_number_of_votes = max(max_number_of_votes, pollchoice.number_of_votes)
    pollchoices = []
    for pollchoice in pollchoices_raw:
        pollchoices.append((
            pollchoice,
            100.0 * pollchoice.number_of_votes / sum_number_of_votes if sum_number_of_votes > 0 else None,
            int(300.0 * pollchoice.number_of_votes / max_number_of_votes) if max_number_of_votes > 0 else 0,
        ))
    return render(request, 'ktapp/poll.html', {
        'poll': selected_poll,
        'pollchoices': pollchoices,
        'sum_number_of_votes': sum_number_of_votes,
        'comments': models.Comment.objects.filter(domain=models.Comment.DOMAIN_POLL, poll=selected_poll).select_related('created_by', 'reply_to', 'reply_to__created_by'),
    })


def registration(request):

    def is_valid_email(email):
        try:
            validate_email(email)
        except ValidationError:
            return False
        return True

    next_url = request.GET.get('next', request.POST.get('next', request.META.get('HTTP_REFERER')))
    error_type = ''
    username = kt_utils.strip_whitespace(request.POST.get('username', ''))
    email = kt_utils.strip_whitespace(request.POST.get('email', ''))
    nickname = request.POST.get('nickname', '')
    if request.method == 'POST':
        if nickname != '':
            error_type = 'robot'
        elif username == '':
            error_type = 'name_empty'
        elif ',' in username or ';' in username:
            error_type = 'name_invalid'
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
            ip = get_ip(request)
            user.ip_at_registration = ip
            user.ip_at_last_login = ip
            user.last_activity_at = datetime.datetime.now()
            user.save()
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
        elif not password:
            error_type = 'password_empty'
        else:
            user = kt_utils.custom_authenticate(models.KTUser, username_or_email, password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    ip = get_ip(request)
                    user.ip_at_last_login = ip
                    user.last_activity_at = datetime.datetime.now()
                    user.save()
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
    if request.user.is_authenticated():
        number_of_messages = models.Message.objects.filter(private=True).filter(owned_by=request.user).filter(Q(sent_by=selected_user) | Q(sent_to=selected_user)).count()
    else:
        number_of_messages = 0
    this_year = datetime.date.today().year
    number_of_votes = selected_user.vote_set.count()
    number_of_vapiti_votes = selected_user.vote_set.filter(film__main_premier_year=this_year).count()
    return render(request, 'ktapp/user_profile_subpages/user_profile.html', {
        'active_tab': 'profile',
        'selected_user': selected_user,
        'number_of_votes': number_of_votes,
        'number_of_comments': selected_user.comment_set.count(),
        'number_of_wishes': selected_user.wishlist_set.count(),
        'number_of_messages': number_of_messages,
        'number_of_vapiti_votes': number_of_vapiti_votes,
        'vapiti_weight': number_of_votes + 25 * number_of_vapiti_votes,
        'tab_width': 20 if request.user.is_authenticated() and request.user.id != selected_user.id else 25,
        'latest_votes': selected_user.votes().select_related('film').order_by('-when', '-id')[:10],
        'latest_comments': models.Comment.objects.select_related('film', 'topic', 'poll', 'created_by', 'reply_to', 'reply_to__created_by').filter(created_by=selected_user)[:10],
    })


def user_films(request, id, name_slug):
    selected_user = get_object_or_404(models.KTUser, pk=id)
    if request.user.is_authenticated():
        number_of_messages = models.Message.objects.filter(private=True).filter(owned_by=request.user).filter(Q(sent_by=selected_user) | Q(sent_to=selected_user)).count()
    else:
        number_of_messages = 0

    qs = models.Vote.objects.filter(user=selected_user).select_related('film')

    title = kt_utils.strip_whitespace(request.GET.get('title', ''))
    if title:
        qs = qs.filter(
            Q(film__orig_title__icontains=title)
            | Q(film__second_title__icontains=title)
            | Q(film__third_title__icontains=title)
        )

    year = kt_utils.strip_whitespace(request.GET.get('year', ''))
    year_interval = kt_utils.str2interval(year, int)
    if year_interval:
        qs = qs.filter(film__year__range=year_interval)

    directors = kt_utils.strip_whitespace(request.GET.get('directors', '')).strip(',')
    for director_name in directors.split(','):
        if director_name.strip():
            try:
                director = models.Artist.objects.filter(name=director_name.strip())[0]
            except IndexError:
                director = None
            if director:
                qs = qs.filter(film__artists__id=director.id, film__filmartistrelationship__role_type=models.FilmArtistRelationship.ROLE_TYPE_DIRECTOR)

    actors = kt_utils.strip_whitespace(request.GET.get('actors', '')).strip(',')
    for actor_name in actors.split(','):
        if actor_name.strip():
            try:
                actor = models.Artist.objects.filter(name=actor_name.strip())[0]
            except IndexError:
                actor = None
            if actor:
                qs = qs.filter(film__artists__id=actor.id, film__filmartistrelationship__role_type=models.FilmArtistRelationship.ROLE_TYPE_ACTOR)

    countries = kt_utils.strip_whitespace(request.GET.get('countries', '')).strip(',')
    for country_name in countries.split(','):
        if country_name.strip():
            try:
                country = models.Keyword.objects.filter(name=country_name.strip(), keyword_type=models.Keyword.KEYWORD_TYPE_COUNTRY)[0]
            except IndexError:
                country = None
            if country:
                qs = qs.filter(film__keywords__id=country.id)

    genres = kt_utils.strip_whitespace(request.GET.get('genres', '')).strip(',')
    for genre_name in genres.split(','):
        if genre_name.strip():
            try:
                genre = models.Keyword.objects.filter(name=genre_name.strip(), keyword_type=models.Keyword.KEYWORD_TYPE_GENRE)[0]
            except IndexError:
                genre = None
            if genre:
                qs = qs.filter(film__keywords__id=genre.id)

    keywords = kt_utils.strip_whitespace(request.GET.get('keywords', '')).strip(',')
    for keyword_name in keywords.split(','):
        if keyword_name.strip():
            try:
                keyword = models.Keyword.objects.filter(name=keyword_name.strip(), keyword_type__in=[models.Keyword.KEYWORD_TYPE_MAJOR, models.Keyword.KEYWORD_TYPE_OTHER])[0]
            except IndexError:
                keyword = None
            if keyword:
                qs = qs.filter(film__keywords__id=keyword.id)

    try:
        avg_rating_min = float(kt_utils.strip_whitespace(request.GET.get('avg_rating_min', '')).replace(',', '.'))
    except ValueError:
        avg_rating_min = None
    try:
        avg_rating_max = float(kt_utils.strip_whitespace(request.GET.get('avg_rating_max', '')).replace(',', '.'))
    except ValueError:
        avg_rating_max = None
    avg_rating_interval = kt_utils.minmax2interval(avg_rating_min, avg_rating_max, 0.0, 5.0)
    if avg_rating_interval:
        qs = qs.filter(film__average_rating__range=avg_rating_interval)

    try:
        num_rating_min = int(kt_utils.strip_whitespace(request.GET.get('num_rating_min', '')))
    except ValueError:
        num_rating_min = None
    try:
        num_rating_max = int(kt_utils.strip_whitespace(request.GET.get('num_rating_max', '')))
    except ValueError:
        num_rating_max = None
    num_rating_interval = kt_utils.minmax2interval(num_rating_min, num_rating_max, 0, 99999)
    if num_rating_interval:
        qs = qs.filter(film__number_of_ratings__range=num_rating_interval)

    qs = qs.distinct()
    result_count = qs.count()

    try:
        p = int(request.GET.get('p', 0))
    except ValueError:
        p = 0
    max_pages = int(math.ceil(1.0 * result_count / 100))
    if max_pages == 0:
        max_pages = 1
    if p == 0:
        p = 1
    if p > max_pages:
        p = max_pages

    results = qs.order_by('-when', '-id', 'film__orig_title', 'film__year', 'film__id')[(p-1) * 100:p * 100]
    return render(request, 'ktapp/user_profile_subpages/user_films.html', {
        'active_tab': 'films',
        'selected_user': selected_user,
        'number_of_votes': selected_user.vote_set.count(),
        'number_of_comments': selected_user.comment_set.count(),
        'number_of_wishes': selected_user.wishlist_set.count(),
        'number_of_messages': number_of_messages,
        'tab_width': 20 if request.user.is_authenticated() and request.user.id != selected_user.id else 25,
        'result_count': result_count,
        'querystring': {
            'title': title,
            'year': year,
            'directors': directors,
            'actors': actors,
            'countries': countries,
            'genres': genres,
            'keywords': keywords,
            'avg_rating_min': kt_utils.coalesce(avg_rating_min, ''),
            'avg_rating_max': kt_utils.coalesce(avg_rating_max, ''),
            'num_rating_min': kt_utils.coalesce(num_rating_min, ''),
            'num_rating_max': kt_utils.coalesce(num_rating_max, ''),
        },
        'p': p,
        'max_pages': max_pages,
        'results': results,
    })


def user_comments(request, id, name_slug):
    selected_user = get_object_or_404(models.KTUser, pk=id)
    if request.user.is_authenticated():
        number_of_messages = models.Message.objects.filter(private=True).filter(owned_by=request.user).filter(Q(sent_by=selected_user) | Q(sent_to=selected_user)).count()
    else:
        number_of_messages = 0
    number_of_comments = selected_user.comment_set.count()
    p = int(request.GET.get('p', 0))
    if p == 1:
        return HttpResponseRedirect(reverse('user_comments', args=(selected_user.id, selected_user.slug_cache)))
    max_pages = int(math.ceil(1.0 * number_of_comments / COMMENTS_PER_PAGE))
    if max_pages == 0:
        max_pages = 1
    if p == 0:
        p = 1
    if p > max_pages:
        return HttpResponseRedirect(reverse('user_comments', args=(selected_user.id, selected_user.slug_cache)) + '?p=' + str(max_pages))
    return render(request, 'ktapp/user_profile_subpages/user_comments.html', {
        'active_tab': 'comments',
        'selected_user': selected_user,
        'number_of_votes': selected_user.vote_set.count(),
        'number_of_comments': number_of_comments,
        'number_of_wishes': selected_user.wishlist_set.count(),
        'number_of_messages': number_of_messages,
        'tab_width': 20 if request.user.is_authenticated() and request.user.id != selected_user.id else 25,
        'comments': selected_user.comment_set.select_related('film', 'topic', 'poll', 'reply_to', 'reply_to__created_by').all().order_by('-created_at')[(p-1) * COMMENTS_PER_PAGE:p * COMMENTS_PER_PAGE],
        'p': p,
        'max_pages': max_pages,
    })


def user_wishlist(request, id, name_slug):
    selected_user = get_object_or_404(models.KTUser, pk=id)
    if request.user.is_authenticated():
        number_of_messages = models.Message.objects.filter(private=True).filter(owned_by=request.user).filter(Q(sent_by=selected_user) | Q(sent_to=selected_user)).count()
    else:
        number_of_messages = 0
    qs = models.Wishlist.objects.select_related('film').filter(wished_by=selected_user).order_by('film__orig_title', 'film__id')
    return render(request, 'ktapp/user_profile_subpages/user_wishlist.html', {
        'active_tab': 'wishlist',
        'selected_user': selected_user,
        'number_of_votes': selected_user.vote_set.count(),
        'number_of_comments': selected_user.comment_set.count(),
        'number_of_wishes': selected_user.wishlist_set.count(),
        'number_of_messages': number_of_messages,
        'tab_width': 20 if request.user.is_authenticated() and request.user.id != selected_user.id else 25,
        'wishlist_yes': qs.filter(wish_type=models.Wishlist.WISH_TYPE_YES),
        'wishlist_get': qs.filter(wish_type=models.Wishlist.WISH_TYPE_GET),
    })


@login_required()
def user_messages(request, id, name_slug):
    selected_user = get_object_or_404(models.KTUser, pk=id)
    messages_qs = models.Message.objects.filter(private=True).filter(owned_by=request.user).filter(
        Q(sent_by=selected_user)
        | Q(sent_to=selected_user)
    ).select_related('sent_by')
    number_of_messages = messages_qs.count()
    try:
        p = int(request.GET.get('p', 0))
    except ValueError:
        p = 0
    if p == 1:
        return HttpResponseRedirect(reverse('user_messages', args=(selected_user.id, selected_user.slug_cache)))
    max_pages = int(math.ceil(1.0 * number_of_messages / MESSAGES_PER_PAGE))
    if max_pages == 0:
        max_pages = 1
    if p == 0:
        p = 1
    if p > max_pages:
        return HttpResponseRedirect(reverse('user_messages', args=(selected_user.id, selected_user.slug_cache)) + '?p=' + str(max_pages))
    return render(request, 'ktapp/user_profile_subpages/user_messages.html', {
        'active_tab': 'messages',
        'selected_user': selected_user,
        'number_of_votes': selected_user.vote_set.count(),
        'number_of_comments': selected_user.comment_set.count(),
        'number_of_wishes': selected_user.wishlist_set.count(),
        'number_of_messages': number_of_messages,
        'tab_width': 20 if request.user.is_authenticated() and request.user.id != selected_user.id else 25,
        'messages': messages_qs.order_by('-sent_at')[(p-1) * MESSAGES_PER_PAGE:p * MESSAGES_PER_PAGE],
        'p': p,
        'max_pages': max_pages,
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
        token_object = models.PasswordToken.get_token(token)
        if token_object:
            if token_object.valid_until < datetime.datetime.now():
                error_type = 'invalid_token'
            else:
                if request.user.id:
                    if request.user.id != token_object.belongs_to.id:
                        logout(request)
                if not token_object.belongs_to.is_active:
                    error_type = 'ban'
        else:
            error_type = 'invalid_token'
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
    email = ''
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
                    email = user.email
        return render(request, 'ktapp/reset_password.html', {
            'page_type': 'ask',
            'error_type': error_type,
            'username': username_or_email,
            'email': email,
        })
    new_password1 = request.POST.get('new_password1', '')
    new_password2 = request.POST.get('new_password2', '')
    nickname = request.POST.get('nickname', '')
    token_object = None
    if len(token) != 64:
        error_type = 'short_token'
    else:
        token_object = models.PasswordToken.get_token(token)
        if token_object:
            if token_object.valid_until < datetime.datetime.now():
                error_type = 'invalid_token'
            else:
                if request.user.id:
                    if request.user.id != token_object.belongs_to.id:
                        logout(request)
                if not token_object.belongs_to.is_active:
                    error_type = 'ban'
        else:
            error_type = 'invalid_token'
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
    messages_qs = models.Message.objects.filter(owned_by=request.user).select_related('sent_by')
    number_of_messages = messages_qs.count()
    try:
        p = int(request.GET.get('p', 0))
    except ValueError:
        p = 0
    if p == 1:
        return HttpResponseRedirect(reverse('messages'))
    max_pages = int(math.ceil(1.0 * number_of_messages / MESSAGES_PER_PAGE))
    if max_pages == 0:
        max_pages = 1
    if p == 0:
        p = 1
    if p > max_pages:
        return HttpResponseRedirect(reverse('messages') + '?p=' + str(max_pages))
    request.user.last_message_checking_at = datetime.datetime.now()
    request.user.save()
    if request.user.is_staff:
        staff_ids = ','.join([str(u.id) for u in models.KTUser.objects.filter(is_staff=True).order_by('id')])
    else:
        staff_ids = ''
    return render(request, 'ktapp/messages.html', {
        'messages': messages_qs.order_by('-sent_at')[(p-1) * MESSAGES_PER_PAGE:p * MESSAGES_PER_PAGE],
        'p': p,
        'max_pages': max_pages,
        'staff_ids': staff_ids,
    })


@login_required
def new_message(request):
    next_url = request.GET.get('next', request.POST.get('next', reverse('messages')))
    if not request.user.validated_email:
        return HttpResponseRedirect(next_url)
    if request.POST:
        raw_content = request.POST['content']
        content = strip_tags(raw_content).strip()
        if len(content) == 0:
            return HttpResponseRedirect(next_url)
        raw_recipients = request.POST['recipients']
        recipients = set()
        for recipient_name in raw_recipients.strip().split(','):
            recipient = models.KTUser.get_user_by_name(recipient_name.strip())
            if recipient is None:
                continue
            recipients.add(recipient)
        if len(recipients) == 0:
            return HttpResponseRedirect(next_url)
        owners = recipients | {request.user}
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
        # TODO: check KTUser.email_notification
        # for recipient in recipients:
        #     recipient.email_user(
        #         texts.PM_EMAIL_SUBJECT.format(sent_by=request.user.username),
        #         texts.PM_EMAIL_BODY.format(
        #             username=recipient.username,
        #             sent_by=request.user.username,
        #             content=content,
        #         )
        #     )
        return HttpResponseRedirect(next_url)
    list_of_user_ids = request.GET.get('u', '')
    users = set()
    for raw_user_id in request.GET.get('u', '').split(','):
        try:
            user_id = int(raw_user_id.strip())
        except ValueError:
            continue
        try:
            user = models.KTUser.objects.get(id=user_id)
        except models.KTUser.DoesNotExist:
            continue
        users.add(user)
    return render(request, 'ktapp/new_message.html', {
        'list_of_recipients': sorted(list(users), key=lambda u: u.username.upper()),
    })


@login_required
@kt_utils.kt_permission_required('check_changes')
def changes(request):

    return render(request, 'ktapp/changes.html', {
        'changes': [{
            'created_by': c.created_by,
            'created_at': c.created_at,
            'action': c.action,
            'object': c.object,
            'object_type': c.object.split(':')[0],
            'object_id': c.object.split(':')[1],
            'state_before': sorted([(key, val) for key, val in json.loads(c.state_before).iteritems()]) if c.state_before else {},
            'state_after': sorted([(key, val) for key, val in json.loads(c.state_after).iteritems()]) if c.state_after else {},
        } for c in models.Change.objects.all().order_by('-id')[:100]],
    })
