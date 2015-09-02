# -*- coding: utf-8 -*-

import datetime
import math

from django.db import connection
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Max

from ktapp import models
from ktapp import utils as kt_utils


COMMENTS_PER_PAGE = 100
MESSAGES_PER_PAGE = 50


USER_PROFILE_TAB_WIDTH = {
    True: 14,
    False: 16,
}


def _get_user_profile_numbers(request, selected_user):
    if request.user.is_authenticated() and request.user.id != selected_user.id:
        number_of_messages = models.MessageCountCache.get_count(owned_by=request.user, partner=selected_user)
    else:
        number_of_messages = 0
    return (
        selected_user.number_of_ratings,
        selected_user.number_of_comments,
        selected_user.number_of_wishes_yes + selected_user.number_of_wishes_get,
        selected_user.number_of_toplists,
        number_of_messages,
    )


def user_profile(request, id, name_slug):
    selected_user = get_object_or_404(models.KTUser, pk=id)
    number_of_votes, number_of_comments, number_of_wishes, number_of_toplists, number_of_messages = _get_user_profile_numbers(request, selected_user)
    this_year = datetime.date.today().year
    number_of_vapiti_votes = selected_user.vote_set.filter(film__main_premier_year=this_year).count()
    latest_votes = [int(v) for v in selected_user.latest_votes.split(',') if v != ''][:10]
    latest_comments = [int(c) for c in selected_user.latest_comments.split(',') if c != ''][:10]
    return render(request, 'ktapp/user_profile_subpages/user_profile.html', {
        'active_tab': 'profile',
        'selected_user': selected_user,
        'number_of_votes': number_of_votes,
        'number_of_comments': number_of_comments,
        'number_of_wishes': number_of_wishes,
        'number_of_toplists': number_of_toplists,
        'number_of_messages': number_of_messages,
        'number_of_vapiti_votes': number_of_vapiti_votes,
        'vapiti_weight': number_of_votes + 25 * number_of_vapiti_votes,
        'tab_width': USER_PROFILE_TAB_WIDTH[request.user.is_authenticated() and request.user.id != selected_user.id],
        'latest_votes': selected_user.vote_set.filter(id__in=latest_votes).select_related('film').order_by('-when', '-id'),
        'latest_comments': models.Comment.objects.filter(id__in=latest_comments).select_related('film', 'topic', 'poll', 'created_by', 'reply_to', 'reply_to__created_by'),
        'myfav': models.Follow.objects.filter(who=request.user, whom=selected_user).count() if request.user.is_authenticated() else 0,
    })


def user_films(request, id, name_slug):
    selected_user = get_object_or_404(models.KTUser, pk=id)
    number_of_votes, number_of_comments, number_of_wishes, number_of_toplists, number_of_messages = _get_user_profile_numbers(request, selected_user)

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
        'number_of_votes': number_of_votes,
        'number_of_comments': number_of_comments,
        'number_of_wishes': number_of_wishes,
        'number_of_toplists': number_of_toplists,
        'number_of_messages': number_of_messages,
        'tab_width': USER_PROFILE_TAB_WIDTH[request.user.is_authenticated() and request.user.id != selected_user.id],
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
    number_of_votes, number_of_comments, number_of_wishes, number_of_toplists, number_of_messages = _get_user_profile_numbers(request, selected_user)
    p = int(request.GET.get('p', 0))
    if p == 1:
        return HttpResponseRedirect(reverse('user_comments', args=(selected_user.id, selected_user.slug_cache)))
    max_pages = int(math.ceil(1.0 * selected_user.number_of_comments / COMMENTS_PER_PAGE))
    if max_pages == 0:
        max_pages = 1
    if p == 0:
        p = 1
    if p > max_pages:
        return HttpResponseRedirect(reverse('user_comments', args=(selected_user.id, selected_user.slug_cache)) + '?p=' + str(max_pages))
    comments_qs = selected_user.comment_set.select_related('film', 'topic', 'poll', 'reply_to', 'reply_to__created_by')
    if max_pages > 1:
        first_comment = selected_user.number_of_comments - COMMENTS_PER_PAGE * (p - 1) - (COMMENTS_PER_PAGE - 1)
        last_comment = selected_user.number_of_comments - COMMENTS_PER_PAGE * (p - 1)
        print first_comment
        print last_comment
        comments = comments_qs.filter(serial_number_by_user__lte=last_comment, serial_number_by_user__gte=first_comment)
    else:
        comments = comments_qs.all()
    return render(request, 'ktapp/user_profile_subpages/user_comments.html', {
        'active_tab': 'comments',
        'selected_user': selected_user,
        'number_of_votes': number_of_votes,
        'number_of_comments': number_of_comments,
        'number_of_wishes': number_of_wishes,
        'number_of_toplists': number_of_toplists,
        'number_of_messages': number_of_messages,
        'tab_width': USER_PROFILE_TAB_WIDTH[request.user.is_authenticated() and request.user.id != selected_user.id],
        'comments': comments.order_by('-created_at'),
        'p': p,
        'max_pages': max_pages,
    })


