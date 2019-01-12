# -*- coding: utf-8 -*-

import datetime
import json
from collections import OrderedDict

from django.conf import settings
from django.http import HttpResponse
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from ktapp import models
from ktapp import serializers
from ktapp import utils as kt_utils
from ktapp.helpers import filmlist, search as kt_search


HUNGARIAN_MONTHS = [
    u'jan', u'feb', u'márc',
    u'ápr', u'máj', u'jún',
    u'júl', u'aug', u'szept',
    u'okt', u'nov', u'dec',
]


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.KTUser.objects.all()
    serializer_class = serializers.UserSerializer

    @detail_route(methods=['get'])
    def votes(self, request, pk=None):
        user = self.get_object()
        serializer = serializers.UserWithVotesSerializer(
            instance=user,
            context={'request': request}
        )
        return Response(serializer.data)


class FilmViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Film.objects.all()
    serializer_class = serializers.FilmSerializer


class KeywordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Keyword.objects.all()
    serializer_class = serializers.ShortKeywordSerializer


class ArtistViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Artist.objects.all()
    serializer_class = serializers.ArtistSerializer


class SequelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Sequel.objects.all()
    serializer_class = serializers.SequelSerializer


def search(request):

    def film_title(film):
        if film.year:
            return u'%s (%d)' % (film.orig_title, film.year)
        return film.orig_title

    def nice_date(d):
        return '%d %s %d' % (
            d.year,
            HUNGARIAN_MONTHS[int(d.month) - 1],
            d.day,
        )

    def nice_date_interval(d1, d2):
        if d1.year != d2.year:
            return '%s - %s' % (nice_date(d1), nice_date(d2))
        if d1.month != d2.month:
            return '%d %s %d - %s %d' % (
                d1.year,
                HUNGARIAN_MONTHS[int(d1.month) - 1],
                d1.day,
                HUNGARIAN_MONTHS[int(d2.month) - 1],
                d2.day,
            )
        return '%d %s %d-%d' % (
            d1.year,
            HUNGARIAN_MONTHS[int(d1.month) - 1],
            d1.day,
            d2.day,
        )

    q = request.GET.get('q', '')
    if len(q) < 2:
        return HttpResponse(json.dumps({
            'q': q,
            'results': [],
        }), content_type='application/json')
    q_pieces = kt_search.get_q_pieces(q)

    film = kt_search.find_film_by_link(q)
    if film:
        films = [film]
    else:
        films, _ = filmlist.filmlist(
            user_id=request.user.id,
            filters=[('title', q)],
            ordering='title_match',
            films_per_page=5,
        )
        films = list(films)
    artists = list(kt_search.find_artists(q_pieces, 5))
    # roles = list(kt_search.find_roles(q_pieces, 5))
    roles = []
    sequels = list(kt_search.find_sequels(q_pieces, 5))
    users = list(kt_search.find_users(q_pieces, 5))
    topics = list(kt_search.find_topics(q_pieces, 5))
    polls = list(kt_search.find_polls(q_pieces, 5))

    number_of_items = len(films) + len(artists) + len(roles) + len(sequels) + len(users) + len(topics) + len(polls)
    if number_of_items > 10:
        films = films[:5 * 10 / number_of_items]
        artists = artists[:5 * 10 / number_of_items]
        # roles = roles[:5 * 10 / number_of_items]
        sequels = sequels[:5 * 10 / number_of_items]
        users = users[:5 * 10 / number_of_items]
        topics = topics[:5 * 10 / number_of_items]
        polls = polls[:5 * 10 / number_of_items]

    results = []
    if films:
        film_results = []
        for film in films:
            actors = [r.artist.name for r in models.FilmArtistRelationship.objects.filter(film=film, role_type=models.FilmArtistRelationship.ROLE_TYPE_ACTOR, is_main_role=True).select_related('artist').order_by('artist__name')[:3]]
            film_results.append({
                'url': reverse('film_main', args=(film.id, film.slug_cache)),
                'title': film_title(film),
                'subtitle': film.second_title,
                'subsubtitle': 'R: %s%s' % (
                    film.director_names_cache.split(',')[0] if film.director_names_cache else '?',
                    '; Sz: %s' % ', '.join(actors) if actors else '',
                ),
                'thumbnail': film.main_poster.get_display_urls()['min'] if film.main_poster else '',
            })
        results.append({
            'domain': 'films',
            'results': film_results,
        })
    if artists:
        artist_results = []
        for artist in artists:
            films_as_actor = [film_title(r.film) for r in models.FilmArtistRelationship.objects.filter(artist=artist, role_type=models.FilmArtistRelationship.ROLE_TYPE_ACTOR).select_related('film').order_by('-film__number_of_ratings')[:3]]
            films_as_director = [film_title(r.film) for r in models.FilmArtistRelationship.objects.filter(artist=artist, role_type=models.FilmArtistRelationship.ROLE_TYPE_DIRECTOR).select_related('film').order_by('-film__number_of_ratings')[:3]]
            subtitle = ''
            subsubtitle = ''
            if len(films_as_actor) + len(films_as_director):
                if artist.number_of_ratings_as_actor > artist.number_of_ratings_as_director:
                    if films_as_actor: subtitle = u'Színész: %s' % (', '.join(films_as_actor))
                    if films_as_director: subsubtitle = u'Rendező: %s' % (', '.join(films_as_director))
                else:
                    if films_as_director: subtitle = u'Rendező: %s' % (', '.join(films_as_director))
                    if films_as_actor: subsubtitle = u'Színész: %s' % (', '.join(films_as_actor))
            artist_results.append({
                'url': reverse('artist', args=(artist.id, artist.slug_cache)),
                'title': artist.name,
                'subtitle': subtitle,
                'subsubtitle': subsubtitle,
                'thumbnail': artist.main_picture.get_display_urls()['min'] if artist.main_picture else '',
                'thumbnail_margin_left': artist.main_picture.get_margin_left_autocomplete() if artist.main_picture else 0,
            })
        results.append({
            'domain': 'artists',
            'results': artist_results,
        })
    if roles:
        results.append({
            'domain': 'roles',
            'results': [
                {
                    'url': reverse('role', args=(role.id, role.slug_cache)),
                    'title': role.role_name,
                    'subtitle': u'Sz: %s' % role.artist.name,
                    'subsubtitle': u'F: %s' % film_title(role.film),
                    'thumbnail': role.main_picture.get_display_urls()['min'] if role.main_picture else '',
                } for role in roles
            ],
        })
    if sequels:
        sequel_results = []
        for sequel in sequels:
            films = list(sequel.all_films()[:3])
            thumbnail = ''
            if films:
                if films[0].main_poster:
                    thumbnail = films[0].main_poster.get_display_urls()['min']
            sequel_results.append({
                'url': reverse('sequel', args=(sequel.id, sequel.slug_cache)),
                'title': sequel.name,
                'subtitle': {
                    models.Sequel.SEQUEL_TYPE_SEQUEL: u'Folytatás',
                    models.Sequel.SEQUEL_TYPE_ADAPTATION: u'Adaptáció',
                    models.Sequel.SEQUEL_TYPE_REMAKE: u'Remake',
                }[sequel.sequel_type],
                'subsubtitle': ', '.join([film_title(f) for f in films]),
                'thumbnail': thumbnail,
            })
        results.append({
            'domain': 'sequels',
            'results': sequel_results,
        })
    if users:
        now = datetime.datetime.now()
        user_results = []
        for user in users:
            reg_days_ago = (now - user.date_joined).days
            if reg_days_ago >= 365:
                reg = u'%d éve' % (reg_days_ago / 365)
            elif reg_days_ago >= 30:
                reg = u'%d hónapja' % (reg_days_ago / 30)
            elif reg_days_ago >= 7:
                reg = u'%d hete' % (reg_days_ago / 7)
            else:
                reg = u'nemrég'
            user_results.append({
                'url': reverse('user_profile', args=(user.id, user.slug_cache)),
                'title': user.username,
                'subtitle': u'Tapasztalat: %d film; Reg: %s' % (user.number_of_ratings, reg),
                'subsubtitle': user.bio_snippet[:200],
                'thumbnail': '',
            })
        results.append({
            'domain': 'users',
            'results': user_results,
        })
    if topics:
        results.append({
            'domain': 'topics',
            'results': [
                {
                    'url': reverse('forum', args=(topic.id, topic.slug_cache)),
                    'title': topic.title,
                    'subtitle': '%s vélemény' % topic.number_of_comments,
                    'subsubtitle': u'Utolsó: %s %s' % (topic.last_comment.created_at.strftime('%Y-%m-%d'), topic.last_comment.created_by.username),
                    'thumbnail': '',
                } for topic in topics
            ],
        })
    if polls:
        poll_results = []
        for poll in polls:
            subtitle = ''
            if poll.open_from:
                if poll.open_until:
                    subtitle = u'Régi: %s' % nice_date_interval(poll.open_from, poll.open_until)
                else:
                    subtitle = u'Aktuális: %s-' % nice_date(poll.open_from)
            else:
                subtitle = u'Leendő'
            poll_results.append({
                'url': reverse('poll', args=(poll.id, poll.slug_cache)),
                'title': poll.title,
                'subtitle': subtitle,
                'subsubtitle': u'%d válasz, %d komment' % (poll.number_of_votes, poll.number_of_comments) if poll.number_of_votes or poll.number_of_comments else '',
                'thumbnail': '',
            })
        results.append({
            'domain': 'polls',
            'results': poll_results,
        })
    return HttpResponse(json.dumps({
        'q': q,
        'results': results,
    }), content_type='application/json')


