# -*- coding: utf-8 -*-

import copy
import datetime
import hashlib
import math
import json
import subprocess
from collections import defaultdict

from django.conf import settings
from django.db import connection
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, Http404, HttpResponse, HttpResponseNotFound
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django import forms
from django.utils.http import urlquote_plus

from ktapp import models
from ktapp import forms as kt_forms
from ktapp import utils as kt_utils
from ktapp.helpers import filmlist, search as kt_search
from ktapp import sqls as kt_sqls
from ktapp import texts


ARTICLES_PER_PAGE = 50
COMMENTS_PER_PAGE = 100
MESSAGES_PER_PAGE = 50
FILMS_PER_PAGE = 100
USERS_PER_PAGE = 100

MINIMUM_YEAR = 1920


def index(request):
    now = datetime.datetime.now()
    hash_of_the_day = int(hashlib.md5(now.strftime('%Y-%m-%d')).hexdigest(), 16)
    # film of the day
    try:
        film_of_the_day = models.OfTheDay.objects.filter(domain='F', public=True).order_by('-day')[0].film
    except Exception:
        film_of_the_day = None
    # premiers
    premier_film_list = kt_utils.get_premiers_for_today()
    try:
        cookie_kt_carousel_premiers_index = int(request.COOKIES.get('kt-carousel-premiers-index', '0'))
    except:
        cookie_kt_carousel_premiers_index = 0
    if cookie_kt_carousel_premiers_index > len(premier_film_list) - 1:
        cookie_kt_carousel_premiers_index = 0
    # latest_content
    latest_content = []
    for item in models.Review.objects.select_related('film', 'created_by').filter(approved=True).order_by('-created_at')[:10]:
        latest_content.append((item.created_at, 'review', item))
    for item in models.Link.objects.filter(featured=True).exclude(lead='').select_related('author', 'created_by', 'film', 'artist').order_by('-created_at')[:10]:
        latest_content.append((item.created_at, 'link', item))
    # toplist of the day
    number_of_toplists = models.UserToplist.objects.filter(quality=True).count()
    if number_of_toplists:
        toplist_no_of_the_day = hash_of_the_day % number_of_toplists
        try:
            toplist_of_the_day = models.UserToplist.objects.filter(quality=True).order_by('id')[toplist_no_of_the_day]
        except Exception:
            toplist_of_the_day = None
    else:
        toplist_of_the_day = None
    # buzz
    buzz_comment_domains = {}
    for comment in models.Comment.objects.exclude(topic_id=87)[:1000]:  # skip OFF topic
        key = (comment.domain, comment.film_id, comment.topic_id, comment.poll_id)
        if key not in buzz_comment_domains:
            buzz_comment_domains[key] = (comment.id, comment.created_at)
        else:
            if comment.created_at > buzz_comment_domains[key][1]:
                buzz_comment_domains[key] = (comment.id, comment.created_at)
    buzz_comment_ids = [id for id, _ in sorted(buzz_comment_domains.values(), key=lambda x: x[1], reverse=True)[:20]]
    buzz_comments = models.Comment.objects.select_related('film', 'topic', 'poll', 'created_by', 'reply_to', 'reply_to__created_by').filter(id__in=buzz_comment_ids)
    # random poll, quote and trivia
    random_poll = kt_utils.get_random_item(models.Poll.objects.filter(state=models.Poll.STATE_OPEN))
    random_quote = kt_utils.get_random_item(models.Quote.objects)
    random_trivia = kt_utils.get_random_item(models.Trivia.objects)

    # vapiti
    vapiti_round, round_1_dates, round_2_dates, result_day = kt_utils.get_vapiti_round()
    vapiti_round_1_end_datetime = datetime.datetime.strptime(round_2_dates[0], '%Y-%m-%d')
    vapiti_round_2_end_datetime = datetime.datetime.strptime(result_day, '%Y-%m-%d')
    vapiti_round_2_has_nominees = False
    if vapiti_round == 2:
        if kt_utils.get_vapiti_nominees(models.Award, models.VapitiVote.VAPITI_TYPE_GOLD):
            vapiti_round_2_has_nominees = True
    vapiti_comment = None
    if vapiti_round == 1 or vapiti_round == 2:
        if settings.VAPITI_TOPIC_ID:
            vapiti_in_buzz = False
            for c in buzz_comments:
                if c.topic_id == settings.VAPITI_TOPIC_ID:
                    vapiti_in_buzz = True
            if not vapiti_in_buzz:
                try:
                    vapiti_comment = models.Comment.objects.select_related('topic', 'created_by', 'reply_to', 'reply_to__created_by').filter(topic_id=settings.VAPITI_TOPIC_ID)[0]
                except Exception:
                    pass

    vapiti_film_list = []
    if vapiti_round == 2 and vapiti_round_2_has_nominees:
        vapiti_film_ids = set()
        for film_id in kt_utils.get_vapiti_nominees(models.Award, models.VapitiVote.VAPITI_TYPE_GOLD):
            vapiti_film_ids.add(film_id)
        for film_id, artist_id in kt_utils.get_vapiti_nominees(models.Award, models.VapitiVote.VAPITI_TYPE_SILVER_FEMALE):
            vapiti_film_ids.add(film_id)
        for film_id, artist_id in kt_utils.get_vapiti_nominees(models.Award, models.VapitiVote.VAPITI_TYPE_SILVER_MALE):
            vapiti_film_ids.add(film_id)
        vapiti_film_list = [film for film in models.Film.objects.filter(id__in=vapiti_film_ids).order_by('orig_title', 'id')]
    try:
        cookie_kt_carousel_vapiti_index = int(request.COOKIES.get('kt-carousel-vapiti-index', '0'))
    except:
        cookie_kt_carousel_vapiti_index = 0
    if cookie_kt_carousel_vapiti_index > len(vapiti_film_list) - 1:
        cookie_kt_carousel_vapiti_index = 0

    # game
    # before_game = (now.weekday() == 5 or now.weekday() == 6 and now.hour < 20)
    # during_game = (now.weekday() == 6 and now.hour >= 20 or now.weekday() == 0)
    before_game = False
    during_game = False
    # banners
    banners = []
    if request.user.is_authenticated():
        banners = models.Banner.objects.filter(
            where='index',
            user=request.user,
            status__in=[models.Banner.BANNER_STATUS_PUBLISHED, models.Banner.BANNER_STATUS_VIEWED],
        )
    for banner in banners:
        if banner.status == models.Banner.BANNER_STATUS_PUBLISHED:
            banner.status = models.Banner.BANNER_STATUS_VIEWED
            banner.first_viewed_at = datetime.datetime.now()
        banner.viewed += 1
        banner.save()
    finance_status, finance_missing = kt_utils.get_finance(models.Donation)
    number_of_donators, amount_of_donation = kt_utils.get_banner_version(request.user.id)
    #
    return render(request, 'ktapp/index.html', {
        'film': film_of_the_day,
        'ratings': range(1, 6),
        'film_avg_rating_int': int(film_of_the_day.average_rating) if film_of_the_day and film_of_the_day.average_rating else 0,
        'film_avg_rating_frac': int(10 * (film_of_the_day.average_rating - int(film_of_the_day.average_rating))) if film_of_the_day and film_of_the_day.average_rating else 0,
        'premier_film_list': premier_film_list,
        'cookie_kt_carousel_premiers_index': cookie_kt_carousel_premiers_index,
        'latest_content': sorted(latest_content, key=lambda x: x[0], reverse=True)[:10],
        'toplist': toplist_of_the_day,
        'toplist_list': models.UserToplistItem.objects.filter(usertoplist=toplist_of_the_day).select_related('film', 'director', 'actor').order_by('serial_number') if toplist_of_the_day else None,
        'buzz_comments': buzz_comments,
        'random_poll': random_poll,
        'random_quote': random_quote,
        'random_trivia': random_trivia,
        'vapiti_year': settings.VAPITI_YEAR,
        'vapiti_round': vapiti_round,
        'vapiti_round_1_end_datetime': vapiti_round_1_end_datetime,
        'vapiti_round_2_end_datetime': vapiti_round_2_end_datetime,
        'vapiti_round_2_has_nominees': vapiti_round_2_has_nominees,
        'vapiti_end_of_round_2': round_2_dates[1][-2:],
        'vapiti_result_day': result_day[-2:],
        'vapiti_event_url': settings.VAPITI_EVENT_URL,
        'vapiti_event_location': settings.VAPITI_EVENT_LOCATION,
        'vapiti_comment': vapiti_comment,
        'vapiti_film_list': vapiti_film_list,
        'cookie_kt_carousel_vapiti_index': cookie_kt_carousel_vapiti_index,
        'before_game': before_game,
        'during_game': during_game,
        'banners': banners,
        'finance_status': finance_status,
        'finance_amount': finance_missing,
        'number_of_donators': number_of_donators,
        'amount_of_donation': amount_of_donation,
    })


def premiers(request):
    today = datetime.date.today()
    this_year = today.year
    offset = today.weekday()  # this Monday
    from_date = today - datetime.timedelta(days=offset+14)
    until_date = today - datetime.timedelta(days=offset-6)
    premier_list = []
    film_list = []
    for film in models.Film.objects.filter(main_premier__gte=from_date, main_premier__lte=until_date):
        film_list.append((film.main_premier, film))
    for item in models.Premier.objects.filter(when__gte=from_date, when__lte=until_date).select_related('film'):
        film_list.append((item.when, item.film))
    film_list.sort(key=lambda item: (item[0], item[1].orig_title, item[1].id))
    for premier_date, film in film_list:
        if premier_list:
            if premier_list[-1][0] != premier_date:
                premier_list.append([premier_date, []])
        else:
            premier_list.append([premier_date, []])
        premier_list[-1][1].append(film)
    premier_list.sort(reverse=True)
    return render(request, 'ktapp/premier_subpages/premiers.html', {
        'active_tab': 'nowadays',
        'this_premier_year': this_year,
        'before_this_premier_year': this_year - 1,
        'this_year': today.strftime('%Y'),
        'this_month': today.strftime('%m'),
        'this_day': today.strftime('%d'),
        'premier_list': premier_list,
    })