def user_wishlist(request, id, name_slug):
    selected_user = get_object_or_404(models.KTUser, pk=id)
    number_of_votes, number_of_comments, number_of_wishes, number_of_toplists, number_of_messages = _get_user_profile_numbers(request, selected_user)
    qs = models.Wishlist.objects.select_related('film').filter(wished_by=selected_user).order_by('film__orig_title', 'film__id')
    return render(request, 'ktapp/user_profile_subpages/user_wishlist.html', {
        'active_tab': 'wishlist',
        'selected_user': selected_user,
        'number_of_votes': number_of_votes,
        'number_of_comments': number_of_comments,
        'number_of_wishes': number_of_wishes,
        'number_of_toplists': number_of_toplists,
        'number_of_messages': number_of_messages,
        'tab_width': USER_PROFILE_TAB_WIDTH[request.user.is_authenticated() and request.user.id != selected_user.id],
        'wishlist_yes': qs.filter(wish_type=models.Wishlist.WISH_TYPE_YES),
        'wishlist_get': qs.filter(wish_type=models.Wishlist.WISH_TYPE_GET),
    })


def user_toplists(request, id, name_slug):
    selected_user = get_object_or_404(models.KTUser, pk=id)
    number_of_votes, number_of_comments, number_of_wishes, number_of_toplists, number_of_messages = _get_user_profile_numbers(request, selected_user)
    toplists = models.UserToplist.objects.filter(created_by=selected_user).order_by('-created_at')
    toplist_details = []
    for toplist in toplists:
        toplist_list = []
        with_comments = False
        for item in models.UserToplistItem.objects.filter(usertoplist=toplist).select_related('film', 'director', 'actor').order_by('serial_number'):
            toplist_list.append(item)
            if item.comment:
                with_comments = True
        toplist_details.append((
            toplist,
            toplist_list,
            with_comments,
        ))
    return render(request, 'ktapp/user_profile_subpages/user_toplists.html', {
        'active_tab': 'toplists',
        'selected_user': selected_user,
        'number_of_votes': number_of_votes,
        'number_of_comments': number_of_comments,
        'number_of_wishes': number_of_wishes,
        'number_of_toplists': number_of_toplists,
        'number_of_messages': number_of_messages,
        'tab_width': USER_PROFILE_TAB_WIDTH[request.user.is_authenticated() and request.user.id != selected_user.id],
        'toplist_details': toplist_details,
    })


