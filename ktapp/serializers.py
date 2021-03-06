from rest_framework import serializers

from ktapp import models


class UserSerializer(serializers.HyperlinkedModelSerializer):
    votes_url = serializers.HyperlinkedIdentityField(view_name='ktuser-votes', lookup_field='pk')

    class Meta:
        model = models.KTUser
        fields = ('url', 'username', 'votes_url')


class UserVoteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Vote
        fields = ('film', 'rating')


class UserWithVotesSerializer(serializers.HyperlinkedModelSerializer):
    votes = UserVoteSerializer(many=True)

    class Meta:
        model = models.KTUser
        fields = ('url', 'username', 'votes')


class KeywordSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Keyword


class ShortKeywordSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Keyword
        fields = ('url', 'name',)


class ArtistSerializer(serializers.HyperlinkedModelSerializer):  # TODO: films directed, roles
    class Meta:
        model = models.Artist
        fields = ('url', 'name', 'gender', 'number_of_films', 'number_of_ratings', 'average_rating')


class ShortArtistSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Artist
        fields = ('url', 'name',)


class SequelSerializer(serializers.HyperlinkedModelSerializer):  # TODO: serial_number of films
    class Meta:
        model = models.Sequel


class ShortSequelSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Sequel
        fields = ('url', 'name', 'sequel_type',)


class FilmSerializer(serializers.HyperlinkedModelSerializer):
    directors = ShortArtistSerializer(many=True)
    countries = ShortKeywordSerializer(many=True)
    genres = ShortKeywordSerializer(many=True)
    sequels = ShortSequelSerializer(many=True)

    class Meta:
        model = models.Film
        fields = (
            'url', 'orig_title', 'second_title', 'third_title', 'year',
            'plot_summary',
            'main_premier', 'main_premier_year',

            'directors',
            'countries',
            'genres',
            'sequels',

            'number_of_ratings', 'average_rating',

            'imdb_link', 'porthu_link', 'wikipedia_link_en', 'wikipedia_link_hu',

            'number_of_ratings_1', 'number_of_ratings_2', 'number_of_ratings_3', 'number_of_ratings_4', 'number_of_ratings_5',
            'number_of_comments', 'number_of_quotes', 'number_of_trivias', 'number_of_reviews', 'number_of_keywords',
            'number_of_awards', 'number_of_links', 'number_of_pictures',
            'imdb_rating',
        )
        read_only_fields = (
            'number_of_ratings_1', 'number_of_ratings_2', 'number_of_ratings_3', 'number_of_ratings_4', 'number_of_ratings_5',
            'number_of_comments', 'number_of_quotes', 'number_of_trivias', 'number_of_reviews', 'number_of_keywords',
            'number_of_awards', 'number_of_links', 'number_of_pictures',
            'imdb_rating',
        )
