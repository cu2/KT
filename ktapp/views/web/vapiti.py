# -*- coding: utf-8 -*-

import copy
import datetime
import json
from collections import defaultdict

from django.conf import settings
from django.db import connection
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from ktapp import models
from ktapp import utils as kt_utils
from ktapp import sqls as kt_sqls
from ktapp import texts
from ktapp.helpers import filmlist


def vapiti_general(request):
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


@require_POST
@login_required
@kt_utils.kt_permission_required('vote_vapiti')
def vote_vapiti(request):
    vapiti_type = request.POST.get('vapiti_type', '')
    if vapiti_type not in {'G', 'M', 'F'}:
        vapiti_type = 'G'
    vapiti_round, round_1_dates, round_2_dates, result_day = kt_utils.get_vapiti_round()
    if vapiti_round == 1:
        if vapiti_type == 'G':
            models.VapitiVote.objects.filter(
                user=request.user,
                year=settings.VAPITI_YEAR,
                vapiti_round=vapiti_round,
                vapiti_type=vapiti_type,
            ).delete()
            film_ids = set()
            for serial_number in xrange(1, 4):
                film_title = request.POST.get('film_%d' % serial_number, '')
                if '/' in film_title:
                    orig_title, second_title = film_title.split('/', 1)
                else:
                    orig_title, second_title = film_title, ''
                orig_title = orig_title.strip()
                second_title = second_title.strip()
                if orig_title == '':
                    continue
                films, _ = filmlist.filmlist(
                    user_id=request.user.id,
                    filters=[
                        ('vapiti_year', settings.VAPITI_YEAR),
                        ('title', '%s %s' % (orig_title, second_title)),
                        ('seen_it', '1'),
                    ],
                    ordering='title',
                    films_per_page=10,
                )
                film = None
                for f in films:
                    if f.orig_title != orig_title:
                        continue
                    if second_title:
                        if f.second_title != second_title:
                            continue
                    film = f
                    break
                if film and film.id not in film_ids:
                    film_ids.add(film.id)
                    models.VapitiVote.objects.create(
                        user=request.user,
                        year=settings.VAPITI_YEAR,
                        vapiti_round=vapiti_round,
                        vapiti_type=vapiti_type,
                        serial_number=serial_number,
                        film=film,
                    )
            models.Event.objects.create(
                user=request.user,
                event_type=models.Event.EVENT_TYPE_VAPITI_VOTE,
            )
            return HttpResponseRedirect(reverse('vapiti_gold'))
        elif vapiti_type in {'M', 'F'}:
            models.VapitiVote.objects.filter(
                user=request.user,
                year=settings.VAPITI_YEAR,
                vapiti_round=vapiti_round,
                vapiti_type=vapiti_type,
            ).delete()
            role_ids = set()
            for serial_number in xrange(1, 4):
                film_artist_title = request.POST.get('artist_%d' % serial_number, '').strip()[:-1]
                if '[' not in film_artist_title:
                    continue
                artist_name, film_title = film_artist_title.split('[', 1)
                if '/' in film_title:
                    orig_title, second_title = film_title.split('/', 1)
                else:
                    orig_title, second_title = film_title, ''
                artist_name = artist_name.strip()
                orig_title = orig_title.strip()
                second_title = second_title.strip()
                if artist_name == '':
                    continue
                roles = models.FilmArtistRelationship.objects.raw('''
                SELECT
                  r.id,
                  a.id AS artist_id,
                  f.id AS film_id
                FROM ktapp_filmartistrelationship r
                INNER JOIN ktapp_artist a ON a.id = r.artist_id
                INNER JOIN ktapp_film f ON f.id = r.film_id
                INNER JOIN ktapp_vote v ON v.film_id = f.id AND v.user_id = {user_id}
                WHERE r.role_type = 'A' AND r.actor_subtype = 'F'
                AND f.vapiti_year = {vapiti_year}
                AND a.gender = '{gender}'
                AND a.name = %s
                AND f.orig_title = %s
                ORDER BY a.name, a.id, r.role_name, r.id
                LIMIT 1
                '''.format(
                    user_id=request.user.id,
                    vapiti_year=settings.VAPITI_YEAR,
                    gender=vapiti_type,
                ), [artist_name, orig_title])
                if roles:
                    role = roles[0]
                else:
                    continue
                if role.id not in role_ids:
                    role_ids.add(role.id)
                    models.VapitiVote.objects.create(
                        user=request.user,
                        year=settings.VAPITI_YEAR,
                        vapiti_round=vapiti_round,
                        vapiti_type=vapiti_type,
                        serial_number=serial_number,
                        film_id=role.film_id,
                        artist_id=role.artist_id,
                    )
            models.Event.objects.create(
                user=request.user,
                event_type=models.Event.EVENT_TYPE_VAPITI_VOTE,
            )
            return HttpResponseRedirect(reverse('vapiti_silver', args=('ferfi' if vapiti_type == 'M' else 'noi',)))
    if vapiti_round == 2:
        try:
            vapiti_id = int(request.POST.get('vapiti_id', 0))
        except:
            vapiti_id = 0
        if vapiti_id:
            vapiti_yes = request.POST.get('vapiti_yes', '') == '1'
            if vapiti_type == 'G':
                nominee_ids = kt_utils.get_vapiti_nominees(models.Award, vapiti_type)
                if vapiti_id in set(nominee_ids):
                    try:
                        film = models.Film.objects.get(id=vapiti_id)
                    except models.Film.DoesNotExist:
                        film = None
                    if film:
                        if models.Vote.objects.filter(film=film, user=request.user):
                            models.VapitiVote.objects.filter(
                                user=request.user,
                                year=settings.VAPITI_YEAR,
                                vapiti_round=vapiti_round,
                                vapiti_type=vapiti_type,
                            ).delete()
                            if vapiti_yes:
                                models.VapitiVote.objects.create(
                                    user=request.user,
                                    year=settings.VAPITI_YEAR,
                                    vapiti_round=vapiti_round,
                                    vapiti_type=vapiti_type,
                                    serial_number=1,
                                    film=film,
                                )
                            models.Event.objects.create(
                                user=request.user,
                                event_type=models.Event.EVENT_TYPE_VAPITI_VOTE,
                            )
                            return HttpResponse(json.dumps({'success': True}), content_type='application/json')
            elif vapiti_type in {'M', 'F'}:
                nominee_ids = kt_utils.get_vapiti_nominees(models.Award, vapiti_type)
                selected_nominee = None
                for film_id, artist_id in nominee_ids:
                    try:
                        role = models.FilmArtistRelationship.objects.select_related('film', 'artist').get(film_id=film_id, artist_id=artist_id, role_type=models.FilmArtistRelationship.ROLE_TYPE_ACTOR)
                    except models.FilmArtistRelationship.DoesNotExist:
                        continue
                    if role.id == vapiti_id:
                        selected_nominee = role
                if selected_nominee:
                    if models.Vote.objects.filter(film=selected_nominee.film, user=request.user):
                        models.VapitiVote.objects.filter(
                            user=request.user,
                            year=settings.VAPITI_YEAR,
                            vapiti_round=vapiti_round,
                            vapiti_type=vapiti_type,
                        ).delete()
                        if vapiti_yes:
                            models.VapitiVote.objects.create(
                                user=request.user,
                                year=settings.VAPITI_YEAR,
                                vapiti_round=vapiti_round,
                                vapiti_type=vapiti_type,
                                serial_number=1,
                                film=selected_nominee.film,
                                artist=selected_nominee.artist,
                            )
                        models.Event.objects.create(
                            user=request.user,
                            event_type=models.Event.EVENT_TYPE_VAPITI_VOTE,
                        )
                        return HttpResponse(json.dumps({'success': True}), content_type='application/json')
    return HttpResponseForbidden()