def user_activity(request, id, name_slug):
    selected_user = get_object_or_404(models.KTUser, pk=id)
    number_of_votes, number_of_comments, number_of_wishes, number_of_toplists, number_of_messages = _get_user_profile_numbers(request, selected_user)
    cursor = connection.cursor()
    max_max_vote = models.KTUser.objects.all().aggregate(Max('number_of_ratings'))['number_of_ratings__max']
    max_max_comment = models.KTUser.objects.all().aggregate(Max('number_of_comments'))['number_of_comments__max']
    scale_vote = (1.0 * selected_user.number_of_ratings / max_max_vote)**0.3
    scale_comment = (1.0 * selected_user.number_of_comments / max_max_comment)**0.3
    min_year = selected_user.date_joined.year
    max_year = datetime.date.today().year
    years = range(max_year, min_year - 1, -1)
    min_month = selected_user.date_joined.month
    max_month = datetime.date.today().month
    months = []
    if len(years) == 1:
        for month in range(max_month, min_month - 1, -1):
            months.append('%04d-%02d' % (years[0], month))
    else:
        for year in years:
            if year == max_year:
                for month in range(max_month, 0, -1):
                    months.append('%04d-%02d' % (year, month))
            elif year == min_year:
                for month in range(12, min_month - 1, -1):
                    months.append('%04d-%02d' % (year, month))
            else:
                for month in range(12, 0, -1):
                    months.append('%04d-%02d' % (year, month))
    years = ['%04d' % y for y in years]
    vote_data = {
        'm': {},
        'y': {},
    }
    comment_data = {
        'm': {},
        'y': {},
    }
    max_vote = {
        'm': 0,
        'y': 0,
    }
    max_comment = {
        'm': 0,
        'y': 0,
    }
    cursor.execute('SELECT LEFT(`when`, 7) AS dt, COUNT(1) FROM ktapp_vote WHERE user_id = %s AND `when` IS NOT NULL GROUP BY dt', [selected_user.id])
    for row in cursor.fetchall():
        vote_data['m'][row[0]] = row[1]
        if row[1] > max_vote['m']:
            max_vote['m'] = row[1]
    cursor.execute('SELECT LEFT(`when`, 4) AS dt, COUNT(1) FROM ktapp_vote WHERE user_id = %s AND `when` IS NOT NULL GROUP BY dt', [selected_user.id])
    for row in cursor.fetchall():
        vote_data['y'][row[0]] = row[1]
        if row[1] > max_vote['y']:
            max_vote['y'] = row[1]
    cursor.execute('SELECT LEFT(created_at, 7) AS dt, COUNT(1) FROM ktapp_comment WHERE created_by_id = %s AND created_at IS NOT NULL GROUP BY dt', [selected_user.id])
    for row in cursor.fetchall():
        comment_data['m'][row[0]] = row[1]
        if row[1] > max_comment['m']:
            max_comment['m'] = row[1]
    cursor.execute('SELECT LEFT(created_at, 4) AS dt, COUNT(1) FROM ktapp_comment WHERE created_by_id = %s AND created_at IS NOT NULL GROUP BY dt', [selected_user.id])
    for row in cursor.fetchall():
        comment_data['y'][row[0]] = row[1]
        if row[1] > max_comment['y']:
            max_comment['y'] = row[1]
    data_month = []
    for month in months:
        data_month.append((
            month,
            vote_data['m'].get(month, 0),
            comment_data['m'].get(month, 0),
            int(100.0 * scale_vote * vote_data['m'].get(month, 0) / max_vote['m']) if max_vote['m'] > 0 else 0,
            int(100.0 * scale_comment * comment_data['m'].get(month, 0) / max_comment['m']) if max_comment['m'] > 0 else 0,
        ))
    data_year = []
    for year in years:
        data_year.append((
            year,
            vote_data['y'].get(year, 0),
            comment_data['y'].get(year, 0),
            int(100.0 * scale_vote * vote_data['y'].get(year, 0) / max_vote['y']) if max_vote['y'] > 0 else 0,
            int(100.0 * scale_comment * comment_data['y'].get(year, 0) / max_comment['y']) if max_comment['y'] > 0 else 0,
        ))

    return render(request, 'ktapp/user_profile_subpages/user_activity.html', {
        'active_tab': 'activity',
        'selected_user': selected_user,
        'number_of_votes': number_of_votes,
        'number_of_comments': number_of_comments,
        'number_of_wishes': number_of_wishes,
        'number_of_toplists': number_of_toplists,
        'number_of_messages': number_of_messages,
        'tab_width': USER_PROFILE_TAB_WIDTH[request.user.is_authenticated() and request.user.id != selected_user.id],
        'data_month': data_month,
        'data_year': data_year,
    })


@login_required()
def user_messages(request, id, name_slug):
    selected_user = get_object_or_404(models.KTUser, pk=id)
    number_of_votes, number_of_comments, number_of_wishes, number_of_toplists, number_of_messages = _get_user_profile_numbers(request, selected_user)
    messages_qs = models.Message.objects.filter(private=True).filter(owned_by=request.user).filter(
        Q(sent_by=selected_user)
        | Q(sent_to=selected_user)
    ).select_related('sent_by')
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
        'number_of_votes': number_of_votes,
        'number_of_comments': number_of_comments,
        'number_of_wishes': number_of_wishes,
        'number_of_toplists': number_of_toplists,
        'number_of_messages': number_of_messages,
        'tab_width': USER_PROFILE_TAB_WIDTH[request.user.is_authenticated() and request.user.id != selected_user.id],
        'messages': messages_qs.order_by('-sent_at')[(p-1) * MESSAGES_PER_PAGE:p * MESSAGES_PER_PAGE],
        'p': p,
        'max_pages': max_pages,
    })
