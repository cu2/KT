import json
from urlparse import urlparse

from django.db import models


class OfTheDay(models.Model):
    DOMAIN_FILM = 'F'
    DOMAINS = [
        (DOMAIN_FILM, 'Film'),
    ]
    domain = models.CharField(max_length=1, choices=DOMAINS, default=DOMAIN_FILM)
    day = models.DateField()
    film = models.ForeignKey('Film')
    public = models.BooleanField(default=False)

    class Meta:
        unique_together = ['domain', 'day']


class Change(models.Model):
    created_by = models.ForeignKey('KTUser', blank=True, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=250)
    object = models.CharField(max_length=250)
    state_before = models.TextField(blank=True)
    state_after = models.TextField(blank=True)


class Event(models.Model):
    user = models.ForeignKey('KTUser', blank=True, null=True, on_delete=models.SET_NULL)
    event_datetime = models.DateTimeField(auto_now_add=True)
    EVENT_TYPE_NEW_VOTE = 'NV'
    EVENT_TYPE_CHANGE_VOTE = 'CV'
    EVENT_TYPE_DELETE_VOTE = 'DV'
    EVENT_TYPE_ADD_TO_WISHLIST = 'AW'
    EVENT_TYPE_REMOVE_FROM_WISHLIST = 'RW'
    EVENT_TYPE_NEW_COMMENT = 'NC'
    EVENT_TYPE_EDIT_COMMENT = 'EC'
    EVENT_TYPE_SIGNUP = 'SU'
    EVENT_TYPE_EDIT_PROFILE = 'EP'
    EVENT_TYPE_UPLOAD_PROFILE_PIC = 'UP'
    EVENT_TYPE_DELETE_PROFILE_PIC = 'DP'
    EVENT_TYPE_EDIT_USER_SETTINGS = 'ES'
    EVENT_TYPE_FOLLOW = 'FO'
    EVENT_TYPE_UNFOLLOW = 'UF'
    EVENT_TYPE_POLL_VOTE = 'PV'
    EVENT_TYPE_VAPITI_VOTE = 'VV'
    EVENT_TYPE_NEW_TOPLIST = 'NT'
    EVENT_TYPE_EDIT_TOPLIST = 'ET'
    EVENT_TYPE_DELETE_TOPLIST = 'DT'
    EVENT_TYPES = [
        (EVENT_TYPE_NEW_VOTE, 'New vote'),
        (EVENT_TYPE_CHANGE_VOTE, 'Change vote'),
        (EVENT_TYPE_DELETE_VOTE, 'Delete vote'),
        (EVENT_TYPE_ADD_TO_WISHLIST, 'Add to wishlist'),
        (EVENT_TYPE_REMOVE_FROM_WISHLIST, 'Remove from wishlist'),
        (EVENT_TYPE_NEW_COMMENT, 'New comment'),
        (EVENT_TYPE_EDIT_COMMENT, 'Edit comment'),
        (EVENT_TYPE_SIGNUP, 'Signup'),
        (EVENT_TYPE_EDIT_PROFILE, 'Edit profile'),
        (EVENT_TYPE_UPLOAD_PROFILE_PIC, 'Upload profile pic'),
        (EVENT_TYPE_DELETE_PROFILE_PIC, 'Delete profile pic'),
        (EVENT_TYPE_EDIT_USER_SETTINGS, 'Edit user settings'),
        (EVENT_TYPE_FOLLOW, 'Follow'),
        (EVENT_TYPE_UNFOLLOW, 'Unfollow'),
        (EVENT_TYPE_POLL_VOTE, 'Poll vote'),
        (EVENT_TYPE_VAPITI_VOTE, 'Vapiti vote'),
        (EVENT_TYPE_NEW_TOPLIST, 'New toplist'),
        (EVENT_TYPE_EDIT_TOPLIST, 'Edit toplist'),
        (EVENT_TYPE_DELETE_TOPLIST, 'Delete toplist'),
    ]
    event_type = models.CharField(max_length=2, choices=EVENT_TYPES, default=EVENT_TYPE_NEW_VOTE)
    film = models.ForeignKey('Film', blank=True, null=True, on_delete=models.SET_NULL)
    topic = models.ForeignKey('Topic', blank=True, null=True, on_delete=models.SET_NULL)
    poll = models.ForeignKey('Poll', blank=True, null=True, on_delete=models.SET_NULL)
    some_id = models.PositiveIntegerField(default=0)
    details = models.CharField(max_length=250, blank=True, null=True)

    def get_details(self):
        if self.details:
            return json.loads(self.details)
        return {}

    def get_comment(self):
        from .user_content import Comment
        try:
            return Comment.objects.get(id=self.some_id)
        except Comment.DoesNotExist:
            return None