def get_users(request):
    q = request.GET.get('q', '')
    if len(q) < 2:
        return HttpResponse(json.dumps([]), content_type='application/json')
    return HttpResponse(json.dumps(
        [user.username for user in models.KTUser.objects.filter(username__istartswith=q).order_by('username', 'id')[:10]]
    ), content_type='application/json')


def get_artists(request):
    q = request.GET.get('q', '')
    f = request.GET.get('f', '')
    if len(q) < 2:
        return HttpResponse(json.dumps([]), content_type='application/json')
    if f:
        roles = models.FilmArtistRelationship.objects.filter(film_id=f)
        return HttpResponse(json.dumps(
            [{'label': role.artist.name, 'value': role.artist.name, 'id': role.artist.id, 'gender': role.artist.gender} for role in roles.filter(artist__name__icontains=q).order_by('-artist__number_of_ratings', 'artist__name', 'artist_id')[:10]]
        ), content_type='application/json')
    return HttpResponse(json.dumps(
        [{'label': artist.name, 'value': artist.name, 'id': artist.id, 'gender': artist.gender} for artist in models.Artist.objects.filter(name__icontains=q).order_by('-number_of_ratings', 'name', 'id')[:10]]
    ), content_type='application/json')


def get_keywords(request):
    t = request.GET.get('t', '')
    q = request.GET.get('q', '')
    if q.endswith('*'):
        q = q[:-1]
    if len(q) < 2:
        return HttpResponse(json.dumps([]), content_type='application/json')
    keywords = models.Keyword.objects
    if t != '':
        if t == 'MO':
            keywords = keywords.filter(keyword_type__in=['M', 'O'])
        else:
            keywords = keywords.filter(keyword_type=t)
    return HttpResponse(json.dumps(
        [keyword.name for keyword in keywords.filter(name__istartswith=q).order_by('name', 'id')[:10]]
    ), content_type='application/json')


