import json
from collections import OrderedDict

from django.http import HttpResponse
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from ktapp import models
from ktapp import serializers


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
    q = request.GET.get('q', '')
    if len(q) < 2:
        return HttpResponse(json.dumps([]), content_type='application/json')
    return HttpResponse(json.dumps(
        [
            {
                'id': film.id,
                'orig_title': film.orig_title,
                'second_title': film.second_title,
                'third_title': film.third_title,
                'year': film.year,
                'slug': film.slug_cache,
            } for film in models.Film.objects.filter(
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
            'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'content': comment.content_html,
            'created_by': {
                'id': comment.created_by.id,
                'username': comment.created_by.username,
            },
        })
    return HttpResponse(json.dumps(comments), content_type='application/json')