def premiers_in_a_year(request, year):
    today = datetime.date.today()
    this_year = today.year
    year = int(year)
    if year < settings.FIRST_PREMIER_YEAR:
        return HttpResponseRedirect(reverse('premiers_in_a_year', args=(settings.FIRST_PREMIER_YEAR,)))
    if year > this_year:
        return HttpResponseRedirect(reverse('premiers_in_a_year', args=(this_year,)))
    films, nice_filters = filmlist.filmlist(
        user_id=request.user.id,
        filters=[('premier_year', year)],
        ordering='premier_date',
        films_per_page=None,
    )
    active_tab = 'this_year'
    if year < this_year:
        active_tab = 'other_year'
    if year > this_year:
        active_tab = 'next_year'
    return render(request, 'ktapp/premier_subpages/premiers_in_a_year.html', {
        'active_tab': active_tab,
        'this_premier_year': this_year,
        'before_this_premier_year': this_year - 1,
        'premier_list_full': films,
        'selected_year': year,
        'this_year': today.strftime('%Y'),
        'this_month': today.strftime('%m'),
        'this_day': today.strftime('%d'),
        'premier_years': range(settings.FIRST_PREMIER_YEAR, this_year),
    })


def premier_anniversaries(request, year, month, day):
    today = datetime.date.today()
    this_year = today.year
    year, month, day = int(year), int(month), int(day)
    try:
        selected_day = datetime.date(year, month, day)
    except ValueError:
        raise Http404
    prev_day = selected_day - datetime.timedelta(days=1)
    next_day = selected_day + datetime.timedelta(days=1)
    premier_days = []
    for year_offset in xrange(10, 101):
        try:
            premier_days.append(datetime.date(
                year - year_offset,
                month,
                day,
            ))
        except ValueError:
            pass
    film_id_list = [film.id for film in models.Film.objects.filter(main_premier__in=premier_days)]
    if film_id_list:
        raw_films, _ = filmlist.filmlist(
            user_id=request.user.id,
            filters=[('film_id_list', ','.join([str(film_id) for film_id in film_id_list]))],
            ordering=('main_premier', 'DESC'),
            films_per_page=None,
        )
        films = []
        for film in raw_films:
            film.premier_anniversary = year - film.main_premier_year
            films.append(film)
    else:
        films = []
    return render(request, 'ktapp/premier_subpages/premier_anniversaries.html', {
        'active_tab': 'anniversaries',
        'this_premier_year': this_year,
        'before_this_premier_year': this_year - 1,
        'this_year': today.strftime('%Y'),
        'this_month': today.strftime('%m'),
        'this_day': today.strftime('%d'),
        'selected_day': selected_day,
        'prev_day_year': prev_day.strftime('%Y'),
        'prev_day_month': prev_day.strftime('%m'),
        'prev_day_day': prev_day.strftime('%d'),
        'next_day_year': next_day.strftime('%Y'),
        'next_day_month': next_day.strftime('%m'),
        'next_day_day': next_day.strftime('%d'),
        'films': films,
    })


def films_of_past_days(request):
    public_films, _ = filmlist.filmlist(
        user_id=request.user.id,
        filters=[('of_the_day', 1)],
        ordering=('of_the_day', 'DESC'),
        films_per_page=None,
    )
    if request.user.is_authenticated() and request.user.id in {1, 13114}:
        secret_films, _ = filmlist.filmlist(
            user_id=request.user.id,
            filters=[('of_the_day', 2)],
            ordering=('of_the_day', 'DESC'),
            films_per_page=None,
        )
    else:
        secret_films = []
    return render(request, 'ktapp/films_of_past_days.html', {
        'public_films': public_films,
        'secret_films': secret_films,
    })


def browse(request):
    ordering_str = kt_utils.strip_whitespace(request.GET.get('o', ''))
    if ordering_str == '':
        ordering_str = '-number_of_ratings'
    if ordering_str[0] == '-':
        ordering = (ordering_str[1:], 'DESC')
    else:
        ordering = (ordering_str, 'ASC')
    filters = filmlist.get_filters_from_request(request)
    films, nice_filters = filmlist.filmlist(
        user_id=request.user.id,
        filters=filters,
        ordering=ordering,
        films_per_page=1000,
    )
    querystring = {}
    for filter_type, filter_value in nice_filters:
        if filter_type in {'title', 'year', 'director', 'actor', 'country', 'genre', 'keyword', 'my_rating', 'my_wish'}:
            querystring[filter_type] = filter_value
        elif filter_type == 'number_of_ratings':
            min_value, max_value = filter_value.split('-')
            querystring['num_rating_min'] = kt_utils.coalesce(min_value, '')
            querystring['num_rating_max'] = kt_utils.coalesce(max_value, '')
        elif filter_type == 'average_rating':
            min_value, max_value = filter_value.split('-')
            querystring['avg_rating_min'] = kt_utils.coalesce(min_value, '')
            querystring['avg_rating_max'] = kt_utils.coalesce(max_value, '')
        elif filter_type == 'fav_average_rating':
            min_value, max_value = filter_value.split('-')
            querystring['fav_avg_rating_min'] = kt_utils.coalesce(min_value, '')
            querystring['fav_avg_rating_max'] = kt_utils.coalesce(max_value, '')

    qs_combined = '&'.join('%s=%s' % (key, val) for key, val in querystring.iteritems())
    if qs_combined != '':
        qs_combined = '&' + qs_combined

    films = list(films)
    result_count = len(films)

    try:
        p = int(request.GET.get('p', 0))
    except ValueError:
        p = 0
    max_pages = int(math.ceil(1.0 * result_count / FILMS_PER_PAGE))
    if max_pages == 0:
        max_pages = 1
    if p == 0:
        p = 1
    if p > max_pages:
        p = max_pages

    films = films[(p-1) * FILMS_PER_PAGE:p * FILMS_PER_PAGE]

    return render(request, 'ktapp/browse.html', {
        'result_count': result_count,
        'querystring': querystring,
        'qs_combined': qs_combined,
        'ordering_str': ordering_str,
        'p': p,
        'max_pages': max_pages,
        'films': films,
    })


def search(request):
    q = request.GET.get('q', '')
    if len(q) < 2:
        return HttpResponseRedirect(reverse('index'))
    q_pieces = kt_search.get_q_pieces(q)
    film = kt_search.find_film_by_link(q)
    if film:
        return HttpResponseRedirect(reverse('film_main', args=(film.id, film.slug_cache)))
    films, _ = filmlist.filmlist(
        user_id=request.user.id,
        filters=[('title', q)],
        ordering='title_match',
        films_per_page=settings.MAX_SEARCH_RESULTS + 1,
    )
    films = list(films)
    artists = kt_search.find_artists(q_pieces, settings.MAX_SEARCH_RESULTS + 1)
    roles = kt_search.find_roles(q_pieces, settings.MAX_SEARCH_RESULTS + 1)
    sequels = kt_search.find_sequels(q_pieces, settings.MAX_SEARCH_RESULTS + 1)
    users = kt_search.find_users(q_pieces, settings.MAX_SEARCH_RESULTS + 1)
    topics = kt_search.find_topics(q_pieces, settings.MAX_SEARCH_RESULTS + 1)
    polls = kt_search.find_polls(q_pieces, settings.MAX_SEARCH_RESULTS + 1)
    # redirect to single hit:
    if len(films) + len(artists) + len(roles) + len(sequels) + len(topics) + len(polls) + len(users) == 1:
        if films:
            item = films[0]
            return HttpResponseRedirect(reverse('film_main', args=(item.id, item.slug_cache)))
        if artists:
            item = artists[0]
            return HttpResponseRedirect(reverse('artist', args=(item.id, item.slug_cache)))
        if roles:
            item = roles[0]
            return HttpResponseRedirect(reverse('role', args=(item.id, item.slug_cache)))
        if sequels:
            item = sequels[0]
            return HttpResponseRedirect(reverse('sequel', args=(item.id, item.slug_cache)))
        if topics:
            item = topics[0]
            return HttpResponseRedirect(reverse('forum', args=(item.id, item.slug_cache)))
        if polls:
            item = polls[0]
            return HttpResponseRedirect(reverse('poll', args=(item.id, item.slug_cache)))
        if users:
            item = users[0]
            return HttpResponseRedirect(reverse('user_profile', args=(item.id, item.slug_cache)))
    return render(request, 'ktapp/search.html', {
        'q': q,
        'films': films[:settings.MAX_SEARCH_RESULTS],
        'more_films': len(films) > settings.MAX_SEARCH_RESULTS,
        'sequels': sequels[:settings.MAX_SEARCH_RESULTS],
        'topics': topics[:settings.MAX_SEARCH_RESULTS],
        'polls': polls[:settings.MAX_SEARCH_RESULTS],
        'artists': artists[:settings.MAX_SEARCH_RESULTS],
        'roles': roles[:settings.MAX_SEARCH_RESULTS],
        'users': users[:settings.MAX_SEARCH_RESULTS],
    })


def _get_type_and_filter(request):
    today = datetime.date.today()
    this_year = today.year
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
        if year < MINIMUM_YEAR:
            year = MINIMUM_YEAR - 10
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


def _get_film_list(user_id, toplist_type, filter_type, filter_value):
    thresholds = {
        'legjobb': 100,
        'ismeretlen': 30,
        'legrosszabb': 100,
        'legerdekesebb': 50,
        'legnezettebb': 100,
    }
    filters = []
    if filter_type == 'ev':
        if filter_value < MINIMUM_YEAR:
            filters.append(('year', '-%s' % (filter_value+9)))
        else:
            filters.append(('year', '%s-%s' % (filter_value, filter_value+9)))
    elif filter_type == 'bemutato':
        filters.append(('main_premier_year', filter_value))
    elif filter_type == 'orszag':
        filters.append(('country', filter_value.name))
    elif filter_type == 'mufaj':
        filters.append(('genre', filter_value.name))

    if filter_type == 'mufaj':
        if filter_value.id != 314:
            filters.append(('no_music_video', 1))
        if filter_value.id != 4150:
            filters.append(('no_mini', 1))
        if filter_value.id != 120:
            filters.append(('no_short', 1))
    else:
        filters.append(('no_music_video', 1))
        filters.append(('no_mini', 1))
        filters.append(('no_short', 1))

    if toplist_type in {'legjobb', 'legrosszabb', 'legnezettebb'}:
        if toplist_type == 'legjobb':
            filters.append(('average_rating', '3.5-'))
            ordering = ('average_rating', 'DESC')
        elif toplist_type == 'legrosszabb':
            filters.append(('average_rating', '-2.5'))
            ordering = ('average_rating', 'ASC')
        else:
            ordering = ('number_of_ratings', 'DESC')
        films, _ = filmlist.filmlist(
            user_id=user_id,
            filters=filters + [('number_of_ratings', '%s-' % thresholds[toplist_type])],
            ordering=ordering,
            films_per_page=250,
        )
        films = list(films)
        if len(films) >= 50:
            return films
        films, _ = filmlist.filmlist(
            user_id=user_id,
            filters=filters + [('number_of_ratings', '%s-' % (thresholds[toplist_type]/2))],
            ordering=ordering,
            films_per_page=250,
        )
        films = list(films)
        if len(films) >= 20:
            return films
        films, _ = filmlist.filmlist(
            user_id=user_id,
            filters=filters + [('number_of_ratings', '10-')],
            ordering=ordering,
            films_per_page=250,
        )
        return list(films)

    if toplist_type == 'ismeretlen':
        ordering = ('average_rating', 'DESC')
        films, _ = filmlist.filmlist(
            user_id=user_id,
            filters=filters + [('number_of_ratings', '10-%s' % (thresholds[toplist_type]-1))],
            ordering=ordering,
            films_per_page=250,
        )
        return list(films)

    if toplist_type == 'legerdekesebb':
        ordering = ('number_of_comments', 'DESC')
        films, _ = filmlist.filmlist(
            user_id=user_id,
            filters=filters + [('number_of_comments', '%s-' % thresholds[toplist_type])],
            ordering=ordering,
            films_per_page=250,
        )
        films = list(films)
        if len(films) >= 50:
            return films
        films, _ = filmlist.filmlist(
            user_id=user_id,
            filters=filters + [('number_of_comments', '%s-' % (thresholds[toplist_type]/2))],
            ordering=ordering,
            films_per_page=250,
        )
        films = list(films)
        if len(films) >= 20:
            return films
        films, _ = filmlist.filmlist(
            user_id=user_id,
            filters=filters + [('number_of_comments', '10-')],
            ordering=ordering,
            films_per_page=250,
        )
        return list(films)

    return []


