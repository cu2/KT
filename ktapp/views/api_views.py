import json
from collections import OrderedDict

from django.http import HttpResponse
from django.db.models import Q
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
    paginate_by = 10
    paginate_by_param = 'page_size'
    max_paginate_by = 100


class KeywordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Keyword.objects.all()
    serializer_class = serializers.KeywordSerializer


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
    if len(q) < 2:
        return HttpResponse(json.dumps([]), content_type='application/json')
    return HttpResponse(json.dumps(
        [{'label': artist.name, 'value': artist.name, 'id': artist.id, 'gender': artist.gender} for artist in models.Artist.objects.filter(name__icontains=q).order_by('name', 'id')[:10]]
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
