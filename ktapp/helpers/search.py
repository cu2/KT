from django.db.models import Q
from django.template.defaultfilters import slugify

from ktapp import models


def find_film_by_link(q):
    # search by IMDB link:
    if 'imdb.com/title' in q:
        try:
            imdb_link = q[q.index('imdb.com/title')+15:].split('/')[0]
        except Exception:
            imdb_link = None
        if imdb_link:
            try:
                film = models.Film.objects.get(imdb_link=imdb_link)
            except models.Film.DoesNotExist:
                film = None
            if film:
                return film
    # search by port.hu link:
    if 'port.hu' in q:
        try:
            porthu_link = q[q.index('i_film_id=')+10:].split('&')[0]
        except Exception:
            porthu_link = None
        if porthu_link:
            try:
                film = models.Film.objects.get(porthu_link=porthu_link)
            except models.Film.DoesNotExist:
                film = None
            if film:
                return film
    # search by wikipedia link:
    if 'wikipedia.org' in q:
        try:
            wikipedia_link = q[q.index('://')+3:]
        except Exception:
            wikipedia_link = None
        if wikipedia_link:
            try:
                film = models.Film.objects.get(wikipedia_link_en__contains=wikipedia_link)
            except (models.Film.DoesNotExist, models.Film.MultipleObjectsReturned):
                try:
                    film = models.Film.objects.get(wikipedia_link_hu__contains=wikipedia_link)
                except (models.Film.DoesNotExist, models.Film.MultipleObjectsReturned):
                    film = None
            if film:
                return film
    return None


def find_artists(q_pieces, limit):
    artists = models.Artist.objects
    artists = artists.filter(slug_cache__search=' '.join(['+%s*' % slugify(q_piece) for q_piece in q_pieces]))
    return artists.order_by('-number_of_ratings')[:limit]


def find_users(q_pieces, limit):
    users = models.KTUser.objects
    for q_piece in q_pieces:
        users = users.filter(
            Q(username__icontains=q_piece)
            | Q(slug_cache__icontains=slugify(q_piece))
        )
    return users.order_by('username')[:limit]


def find_topics(q_pieces, limit):
    topics = models.Topic.objects.select_related('last_comment', 'last_comment__created_by')
    for q_piece in q_pieces:
        topics = topics.filter(
            Q(title__icontains=q_piece)
            | Q(slug_cache__icontains=slugify(q_piece))
        )
    return topics.order_by('-number_of_comments')[:limit]


def find_polls(q_pieces, limit):
    polls = models.Poll.objects
    for q_piece in q_pieces:
        polls = polls.filter(
            Q(title__icontains=q_piece)
            | Q(slug_cache__icontains=slugify(q_piece))
        )
    return polls.order_by('-number_of_votes')[:limit]


def find_roles(q_pieces, limit):
    roles = models.FilmArtistRelationship.objects.select_related('artist', 'film').filter(role_type=models.FilmArtistRelationship.ROLE_TYPE_ACTOR)
    for q_piece in q_pieces:
        roles = roles.filter(
            Q(role_name__icontains=q_piece)
            | Q(slug_cache__icontains=slugify(q_piece))
        )
    return roles.order_by('-film__number_of_ratings', '-artist__number_of_ratings')[:limit]


def find_sequels(q_pieces, limit):
    sequels = models.Sequel.objects
    for q_piece in q_pieces:
        sequels = sequels.filter(
            Q(name__icontains=q_piece)
            | Q(slug_cache__icontains=slugify(q_piece))
        )
    return sequels.order_by('name')[:limit]
