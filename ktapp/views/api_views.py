from rest_framework import viewsets

from ktapp import models
from ktapp import serializers


class UserViewSet(viewsets.ModelViewSet):
    model = models.KTUser
    serializer_class = serializers.UserSerializer


class FilmViewSet(viewsets.ModelViewSet):
    model = models.Film
    serializer_class = serializers.FilmSerializer


class KeywordViewSet(viewsets.ModelViewSet):
    model = models.Keyword
    serializer_class = serializers.KeywordSerializer


class ArtistViewSet(viewsets.ModelViewSet):
    model = models.Artist
    serializer_class = serializers.ArtistSerializer


class SequelViewSet(viewsets.ModelViewSet):
    model = models.Sequel
    serializer_class = serializers.SequelSerializer