def get_films(request):

    def get_plain_film(film):
        if film.second_title:
            if film.year:
                return u'%s (%s) / %s' % (film.orig_title, film.year, film.second_title)
            else:
                return u'%s / %s' % (film.orig_title, film.second_title)
        if film.year:
            return u'%s (%s)' % (film.orig_title, film.year)
        else:
            return film.orig_title

    q = request.GET.get('q', '')
    if len(q) < 2:
        return HttpResponse(json.dumps([]), content_type='application/json')
    films = models.Film.objects.filter(
        Q(orig_title__icontains=q)
        | Q(second_title__icontains=q)
        | Q(third_title__icontains=q)
    ).extra(
        select=OrderedDict([
            ('difflen', '''LEAST(
                CASE WHEN LOCATE(%s, orig_title) = 0 THEN 99 ELSE ABS(CHAR_LENGTH(orig_title) - {lenq}) + LOCATE(%s, orig_title) END,
                CASE WHEN LOCATE(%s, second_title) = 0 THEN 99 ELSE ABS(CHAR_LENGTH(second_title) - {lenq}) + LOCATE(%s, second_title) END,
                CASE WHEN LOCATE(%s, third_title) = 0 THEN 99 ELSE ABS(CHAR_LENGTH(third_title) - {lenq}) + LOCATE(%s, third_title) END
            )-CAST(number_of_ratings AS SIGNED)'''.format(lenq=len(q))),
        ]),
        select_params=[q, q, q, q, q, q],
        order_by=['difflen', '-number_of_ratings', 'orig_title', 'second_title', 'third_title', 'id']
    )[:10]
    result_format = request.GET.get('f', '')
    if result_format == 'plain':
        return HttpResponse(json.dumps(
            [get_plain_film(film) for film in films]
        ), content_type='application/json')
    return HttpResponse(json.dumps(
        [
            {
                'id': film.id,
                'orig_title': film.orig_title,
                'second_title': film.second_title,
                'third_title': film.third_title,
                'year': film.year,
                'slug': film.slug_cache,
            } for film in films
        ]
    ), content_type='application/json')


