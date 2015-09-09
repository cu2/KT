# -*- coding: utf-8 -*-

import datetime
import hashlib
import math
import json

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django import forms
from django.db.models import Q

from ktapp import models
from ktapp import forms as kt_forms
from ktapp import utils as kt_utils
from ktapp.helpers import filmlist


COMMENTS_PER_PAGE = 100
MESSAGES_PER_PAGE = 50


def index(request):
    hash_of_the_day = int(hashlib.md5(datetime.datetime.now().strftime('%Y-%m-%d')).hexdigest(), 16)
    # film of the day
    film_of_the_day_qs = models.Film.objects.filter(
        main_poster__isnull=False,
        number_of_ratings__gte=10,
        average_rating__gte=4,
        number_of_comments__gte=3,
    )
    number_of_films = film_of_the_day_qs.count()  # cca 1600
    film_no_of_the_day = hash_of_the_day % number_of_films
    try:
        film_of_the_day = film_of_the_day_qs.order_by('id')[film_no_of_the_day]
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
    # random poll
    try:
        random_poll = models.Poll.objects.filter(state=models.Poll.STATE_OPEN).order_by('?')[0]
    except IndexError:
        random_poll = None
    return render(request, 'ktapp/index.html', {
        'film': film_of_the_day,
        'toplist': toplist_of_the_day,
        'toplist_list': models.UserToplistItem.objects.filter(usertoplist=toplist_of_the_day).select_related('film', 'director', 'actor').order_by('serial_number'),
        'buzz_comments': models.Comment.objects.select_related('film', 'topic', 'poll', 'created_by', 'reply_to', 'reply_to__created_by').filter(id__in=buzz_comment_ids),
        'random_poll': random_poll,
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
            'url': reverse('sequel', args=(result.id, result.slug_cache)),
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
            'url': reverse('poll', args=(result.id, result.slug_cache)),
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
                created_by=request.user,
            )

        for type_name, type_code in [('countries', 'C'), ('genres', 'G')]:
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
            for keyword_id in new_keywords:
                models.FilmKeywordRelationship.objects.create(
                    film=film,
                    keyword=models.Keyword.objects.get(id=keyword_id),
                    created_by=request.user,
                    spoiler=False,
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


def artist_main(request, id, name_slug):
    artist = get_object_or_404(models.Artist, pk=id)
    try:
        random_picture = artist.picture_set.all().order_by('?')[0]
    except IndexError:
        random_picture = None
    if request.POST:
        if kt_utils.check_permission('edit_artist', request.user):
            artist_name = kt_utils.strip_whitespace_and_separator(request.POST.get('artist_name', ''))
            artist_gender = kt_utils.strip_whitespace(request.POST.get('artist_gender', ''))
            if artist_gender in ['U', 'M', 'F']:
                artist.name = artist_name
                artist.gender = artist_gender
                artist.save()
            return HttpResponseRedirect(reverse('artist', args=(artist.id, artist.slug_cache)))

    directions, _ = filmlist.filmlist(
        user_id=request.user.id,
        filters=[('director_id', artist.id)],
        ordering=('year', 'DESC'),
        films_per_page=None,
    )
    number_of_directions = 0  # RawQuerySet has no __bool__() or __len__(), so we do it manually
    director_vote_count = 0
    director_vote_avg = 0
    if directions:
        director_votes = {
            'nr1': 0,
            'nr2': 0,
            'nr3': 0,
            'nr4': 0,
            'nr5': 0,
        }
        for x in directions:
            number_of_directions += 1
            director_votes['nr1'] += x.number_of_ratings_1
            director_votes['nr2'] += x.number_of_ratings_2
            director_votes['nr3'] += x.number_of_ratings_3
            director_votes['nr4'] += x.number_of_ratings_4
            director_votes['nr5'] += x.number_of_ratings_5
            director_vote_count += x.number_of_ratings
        if director_vote_count:
            director_vote_avg = 1.0 * (director_votes.get('nr1', 0) + 2*director_votes.get('nr2', 0) + 3*director_votes.get('nr3', 0) + 4*director_votes.get('nr4', 0) + 5*director_votes.get('nr5', 0)) / director_vote_count

    roles, _ = filmlist.filmlist(
        user_id=request.user.id,
        filters=[('actor_id', artist.id)],
        ordering=('year', 'DESC'),
        films_per_page=None,
    )
    number_of_roles = 0
    actor_vote_count = 0
    actor_vote_avg = 0
    if roles:
        actor_votes = {
            'nr1': 0,
            'nr2': 0,
            'nr3': 0,
            'nr4': 0,
            'nr5': 0,
        }
        for x in roles:
            number_of_roles += 1
            actor_votes['nr1'] += x.number_of_ratings_1
            actor_votes['nr2'] += x.number_of_ratings_2
            actor_votes['nr3'] += x.number_of_ratings_3
            actor_votes['nr4'] += x.number_of_ratings_4
            actor_votes['nr5'] += x.number_of_ratings_5
            actor_vote_count += x.number_of_ratings
        if actor_vote_count:
            actor_vote_avg = 1.0 * (actor_votes.get('nr1', 0) + 2*actor_votes.get('nr2', 0) + 3*actor_votes.get('nr3', 0) + 4*actor_votes.get('nr4', 0) + 5*actor_votes.get('nr5', 0)) / actor_vote_count

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
        'number_of_directions': number_of_directions,
        'number_of_roles': number_of_roles,
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
        next_picture = kt_utils.get_next_picture(pictures, picture)
        context.update(kt_utils.get_selected_picture_details(models.Picture, picture.film, picture, next_picture))
        context.update({'film': picture.film})
    return render(request, 'ktapp/artist_pictures.html', context)


def artist_picture(request, id, name_slug, picture_id):
    artist = get_object_or_404(models.Artist, pk=id)
    picture = get_object_or_404(models.Picture, pk=picture_id)
    pictures = sorted(artist.picture_set.all(), key=lambda pic: (-pic.film.year, pic.film.orig_title, pic.id))
    next_picture = kt_utils.get_next_picture(pictures, picture)
    context = {
        'artist': artist,
        'film': picture.film,
        'pictures': pictures,
    }
    context.update(kt_utils.get_selected_picture_details(models.Picture, picture.film, picture, next_picture))
    return render(request, 'ktapp/artist_pictures.html', context)


def role(request, id, name_slug):
    role = get_object_or_404(models.FilmArtistRelationship, pk=id)
    if request.POST:
        if kt_utils.check_permission('edit_role', request.user):
            role_name = kt_utils.strip_whitespace(request.POST.get('role_name', ''))  # NOTE: role name *can* contain , or ;
            role_type = kt_utils.strip_whitespace(request.POST.get('role_type', ''))
            if role_name != '' and role_type in ['F', 'V']:
                role.role_name = role_name
                role.actor_subtype = role_type
                role.save()
            return HttpResponseRedirect(reverse('role', args=(role.id, role.slug_cache)))
    context = {
        'role': role,
        'permission_edit_role': kt_utils.check_permission('edit_role', request.user),
        'permission_delete_role': kt_utils.check_permission('delete_role', request.user),
    }
    pictures = sorted(role.artist.picture_set.filter(film=role.film), key=lambda pic: (-pic.film.year, pic.film.orig_title, pic.id))
    if pictures:
        context.update({
            'pictures': pictures,
        })
        selected_picture_id = request.GET.get('p', 0)
        if selected_picture_id:
            try:
                picture = models.Picture.objects.get(id=selected_picture_id, film=role.film, artists__id=role.artist.id)
            except models.Picture.DoesNotExist:
                return HttpResponseRedirect(reverse('role', args=(role.id, role.slug_cache)))
        else:
            picture = None
        if len(pictures) == 1:
            picture = pictures[0]
        if picture:
            next_picture = kt_utils.get_next_picture(pictures, picture)
            context.update(kt_utils.get_selected_picture_details(models.Picture, picture.film, picture, next_picture))
            context.update({'film': picture.film})
    return render(request, 'ktapp/role.html', context)


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
def favourites(request):
    favourites = []
    favourite_ids = []
    latest_fav_votes = []
    latest_fav_comments = []
    for fav in request.user.get_follows().order_by('username', 'id'):
        favourites.append(fav)
        favourite_ids.append(fav.id)
        latest_fav_votes.append(fav.latest_votes)
        latest_fav_comments.append(fav.latest_comments)
    latest_fav_votes = [int(v) for v in ','.join(latest_fav_votes).split(',') if v != '']
    latest_fav_comments = [int(c) for c in ','.join(latest_fav_comments).split(',') if c != '']
    return render(request, 'ktapp/favourites.html', {
        'favourites': favourites,
        'latest_votes': models.Vote.objects.filter(id__in=latest_fav_votes).select_related('user', 'film').order_by('-when', '-id')[:50],
        'latest_comments': models.Comment.objects.filter(id__in=latest_fav_comments).select_related('film', 'topic', 'poll', 'created_by', 'reply_to', 'reply_to__created_by').all()[:20],
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
            'permission_poll_admin': kt_utils.check_permission('poll_admin', request.user),
            'permission_new_poll': kt_utils.check_permission('new_poll', request.user),
            'myself': ',%s,' % request.user.id if request.user.is_authenticated() else '',
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
            models.PollVote.objects.filter(user=request.user, pollchoice=pollchoice).count() if request.user.is_authenticated() else 0,
        ))
    try:
        reply_to_comment = models.Comment.objects.get(id=request.GET.get('valasz', 0))
        reply_to_id = reply_to_comment.id
    except models.Comment.DoesNotExist:
        reply_to_comment = None
        reply_to_id = None
    comment_form = kt_forms.CommentForm(initial={
        'domain': models.Comment.DOMAIN_POLL,
        'film': None,
        'topic': None,
        'poll': selected_poll,
        'reply_to': reply_to_id,
    })
    comment_form.fields['domain'].widget = forms.HiddenInput()
    comment_form.fields['film'].widget = forms.HiddenInput()
    comment_form.fields['topic'].widget = forms.HiddenInput()
    comment_form.fields['poll'].widget = forms.HiddenInput()
    comment_form.fields['reply_to'].widget = forms.HiddenInput()
    return render(request, 'ktapp/poll.html', {
        'poll': selected_poll,
        'pollchoices': pollchoices,
        'sum_number_of_votes': sum_number_of_votes,
        'comments': selected_poll.comment_set.select_related('created_by', 'reply_to', 'reply_to__created_by').all(),
        'comment_form': comment_form,
        'reply_to_comment': reply_to_comment,
        'permission_poll_admin': kt_utils.check_permission('poll_admin', request.user),
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


def list_of_reviews(request):
    unapproved_reviews = []
    if request.user.is_authenticated():
        if kt_utils.check_permission('approve_review', request.user):
            unapproved_reviews = models.Review.objects.select_related('film', 'created_by').filter(approved=False).order_by('-created_at')
    return render(request, 'ktapp/list_of_reviews.html', {
        'reviews': models.Review.objects.select_related('film', 'created_by').filter(approved=True).order_by('-created_at'),
        'unapproved_reviews': unapproved_reviews,
    })


def list_of_bios(request):
    unapproved_bios = []
    if request.user.is_authenticated():
        if kt_utils.check_permission('approve_bio', request.user):
            unapproved_bios = models.Biography.objects.select_related('artist', 'created_by').filter(approved=False).order_by('-created_at')
    return render(request, 'ktapp/list_of_bios.html', {
        'bios': models.Biography.objects.select_related('artist', 'created_by').filter(approved=True).order_by('-created_at'),
        'unapproved_bios': unapproved_bios,
    })


def latest_pictures(request):
    return render(request, 'ktapp/latest_pictures.html', {
        'pictures': models.Picture.objects.select_related('film').all().order_by('-created_at')[:100],
    })


def latest_quotes(request):
    return render(request, 'ktapp/latest_quotes.html', {
        'quotes': models.Quote.objects.select_related('film').all().order_by('-created_at')[:100],
    })


def latest_trivias(request):
    return render(request, 'ktapp/latest_trivias.html', {
        'trivias': models.Trivia.objects.select_related('film').all().order_by('-created_at')[:100],
    })


def sequels(request):
    return render(request, 'ktapp/sequels.html', {
        'sequels': models.Sequel.objects.all().order_by('name'),
    })


def sequel(request, id, title_slug):
    selected_sequel = get_object_or_404(models.Sequel, pk=id)
    return render(request, 'ktapp/sequel.html', {
        'sequel': selected_sequel,
    })



def old_url(request):
    print request.path
    if request.path == '/film.php':
        film = get_object_or_404(models.Film, pk=request.GET.get('fid', 0))
        return HttpResponseRedirect(reverse('film_main', args=(film.id, film.slug_cache)))
    if request.path == '/filmvel.php':
        film = get_object_or_404(models.Film, pk=request.GET.get('fid', 0))
        return HttpResponseRedirect(reverse('film_comments', args=(film.id, film.slug_cache)))
    if request.path == '/filmpix.php':
        film = get_object_or_404(models.Film, pk=request.GET.get('fid', 0))
        return HttpResponseRedirect(reverse('film_pictures', args=(film.id, film.slug_cache)))
    if request.path == '/filmdij.php':
        film = get_object_or_404(models.Film, pk=request.GET.get('fid', 0))
        return HttpResponseRedirect(reverse('film_awards', args=(film.id, film.slug_cache)))
    if request.path == '/filmelem.php':
        film = get_object_or_404(models.Film, pk=request.GET.get('fid', 0))
        return HttpResponseRedirect(reverse('film_reviews', args=(film.id, film.slug_cache)))
    if request.path == '/filmid.php':
        film = get_object_or_404(models.Film, pk=request.GET.get('fid', 0))
        return HttpResponseRedirect(reverse('film_quotes', args=(film.id, film.slug_cache)))
    if request.path == '/filmtriv.php':
        film = get_object_or_404(models.Film, pk=request.GET.get('fid', 0))
        return HttpResponseRedirect(reverse('film_trivias', args=(film.id, film.slug_cache)))
    if request.path == '/filmksz.php':
        film = get_object_or_404(models.Film, pk=request.GET.get('fid', 0))
        return HttpResponseRedirect(reverse('film_keywords', args=(film.id, film.slug_cache)))
    if request.path == '/filmlink.php':
        film = get_object_or_404(models.Film, pk=request.GET.get('fid', 0))
        return HttpResponseRedirect(reverse('film_links', args=(film.id, film.slug_cache)))
    if request.path == '/szinesz.php':
        artist = get_object_or_404(models.Artist, pk=request.GET.get('aid', 0))
        return HttpResponseRedirect(reverse('artist', args=(artist.id, artist.slug_cache)))
    if request.path == '/szineszpix.php':
        artist = get_object_or_404(models.Artist, pk=request.GET.get('aid', 0))
        return HttpResponseRedirect(reverse('artist_pictures', args=(artist.id, artist.slug_cache)))
    if request.path == '/szereplo.php':
        role = get_object_or_404(models.FilmArtistRelationship, pk=request.GET.get('rid', 0))
        return HttpResponseRedirect(reverse('role', args=(role.id, role.slug_cache)))
    if request.path == '/usertoplistak.php':
        utl_id = request.GET.get('tlId', 0)
        if utl_id == 0:
            return HttpResponseRedirect(reverse('usertoplists'))
        usertoplist = get_object_or_404(models.UserToplist, pk=utl_id)
        return HttpResponseRedirect(reverse('usertoplist', args=(usertoplist.id, usertoplist.slug_cache)))
    if request.path == '/keres.php':
        q = request.GET.get('rendezo', '')
        if q != '':
            try:
                artist = models.Artist.objects.get(name__icontains=q)
            except models.Artist.DoesNotExist:
                artist = None
            if artist:
                return HttpResponseRedirect(reverse('artist', args=(artist.id, artist.slug_cache)))
        else:
            q = request.GET.get('cim', '')
        return HttpResponseRedirect(reverse('search') + '?q=' + q)
    if request.path == '/ember.php':
        user = get_object_or_404(models.KTUser, pk=request.GET.get('uid', 0))
        return HttpResponseRedirect(reverse('user_profile', args=(user.id, user.slug_cache)))
    if request.path == '/beszolasok.php':
        return HttpResponseRedirect(reverse('latest_comments'))
    if request.path == '/forum.php':
        topic_id = request.GET.get('tid', 0)
        if topic_id == 0:
            return HttpResponseRedirect(reverse('list_of_topics'))
        topic = get_object_or_404(models.Topic, pk=topic_id)
        return HttpResponseRedirect(reverse('forum', args=(topic.id, topic.slug_cache)))
    if request.path == '/index.php':
        return HttpResponseRedirect(reverse('index'))
    if request.path == '/top.php':
        return HttpResponseRedirect(reverse('top_films'))
    if request.path == '/pollforum.php' or request.path == '/pollregi.php':
        poll = get_object_or_404(models.Poll, pk=request.GET.get('pkid', 0))
        return HttpResponseRedirect(reverse('poll', args=(poll.id, poll.slug_cache)))
    raise Http404
