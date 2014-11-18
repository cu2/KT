from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from ktapp import models
from ktapp import serializers


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    model = models.KTUser
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
    model = models.Film
    serializer_class = serializers.FilmSerializer
    paginate_by = 10
    paginate_by_param = 'page_size'
    max_paginate_by = 100


class KeywordViewSet(viewsets.ReadOnlyModelViewSet):
    model = models.Keyword
    serializer_class = serializers.KeywordSerializer


class ArtistViewSet(viewsets.ReadOnlyModelViewSet):
    model = models.Artist
    serializer_class = serializers.ArtistSerializer


class SequelViewSet(viewsets.ReadOnlyModelViewSet):
    model = models.Sequel
    serializer_class = serializers.SequelSerializer