class LinkClick(models.Model):
    url = models.CharField(max_length=250)
    url_domain = models.CharField(max_length=250)
    referer = models.CharField(max_length=250, blank=True)
    user = models.ForeignKey('KTUser', blank=True, null=True, on_delete=models.SET_NULL)
    clicked_at = models.DateTimeField(auto_now_add=True)
    LINK_TYPE_LINK = 'LI'
    LINK_TYPE_FILM_IMDB = 'IM'
    LINK_TYPE_FILM_PORTHU = 'PO'
    LINK_TYPE_FILM_RT = 'RT'
    LINK_TYPE_FILM_YOUTUBE = 'YT'
    LINK_TYPE_FILM_WIKI_EN = 'WE'
    LINK_TYPE_FILM_WIKI_HU = 'WH'
    LINK_TYPE_FILM_ISZDB = 'IS'
    LINK_TYPE_ARTIST_IMDB = 'AI'
    LINK_TYPE_ARTIST_WIKI_EN = 'AE'
    LINK_TYPE_ARTIST_WIKI_HU = 'AH'
    LINK_TYPE_OTHER = '-'
    LINK_TYPES = [
        (LINK_TYPE_LINK, 'Link'),
        (LINK_TYPE_FILM_IMDB, 'Film / IMDb'),
        (LINK_TYPE_FILM_PORTHU, 'Film / Port.hu'),
        (LINK_TYPE_FILM_RT, 'Film / Rotten Tomatoes'),
        (LINK_TYPE_FILM_YOUTUBE, 'Film / YouTube'),
        (LINK_TYPE_FILM_WIKI_EN, 'Film / Wikipedia EN'),
        (LINK_TYPE_FILM_WIKI_HU, 'Film / Wikipedia HU'),
        (LINK_TYPE_FILM_ISZDB, 'Film / ISZDb'),
        (LINK_TYPE_ARTIST_IMDB, 'Artist / IMDb'),
        (LINK_TYPE_ARTIST_WIKI_EN, 'Artist / Wikipedia EN'),
        (LINK_TYPE_ARTIST_WIKI_HU, 'Artist / Wikipedia HU'),
        (LINK_TYPE_OTHER, 'Other'),
    ]
    link_type = models.CharField(max_length=2, choices=LINK_TYPES, default=LINK_TYPE_OTHER)
    link = models.ForeignKey('Link', blank=True, null=True)
    film = models.ForeignKey('Film', blank=True, null=True)
    artist = models.ForeignKey('Artist', blank=True, null=True)

    def save(self, *args, **kwargs):
        self.url_domain = urlparse(self.url).netloc
        super(LinkClick, self).save(*args, **kwargs)


class AppConfig(models.Model):
    vapiti_year = models.PositiveIntegerField()
    vapiti_topic_id = models.PositiveIntegerField()

    @classmethod
    def get(cls):
        fields = [
            "vapiti_year",
            "vapiti_topic_id",
        ]
        raw_app_config = cls.objects.first()
        if raw_app_config:
            return {
                field: getattr(raw_app_config, field)
                for field in fields
            }
        return {
            field: None
            for field in fields
        }
