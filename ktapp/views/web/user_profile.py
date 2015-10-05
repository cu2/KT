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
from ktapp.helpers import filmlist
from ktapp.texts import LONG_YEARS


COMMENTS_PER_PAGE = 100
MESSAGES_PER_PAGE = 50
FILMS_PER_PAGE = 100

MINIMUM_YEAR = 1920

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
        selected_user.number_of_wishes_yes + selected_user.number_of_wishes_no + selected_user.number_of_wishes_get,
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
    # profile
    profile = {
        'major_genres': [],
        'minor_genres': [],
        'major_countries': [],
        'minor_countries': [],
        'major_years': [],
        'minor_years': [],
    }
    for keyword in models.Keyword.objects.raw('''
        SELECT k.*, ups.score AS ups_score
        FROM ktapp_userprofilesegment ups
        INNER JOIN ktapp_profilesegment ps ON ps.id = ups.segment_id AND ps.dimension = 'genre'
        LEFT JOIN ktapp_keyword k ON k.id = ps.segment
        WHERE ups.user_id = {user_id} AND ups.score >= 50
        ORDER BY ups.score DESC;
    '''.format(user_id=selected_user.id)):
        if keyword.ups_score >= 100:
            profile['major_genres'].append(keyword)
        else:
            profile['minor_genres'].append(keyword)
    for keyword in models.Keyword.objects.raw('''
        SELECT k.*, ups.score AS ups_score
        FROM ktapp_userprofilesegment ups
        INNER JOIN ktapp_profilesegment ps ON ps.id = ups.segment_id AND ps.dimension = 'country'
        LEFT JOIN ktapp_keyword k ON k.id = ps.segment
        WHERE ups.user_id = {user_id} AND ups.score >= 100
        ORDER BY ups.score DESC;
    '''.format(user_id=selected_user.id)):
        if keyword.ups_score >= 200:
            profile['major_countries'].append(keyword)
        else:
            profile['minor_countries'].append(keyword)
    for year in models.UserProfileSegment.objects.raw('''
        SELECT ups.*, ps.segment as ps_segment
        FROM ktapp_userprofilesegment ups
        INNER JOIN ktapp_profilesegment ps ON ps.id = ups.segment_id AND ps.dimension = 'year'
        LEFT JOIN ktapp_keyword k ON k.id = ps.segment
        WHERE ups.user_id = {user_id} AND ups.score >= 50
        ORDER BY ups.score DESC;
    '''.format(user_id=selected_user.id)):
        year_str = LONG_YEARS[int(year.ps_segment)]
        if year.score >= 100:
            profile['major_years'].append(year_str)
        else:
            profile['minor_years'].append(year_str)
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
        'profile': profile,
        'fav_directors': list(models.Artist.objects.raw('''
            SELECT a.*
            FROM ktapp_artist a
            INNER JOIN ktapp_userfavourite uf ON uf.fav_id = a.id
            WHERE uf.user_id = %s AND uf.domain = %s
            ORDER BY a.name, a.id
        ''', [selected_user.id, models.UserFavourite.DOMAIN_DIRECTOR])),
        'fav_actors': list(models.Artist.objects.raw('''
            SELECT a.*
            FROM ktapp_artist a
            INNER JOIN ktapp_userfavourite uf ON uf.fav_id = a.id
            WHERE uf.user_id = %s AND uf.domain = %s
            ORDER BY a.name, a.id
        ''', [selected_user.id, models.UserFavourite.DOMAIN_ACTOR])),
        'fav_genres': list(models.Keyword.objects.raw('''
            SELECT k.*
            FROM ktapp_keyword k
            INNER JOIN ktapp_userfavourite uf ON uf.fav_id = k.id
            WHERE uf.user_id = %s AND uf.domain = %s AND k.keyword_type = %s
            ORDER BY k.name, k.id
        ''', [selected_user.id, models.UserFavourite.DOMAIN_GENRE, models.Keyword.KEYWORD_TYPE_GENRE])),
        'fav_countries': list(models.Keyword.objects.raw('''
            SELECT k.*
            FROM ktapp_keyword k
            INNER JOIN ktapp_userfavourite uf ON uf.fav_id = k.id
            WHERE uf.user_id = %s AND uf.domain = %s AND k.keyword_type = %s
            ORDER BY k.name, k.id
        ''', [selected_user.id, models.UserFavourite.DOMAIN_COUNTRY, models.Keyword.KEYWORD_TYPE_COUNTRY])),
    })