@login_required
@kt_utils.kt_permission_required('vapiti_admin')
def vapiti_admin(request):
    today_str = datetime.date.today().strftime('%Y-%m-%d')
    vapiti_round, round_1_dates, round_2_dates, result_day = kt_utils.get_vapiti_round()
    nominee_days = [
        round_2_dates[0],
        (datetime.datetime.strptime(round_2_dates[0], '%Y-%m-%d') + datetime.timedelta(days=1)).strftime('%Y-%m-%d'),
    ]

    nominees = None
    if today_str == nominee_days[0] or today_str == nominee_days[1]:
        nominees = get_nominees()
        if request.POST:
            models.Award.objects.filter(name='Vapiti', year=settings.VAPITI_YEAR, category=texts.VAPITI_NOMINEE_CATEGORIES[models.VapitiVote.VAPITI_TYPE_GOLD]).delete()
            for film_id in nominees[models.VapitiVote.VAPITI_TYPE_GOLD]['ids']:
                film = models.Film.objects.get(id=film_id)
                models.Award.objects.get_or_create(
                    film=film,
                    name='Vapiti',
                    year=settings.VAPITI_YEAR,
                    category=texts.VAPITI_NOMINEE_CATEGORIES[models.VapitiVote.VAPITI_TYPE_GOLD],
                    artist=None,
                    created_by_id=None,
                )
            kt_utils.reset_vapiti_nominees_cache(models.VapitiVote.VAPITI_TYPE_GOLD)

            for vapiti_type in [models.VapitiVote.VAPITI_TYPE_SILVER_FEMALE, models.VapitiVote.VAPITI_TYPE_SILVER_MALE]:
                models.Award.objects.filter(name='Vapiti', year=settings.VAPITI_YEAR, category=texts.VAPITI_NOMINEE_CATEGORIES[vapiti_type]).delete()
                for role_id in nominees[vapiti_type]['ids']:
                    role = models.FilmArtistRelationship.objects.get(id=role_id)
                    film = models.Film.objects.get(id=role.film_id)
                    artist = models.Artist.objects.get(id=role.artist_id)
                    models.Award.objects.get_or_create(
                        film=film,
                        name='Vapiti',
                        year=settings.VAPITI_YEAR,
                        category=texts.VAPITI_NOMINEE_CATEGORIES[vapiti_type],
                        artist=artist,
                        created_by_id=None,
                    )
                kt_utils.reset_vapiti_nominees_cache(vapiti_type)

            return HttpResponseRedirect(reverse('vapiti_admin'))

    have_official_nominees = models.Award.objects.filter(name='Vapiti', year=settings.VAPITI_YEAR, category=texts.VAPITI_NOMINEE_CATEGORIES[models.VapitiVote.VAPITI_TYPE_GOLD]).count() > 0

    winners = None
    if today_str == result_day:
        winners = get_winners()

    return render(request, 'ktapp/vapiti_subpages/vapiti_admin.html', {
        'today_str': today_str,
        'vapiti_year': settings.VAPITI_YEAR,
        'nominee_days': nominee_days,
        'nominees': nominees,
        'have_official_nominees': have_official_nominees,
        'result_day': result_day,
        'winners': winners,
    })