def get_films_imdb(request):
    raw_imdb_link = kt_utils.strip_whitespace(request.GET.get('q', ''))
    if raw_imdb_link.startswith('tt'):
        imdb_link = raw_imdb_link
    elif 'imdb.com' in raw_imdb_link and '/tt' in raw_imdb_link:
        imdb_link = raw_imdb_link[raw_imdb_link.index('/tt')+1:].split('/')[0]
    else:
        return HttpResponse(json.dumps([]), content_type='application/json')
    films = models.Film.objects.filter(imdb_link=imdb_link)[:10]
    return HttpResponse(json.dumps(
        [
            {
                'id': film.id,
                'orig_title': film.orig_title,
                'second_title': film.second_title,
                'third_title': film.third_title,
                'year': film.year,
                'slug': film.slug_cache,
            } for film in films
        ]
    ), content_type='application/json')


def get_sequels(request):
    q = request.GET.get('q', '')
    if len(q) < 2:
        return HttpResponse(json.dumps([]), content_type='application/json')
    if q[:3] in {'(A)', '(S)', '(R)'}:
        sequel_type = q[1]
        sequel_name = q[3:].strip()
    else:
        sequel_type = None
        sequel_name = q
    if len(sequel_name) < 2:
        return HttpResponse(json.dumps([]), content_type='application/json')
    if sequel_type:
        seq_qs = models.Sequel.objects.filter(sequel_type=sequel_type, name__icontains=sequel_name)
    else:
        seq_qs = models.Sequel.objects.filter(name__icontains=sequel_name)
    return HttpResponse(json.dumps(
        ['(%s) %s' % (seq.sequel_type, seq.name) for seq in seq_qs.order_by('name', 'id')[:10]]
    ), content_type='application/json')


def get_awards(request):
    t = request.GET.get('t', '')
    q = request.GET.get('q', '')
    if len(q) < 2:
        return HttpResponse(json.dumps([]), content_type='application/json')
    if t not in {'N', 'Y', 'C'}:
        t = 'N'
    if t == 'N':
        return HttpResponse(json.dumps(
            [a['name'] for a in models.Award.objects.filter(name__icontains=q).values('name').distinct()[:10]]
        ), content_type='application/json')
    elif t == 'Y':
        return HttpResponse(json.dumps(
            [a['year'] for a in models.Award.objects.filter(year__icontains=q).values('year').distinct()[:10]]
        ), content_type='application/json')
    else:
        return HttpResponse(json.dumps(
            [a['category'] for a in models.Award.objects.filter(category__icontains=q).values('category').distinct()[:10]]
        ), content_type='application/json')


@login_required
def get_vapiti_films(request):
    q = request.GET.get('q', '')
    if len(q) < 2:
        return HttpResponse(json.dumps([]), content_type='application/json')
    films, _ = filmlist.filmlist(
        user_id=request.user.id,
        filters=[
            ('main_premier_year', settings.VAPITI_YEAR),
            ('title', q),
            ('seen_it', '1'),
        ],
        ordering='title',
        films_per_page=10,
    )
    return HttpResponse(json.dumps([
        (u'%s / %s' % (film.orig_title, film.second_title)) if film.second_title else film.orig_title
        for film in films
    ]), content_type='application/json')