def user_films(request, id, name_slug):
    selected_user = get_object_or_404(models.KTUser, pk=id)
    number_of_votes, number_of_comments, number_of_wishes, number_of_toplists, number_of_messages = _get_user_profile_numbers(request, selected_user)

    ordering_str = kt_utils.strip_whitespace(request.GET.get('o', ''))
    if ordering_str == '':
        ordering_str = '-other_rating_when'
    if ordering_str[0] == '-':
        ordering = (ordering_str[1:], 'DESC')
    else:
        ordering = (ordering_str, 'ASC')
    filters = [('seen_by_id', selected_user.id)] + filmlist.get_filters_from_request(request)
    films, nice_filters = filmlist.filmlist(
        user_id=request.user.id,
        filters=filters,
        ordering=ordering,
        films_per_page=None,
    )
    querystring = {}
    for filter_type, filter_value in nice_filters:
        if filter_type in {'title', 'year', 'director', 'actor', 'country', 'genre', 'keyword', 'my_rating', 'other_rating', 'my_wish'}:
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
        'querystring': querystring,
        'qs_combined': qs_combined,
        'ordering_str': ordering_str,
        'p': p,
        'max_pages': max_pages,
        'films': films,
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
    wishlist_type = request.GET.get('t', 'igen')
    if wishlist_type == 'nem':
        wishlist_type = 'N'
    elif wishlist_type == 'szerez':
        wishlist_type = 'G'
    else:
        wishlist_type = 'Y'

    filters = [('wished_by_id', '%s:%s' % (wishlist_type, selected_user.id))] + filmlist.get_filters_from_request(request)
    films, nice_filters = filmlist.filmlist(
        user_id=request.user.id,
        filters=filters,
        ordering=('average_rating', 'DESC'),
        films_per_page=None,
    )
    querystring = {}
    for filter_type, filter_value in nice_filters:
        if filter_type in {'title', 'year', 'director', 'actor', 'country', 'genre', 'keyword', 'my_rating', 'other_rating', 'my_wish'}:
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
    if wishlist_type == 'N':
        querystring['t'] = 'nem'
    if wishlist_type == 'G':
        querystring['t'] = 'szerez'

    qs_combined = '&'.join('%s=%s' % (key, val) for key, val in querystring.iteritems())
    if qs_combined != '':
        qs_combined = '&' + qs_combined

    films = list(films)
    result_count = len(films)

    return render(request, 'ktapp/user_profile_subpages/user_wishlist.html', {
        'active_tab': 'wishlist',
        'selected_user': selected_user,
        'number_of_votes': number_of_votes,
        'number_of_comments': number_of_comments,
        'number_of_wishes': number_of_wishes,
        'number_of_toplists': number_of_toplists,
        'number_of_messages': number_of_messages,
        'tab_width': USER_PROFILE_TAB_WIDTH[request.user.is_authenticated() and request.user.id != selected_user.id],
        'result_count': result_count,
        'querystring': querystring,
        'qs_combined': qs_combined,
        'films': films,
        'wishlist_type': wishlist_type,
        'number_of_wishes_yes': selected_user.number_of_wishes_yes,
        'number_of_wishes_no': selected_user.number_of_wishes_no,
        'number_of_wishes_get': selected_user.number_of_wishes_get,
    })


def user_toplists(request, id, name_slug):
    selected_user = get_object_or_404(models.KTUser, pk=id)
    number_of_votes, number_of_comments, number_of_wishes, number_of_toplists, number_of_messages = _get_user_profile_numbers(request, selected_user)
    toplists = models.UserToplist.objects.filter(created_by=selected_user).order_by('-created_at')
    toplist_details = []
    for toplist in toplists:
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