def get_nominees():
    cursor = connection.cursor()
    nominees = {}
    for vapiti_type, names_or_titles, sql in [
        (models.VapitiVote.VAPITI_TYPE_GOLD, 'titles', kt_sqls.VAPITI_NOMINEES_GOLD),
        (models.VapitiVote.VAPITI_TYPE_SILVER_FEMALE, 'names', kt_sqls.VAPITI_NOMINEES_SILVER_FEMALE),
        (models.VapitiVote.VAPITI_TYPE_SILVER_MALE, 'names', kt_sqls.VAPITI_NOMINEES_SILVER_MALE)
    ]:
        nominees[vapiti_type] = {
            'ids': [],
            names_or_titles: [],
        }
        cursor.execute(sql, (settings.VAPITI_YEAR,))
        for row in cursor.fetchall():
            nominees[vapiti_type]['ids'].append(int(row[0]))
            nominees[vapiti_type][names_or_titles].append(row[1])
        nominees[vapiti_type][names_or_titles] = '\n'.join(nominees[vapiti_type][names_or_titles])

    return nominees


def get_winners():
    cursor = connection.cursor()
    try:
        cursor.execute(kt_sqls.VAPITI_WINNER_GOLD, (settings.VAPITI_YEAR,))
        winner_film = models.Film.objects.get(id=cursor.fetchone()[0])
        cursor.execute(kt_sqls.VAPITI_WINNER_SILVER_FEMALE, (settings.VAPITI_YEAR,))
        winner_female_role = models.FilmArtistRelationship.objects.get(id=cursor.fetchone()[0])
        cursor.execute(kt_sqls.VAPITI_WINNER_SILVER_MALE, (settings.VAPITI_YEAR,))
        winner_male_role = models.FilmArtistRelationship.objects.get(id=cursor.fetchone()[0])
        return {
            models.VapitiVote.VAPITI_TYPE_GOLD: winner_film,
            models.VapitiVote.VAPITI_TYPE_SILVER_FEMALE: {
                'artist': models.Artist.objects.get(id=winner_female_role.artist_id),
                'film': models.Film.objects.get(id=winner_female_role.film_id),
            },
            models.VapitiVote.VAPITI_TYPE_SILVER_MALE: {
                'artist': models.Artist.objects.get(id=winner_male_role.artist_id),
                'film': models.Film.objects.get(id=winner_male_role.film_id),
            },
        }
    except Exception:
        return None
