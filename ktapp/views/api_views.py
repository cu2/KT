import json

from django.http import HttpResponse
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
        return HttpResponse(json.dumps({
            'results': [],
        }), content_type='application/json')
    return HttpResponse(json.dumps(
        [user.username for user in models.KTUser.objects.filter(username__startswith=q).order_by('username', 'id')[:10]]
    ), content_type='application/json')