def top_films(request):
    today = datetime.date.today()
    this_year = today.year
    minimum_premier = 1970
    toplist_type, filter_type, filter_value = _get_type_and_filter(request)
    films = _get_film_list(request.user.id, toplist_type, filter_type, filter_value)
    links = []
    if filter_type == 'ev':
        links.append((MINIMUM_YEAR - 10, '-%s' % (MINIMUM_YEAR - 1)))
        for y in range(MINIMUM_YEAR, this_year, 10):
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


def artist_main(request, id, name_slug):
    artist = get_object_or_404(models.Artist, pk=id)
    if request.POST:
        if kt_utils.check_permission('edit_artist', request.user):
            artist_name = kt_utils.strip_whitespace_and_separator(request.POST.get('artist_name', ''))
            artist_gender = kt_utils.strip_whitespace(request.POST.get('artist_gender', ''))
            if artist_gender in ['U', 'M', 'F']:
                artist.name = artist_name
                artist.gender = artist_gender
                artist.save()
            return HttpResponseRedirect(reverse('artist', args=(artist.id, artist.slug_cache)))
    random_picture = artist.main_picture
    if random_picture is None:
        try:
            random_picture = artist.picture_set.all().order_by('?')[0]
        except IndexError:
            random_picture = None
    directions, _ = filmlist.filmlist(
        user_id=request.user.id,
        filters=[('director_id', artist.id)],
        ordering=('year', 'DESC'),
        films_per_page=None,
    )
    roles, _ = filmlist.filmlist(
        user_id=request.user.id,
        filters=[('actor_id', artist.id)],
        ordering=('year', 'DESC'),
        films_per_page=None,
    )
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
        'number_of_directions': artist.number_of_films_as_director,
        'number_of_roles': artist.number_of_films_as_actor,
        'director_vote_count': artist.number_of_ratings_as_director,
        'actor_vote_count': artist.number_of_ratings_as_actor,
        'director_vote_avg': artist.average_rating_as_director,
        'actor_vote_avg': artist.average_rating_as_actor,
        'awards': models.Award.objects.filter(artist=artist).order_by('name', 'year', 'category'),
        'biographies': models.Biography.objects.filter(artist=artist, approved=True),
        'unapproved_biographies': models.Biography.objects.filter(artist=artist, approved=False),
        'similar_artists': similar_artists,
        'permission_edit_artist': kt_utils.check_permission('edit_artist', request.user),
        'permission_merge_artist': kt_utils.check_permission('merge_artist', request.user),
        'permission_approve_bio': kt_utils.check_permission('approve_bio', request.user),
        'permission_set_main_picture': kt_utils.check_permission('set_main_picture', request.user),
        'imdb_link': 'https://imdb.com/find?s=nm&q=' + urlquote_plus(artist.name),
        'wiki_en_link': 'https://en.wikipedia.org/w/wiki.phtml?search=' + urlquote_plus(artist.name),
        'wiki_hu_link': 'https://hu.wikipedia.org/w/wiki.phtml?search=' + urlquote_plus(artist.name),
    })