@login_required()
def edit_profile(request):

    def set_fav(field_name, domain, get_object_function):
        old_items = set()
        for item in models.UserFavourite.objects.filter(user=request.user, domain=domain):
            old_items.add(item.fav_id)
        new_items = set()
        for name in kt_utils.strip_whitespace(request.POST.get(field_name, '')).split(','):
            name = kt_utils.strip_whitespace(name)
            item = get_object_function(name)
            if item:
                new_items.add(item.id)
        for item_id in old_items - new_items:
            models.UserFavourite.objects.filter(user=request.user, domain=domain, fav_id=item_id).delete()
        for item_id in new_items - old_items:
            models.UserFavourite.objects.create(user=request.user, domain=domain, fav_id=item_id)

    next_url = request.GET.get('next', request.POST.get('next', reverse('user_profile', args=(request.user.id, request.user.slug_cache))))
    if not request.user.validated_email:
        return HttpResponseRedirect(next_url)
    if request.POST:
        request.user.bio = request.POST.get('bio', '').strip()
        gender = request.POST.get('gender', '')
        if gender not in {'U', 'M', 'F'}:
            gender = 'U'
        request.user.gender = gender
        try:
            request.user.year_of_birth = int(request.POST.get('year_of_birth', 0))
        except ValueError:
            request.user.year_of_birth = 0
        request.user.location = kt_utils.strip_whitespace(request.POST.get('location', ''))
        request.user.public_gender = bool(request.POST.get('public_gender', ''))
        request.user.public_year_of_birth = bool(request.POST.get('public_year_of_birth', ''))
        request.user.public_location = bool(request.POST.get('public_location', ''))
        set_fav('fav_director', models.UserFavourite.DOMAIN_DIRECTOR, models.Artist.get_artist_by_name)
        set_fav('fav_actor', models.UserFavourite.DOMAIN_ACTOR, models.Artist.get_artist_by_name)
        set_fav('fav_genre', models.UserFavourite.DOMAIN_GENRE, lambda name: models.Keyword.get_keyword_by_name(name, models.Keyword.KEYWORD_TYPE_GENRE))
        set_fav('fav_country', models.UserFavourite.DOMAIN_COUNTRY, lambda name: models.Keyword.get_keyword_by_name(name, models.Keyword.KEYWORD_TYPE_COUNTRY))
        request.user.fav_period = kt_utils.strip_whitespace(request.POST.get('fav_period', ''))
        request.user.save()
        return HttpResponseRedirect(next_url)
    number_of_votes, number_of_comments, number_of_wishes, number_of_toplists, number_of_messages = _get_user_profile_numbers(request, request.user)
    return render(request, 'ktapp/user_profile_subpages/edit_profile.html', {
        'active_tab': 'profile',
        'selected_user': request.user,
        'number_of_votes': number_of_votes,
        'number_of_comments': number_of_comments,
        'number_of_wishes': number_of_wishes,
        'number_of_toplists': number_of_toplists,
        'tab_width': USER_PROFILE_TAB_WIDTH[False],
        'fav_directors': models.Artist.objects.raw('''
            SELECT a.*
            FROM ktapp_artist a
            INNER JOIN ktapp_userfavourite uf ON uf.fav_id = a.id
            WHERE uf.user_id = %s AND uf.domain = %s
            ORDER BY a.name, a.id
        ''', [request.user.id, models.UserFavourite.DOMAIN_DIRECTOR]),
        'fav_actors': models.Artist.objects.raw('''
            SELECT a.*
            FROM ktapp_artist a
            INNER JOIN ktapp_userfavourite uf ON uf.fav_id = a.id
            WHERE uf.user_id = %s AND uf.domain = %s
            ORDER BY a.name, a.id
        ''', [request.user.id, models.UserFavourite.DOMAIN_ACTOR]),
        'fav_genres': models.Keyword.objects.raw('''
            SELECT k.*
            FROM ktapp_keyword k
            INNER JOIN ktapp_userfavourite uf ON uf.fav_id = k.id
            WHERE uf.user_id = %s AND uf.domain = %s AND k.keyword_type = %s
            ORDER BY k.name, k.id
        ''', [request.user.id, models.UserFavourite.DOMAIN_GENRE, models.Keyword.KEYWORD_TYPE_GENRE]),
        'fav_countries': models.Keyword.objects.raw('''
            SELECT k.*
            FROM ktapp_keyword k
            INNER JOIN ktapp_userfavourite uf ON uf.fav_id = k.id
            WHERE uf.user_id = %s AND uf.domain = %s AND k.keyword_type = %s
            ORDER BY k.name, k.id
        ''', [request.user.id, models.UserFavourite.DOMAIN_COUNTRY, models.Keyword.KEYWORD_TYPE_COUNTRY]),
    })