@login_required
def get_vapiti_artists(request):
    q = request.GET.get('q', '')
    if len(q) < 2:
        return HttpResponse(json.dumps([]), content_type='application/json')
    gender = request.GET.get('g', '')
    if gender not in {'M', 'F'}:
        gender = 'M'
    roles = models.FilmArtistRelationship.objects.raw('''
    SELECT
      r.id,
      a.name AS name,
      f.orig_title AS orig_title,
      f.second_title AS second_title
    FROM ktapp_filmartistrelationship r
    INNER JOIN ktapp_artist a ON a.id = r.artist_id
    INNER JOIN ktapp_film f ON f.id = r.film_id
    INNER JOIN ktapp_vote v ON v.film_id = f.id AND v.user_id = {user_id}
    WHERE r.role_type = 'A' AND r.actor_subtype = 'F'
    AND f.main_premier_year = {vapiti_year}
    AND a.gender = '{gender}'
    AND a.name LIKE %s
    ORDER BY a.name, a.id, r.role_name, r.id
    LIMIT 10
    '''.format(
            user_id=request.user.id,
            vapiti_year=settings.VAPITI_YEAR,
            gender=gender,
    ), [u'%{name}%'.format(name=q)])
    return HttpResponse(json.dumps([
        u'%s [%s]' % (
            role.name,
            (u'%s / %s' % (role.orig_title, role.second_title)) if role.second_title else role.orig_title,
        )
        for role in roles
    ]), content_type='application/json')


def buzz(request):
    buzz_comment_domains = {}
    for comment in models.Comment.objects.all()[:100]:
        key = (comment.domain, comment.film_id, comment.topic_id, comment.poll_id)
        if key not in buzz_comment_domains:
            buzz_comment_domains[key] = (comment.id, comment.created_at)
        else:
            if comment.created_at > buzz_comment_domains[key][1]:
                buzz_comment_domains[key] = (comment.id, comment.created_at)
    buzz_comment_ids = [id for id, _ in sorted(buzz_comment_domains.values(), key=lambda x: x[1], reverse=True)[:10]]
    buzz_comments = []
    for comment in models.Comment.objects.select_related('film', 'topic', 'poll', 'created_by', 'reply_to', 'reply_to__created_by').filter(id__in=buzz_comment_ids):
        buzz_comments.append({
            'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'serial_number': comment.serial_number,
            'content': comment.content_html,
            'domain': comment.domain,
            'domain_object': {
                'id': comment.domain_object.id,
                'title': getattr(comment.domain_object, 'orig_title', getattr(comment.domain_object, 'title', '???')),
            },
            'created_by': {
                'id': comment.created_by.id,
                'username': comment.created_by.username,
            },
            'rating': comment.rating,
        })
    return HttpResponse(json.dumps(buzz_comments), content_type='application/json')


def comment_page(request, domain, id):
    COMMENTS_PER_PAGE = 10
    if domain == 'film':
        domain = 'F'
    elif domain == 'topic':
        domain = 'T'
    else:
        domain = 'P'
    if domain == 'F':
        domain_object = get_object_or_404(models.Film, id=id)
        qs = models.Comment.objects.filter(
            domain=domain,
            film_id=id,
        )
    elif domain == 'T':
        domain_object = get_object_or_404(models.Topic, id=id)
        qs = models.Comment.objects.filter(
            domain=domain,
            topic_id=id,
        )
    else:
        domain_object = get_object_or_404(models.Poll, id=id)
        qs = models.Comment.objects.filter(
            domain=domain,
            poll_id=id,
        )
    qs = qs.select_related('created_by', 'reply_to', 'reply_to__created_by')
    p = int(request.GET.get('p', 0))
    if p < 1:
        p = 1
    first_comment = domain_object.number_of_comments - COMMENTS_PER_PAGE * (p - 1) - (COMMENTS_PER_PAGE - 1)
    last_comment = domain_object.number_of_comments - COMMENTS_PER_PAGE * (p - 1)
    qs = qs.filter(serial_number__lte=last_comment, serial_number__gte=first_comment)
    comments = []
    for comment in qs.order_by('-serial_number')[:COMMENTS_PER_PAGE]:
        comments.append({
            'domain': domain,
            'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'serial_number': comment.serial_number,
            'content': comment.content_html,
            'created_by': {
                'id': comment.created_by.id,
                'username': comment.created_by.username,
            },
            'rating': comment.rating,
        })
    return HttpResponse(json.dumps({
        'comments': comments,
        'domain': domain,
        'domain_object': {
            'id': domain_object.id,
            'title': getattr(domain_object, 'orig_title', getattr(domain_object, 'title', '???')),
        },
    }), content_type='application/json')