def artist_pictures(request, id, name_slug):
    artist = get_object_or_404(models.Artist, pk=id)
    pictures = sorted(artist.picture_set.all(), key=lambda pic: (-pic.film.year if pic.film else -9999, pic.film.orig_title if pic.film else '', pic.id))
    context = {
        'artist': artist,
        'pictures': pictures,
        'permission_new_picture': kt_utils.check_permission('new_picture', request.user),
        'permission_edit_picture': kt_utils.check_permission('edit_picture', request.user),
        'permission_delete_picture': kt_utils.check_permission('delete_picture', request.user),
        'permission_set_main_picture': kt_utils.check_permission('set_main_picture', request.user),
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
    pictures = sorted(artist.picture_set.all(), key=lambda pic: (-pic.film.year if pic.film else -9999, pic.film.orig_title if pic.film else '', pic.id))
    next_picture = kt_utils.get_next_picture(pictures, picture)
    context = {
        'artist': artist,
        'film': picture.film,
        'pictures': pictures,
        'permission_new_picture': kt_utils.check_permission('new_picture', request.user),
        'permission_edit_picture': kt_utils.check_permission('edit_picture', request.user),
        'permission_delete_picture': kt_utils.check_permission('delete_picture', request.user),
        'permission_set_main_picture': kt_utils.check_permission('set_main_picture', request.user),
    }
    context.update(kt_utils.get_selected_picture_details(models.Picture, picture.film, picture, next_picture))
    return render(request, 'ktapp/artist_pictures.html', context)


@login_required
@kt_utils.kt_permission_required('set_main_picture')
def crop_picture(request, id):
    picture = get_object_or_404(models.Picture, id=id)
    artist = picture.artist
    if request.POST:
        x = float(request.POST.get('x'))
        y = float(request.POST.get('y'))
        w = float(request.POST.get('w'))
        h = float(request.POST.get('h'))
        picture.crop(x, y, w, h)
        return HttpResponseRedirect(reverse('artist_picture', args=(artist.id, artist.slug_cache, picture.id)) + '#pix')
    return render(request, 'ktapp/crop_picture.html', {
        'picture': picture,
        'artist': artist,
    })


def role(request, id, name_slug):
    role = get_object_or_404(models.FilmArtistRelationship, pk=id)
    if request.POST:
        if kt_utils.check_permission('edit_role', request.user):
            role_name = kt_utils.strip_whitespace(request.POST.get('role_name', ''))  # NOTE: role name *can* contain , or ;
            role_type = kt_utils.strip_whitespace(request.POST.get('role_type', ''))
            if role_type not in {'F', 'V'}:
                role_type = 'F'
            is_main_role = kt_utils.strip_whitespace(request.POST.get('is_main_role', '')) == '1'
            if role_name != '':
                role.role_name = role_name
                role.actor_subtype = role_type
                role.is_main_role = is_main_role
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


@login_required
@kt_utils.kt_permission_required('check_missing_data')
def artists_with_missing_data(request):
    p = int(request.GET.get('p', 0))
    if p < 1:
        p = 1
    offset_min, offset_max = (p - 1) * 100, p * 100
    miss_type = request.GET.get('tipus', '')
    if miss_type not in {'szinesz_profilkep', 'rendezo_profilkep', 'kepek', 'nem'}:
        miss_type = 'szinesz_profilkep'
    if miss_type == 'szinesz_profilkep':
        artists = models.Artist.objects.raw('''
        SELECT a.*
        FROM ktapp_artist a
        LEFT JOIN ktapp_picture p ON p.artist_id = a.id
        WHERE p.id IS NULL
        ORDER BY a.number_of_ratings_as_actor DESC
        LIMIT {offset}, {limit}
        '''.format(offset=offset_min, limit=100))
    elif miss_type == 'rendezo_profilkep':
        artists = models.Artist.objects.raw('''
        SELECT a.*
        FROM ktapp_artist a
        LEFT JOIN ktapp_picture p ON p.artist_id = a.id
        WHERE p.id IS NULL
        ORDER BY a.number_of_ratings_as_director DESC
        LIMIT {offset}, {limit}
        '''.format(offset=offset_min, limit=100))
    elif miss_type == 'kepek':
        artists = models.Artist.objects.raw('''
        SELECT a.*
        FROM ktapp_artist a
        LEFT JOIN ktapp_picture_artists pa ON pa.artist_id = a.id
        GROUP BY a.id
        HAVING COUNT(pa.id) = 0
        ORDER BY a.number_of_ratings_as_actor DESC
        LIMIT {offset}, {limit}
        '''.format(offset=offset_min, limit=100))
    elif miss_type == 'nem':
        artists = models.Artist.objects.filter(gender=models.Artist.GENDER_TYPE_UNKNOWN).order_by('-number_of_ratings')[offset_min:offset_max]
    else:
        raise Http404
    return render(request, 'ktapp/artists_with_missing_data.html', {
        'active_tab': miss_type,
        'artists': artists,
        'p': p,
    })


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
    now = datetime.datetime.now()
    if request.user.is_authenticated():
        noti_comment_ids = {noti.comment_id for noti in models.Notification.objects.filter(target_user=request.user, notification_type=models.Notification.NOTIFICATION_TYPE_COMMENT, topic=topic)}
        models.Notification.objects.filter(target_user=request.user, notification_type=models.Notification.NOTIFICATION_TYPE_COMMENT, topic=topic).delete()
        extended_comments = []
        for comment in comments:
            if comment.id in noti_comment_ids:
                comment.notified = True
            extended_comments.append(comment)
    else:
        extended_comments = comments
    your_subscription = ''
    if request.user.is_authenticated():
        your_subscription = models.Subscription.get_subscription_status(
            user=request.user,
            topic=topic,
        )
    return render(request, 'ktapp/forum.html', {
        'topic': topic,
        'closed': (topic.closed_until > now) if topic.closed_until else False,
        'closed_seconds': int((topic.closed_until - now).total_seconds()) if topic.closed_until else 0,
        'comments': extended_comments,
        'comment_form': comment_form,
        'reply_to_comment': reply_to_comment,
        'p': p,
        'max_pages': max_pages,
        'your_subscription': your_subscription,
    })


def latest_comments(request):
    t = request.GET.get('t', '')
    if t not in {'', 'filmes'}:
        t = ''
    if t == 'filmes':
        comments = models.Comment.objects.filter(domain='F').select_related('film', 'created_by', 'reply_to', 'reply_to__created_by').all()[:100]
    else:
        comments = models.Comment.objects.exclude(topic_id=38).exclude(topic_id=87).select_related('film', 'topic', 'poll', 'created_by', 'reply_to', 'reply_to__created_by').all()[:100]  # skip Game and OFF topics
    return render(request, 'ktapp/latest_comments.html', {
        'comments': comments,
        't': t,
    })


def favourites(request):
    if not request.user.is_authenticated():
        return render(request, 'ktapp/favourites.html')

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


def similar_users(request):
    if not request.user.is_authenticated():
        return render(request, 'ktapp/similar_users.html')

    genre_slug_cache = kt_utils.strip_whitespace(request.GET.get('mufaj', ''))
    try:
        genre = models.Keyword.objects.get(slug_cache=genre_slug_cache, keyword_type=models.Keyword.KEYWORD_TYPE_GENRE)
    except models.Keyword.DoesNotExist:
        genre = None
    if genre:
        genre_slug_cache = genre.slug_cache
        genre_name = genre.name
    else:
        genre_slug_cache = ''
        genre_name = ''
    links = [('', u'általában')]
    for keyword in models.Keyword.objects.filter(keyword_type=models.Keyword.KEYWORD_TYPE_GENRE).order_by('name'):
        links.append((keyword.slug_cache, keyword.name))

    user_list = []
    cursor = connection.cursor()
    if genre:
        try:
            self_uur = models.UserUserRating.objects.get(user_1=request.user, user_2=request.user, keyword=genre)
        except models.UserUserRating.DoesNotExist:
            self_uur = None
        if self_uur:
            number_of_ratings_limit = self_uur.number_of_ratings / 4
        else:
            number_of_ratings_limit = 0
        cursor.execute(kt_sqls.SIMILAR_USERS_PER_GENRE, (request.user.id, request.user.id, number_of_ratings_limit, genre.id))
    else:
        number_of_ratings_limit = request.user.number_of_ratings / 5
        cursor.execute(kt_sqls.SIMILAR_USERS, (request.user.id, request.user.id, number_of_ratings_limit))
    for row in cursor.fetchall():
        if row[1] < 75:
            break
        user_list.append(row)

    return render(request, 'ktapp/similar_users.html', {
        'links': links,
        'genre_name': genre_name,
        'genre_slug_cache': genre_slug_cache,
        'user_list': user_list,
        'number_of_ratings_limit': number_of_ratings_limit * 2,
    })


def usertoplists(request):
    return render(request, 'ktapp/usertoplists.html', {
        'usertoplists': models.UserToplist.objects.all().select_related('created_by').order_by('-created_at'),
        'permission_new_usertoplist': kt_utils.check_permission('new_usertoplist', request.user),
    })


def usertoplist(request, id, title_slug):
    toplist = get_object_or_404(models.UserToplist, pk=id)
    next_url = request.GET.get('next', request.POST.get('next', reverse('usertoplist', args=(toplist.id, toplist.slug_cache))))
    if request.POST:
        if not kt_utils.check_permission('edit_usertoplist', request.user):
            return HttpResponseRedirect(next_url)
        if request.user.id != toplist.created_by_id:
            return HttpResponseRedirect(next_url)
        title = request.POST.get('title', '').strip()
        if title == '':
            return HttpResponseRedirect(next_url)
        ordered = 1 if request.POST.get('ordered', '') == '1' else 0
        items = []
        for r in xrange(1, 21):
            raw_comment = request.POST.get('comment_%d' % r, '').strip()
            if toplist.toplist_type == 'F':
                raw_film = request.POST.get('film_%d' % r, '').strip()
                if raw_film == '':
                    continue
                if ' / ' in raw_film:
                    raw_orig_title, raw_second_title = raw_film.split(' / ', 1)
                else:
                    raw_orig_title, raw_second_title = raw_film, ''
                raw_orig_title = raw_orig_title.strip()
                if raw_orig_title[-1] == ')':
                    raw_orig_title, raw_year = raw_orig_title[:-1].rsplit('(', 1)
                else:
                    raw_year = None
                orig_title = raw_orig_title.strip()
                second_title = raw_second_title.strip()
                try:
                    year = int(raw_year)
                except:
                    year = None
                films = models.Film.objects.filter(orig_title=orig_title)
                if second_title:
                    films = films.filter(second_title=second_title)
                if year:
                    films = films.filter(year=year)
                films = list(films[:1])
                if len(films) == 0:
                    continue
                film = films[0]
                items.append((film, raw_comment))
            else:
                raw_artist = request.POST.get('artist_%d' % r, '').strip()
                if raw_artist == '':
                    continue
                artist = models.Artist.get_artist_by_name(raw_artist)
                if artist is None:
                    continue
                items.append((artist, raw_comment))
        if len(items) < 3 or len(items) > 20:
            return HttpResponseRedirect(next_url)
        number_of_comments = 0
        for item_object, comment in items:
            if comment:
                number_of_comments += 1
        toplist.title = title
        toplist.ordered = ordered
        toplist.quality = 1 if number_of_comments == len(items) else 0
        toplist.number_of_items = len(items)
        toplist.save()
        models.UserToplistItem.objects.filter(usertoplist=toplist).delete()
        for idx, (item_object, comment) in enumerate(items):
            if toplist.toplist_type == 'F':
                film, director, actor = item_object, None, None
            elif toplist.toplist_type == 'D':
                film, director, actor = None, item_object, None
            else:
                film, director, actor = None, None, item_object
            models.UserToplistItem.objects.create(
                usertoplist=toplist,
                serial_number=idx + 1,
                film=film,
                director=director,
                actor=actor,
                comment=comment,
            )
        models.Event.objects.create(
            user=request.user,
            event_type=models.Event.EVENT_TYPE_EDIT_TOPLIST,
            some_id=toplist.id,
        )
        return HttpResponseRedirect(reverse('usertoplist', args=(toplist.id, toplist.slug_cache)))

    if toplist.toplist_type == models.UserToplist.TOPLIST_TYPE_FILM:
        items, _ = filmlist.filmlist(
            user_id=request.user.id,
            filters=[('usertoplist_id', toplist.id)],
            ordering='serial_number',
            films_per_page=None,
        )
        toplist_list = []
        with_comments = False
        for item in items:
            toplist_list.append(item)
            if item.comment:
                with_comments = True
    else:
        toplist_list = []
        with_comments = False
        for item in models.UserToplistItem.objects.filter(usertoplist=toplist).select_related('director', 'actor').order_by('serial_number'):
            toplist_list.append(item)
            if item.comment:
                with_comments = True
    return render(request, 'ktapp/usertoplist.html', {
        'toplist': toplist,
        'toplist_list': toplist_list,
        'with_comments': with_comments,
        'rows': [(r+1, toplist_list[r] if r < len(toplist_list) else None) for r in xrange(20)],
        'permission_edit_usertoplist': kt_utils.check_permission('edit_usertoplist', request.user),
        'permission_delete_usertoplist': kt_utils.check_permission('delete_usertoplist', request.user),
    })


@login_required
@kt_utils.kt_permission_required('new_usertoplist')
def new_usertoplist(request):
    next_url = request.GET.get('next', request.POST.get('next', reverse('new_usertoplist')))
    if request.POST:
        title = request.POST.get('title', '').strip()
        if title == '':
            return HttpResponseRedirect(next_url)
        toplist_type = request.POST.get('toplist_type', '')
        if toplist_type not in {'F', 'D', 'A'}:
            toplist_type = 'F'
        ordered = 1 if request.POST.get('ordered', '') == '1' else 0
        items = []
        for r in xrange(1, 21):
            raw_comment = request.POST.get('comment_%d' % r, '').strip()
            if toplist_type == 'F':
                raw_film = request.POST.get('film_%d' % r, '').strip()
                if raw_film == '':
                    continue
                if ' / ' in raw_film:
                    raw_orig_title, raw_second_title = raw_film.split(' / ')
                else:
                    raw_orig_title, raw_second_title = raw_film, ''
                raw_orig_title = raw_orig_title.strip()
                if raw_orig_title[-1] == ')':
                    raw_orig_title, raw_year = raw_orig_title[:-1].rsplit('(', 1)
                else:
                    raw_year = None
                orig_title = raw_orig_title.strip()
                second_title = raw_second_title.strip()
                try:
                    year = int(raw_year)
                except:
                    year = None
                films = models.Film.objects.filter(orig_title=orig_title)
                if second_title:
                    films = films.filter(second_title=second_title)
                if year:
                    films = films.filter(year=year)
                films = list(films[:1])
                if len(films) == 0:
                    continue
                film = films[0]
                items.append((film, raw_comment))
            else:
                raw_artist = request.POST.get('artist_%d' % r, '').strip()
                if raw_artist == '':
                    continue
                artist = models.Artist.get_artist_by_name(raw_artist)
                if artist is None:
                    continue
                items.append((artist, raw_comment))
        if len(items) < 3 or len(items) > 20:
            return HttpResponseRedirect(next_url)
        number_of_comments = 0
        for item_object, comment in items:
            if comment:
                number_of_comments += 1
        utl = models.UserToplist.objects.create(
            title=title,
            created_by=request.user,
            ordered=ordered,
            quality=1 if number_of_comments == len(items) else 0,
            number_of_items=len(items),
            toplist_type=toplist_type,
        )
        for idx, (item_object, comment) in enumerate(items):
            if utl.toplist_type == 'F':
                film, director, actor = item_object, None, None
            elif utl.toplist_type == 'D':
                film, director, actor = None, item_object, None
            else:
                film, director, actor = None, None, item_object
            models.UserToplistItem.objects.create(
                usertoplist=utl,
                serial_number=idx + 1,
                film=film,
                director=director,
                actor=actor,
                comment=comment,
            )
        models.Event.objects.create(
            user=request.user,
            event_type=models.Event.EVENT_TYPE_NEW_TOPLIST,
            some_id=utl.id,
        )
        return HttpResponseRedirect(reverse('usertoplist', args=(utl.id, utl.slug_cache)))
    return render(request, 'ktapp/new_usertoplist.html', {
        'rows': xrange(1, 21),
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
    comments = selected_poll.comment_set.select_related('created_by', 'reply_to', 'reply_to__created_by').all()
    if request.user.is_authenticated():
        noti_comment_ids = {noti.comment_id for noti in models.Notification.objects.filter(target_user=request.user, notification_type=models.Notification.NOTIFICATION_TYPE_COMMENT, poll=selected_poll)}
        models.Notification.objects.filter(target_user=request.user, notification_type=models.Notification.NOTIFICATION_TYPE_COMMENT, poll=selected_poll).delete()
        extended_comments = []
        for comment in comments:
            if comment.id in noti_comment_ids:
                comment.notified = True
            extended_comments.append(comment)
    else:
        extended_comments = comments
    your_subscription = ''
    if request.user.is_authenticated():
        your_subscription = models.Subscription.get_subscription_status(
            user=request.user,
            poll=selected_poll,
        )
    return render(request, 'ktapp/poll.html', {
        'poll': selected_poll,
        'pollchoices': pollchoices,
        'sum_number_of_votes': sum_number_of_votes,
        'comments': extended_comments,
        'comment_form': comment_form,
        'reply_to_comment': reply_to_comment,
        'permission_poll_admin': kt_utils.check_permission('poll_admin', request.user),
        'your_subscription': your_subscription,
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


@login_required
@kt_utils.kt_permission_required('approve_review')
def suggested_reviews(request):
    return render(request, 'ktapp/list_of_reviews.html', {
        'unapproved_reviews': models.Review.objects.select_related('film', 'created_by').filter(approved=False).order_by('-created_at'),
    })


@login_required
@kt_utils.kt_permission_required('approve_bio')
def suggested_bios(request):
    return render(request, 'ktapp/list_of_bios.html', {
        'unapproved_bios': models.Biography.objects.select_related('artist', 'created_by').filter(approved=False).order_by('-created_at'),
    })


def latest_pictures(request):
    pictures = list(models.Picture.objects.raw('''
        SELECT
          p.*,
          f.id AS film_id,
          f.slug_cache AS film_slug_cache,
          f.orig_title AS film_orig_title,
          f.second_title AS film_second_title,
          f.year AS film_year,
          a.id AS artist_id,
          a.slug_cache AS artist_slug_cache,
          a.name AS artist_name
        FROM ktapp_picture p USE INDEX (ktapp_picture_created_at_3047bfe36ccde785_uniq)
        LEFT JOIN ktapp_film f ON f.id = p.film_id
        LEFT JOIN ktapp_artist a ON a.id = p.artist_id
        ORDER BY p.created_at DESC
        LIMIT 100
    '''))  # NOTE: apparently MySQL is an idiot
    return render(request, 'ktapp/latest_pictures.html', {
        'pictures': pictures,
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
    films, _ = filmlist.filmlist(
        user_id=request.user.id,
        filters=[('sequel', selected_sequel.id)],
        ordering='sequel',
        films_per_page=None,
    )
    return render(request, 'ktapp/sequel.html', {
        'sequel': selected_sequel,
        'films': films,
    })


def awards(request):
    award_name = request.GET.get('dij', '')
    if award_name:
        award_list = models.Award.objects.filter(name=award_name).select_related('film', 'artist').order_by('-year', 'category')
    else:
        award_list = models.Award.objects.values('name').distinct().order_by('name')
    return render(request, 'ktapp/awards.html', {
        'award_name': award_name,
        'award_list': award_list,
    })


def suggested_links(request):
    return render(request, 'ktapp/suggested_links.html', {
        'permission_new_link': kt_utils.check_permission('new_link', request.user),
        'links': sorted([
            {
                'id': sc.id,
                'created_by': sc.created_by,
                'created_at': sc.created_at,
                'content': json.loads(sc.content),
            }
            for sc in models.SuggestedContent.objects.select_related('created_by').filter(domain=models.SuggestedContent.DOMAIN_LINK)
        ], key=lambda link: (link['content'].get('film')['orig_title'] if link['content'].get('film') else '', link['created_at'])),
    })


def articles(request):
    t = request.GET.get('t', 'latest')
    if t not in {'filmek', 'muveszek', 'egyeb'}:
        t = 'latest'
    if t == 'latest':
        active_tab = 'latest'
        latest_content = []
        for item in models.Review.objects.select_related('film', 'created_by').filter(approved=True).order_by('-created_at')[:50]:
            item.author = item.created_by
            latest_content.append((item.created_at, 'review', item))
        for item in models.Link.objects.filter(featured=True).exclude(lead='').select_related('author', 'created_by', 'film', 'artist').order_by('-created_at')[:50]:
            latest_content.append((item.created_at, 'link', item))
        list_of_articles = sorted(latest_content, key=lambda x: x[0], reverse=True)[:50]
    elif t == 'filmek':
        active_tab = 'films'
        list_of_articles = list(models.Link.objects.raw(u'''
            SELECT
              CONCAT('L', l.id) AS id, l.name, 'link' AS url_type, l.id as orig_id,
              l.url,
              l.link_domain, l.lead,
              f.id AS film_id, f.orig_title AS film_orig_title, f.second_title AS film_second_title, f.slug_cache AS film_slug_cache, f.year AS film_year, f.main_premier_year AS film_main_premier_year, f.vapiti_year AS film_vapiti_year,
              u.id AS author_user_id, u.username AS author_name, u.slug_cache AS author_slug_cache
            FROM ktapp_link l
            INNER JOIN ktapp_film f ON f.id = l.film_id
            LEFT JOIN ktapp_ktuser u ON u.id = l.author_id
            WHERE l.lead != '' AND l.artist_id IS NULL

            UNION

            SELECT
              CONCAT('R', r.id) AS id, CONCAT(f.orig_title, ' (', f.year, ')') AS name, 'review' AS url_type, r.id as orig_id,
              CONCAT('/film/', f.id, '/', f.slug_cache, '/elemzesek/', r.id) AS url,
              'Kritikus Tömeg' AS link_domain, CONCAT(r.snippet, '...') AS lead,
              f.id AS film_id, f.orig_title AS film_orig_title, f.second_title AS film_second_title, f.slug_cache AS film_slug_cache, f.year AS film_year, f.main_premier_year AS film_main_premier_year, f.vapiti_year AS film_vapiti_year,
              u.id AS author_user_id, u.username AS author_name, u.slug_cache AS author_slug_cache
            FROM ktapp_review r
            INNER JOIN ktapp_film f ON f.id = r.film_id
            LEFT JOIN ktapp_ktuser u ON u.id = r.created_by_id
            WHERE r.approved = 1

            ORDER BY film_orig_title, film_year, film_id, id
        '''))
    elif t == 'muveszek':
        active_tab = 'artists'
        list_of_articles = list(models.Link.objects.raw(u'''
            SELECT
              CONCAT('L', l.id) AS id, l.name, 'link' AS url_type, l.id as orig_id,
              l.url,
              l.link_domain, l.lead,
              a.id AS artist_id, a.name AS artist_name, a.slug_cache AS artist_slug_cache,
              u.id AS author_user_id, u.username AS author_name, u.slug_cache AS author_slug_cache
            FROM ktapp_link l
            INNER JOIN ktapp_artist a ON a.id = l.artist_id
            LEFT JOIN ktapp_ktuser u ON u.id = l.author_id
            WHERE l.lead != '' AND l.film_id IS NULL

            UNION

            SELECT
              CONCAT('B', b.id) AS id, a.name AS name, 'bio' AS url_type, b.id as orig_id,
              CONCAT('/muvesz/', a.id, '/', a.slug_cache) AS url,
              'Kritikus Tömeg' AS link_domain, CONCAT(b.snippet, '...') AS lead,
              a.id AS artist_id, a.name AS artist_name, a.slug_cache AS artist_slug_cache,
              u.id AS author_user_id, u.username AS author_name, u.slug_cache AS author_slug_cache
            FROM ktapp_biography b
            INNER JOIN ktapp_artist a ON a.id = b.artist_id
            LEFT JOIN ktapp_ktuser u ON u.id = b.created_by_id
            WHERE b.approved = 1

            ORDER BY artist_name, artist_id, id
        '''))
    else:
        active_tab = 'misc'
        list_of_articles = list(models.Link.objects.raw(u'''
            SELECT
              CONCAT('L', l.id) AS id, l.name, 'link' AS url_type, l.id as orig_id,
              l.url,
              l.link_domain, l.lead,
              u.id AS author_user_id, u.username AS author_name, u.slug_cache AS author_slug_cache
            FROM ktapp_link l
            LEFT JOIN ktapp_ktuser u ON u.id = l.author_id
            WHERE l.lead != '' AND l.film_id IS NULL AND l.artist_id IS NULL
            ORDER BY name, id
        '''))

    p, max_pages = 1, 1
    if t != 'latest':
        number_of_articles = len(list_of_articles)
        p = int(request.GET.get('p', 0))
        if p == 1:
            return HttpResponseRedirect(reverse('articles') + '?t={t}'.format(t=t))
        max_pages = int(math.ceil(1.0 * number_of_articles / ARTICLES_PER_PAGE))
        if max_pages == 0:
            max_pages = 1
        if p == 0:
            p = 1
        if p > max_pages:
            return HttpResponseRedirect(reverse('articles') + '?t={t}&p={p}'.format(t=t, p=max_pages))
        list_of_articles = list_of_articles[(p-1)*ARTICLES_PER_PAGE:p*ARTICLES_PER_PAGE]

    return render(request, 'ktapp/articles_subpages/about_%s.html' % active_tab, {
        'active_tab': active_tab,
        'url_param_t': t,
        'p': p,
        'max_pages': max_pages,
        'articles': list_of_articles,
        'permission_suggest_link': kt_utils.check_permission('suggest_link', request.user),
        'permission_new_link': kt_utils.check_permission('new_link', request.user),
        'permission_edit_link': kt_utils.check_permission('edit_link', request.user),
        'permission_delete_link': kt_utils.check_permission('delete_link', request.user),
    })


def email_header(request):
    user_id = request.GET.get('u', 0)
    email_type = request.GET.get('t', '')
    campaign_id = request.GET.get('c', 0)
    if user_id:
        try:
            user = models.KTUser.objects.get(id=user_id)
        except models.KTUser.DoesNotExist:
            user = None
    else:
        user = None
    if campaign_id:
        try:
            campaign = models.EmailCampaign.objects.get(id=campaign_id)
        except models.EmailCampaign.DoesNotExist:
            campaign = None
    else:
        campaign = None
    models.EmailOpen.objects.create(
        user=user,
        email_type=email_type,
        campaign=campaign,
    )
    email_header_jpg = open('/home/publisher/kt/current/static/ktapp/images/email_header_v2.jpg', 'rb')
    response = HttpResponse(content=email_header_jpg.read())
    response['Content-Type'] = 'image/jpg'
    return response


def click(request):
    user_id = request.GET.get('u', 0)
    email_type = request.GET.get('t', '')
    campaign_id = request.GET.get('c', 0)
    if user_id:
        try:
            user = models.KTUser.objects.get(id=user_id)
        except models.KTUser.DoesNotExist:
            user = None
    else:
        user = None
    if campaign_id:
        try:
            campaign = models.EmailCampaign.objects.get(id=campaign_id)
        except models.EmailCampaign.DoesNotExist:
            campaign = None
    else:
        campaign = None
    url = request.GET.get('url', '')
    models.EmailClick.objects.create(
        user=user,
        email_type=email_type,
        campaign=campaign,
        url=url,
    )
    if url:
        return HttpResponseRedirect(url)
    raise Http404


def link_click(request):
    url = request.GET.get('url', '')
    raw_link_type = request.GET.get('t', '')
    if raw_link_type == 'l':
        link_type = models.LinkClick.LINK_TYPE_LINK
    elif raw_link_type == 'im':
        link_type = models.LinkClick.LINK_TYPE_FILM_IMDB
    elif raw_link_type == 'po':
        link_type = models.LinkClick.LINK_TYPE_FILM_PORTHU
    elif raw_link_type == 'rt':
        link_type = models.LinkClick.LINK_TYPE_FILM_RT
    elif raw_link_type == 'yt':
        link_type = models.LinkClick.LINK_TYPE_FILM_YOUTUBE
    elif raw_link_type == 'we':
        link_type = models.LinkClick.LINK_TYPE_FILM_WIKI_EN
    elif raw_link_type == 'wh':
        link_type = models.LinkClick.LINK_TYPE_FILM_WIKI_HU
    elif raw_link_type == 'is':
        link_type = models.LinkClick.LINK_TYPE_FILM_ISZDB
    elif raw_link_type == 'ai':
        link_type = models.LinkClick.LINK_TYPE_ARTIST_IMDB
    elif raw_link_type == 'ae':
        link_type = models.LinkClick.LINK_TYPE_ARTIST_WIKI_EN
    elif raw_link_type == 'ah':
        link_type = models.LinkClick.LINK_TYPE_ARTIST_WIKI_HU
    else:
        link_type = models.LinkClick.LINK_TYPE_OTHER
    link = None
    raw_link_id = request.GET.get('l', '')
    if raw_link_id:
        try:
            link = models.Link.objects.get(id=raw_link_id)
        except models.Link.DoesNotExist:
            pass
    film = None
    raw_film_id = request.GET.get('f', '')
    if raw_film_id:
        try:
            film = models.Film.objects.get(id=raw_film_id)
        except models.Film.DoesNotExist:
            pass
    artist = None
    raw_artist_id = request.GET.get('a', '')
    if raw_artist_id:
        try:
            artist = models.Artist.objects.get(id=raw_artist_id)
        except models.Artist.DoesNotExist:
            pass
    models.LinkClick.objects.create(
        url=url,
        referer=request.META.get('HTTP_REFERER', ''),
        user=request.user if request.user.is_authenticated() else None,
        link_type=link_type,
        link=link,
        film=film,
        artist=artist,
    )
    if url:
        return HttpResponseRedirect(url)
    raise Http404


def impressum(request):
    return render(request, 'ktapp/impressum.html', {
        'inner_staff': models.KTUser.objects.filter(is_inner_staff=True).order_by('username', 'id'),
        'outer_staff': models.KTUser.objects.filter(is_staff=True).exclude(is_inner_staff=True).order_by('username', 'id'),
    })


def about_page(request):
    return render(request, 'ktapp/about_page.html')


def rulez(request):
    return render(request, 'ktapp/rulez.html')


def privacy_policy(request):
    if request.user.is_authenticated() and request.POST:
        request.user.signed_privacy_policy = True
        request.user.signed_privacy_policy_at = datetime.datetime.now()
        request.user.save()
        return HttpResponseRedirect(reverse('index'))
    return render(request, 'ktapp/privacy_policy.html')


def blacklist(request):
    set_of_user_ids = set()
    list_of_bans = []
    for ban in models.Change.objects.filter(
        action__in=['ban', 'unban', 'warning', 'temp_ban_1d', 'temp_ban_3d', 'temp_ban_7d'],
    ).order_by('-created_at'):
        user_id = int(ban.object[5:])
        set_of_user_ids.add(user_id)
        list_of_bans.append((
            ban.created_at,
            user_id,
            ban.action,
        ))
    banned_users = {}
    for user in models.KTUser.objects.filter(id__in=set_of_user_ids):
        banned_users[user.id] = user
    old_banned_users = models.KTUser.objects.filter(
        is_active=False,
        reason_of_inactivity__in=[models.KTUser.REASON_BANNED, models.KTUser.REASON_TEMPORARILY_BANNED],
    ).exclude(id__in=set_of_user_ids).order_by('-date_joined')
    return render(request, 'ktapp/blacklist.html', {
        'list_of_bans': [
            (
                ban[0],
                banned_users.get(ban[1]),
                texts.BAN_TYPES.get(ban[2]),
            )
            for ban in list_of_bans
        ] + [
            (
                '?',
                u,
                texts.BAN_TYPES['ban'],
            )
            for u in old_banned_users
        ],
    })


def finance(request):
    finance_status, finance_missing = kt_utils.get_finance(models.Donation)
    number_of_donators, amount_of_donation = kt_utils.get_banner_version(request.user.id)
    return render(request, 'ktapp/finance.html', {
        'finance_status': finance_status,
        'finance_amount': finance_missing,
        'number_of_donators': number_of_donators,
        'amount_of_donation': amount_of_donation,
        'donators': models.KTUser.objects.raw('''
        SELECT DISTINCT u.*
        FROM ktapp_ktuser u
        INNER JOIN ktapp_donation d ON d.given_by_id = u.id
        ORDER BY u.username, u.id
        '''),
    })


def vapiti_general(request):
    future_winners = None
    if request.user.is_authenticated() and request.user.id in {1, 13114}:
        today_str = datetime.date.today().strftime('%Y-%m-%d')
        vapiti_round, round_1_dates, round_2_dates, result_day = kt_utils.get_vapiti_round()
        if today_str == result_day:
            try:
                cursor = connection.cursor()
                cursor.execute(kt_sqls.VAPITI_WINNER_GOLD, (settings.VAPITI_YEAR,))
                winner_film = models.Film.objects.get(id=cursor.fetchone()[0])
                cursor.execute(kt_sqls.VAPITI_WINNER_SILVER_FEMALE, (settings.VAPITI_YEAR,))
                winner_female_role = models.FilmArtistRelationship.objects.get(id=cursor.fetchone()[0])
                cursor.execute(kt_sqls.VAPITI_WINNER_SILVER_MALE, (settings.VAPITI_YEAR,))
                winner_male_role = models.FilmArtistRelationship.objects.get(id=cursor.fetchone()[0])
                future_winners = {
                    'year': settings.VAPITI_YEAR,
                    'g': winner_film,
                    'f': {
                        'artist': models.Artist.objects.get(id=winner_female_role.artist_id),
                        'film': models.Film.objects.get(id=winner_female_role.film_id),
                    },
                    'm': {
                        'artist': models.Artist.objects.get(id=winner_male_role.artist_id),
                        'film': models.Film.objects.get(id=winner_male_role.film_id),
                    },
                }
            except Exception:
                pass
    raw_awards = [(a, a.film_id, a.artist) for a in models.Award.objects.filter(
        name=u'Vapiti',
        category__in=texts.VAPITI_WINNER_CATEGORIES.values(),
    ).select_related('artist').order_by('-year', '-id')]
    raw_roles = {
        (role.film_id, role.artist_id): role
        for role in models.FilmArtistRelationship.objects.filter(
            film_id__in=[film_id for _, film_id, _ in raw_awards],
            artist_id__in=[artist.id for _, _, artist in raw_awards if artist],
        )
    }
    films, _ = filmlist.filmlist(
        user_id=request.user.id,
        filters=[('film_id_list', ','.join([str(film_id) for _, film_id, _ in raw_awards]))],
        films_per_page=None,
    )
    raw_films = {film.id: film for film in films}
    awards = defaultdict(list)
    for award, film_id, artist in raw_awards:
        film = copy.deepcopy(raw_films[film_id])
        film.award = award
        film.award_type = {
            texts.VAPITI_WINNER_CATEGORIES['G']: 0,
            texts.VAPITI_WINNER_CATEGORIES['F']: 1,
            texts.VAPITI_WINNER_CATEGORIES['M']: 2
        }[award.category]
        film.artist = artist
        if artist:
            film.role = raw_roles[(film_id, artist.id)]
        else:
            film.role = None
        awards[(award.year, film.award_type)].append(film)
    final_awards = []
    current_year = 0
    for (year, category), film_list in sorted(awards.iteritems(), key=lambda item: item[0][0], reverse=True):
        if year != current_year:
            final_awards.append([[], [], []])
            current_year = year
        for film in sorted(film_list, key=lambda film: film.award.id):
            final_awards[-1][category].append(film)
    return render(request, 'ktapp/vapiti_subpages/vapiti_general.html', {
        'future_winners': future_winners,
        'vapiti_year': settings.VAPITI_YEAR,
        'awards': final_awards,
    })


def vapiti_gold(request):
    vapiti_round, round_1_dates, round_2_dates, result_day = kt_utils.get_vapiti_round()
    my_vapiti_votes = {}
    if request.user.is_authenticated():
        for vv in models.VapitiVote.objects.filter(
            user=request.user,
            year=settings.VAPITI_YEAR,
            vapiti_round=vapiti_round,
            vapiti_type=models.VapitiVote.VAPITI_TYPE_GOLD,
        ).select_related('film'):
            my_vapiti_votes[vv.serial_number] = ('%s / %s' % (vv.film.orig_title, vv.film.second_title)) if vv.film.second_title else vv.film.orig_title
    films, _ = filmlist.filmlist(
        user_id=request.user.id,
        filters=[('vapiti_year', settings.VAPITI_YEAR)],
        ordering='title',
        films_per_page=None,
    )
    films_yes = []
    films_no = []
    for film in films:
        if request.user.is_authenticated():
            if film.my_rating:
                films_yes.append(film)
            else:
                films_no.append(film)
        else:
            films_no.append(film)
    films_yes.sort(key=lambda film: (film.my_rating, film.average_rating, film.number_of_ratings), reverse=True)
    return render(request, 'ktapp/vapiti_subpages/vapiti_gold.html', {
        'vapiti_year': settings.VAPITI_YEAR,
        'active_tab': '',
        'films_yes': films_yes,
        'films_no': films_no,
        'vapiti_round': vapiti_round,
        'round_1_dates': round_1_dates,
        'round_2_dates': round_2_dates,
        'result_day': result_day,
        'my_vapiti_votes': my_vapiti_votes,
    })


def vapiti_gold_2(request):
    vapiti_round, round_1_dates, round_2_dates, result_day = kt_utils.get_vapiti_round()
    nominee_ids = kt_utils.get_vapiti_nominees(models.Award, models.VapitiVote.VAPITI_TYPE_GOLD)
    if request.user.is_authenticated():
        my_votes = {v.film_id: v.rating for v in models.Vote.objects.filter(user_id=request.user.id, film_id__in=nominee_ids)}
    else:
        my_votes = {}
    nominees = []
    for nominee in models.Film.objects.filter(id__in=nominee_ids).order_by('orig_title', 'second_title', 'id'):
        nominee.my_rating = my_votes.get(nominee.id)
        nominees.append(nominee)
    my_vapiti_vote = None
    if request.user.is_authenticated():
        for vv in models.VapitiVote.objects.filter(
                user=request.user,
                year=settings.VAPITI_YEAR,
                vapiti_round=vapiti_round,
                vapiti_type=models.VapitiVote.VAPITI_TYPE_GOLD,
        ):
            my_vapiti_vote = vv.film_id
    return render(request, 'ktapp/vapiti_subpages/vapiti_gold_2.html', {
        'vapiti_year': settings.VAPITI_YEAR,
        'active_tab': '2',
        'vapiti_round': vapiti_round,
        'round_1_dates': round_1_dates,
        'round_2_dates': round_2_dates,
        'result_day': result_day,
        'nominees': nominees,
        'my_vapiti_vote': my_vapiti_vote,
    })


def vapiti_gold_winners(request):
    raw_awards = [(a.year, a.film_id) for a in models.Award.objects.filter(
        name=u'Vapiti',
        category=texts.VAPITI_WINNER_CATEGORIES['G'],
    ).order_by('-year', '-id')]
    films, _ = filmlist.filmlist(
        user_id=request.user.id,
        filters=[('film_id_list', ','.join([str(film_id) for _, film_id in raw_awards]))],
        films_per_page=None,
    )
    raw_films = {film.id: film for film in films}
    awards = []
    for year, film_id in raw_awards:
        film = raw_films[film_id]
        film.award_year = year
        awards.append(film)
    return render(request, 'ktapp/vapiti_subpages/vapiti_gold_winners.html', {
        'vapiti_year': settings.VAPITI_YEAR,
        'active_tab': 'winners',
        'awards': awards,
    })


def vapiti_silver(request, gender):
    vapiti_type = models.VapitiVote.VAPITI_TYPE_SILVER_MALE if gender == 'ferfi' else models.VapitiVote.VAPITI_TYPE_SILVER_FEMALE
    vapiti_round, round_1_dates, round_2_dates, result_day = kt_utils.get_vapiti_round()
    my_vapiti_votes = {}
    if request.user.is_authenticated():
        for vv in models.VapitiVote.objects.filter(
                user=request.user,
                year=settings.VAPITI_YEAR,
                vapiti_round=vapiti_round,
                vapiti_type=vapiti_type,
        ).select_related('film', 'artist'):
            my_vapiti_votes[vv.serial_number] = '%s [%s]' % (
                vv.artist.name,
                ('%s / %s' % (vv.film.orig_title, vv.film.second_title)) if vv.film.second_title else vv.film.orig_title,
            )
    if request.user.is_authenticated():
        my_rating_select = 'v.rating AS my_rating'
        my_rating_join = 'LEFT JOIN ktapp_vote v ON v.film_id = f.id AND v.user_id = {user_id}'.format(user_id=request.user.id)
    else:
        my_rating_select = 'NULL AS my_rating'
        my_rating_join = ''
    roles_yes = []
    roles_no = []
    artist_ids_yes = set()
    artist_ids_no = set()
    for role in models.FilmArtistRelationship.objects.raw('''
    SELECT
      r.*,
      a.id AS artist_id,
      a.slug_cache AS artist_slug_cache,
      a.name AS artist_name,
      f.id AS film_id,
      f.slug_cache AS film_slug_cache,
      f.orig_title AS film_orig_title,
      f.second_title AS film_second_title,
      f.main_premier_year AS film_main_premier_year,
      f.vapiti_year AS film_vapiti_year,
      f.number_of_ratings,
      f.average_rating,
      {my_rating_select}
    FROM ktapp_filmartistrelationship r
    INNER JOIN ktapp_artist a ON a.id = r.artist_id
    INNER JOIN ktapp_film f ON f.id = r.film_id
    {my_rating_join}
    WHERE r.role_type = 'A' AND r.actor_subtype = 'F'
    AND f.vapiti_year = {vapiti_year}
    AND a.gender = '{gender}'
    ORDER BY a.name, a.id, r.role_name, r.id
    '''.format(
        my_rating_select=my_rating_select,
        my_rating_join=my_rating_join,
        vapiti_year=settings.VAPITI_YEAR,
        gender='M' if gender == 'ferfi' else 'F',
    )):
        if role.my_rating:
            roles_yes.append(role)
            artist_ids_yes.add(role.artist_id)
        else:
            roles_no.append(role)
            artist_ids_no.add(role.artist_id)
    # roles_yes.sort(key=lambda role: (-role.my_rating, role.artist_name, role.artist_id, role.role_name, role.id))
    return render(request, 'ktapp/vapiti_subpages/vapiti_silver.html', {
        'vapiti_year': settings.VAPITI_YEAR,
        'gender': gender,
        'active_tab': '',
        'roles_yes': roles_yes,
        'roles_no': roles_no,
        'artists_yes_count': len(artist_ids_yes),
        'artists_no_count': len(artist_ids_no),
        'vapiti_round': vapiti_round,
        'round_1_dates': round_1_dates,
        'round_2_dates': round_2_dates,
        'result_day': result_day,
        'my_vapiti_votes': my_vapiti_votes,
    })


def vapiti_silver_2(request, gender):
    vapiti_type = models.VapitiVote.VAPITI_TYPE_SILVER_MALE if gender == 'ferfi' else models.VapitiVote.VAPITI_TYPE_SILVER_FEMALE
    vapiti_round, round_1_dates, round_2_dates, result_day = kt_utils.get_vapiti_round()
    nominee_ids = kt_utils.get_vapiti_nominees(models.Award, vapiti_type)
    if request.user.is_authenticated():
        my_votes = {v.film_id: v.rating for v in models.Vote.objects.filter(user_id=request.user.id, film_id__in=[film_id for film_id, artist_id in nominee_ids])}
    else:
        my_votes = {}
    nominees = []
    for film_id, artist_id in nominee_ids:
        try:
            role = models.FilmArtistRelationship.objects.select_related('film', 'artist').get(film_id=film_id, artist_id=artist_id, role_type=models.FilmArtistRelationship.ROLE_TYPE_ACTOR)
        except models.FilmArtistRelationship.DoesNotExist:
            continue
        nominee = role
        nominee.my_rating = my_votes.get(film_id)
        nominees.append(nominee)
    nominees.sort(key=lambda nominee: (nominee.artist.name, nominee.artist.id, nominee.film.orig_title, nominee.film.second_title, nominee.film.id))
    my_vapiti_vote_film_id, my_vapiti_vote_artist_id = None, None
    if request.user.is_authenticated():
        for vv in models.VapitiVote.objects.filter(
                user=request.user,
                year=settings.VAPITI_YEAR,
                vapiti_round=vapiti_round,
                vapiti_type=vapiti_type,
        ):
            my_vapiti_vote_film_id = vv.film_id
            my_vapiti_vote_artist_id = vv.artist_id
    return render(request, 'ktapp/vapiti_subpages/vapiti_silver_2.html', {
        'vapiti_year': settings.VAPITI_YEAR,
        'gender': gender,
        'active_tab': '2',
        'vapiti_round': vapiti_round,
        'round_1_dates': round_1_dates,
        'round_2_dates': round_2_dates,
        'result_day': result_day,
        'nominees': nominees,
        'my_vapiti_vote_film_id': my_vapiti_vote_film_id,
        'my_vapiti_vote_artist_id': my_vapiti_vote_artist_id,
    })


def vapiti_silver_winners(request, gender):
    vapiti_type = models.VapitiVote.VAPITI_TYPE_SILVER_MALE if gender == 'ferfi' else models.VapitiVote.VAPITI_TYPE_SILVER_FEMALE
    raw_awards = [(a.year, a.film_id, a.artist) for a in models.Award.objects.filter(
        name=u'Vapiti',
        category=texts.VAPITI_WINNER_CATEGORIES[vapiti_type],
    ).select_related('artist').order_by('-year', '-id')]
    raw_roles = {
        (role.film_id, role.artist_id): role
        for role in models.FilmArtistRelationship.objects.filter(
            film_id__in=[film_id for _, film_id, _ in raw_awards],
            artist_id__in=[artist.id for _, _, artist in raw_awards],
            role_type=models.FilmArtistRelationship.ROLE_TYPE_ACTOR,
        )
    }
    films, _ = filmlist.filmlist(
        user_id=request.user.id,
        filters=[('film_id_list', ','.join([str(film_id) for _, film_id, _ in raw_awards]))],
        films_per_page=None,
    )
    raw_films = {film.id: film for film in films}
    awards = []
    for year, film_id, artist in raw_awards:
        film = raw_films[film_id]
        film.award_year = year
        film.artist = artist
        film.role = raw_roles[(film_id, artist.id)]
        awards.append(film)
    return render(request, 'ktapp/vapiti_subpages/vapiti_silver_winners.html', {
        'vapiti_year': settings.VAPITI_YEAR,
        'gender': gender,
        'active_tab': 'winners',
        'awards': awards,
    })


def contributors(request):
    return render(request, 'ktapp/contributors.html', {
        'users': models.UserContribution.objects.extra(select={'full_rank': 'rank_film + rank_role + rank_keyword + rank_picture + rank_trivia + rank_quote + rank_review + rank_link + rank_biography + rank_poll + rank_usertoplist'}).order_by('full_rank'),
    })


def everybody(request):
    username = kt_utils.strip_whitespace(request.GET.get('username', ''))
    ordering_str = kt_utils.strip_whitespace(request.GET.get('o', ''))
    if ordering_str == '':
        ordering_str = 'id'
    if ordering_str[0] == '-':
        ordering_sign = '-'
        ordering_str = ordering_str[1:]
    else:
        ordering_sign = ''
    if ordering_str not in {
        'id', 'username',
        'number_of_ratings', 'number_of_vapiti_votes', 'vapiti_weight', 'average_rating',
        'number_of_comments', 'number_of_film_comments', 'number_of_topic_comments', 'number_of_poll_comments',
    }:
        ordering_str = 'id'
    if ordering_str in {'id', 'username', 'number_of_ratings'}:
        ordering = (ordering_sign + ordering_str,)
    else:
        ordering = (ordering_sign + ordering_str, '-number_of_ratings',)
    users = models.KTUser.objects
    if username:
        users = users.filter(username__icontains=username)
    result_count = users.count()
    try:
        p = int(request.GET.get('p', 0))
    except ValueError:
        p = 0
    max_pages = int(math.ceil(1.0 * result_count / USERS_PER_PAGE))
    if max_pages == 0:
        max_pages = 1
    if p == 0:
        p = 1
    if p > max_pages:
        p = max_pages
    return render(request, 'ktapp/everybody.html', {
        'users': users.order_by(*ordering)[(p-1) * USERS_PER_PAGE:p * USERS_PER_PAGE],
        'result_count': result_count,
        'p': p,
        'max_pages': max_pages,
        'ordering_str': ordering_sign + ordering_str,
        'username': username,
        'qs_combined': '&username=%s' % username if username else '',
    })


@login_required
def notifications(request):
    notis = list(models.Notification.objects.filter(target_user=request.user).select_related('source_user', 'film', 'topic', 'poll').order_by('-created_at'))
    models.Notification.objects.filter(target_user=request.user).update(is_read=True)
    request.user.unread_notification_count = models.Notification.objects.filter(target_user=request.user, is_read=False).count()
    request.user.save(update_fields=['unread_notification_count'])
    return render(request, 'ktapp/notifications.html', {
        'notifications': notis,
    })


@login_required
@kt_utils.kt_permission_required('analytics')
def analytics(request):

    def date2js(d):
        return 'new Date(%d, %d, %d)' % (
            int(d.strftime('%Y')),
            int(d.strftime('%m')) - 1,
            int(d.strftime('%d')),
        )

    cursor = connection.cursor()
    today = datetime.datetime.today()
    yesterday = (today - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    last_sunday = (today - datetime.timedelta(days=today.weekday()+1)).strftime('%Y-%m-%d')

    # user activity status
    cursor.execute('''
    SELECT day, dau_count, wau_count, mau_count, new_count
    FROM ktapp_activeusercount
    ORDER BY day
    ''')
    activity_data = []
    for row in cursor.fetchall():
        activity_data.append((
            date2js(row[0]),
            row[1],
            row[2],
            row[3],
            row[4],
        ))

    # DAU
    cursor.execute('''
    SELECT day, COUNT(DISTINCT user_id) AS dau
    FROM ktapp_dailyactiveuser
    WHERE day BETWEEN '2015-09-14' AND %s
    GROUP BY day
    ''', [yesterday])
    dau_data = []
    ma7_window = []
    for row in cursor.fetchall():
        ma7_window.append(row[1])
        ma7_window = ma7_window[-7:]
        dau_data.append((
            date2js(row[0]),
            row[1],
            1.0 * sum(ma7_window) / len(ma7_window),
        ))

    # WAU
    cursor.execute('''
    SELECT DATE_SUB(day, INTERVAL WEEKDAY(day) DAY) AS week, COUNT(DISTINCT user_id) AS wau
    FROM ktapp_dailyactiveuser
    WHERE day BETWEEN '2015-09-14' AND %s
    GROUP BY week
    ''', [last_sunday])
    wau_data = []
    for row in cursor.fetchall():
        wau_data.append((
            date2js(row[0]),
            row[1],
        ))

    # forum
    cursor.execute('''
    SELECT DATE_SUB(DATE(created_at), INTERVAL WEEKDAY(DATE(created_at)) DAY) AS week, COUNT(1) AS comment_count, COUNT(DISTINCT created_by_id) AS user_count
    FROM ktapp_comment
    WHERE domain = 'F'
    AND created_at >= '2015-09-14' AND DATE(created_at) <= %s
    GROUP BY week
    ''', [last_sunday])
    forum_data = []
    for row in cursor.fetchall():
        forum_data.append((
            date2js(row[0]),
            row[1],
            row[2],
        ))

    return render(request, 'ktapp/analytics.html', {
        'activity_data': activity_data,
        'dau_data': dau_data,
        'wau_data': wau_data,
        'forum_data': forum_data,
    })


@login_required
@kt_utils.kt_permission_required('analytics')
def email_analytics(request):
    # email
    # NOTE: it's very slow
    cursor = connection.cursor()
    cursor.execute('''
    SELECT
      s.camp, LEFT(s.sent_at, 10) AS sent_at, COALESCE(cmp.subject, '') AS subject,
      s.user_count AS sent_to, s.email_count,
      COALESCE(o.user_count, 0) AS opened_by,
      COALESCE(c.user_count, 0) AS clicked_by,
      COALESCE(ROUND(100.0 * o.user_count / s.user_count), 0) AS open_rate,
      COALESCE(ROUND(100.0 * o.user_count / s.email_count), 0) AS open_email_rate,
      COALESCE(ROUND(100.0 * c.user_count / s.user_count), 0) AS click_rate,
      COALESCE(ROUND(100.0 * c.user_count / s.email_count), 0) AS click_email_rate
    FROM (
        SELECT CASE WHEN email_type = 'c' THEN CONCAT('c #', campaign_id) ELSE email_type END AS camp, COUNT(DISTINCT user_id) AS user_count, MIN(sent_at) AS sent_at, SUM(is_email) AS email_count
        FROM ktapp_emailsend WHERE email_type != '' GROUP BY camp
    ) s
    LEFT JOIN (
        SELECT CONCAT('c #', id) AS camp, title, recipients, subject, sent_at
        FROM ktapp_emailcampaign
    ) cmp ON cmp.camp = s.camp
    LEFT JOIN (
        SELECT CASE WHEN email_type = 'c' THEN CONCAT('c #', campaign_id) ELSE email_type END AS camp, COUNT(DISTINCT user_id) AS user_count
        FROM ktapp_emailopen WHERE email_type != '' GROUP BY camp
    ) o ON o.camp = s.camp
    LEFT JOIN (
        SELECT CASE WHEN email_type = 'c' THEN CONCAT('c #', campaign_id) ELSE email_type END AS camp, COUNT(DISTINCT user_id) AS user_count
        FROM ktapp_emailclick WHERE email_type != '' GROUP BY camp
    ) c ON c.camp = s.camp
    ORDER BY s.sent_at, s.camp
    ''')
    email_data = [row for row in cursor.fetchall()]
    return render(request, 'ktapp/email_analytics.html', {
        'email_data': email_data,
    })


@login_required
@kt_utils.kt_permission_required('logs')
def view_logs(request):
    logtype = request.GET.get('t', '')
    if logtype not in {'cron_log', 'django_debug', 'gunicorn_supervisor', 'kt_access', 'kt_exception'}:
        logtype = 'kt_exception'
    try:
        max_logfile_count = int(request.GET.get('n', '10'))
    except ValueError:
        max_logfile_count = 10
    try:
        max_logfile_length = int(request.GET.get('l', '1000'))
    except ValueError:
        max_logfile_length = 1000

    content = []
    logpath = '/home/publisher/kt/logs/%s' % logtype
    if logtype in {'cron_log', 'gunicorn_supervisor'}:
        if logtype == 'cron_log':
            filename = 'cron.log'
        else:
            filename = 'gunicorn_supervisor.log'
        cmd = 'tail -n ' + str(max_logfile_length) + ' ' + logpath + '/' + filename
        content.append('================================ ' + filename)
        for line in subprocess.check_output(cmd, shell=True).strip().split('\n'):
            content.append(line.strip())
        content.append('================================')
    else:
        cmd = 'ls -lt ' + logpath + ' | awk \'$5{print $9}\' | head -n ' + str(max_logfile_count)
        for filename in subprocess.check_output(cmd, shell=True).strip().split('\n'):
            content.append('================================ ' + filename)
            linecount = 0
            for line in open(logpath + '/' + filename, 'rt'):
                linecount += 1
                if linecount > max_logfile_length:
                    content.append('----------truncated...----------')
                    break
                content.append(line.strip())
            content.append('================================')
            content.append('')
            content.append('')
            content.append('')
    return render(request, 'ktapp/logs.html', {
        'content': '\n'.join(content),
        'logtype': logtype,
        'max_logfile_count': max_logfile_count,
        'max_logfile_length': max_logfile_length,
        'server_time': datetime.datetime.now(),
    })


MISSING_URLS = {
    '/feed_kommentek.php',
    '/feed_bemutatok.php',
    '/wp-login.php',
    '/rendezo.php',
    '/ksz.php',
}

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
        return HttpResponseRedirect(reverse('film_articles', args=(film.id, film.slug_cache)))
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
        return HttpResponseRedirect(reverse('film_articles', args=(film.id, film.slug_cache)))
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
    if request.path == '/elemzesek.php':
        return HttpResponseRedirect(reverse('articles'))
    if request.path == '/idezetek.php':
        return HttpResponseRedirect(reverse('latest_quotes'))
    if request.path == '/dijak.php':
        return HttpResponseRedirect(reverse('awards'))
    if request.path == '/poll2.php':
        return HttpResponseRedirect(reverse('polls') + '?tipus=aktualis')
    if request.path == '/kedvencek.php':
        return HttpResponseRedirect(reverse('favourites'))
    if request.path == '/reg.php':
        return HttpResponseRedirect(reverse('registration'))
    if request.path == '/bemutatok.php':
        return HttpResponseRedirect(reverse('premiers_in_a_year', args=(request.GET.get('ev', ''),)))
    if request.path == '/trivia.php':
        return HttpResponseRedirect(reverse('latest_trivias'))
    if request.path == '/kepek.php':
        return HttpResponseRedirect(reverse('latest_pictures'))
    if request.path == '/hasonlok.php':
        return HttpResponseRedirect(reverse('similar_users'))
    if request.path in MISSING_URLS:
        return HttpResponseNotFound()
    raise Http404
