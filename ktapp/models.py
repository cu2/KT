import datetime
import hashlib
import json
import os
import random
import string
from PIL import Image
from urlparse import urlparse

from django.db import models, connection
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.db.models.signals import post_delete, pre_delete
from django.dispatch.dispatcher import receiver
from django.template.defaultfilters import slugify
from django.utils.crypto import get_random_string
from django.utils.html import strip_tags

from kt import settings
from ktapp import utils as kt_utils
from ktapp import texts


class KTUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=64, unique=True)
    email = models.EmailField(blank=True, unique=True)
    is_staff = models.BooleanField(default=False)  # admin
    is_inner_staff = models.BooleanField(default=False)  # active admin
    is_active = models.BooleanField(default=True)  # delete
    date_joined = models.DateTimeField(auto_now_add=True)
    GENDER_TYPE_MALE = 'M'
    GENDER_TYPE_FEMALE = 'F'
    GENDER_TYPE_UNKNOWN = 'U'
    GENDER_TYPES = [
        (GENDER_TYPE_MALE, 'Male'),
        (GENDER_TYPE_FEMALE, 'Female'),
        (GENDER_TYPE_UNKNOWN, 'Unknown'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_TYPES, default=GENDER_TYPE_UNKNOWN)
    location = models.CharField(max_length=250, blank=True, null=True)
    year_of_birth = models.PositiveIntegerField(default=0)
    public_gender = models.BooleanField(default=True)
    public_location = models.BooleanField(default=True)
    public_year_of_birth = models.BooleanField(default=True)
    follow = models.ManyToManyField('KTUser', symmetrical=False, through='Follow', through_fields=('who', 'whom'))
    slug_cache = models.CharField(max_length=250, blank=True)
    validated_email = models.BooleanField(default=False)
    core_member = models.BooleanField(default=False)
    i_county_id = models.SmallIntegerField(default=-1)
    email_notification = models.BooleanField(default=False)
    facebook_rating_share = models.BooleanField(default=True)
    added_role = models.PositiveIntegerField(default=0)
    added_artist = models.PositiveIntegerField(default=0)
    added_film = models.PositiveIntegerField(default=0)
    added_tvfilm = models.PositiveIntegerField(default=0)
    added_trivia = models.PositiveIntegerField(default=0)
    REASON_BANNED = 'B'
    REASON_TEMPORARILY_BANNED = 'T'
    REASON_QUIT = 'Q'
    REASON_UNKNOWN = 'U'
    REASONS = [
        (REASON_BANNED, 'Banned'),
        (REASON_TEMPORARILY_BANNED, 'Temporarily Banned'),
        (REASON_QUIT, 'Quit'),
        (REASON_UNKNOWN, 'Unknown'),
    ]
    reason_of_inactivity = models.CharField(max_length=1, choices=REASONS, default=REASON_UNKNOWN)
    banned_until = models.DateTimeField(blank=True, null=True)
    old_permissions = models.CharField(max_length=250, blank=True, null=True)
    ip_at_registration = models.CharField(max_length=250, blank=True, null=True)
    ip_at_last_login = models.CharField(max_length=250, blank=True, null=True)
    last_message_at = models.DateTimeField(blank=True, null=True)
    last_message_checking_at = models.DateTimeField(blank=True, null=True)
    old_tv_settings = models.CharField(max_length=250, blank=True, null=True)
    last_activity_at = models.DateTimeField(blank=True, null=True)
    latest_votes = models.TextField(blank=True)
    latest_comments = models.TextField(blank=True)
    number_of_comments = models.PositiveIntegerField(default=0)
    number_of_ratings = models.PositiveIntegerField(default=0)
    number_of_messages = models.PositiveIntegerField(default=0)
    number_of_wishes_yes = models.PositiveIntegerField(default=0)
    number_of_wishes_no = models.PositiveIntegerField(default=0)
    number_of_wishes_get = models.PositiveIntegerField(default=0)
    number_of_toplists = models.PositiveIntegerField(default=0)
    number_of_reviews = models.PositiveIntegerField(default=0)
    number_of_bios = models.PositiveIntegerField(default=0)
    number_of_links = models.PositiveIntegerField(default=0)
    is_reliable = models.BooleanField(default=False)
    bio = models.TextField(blank=True)
    bio_html = models.TextField(blank=True)
    bio_snippet = models.TextField(blank=True)
    fav_period = models.CharField(max_length=250, blank=True, null=True)
    is_game_master = models.BooleanField(default=False)
    number_of_ratings_1 = models.PositiveIntegerField(default=0)
    number_of_ratings_2 = models.PositiveIntegerField(default=0)
    number_of_ratings_3 = models.PositiveIntegerField(default=0)
    number_of_ratings_4 = models.PositiveIntegerField(default=0)
    number_of_ratings_5 = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(default=None, max_digits=2, decimal_places=1, blank=True, null=True)
    number_of_film_comments = models.PositiveIntegerField(default=0)
    number_of_topic_comments = models.PositiveIntegerField(default=0)
    number_of_poll_comments = models.PositiveIntegerField(default=0)
    number_of_vapiti_votes = models.PositiveIntegerField(default=0)
    vapiti_weight = models.PositiveIntegerField(default=0)
    profile_pic = models.ForeignKey('Picture', blank=True, null=True, related_name='profile_pic', on_delete=models.SET_NULL)
    number_of_followers = models.PositiveIntegerField(default=0)
    opinion_leader = models.BooleanField(default=False)
    design_version = models.PositiveSmallIntegerField(default=1)
    subscribed_to_campaigns = models.BooleanField(default=False)
    token_to_unsubscribe = models.CharField(max_length=64, blank=True)
    unread_notification_count = models.PositiveIntegerField(default=0)
    last_uur_calculation_at = models.DateTimeField(blank=True, null=True)
    signed_privacy_policy = models.BooleanField(default=False)
    signed_privacy_policy_at = models.DateTimeField(blank=True, null=True)

    objects = UserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    def email_user(self, subject, html_message, text_message=None, email_type='', campaign_id=0, html_ps='', text_ps='', from_email=settings.DEFAULT_FROM_EMAIL, **kwargs):
        if text_message is None:
            text_message = strip_tags(html_message.replace('</p>\n<p>', '\n\n'))
        if campaign_id:
            html_unsub_ps = texts.EMAIL_UNSUB_PS_HTML.format(
                user_id=self.id,
                token=self.token_to_unsubscribe,
                type=email_type,
                campaign_id=campaign_id,
            )
            unsub_ps = texts.EMAIL_UNSUB_PS_TEXT.format(
                user_id=self.id,
                token=self.token_to_unsubscribe,
                type=email_type,
                campaign_id=campaign_id,
            )
        else:
            html_unsub_ps = ''
            unsub_ps = ''
        html_content = texts.EMAIL_TEMPLATE_HTML.format(
            username=self.username,
            html_message=html_message,
            user_id=self.id,
            type=email_type,
            campaign_id=campaign_id,
            ps=html_ps,
            unsub_ps=html_unsub_ps,
        )
        text_content = texts.EMAIL_TEMPLATE_TEXT.format(
            username=self.username,
            text_message=text_message,
            ps=text_ps,
            unsub_ps=unsub_ps,
        )
        email = EmailMultiAlternatives(
            subject,
            text_content,
            from_email,
            [self.email],
        )
        email.attach_alternative(html_content, 'text/html')
        if settings.LOCAL_MAIL:
            print '[SUBJECT] %s' % email.subject
            print '[FROM] %s' % email.from_email
            print '[TO] %s' % self.email
            print '[BODY]'
            print email.body
            print '[/BODY]'
            print '[HTML]'
            print html_content
            print '[/HTML]'
        else:
            success = email.send()
            if campaign_id:
                try:
                    campaign = EmailCampaign.objects.get(id=campaign_id)
                except EmailCampaign.DoesNotExist:
                    campaign = None
            else:
                campaign = None
            EmailSend.objects.create(
                user=self,
                email_type=email_type,
                campaign=campaign,
                email=self.email,
                is_pm=True,
                is_email=True,
                is_success=success,
            )

    def votes(self):
        return self.vote_set.all()

    def get_follows(self):
        return self.follow.all()

    def get_followed_by(self):
        return [u.who for u in self.followed_by.all().select_related('who')]

    def save(self, *args, **kwargs):
        self.slug_cache = slugify(self.username)
        self.bio = strip_tags(self.bio)
        self.bio_html = kt_utils.bbcode_to_html(self.bio)
        self.bio_snippet = strip_tags(self.bio_html)[:500]
        if self.token_to_unsubscribe == '':
            self.token_to_unsubscribe = get_random_string(64, allowed_chars='abcdefghijklmnopqrstuvwxyz0123456789')
        super(KTUser, self).save(*args, **kwargs)

    @classmethod
    def get_user_by_name(cls, name):  # case and more importantly accent sensitive getter
        user_list = [user for user in cls.objects.filter(username=name) if user.username == name]
        if user_list:
            return user_list[0]
        return None


class Film(models.Model):
    orig_title = models.CharField(max_length=250)
    second_title = models.CharField(max_length=250, blank=True)
    third_title = models.CharField(max_length=250, blank=True)
    year = models.PositiveIntegerField(default=0, blank=True, null=True)
    plot_summary = models.TextField(blank=True)
    number_of_comments = models.PositiveIntegerField(default=0)
    last_comment = models.ForeignKey('Comment', blank=True, null=True, related_name='last_film_comment', on_delete=models.SET_NULL)
    artists = models.ManyToManyField('Artist', through='FilmArtistRelationship')
    number_of_ratings_1 = models.PositiveIntegerField(default=0)
    number_of_ratings_2 = models.PositiveIntegerField(default=0)
    number_of_ratings_3 = models.PositiveIntegerField(default=0)
    number_of_ratings_4 = models.PositiveIntegerField(default=0)
    number_of_ratings_5 = models.PositiveIntegerField(default=0)
    number_of_ratings = models.PositiveIntegerField(default=0, db_index=True)
    average_rating = models.DecimalField(default=0, max_digits=2, decimal_places=1, blank=True, null=True)
    number_of_quotes = models.PositiveIntegerField(default=0)
    number_of_trivias = models.PositiveIntegerField(default=0)
    number_of_reviews = models.PositiveIntegerField(default=0)
    keywords = models.ManyToManyField('Keyword', through='FilmKeywordRelationship')
    number_of_keywords = models.PositiveIntegerField(default=0)
    imdb_link = models.CharField(max_length=16, blank=True)
    porthu_link = models.PositiveIntegerField(default=0, blank=True, null=True)
    wikipedia_link_en = models.CharField(max_length=250, blank=True)
    wikipedia_link_hu = models.CharField(max_length=250, blank=True)
    iszdb_link = models.CharField(max_length=50, blank=True)
    imdb_rating = models.PositiveSmallIntegerField(blank=True, null=True)
    imdb_rating_refreshed_at = models.DateTimeField(blank=True, null=True)
    number_of_awards = models.PositiveIntegerField(default=0)
    number_of_links = models.PositiveIntegerField(default=0)
    number_of_pictures = models.PositiveIntegerField(default=0)
    sequels = models.ManyToManyField('Sequel', through='FilmSequelRelationship')
    main_premier = models.DateField(blank=True, null=True)
    main_premier_year = models.PositiveIntegerField(blank=True, null=True)
    slug_cache = models.CharField(max_length=250, blank=True)
    created_by = models.ForeignKey(KTUser, blank=True, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    open_for_vote_from = models.DateField(blank=True, null=True)
    main_poster = models.ForeignKey('Picture', blank=True, null=True, related_name='main_poster', on_delete=models.SET_NULL)
    directors_cache = models.CharField(max_length=250, blank=True)
    genres_cache = models.CharField(max_length=250, blank=True)
    director_names_cache = models.CharField(max_length=250, blank=True)
    genre_names_cache = models.CharField(max_length=250, blank=True)
    number_of_genres = models.PositiveSmallIntegerField(default=0)
    number_of_countries = models.PositiveSmallIntegerField(default=0)
    genre_cache_is_short = models.BooleanField(default=False)
    genre_cache_is_mini = models.BooleanField(default=False)
    genre_cache_is_music_video = models.BooleanField(default=False)
    genre_cache_is_animation = models.BooleanField(default=False)
    genre_cache_is_docu = models.BooleanField(default=False)
    number_of_actors = models.PositiveIntegerField(default=0)
    main_roles_confirmed = models.BooleanField(default=False)

    def __unicode__(self):
        return self.orig_title + ' [' + unicode(self.year) + ']'

    def num_specific_rating(self, r):
        if 1 <= r <= 5:
            return getattr(self, 'number_of_ratings_' + str(r))

    def directors(self):
        return self.artists.filter(filmartistrelationship__role_type=FilmArtistRelationship.ROLE_TYPE_DIRECTOR)

    def countries(self):
        return self.keywords.filter(filmkeywordrelationship__keyword__keyword_type=Keyword.KEYWORD_TYPE_COUNTRY)

    def genres(self):
        return self.keywords.filter(filmkeywordrelationship__keyword__keyword_type=Keyword.KEYWORD_TYPE_GENRE)

    def imdb_real_rating(self):
        try:
            return self.imdb_rating / 10.0
        except TypeError:
            return None

    def all_sequels(self):
        return self.sequels.all()

    def other_premiers(self):
        return Premier.objects.filter(film=self)

    def save(self, *args, **kwargs):
        if self.second_title:
            self.slug_cache = slugify(self.orig_title) + '-' + slugify(self.second_title) + '-' + slugify(self.year)
        else:
            self.slug_cache = slugify(self.orig_title) + '-' + slugify(self.year)
        super(Film, self).save(*args, **kwargs)

    def fix_keywords(self):
        self.number_of_keywords = self.keywords.filter(filmkeywordrelationship__keyword__keyword_type__in=[Keyword.KEYWORD_TYPE_MAJOR, Keyword.KEYWORD_TYPE_OTHER]).count()
        self.number_of_genres = self.keywords.filter(filmkeywordrelationship__keyword__keyword_type=Keyword.KEYWORD_TYPE_GENRE).count()
        self.number_of_countries = self.keywords.filter(filmkeywordrelationship__keyword__keyword_type=Keyword.KEYWORD_TYPE_COUNTRY).count()
        ids = []
        slugs = []
        names = []
        self.genre_cache_is_music_video = False
        self.genre_cache_is_mini = False
        self.genre_cache_is_short = False
        self.genre_cache_is_animation = False
        self.genre_cache_is_docu = False
        for g in self.genres():
            if g.id == 314:
                self.genre_cache_is_music_video = True
            if g.id == 4150:
                self.genre_cache_is_mini = True
            if g.id == 120:
                self.genre_cache_is_short = True
            if g.id in {368, 27}:  # animation, anime
                self.genre_cache_is_animation = True
            if g.id == 95:
                self.genre_cache_is_docu = True
            ids.append(unicode(g.id))
            slugs.append(g.slug_cache)
            names.append(g.name)
        if len(ids):
            self.genres_cache = ('%s;%s;%s' % (','.join(ids), ','.join(slugs), ','.join(names)))[:250]
            self.genre_names_cache = ','.join(names)[:250]
        else:
            self.genres_cache = ''
            self.genre_names_cache = ''
        self.save()

    def absolute_url(self):
        return 'http://kritikustomeg.org%s' % reverse('film_main', args=(self.id, self.slug_cache))

    def is_open_for_vote_from(self):
        if self.open_for_vote_from is None:
            return True
        return self.open_for_vote_from <= datetime.date.today()

    @property
    def number_of_articles(self):
        return self.number_of_reviews + self.number_of_links


class PremierType(models.Model):
    name = models.CharField(max_length=250)

    def __unicode__(self):
        return self.name


class Premier(models.Model):
    film = models.ForeignKey(Film)
    when = models.DateField()
    premier_type = models.ForeignKey(PremierType, blank=True, null=True, on_delete=models.SET_NULL)

    def __unicode__(self):
        return self.film.orig_title + ': ' + unicode(self.when) + ' [' + unicode(self.premier_type) + ']'

    class Meta:
        ordering = ['when', 'premier_type', 'film']


class Vote(models.Model):
    film = models.ForeignKey(Film)
    user = models.ForeignKey(KTUser)
    rating = models.PositiveSmallIntegerField()
    when = models.DateTimeField(auto_now_add=True, null=True)
    shared_on_facebook = models.BooleanField(default=False)

    def __unicode__(self):
        return self.film.orig_title + ' + ' + self.user.username + ' = ' + unicode(self.rating)

    class Meta:
        unique_together = ['film', 'user']

    def save(self, *args, **kwargs):
        super(Vote, self).save(*args, **kwargs)
        self.film.comment_set.filter(created_by=self.user).update(rating=self.rating)
        Wishlist.objects.filter(film=self.film, wished_by=self.user, wish_type=Wishlist.WISH_TYPE_YES).delete()
        self.user.latest_votes = ','.join([unicode(v.id) for v in self.user.vote_set.all().order_by('-when', '-id')[:100]])
        self.user.number_of_ratings = self.user.vote_set.count()
        self.user.number_of_ratings_1 = self.user.vote_set.filter(rating=1).count()
        self.user.number_of_ratings_2 = self.user.vote_set.filter(rating=2).count()
        self.user.number_of_ratings_3 = self.user.vote_set.filter(rating=3).count()
        self.user.number_of_ratings_4 = self.user.vote_set.filter(rating=4).count()
        self.user.number_of_ratings_5 = self.user.vote_set.filter(rating=5).count()
        self.user.number_of_vapiti_votes = self.user.vote_set.filter(film__main_premier_year=settings.VAPITI_YEAR).count()
        self.user.vapiti_weight = self.user.number_of_ratings + 25 * self.user.number_of_vapiti_votes
        if self.user.number_of_ratings < 10:
            self.user.average_rating = None
        else:
            self.user.average_rating = 1.0 * (
                1*self.user.number_of_ratings_1+
                2*self.user.number_of_ratings_2+
                3*self.user.number_of_ratings_3+
                4*self.user.number_of_ratings_4+
                5*self.user.number_of_ratings_5
            ) / self.user.number_of_ratings
        self.user.save(update_fields=[
            'latest_votes', 'number_of_ratings',
            'number_of_ratings_1', 'number_of_ratings_2', 'number_of_ratings_3', 'number_of_ratings_4', 'number_of_ratings_5',
            'average_rating', 'number_of_vapiti_votes', 'vapiti_weight',
        ])
        Recommendation.recalculate_fav_for_users_and_film(self.user.get_followed_by(), self.film)


@receiver(post_delete, sender=Vote)
def delete_vote(sender, instance, **kwargs):
    try:
        instance.film.comment_set.filter(created_by=instance.user).update(rating=None)
    except Film.DoesNotExist:
        pass
    instance.user.latest_votes = ','.join([unicode(v.id) for v in instance.user.vote_set.all().order_by('-when', '-id')[:100]])
    instance.user.number_of_ratings = instance.user.vote_set.count()
    instance.user.number_of_ratings_1 = instance.user.vote_set.filter(rating=1).count()
    instance.user.number_of_ratings_2 = instance.user.vote_set.filter(rating=2).count()
    instance.user.number_of_ratings_3 = instance.user.vote_set.filter(rating=3).count()
    instance.user.number_of_ratings_4 = instance.user.vote_set.filter(rating=4).count()
    instance.user.number_of_ratings_5 = instance.user.vote_set.filter(rating=5).count()
    instance.user.number_of_vapiti_votes = instance.user.vote_set.filter(film__main_premier_year=settings.VAPITI_YEAR).count()
    instance.user.vapiti_weight = instance.user.number_of_ratings + 25 * instance.user.number_of_vapiti_votes
    if instance.user.number_of_ratings < 10:
        instance.user.average_rating = None
    else:
        instance.user.average_rating = 1.0 * (
            1*instance.user.number_of_ratings_1+
            2*instance.user.number_of_ratings_2+
            3*instance.user.number_of_ratings_3+
            4*instance.user.number_of_ratings_4+
            5*instance.user.number_of_ratings_5
        ) / instance.user.number_of_ratings
    instance.user.save(update_fields=[
        'latest_votes', 'number_of_ratings',
        'number_of_ratings_1', 'number_of_ratings_2', 'number_of_ratings_3', 'number_of_ratings_4', 'number_of_ratings_5',
        'average_rating', 'number_of_vapiti_votes', 'vapiti_weight',
    ])
    Recommendation.recalculate_fav_for_users_and_film(instance.user.get_followed_by(), instance.film)


class Recommendation(models.Model):
    film = models.ForeignKey(Film)
    user = models.ForeignKey(KTUser)
    fav_number_of_ratings = models.PositiveIntegerField(default=0)
    fav_average_rating = models.DecimalField(default=None, max_digits=2, decimal_places=1, blank=True, null=True)

    class Meta:
        unique_together = ['film', 'user']

    @classmethod
    def recalculate_fav_for_user_and_user(cls, who, whom):
        cursor = connection.cursor()
        cursor.execute('''
            DELETE FROM ktapp_recommendation WHERE user_id = %s AND film_id IN (
                SELECT film_id FROM ktapp_vote WHERE user_id = %s
            )
        ''', [who.id, whom.id])
        cursor.execute('''
            INSERT INTO ktapp_recommendation (user_id, film_id, fav_number_of_ratings, fav_average_rating)
            SELECT
              f.who_id AS user_id,
              v.film_id AS film_id,
              COUNT(v.rating) AS fav_number_of_ratings,
              CAST(AVG(v.rating) AS DECIMAL(2, 1)) AS fav_average_rating
            FROM ktapp_follow f
            INNER JOIN ktapp_vote v ON v.user_id = f.whom_id
            WHERE f.who_id = %s AND v.film_id IN (
                SELECT film_id FROM ktapp_vote WHERE user_id = %s
            )
            GROUP BY
              f.who_id,
              v.film_id
        ''', [who.id, whom.id])

    @classmethod
    def recalculate_fav_for_users_and_film(cls, users, film):
        user_ids = ','.join([unicode(u.id) for u in users])
        if user_ids:
            cursor = connection.cursor()
            cursor.execute('DELETE FROM ktapp_recommendation WHERE user_id IN (%s) AND film_id = %s' % (user_ids, film.id))
            cursor.execute('''
                INSERT INTO ktapp_recommendation (user_id, film_id, fav_number_of_ratings, fav_average_rating)
                SELECT
                  f.who_id AS user_id,
                  v.film_id AS film_id,
                  COUNT(v.rating) AS fav_number_of_ratings,
                  CAST(AVG(v.rating) AS DECIMAL(2, 1)) AS fav_average_rating
                FROM ktapp_follow f
                INNER JOIN ktapp_vote v ON v.user_id = f.whom_id
                WHERE f.who_id IN (%s) AND v.film_id = %s
                GROUP BY
                  f.who_id,
                  v.film_id
            ''' % (user_ids, film.id))


class Comment(models.Model):
    DOMAIN_FILM = 'F'
    DOMAIN_TOPIC = 'T'
    DOMAIN_POLL = 'P'
    DOMAINS = [
        (DOMAIN_FILM, 'Film'),
        (DOMAIN_TOPIC, 'Topic'),
        (DOMAIN_POLL, 'Poll'),
    ]
    domain = models.CharField(max_length=1, choices=DOMAINS, default=DOMAIN_FILM)
    film = models.ForeignKey(Film, blank=True, null=True)
    topic = models.ForeignKey('Topic', blank=True, null=True)
    poll = models.ForeignKey('Poll', blank=True, null=True)
    created_by = models.ForeignKey(KTUser, blank=True, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField()  # original w bbcode
    content_html = models.TextField()  # autogenerated from content
    content_old_html = models.TextField(blank=True)  # migrated from old db
    reply_to = models.ForeignKey('self', blank=True, null=True, on_delete=models.SET_NULL)
    rating = models.PositiveSmallIntegerField(blank=True, null=True)  # cache for film comments
    serial_number = models.PositiveIntegerField(default=0)
    serial_number_by_user = models.PositiveIntegerField(default=0)
    hidden = models.BooleanField(default=False)

    def __unicode__(self):
        return self.content[:100]

    class Meta:
        ordering = ['-created_at']
        get_latest_by = 'created_at'
        index_together = [
            ['created_at'],
            ['domain', 'created_at'],
            ['created_by', 'serial_number_by_user', 'created_at'],
            ['film', 'serial_number'],
            ['topic', 'serial_number'],
        ]

    @property
    def domain_object(self):
        if self.domain == Comment.DOMAIN_FILM:
            return self.film
        elif self.domain == Comment.DOMAIN_TOPIC:
            return self.topic
        elif self.domain == Comment.DOMAIN_POLL:
            return self.poll
        raise Exception

    def editable(self):
        return self.domain_object.last_comment_id == self.id

    def save(self, *args, **kwargs):
        """Save comment and update domain object as well"""
        self.content = strip_tags(self.content)
        self.content_html = kt_utils.bbcode_to_html(self.content)
        if 'domain' in kwargs:
            self.serial_number = kwargs['domain'].comment_set.count() + 1
            self.serial_number_by_user = self.created_by.comment_set.count() + 1
            if self.domain == Comment.DOMAIN_FILM:
                try:
                    vote = Vote.objects.get(film=self.film, user=self.created_by)
                    self.rating = vote.rating
                except Vote.DoesNotExist:
                    self.rating = None
        super_kwargs = {key: value for key, value in kwargs.iteritems() if key != 'domain'}
        super(Comment, self).save(*args, **super_kwargs)
        if 'domain' in kwargs:
            kwargs['domain'].number_of_comments = kwargs['domain'].comment_set.count()
            kwargs['domain'].last_comment = kwargs['domain'].comment_set.latest()
            kwargs['domain'].save(update_fields=['number_of_comments', 'last_comment'])
            self.created_by.latest_comments = ','.join([unicode(c.id) for c in self.created_by.comment_set.all().order_by('-created_at', '-id')[:100]])
            self.created_by.number_of_comments = self.created_by.comment_set.count()
            self.created_by.number_of_film_comments = self.created_by.comment_set.filter(domain=Comment.DOMAIN_FILM).count()
            self.created_by.number_of_topic_comments = self.created_by.comment_set.filter(domain=Comment.DOMAIN_TOPIC).count()
            self.created_by.number_of_poll_comments = self.created_by.comment_set.filter(domain=Comment.DOMAIN_POLL).count()
            self.created_by.save(update_fields=[
                'latest_comments', 'number_of_comments',
                'number_of_film_comments', 'number_of_topic_comments', 'number_of_poll_comments',
            ])

    @classmethod
    def fix_comments(cls, domain, domain_object):
        if domain == cls.DOMAIN_FILM:
            domain_id_field = 'film_id'
        elif domain == cls.DOMAIN_TOPIC:
            domain_id_field = 'topic_id'
        elif domain == cls.DOMAIN_POLL:
            domain_id_field = 'poll_id'
        else:
            return
        cursor = connection.cursor()
        cursor.execute('''
            UPDATE ktapp_comment
            SET serial_number = 0
            WHERE
              domain = '{domain}'
              AND {domain_id_field} = {domain_id}
        '''.format(
            domain=domain,
            domain_id_field=domain_id_field,
            domain_id=domain_object.id,
        ))
        cursor.execute('''
            UPDATE
              ktapp_comment c, (
                SELECT
                  c.id, @a:=@a+1 AS serial_number
                FROM
                  ktapp_comment c,
                  (SELECT @a:= 0) AS a
                WHERE
                  domain = '{domain}'
                  AND {domain_id_field} = {domain_id}
                ORDER BY
                  c.created_at, c.id
              ) t
            SET c.serial_number = t.serial_number
            WHERE c.id = t.id
        '''.format(
            domain=domain,
            domain_id_field=domain_id_field,
            domain_id=domain_object.id,
        ))
        domain_object.number_of_comments = domain_object.comment_set.count()
        if domain_object.number_of_comments:
            domain_object.last_comment = domain_object.comment_set.latest()
        else:
            domain_object.last_comment = None
        domain_object.save(update_fields=['number_of_comments', 'last_comment'])


@receiver(post_delete, sender=Comment)
def delete_comment(sender, instance, **kwargs):
    if instance.domain == Comment.DOMAIN_FILM:
        domain = instance.film
        remaining_comments = Comment.objects.filter(domain=instance.domain, film=instance.film)
    elif instance.domain == Comment.DOMAIN_TOPIC:
        domain = instance.topic
        remaining_comments = Comment.objects.filter(domain=instance.domain, topic=instance.topic)
    elif instance.domain == Comment.DOMAIN_POLL:
        domain = instance.poll
        remaining_comments = Comment.objects.filter(domain=instance.domain, poll=instance.poll)
    else:
        return
    for idx, remaining_comment in enumerate(remaining_comments.order_by('created_at', 'id')):
        remaining_comment.serial_number = idx + 1
        remaining_comment.save()
    domain.number_of_comments = domain.comment_set.count()
    if domain.number_of_comments > 0:
        domain.last_comment = domain.comment_set.latest()
    else:
        domain.last_comment = None
    domain.save(update_fields=['number_of_comments', 'last_comment'])
    for idx, remaining_comment in enumerate(Comment.objects.filter(created_by=instance.created_by).order_by('created_at', 'id')):
        remaining_comment.serial_number_by_user = idx + 1
        remaining_comment.save()
    instance.created_by.latest_comments = ','.join([unicode(c.id) for c in instance.created_by.comment_set.all().order_by('-created_at', '-id')[:100]])
    instance.created_by.number_of_comments = instance.created_by.comment_set.count()
    instance.created_by.number_of_film_comments = instance.created_by.comment_set.filter(domain=Comment.DOMAIN_FILM).count()
    instance.created_by.number_of_topic_comments = instance.created_by.comment_set.filter(domain=Comment.DOMAIN_TOPIC).count()
    instance.created_by.number_of_poll_comments = instance.created_by.comment_set.filter(domain=Comment.DOMAIN_POLL).count()
    instance.created_by.save(update_fields=[
        'latest_comments', 'number_of_comments',
        'number_of_film_comments', 'number_of_topic_comments', 'number_of_poll_comments',
    ])


class Topic(models.Model):
    title = models.CharField(max_length=250)
    number_of_comments = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(KTUser, blank=True, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    last_comment = models.ForeignKey(Comment, blank=True, null=True, related_name='last_topic_comment', on_delete=models.SET_NULL)
    slug_cache = models.CharField(max_length=250, blank=True)
    closed_until = models.DateTimeField(blank=True, null=True)
    game_mode = models.BooleanField(default=False)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['-last_comment__id']

    def save(self, *args, **kwargs):
        self.slug_cache = slugify(self.title)
        super(Topic, self).save(*args, **kwargs)


class Poll(models.Model):
    title = models.CharField(max_length=250)
    created_by = models.ForeignKey(KTUser, blank=True, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    nominated_by = models.CharField(max_length=250, blank=True, null=True)
    open_from = models.DateTimeField(blank=True, null=True)
    open_until = models.DateTimeField(blank=True, null=True)
    STATE_WAITING_FOR_APPROVAL = 'W'
    STATE_APPROVED = 'A'
    STATE_OPEN = 'O'
    STATE_CLOSED = 'C'
    STATES = [
        (STATE_WAITING_FOR_APPROVAL, 'Waiting for approval'),
        (STATE_APPROVED, 'Approved'),
        (STATE_OPEN, 'Open'),
        (STATE_CLOSED, 'Closed'),
    ]
    state = models.CharField(max_length=1, choices=STATES, default=STATE_WAITING_FOR_APPROVAL)
    number_of_comments = models.PositiveIntegerField(default=0)
    number_of_votes = models.PositiveIntegerField(default=0)
    number_of_people = models.PositiveIntegerField(default=0)
    slug_cache = models.CharField(max_length=250, blank=True)
    last_comment = models.ForeignKey(Comment, blank=True, null=True, related_name='last_poll_comment', on_delete=models.SET_NULL)

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug_cache = slugify(self.title)
        super(Poll, self).save(*args, **kwargs)

    def pollchoices(self):
        return self.pollchoice_set.all()


class PollChoice(models.Model):
    poll = models.ForeignKey(Poll)
    choice = models.CharField(max_length=250)
    serial_number = models.PositiveSmallIntegerField(default=0)
    number_of_votes = models.PositiveIntegerField(default=0)

    def __unicode__(self):
        return self.choice

    class Meta:
        ordering = ['poll', 'serial_number']


class PollVote(models.Model):
    user = models.ForeignKey(KTUser)
    pollchoice = models.ForeignKey(PollChoice)

    class Meta:
        unique_together = ['user', 'pollchoice']

    def __unicode__(self):
        return u'{}:{}'.format(self.user, self.pollchoice)

    def save(self, *args, **kwargs):
        super(PollVote, self).save(*args, **kwargs)
        self.pollchoice.number_of_votes = self.pollchoice.pollvote_set.count()
        self.pollchoice.save(update_fields=['number_of_votes'])
        self.pollchoice.poll.number_of_votes = sum([pc.number_of_votes for pc in self.pollchoice.poll.pollchoice_set.all()])
        users = set()
        for pc in self.pollchoice.poll.pollchoice_set.all():
            for pv in PollVote.objects.filter(pollchoice=pc):
                users.add(pv.user)
        self.pollchoice.poll.number_of_people = len(users)
        self.pollchoice.poll.save(update_fields=['number_of_votes', 'number_of_people'])


@receiver(post_delete, sender=PollVote)
def delete_pollvote(sender, instance, **kwargs):
    instance.pollchoice.number_of_votes = instance.pollchoice.pollvote_set.count()
    instance.pollchoice.save(update_fields=['number_of_votes'])
    instance.pollchoice.poll.number_of_votes = sum([pc.number_of_votes for pc in instance.pollchoice.poll.pollchoice_set.all()])
    users = set()
    for pc in instance.pollchoice.poll.pollchoice_set.all():
        for pv in PollVote.objects.filter(pollchoice=pc):
            users.add(pv.user)
    instance.pollchoice.poll.number_of_people = len(users)
    instance.pollchoice.poll.save(update_fields=['number_of_votes', 'number_of_people'])


class FilmUserContent(models.Model):
    film = models.ForeignKey(Film)
    created_by = models.ForeignKey(KTUser, blank=True, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField()  # original w bbcode
    content_html = models.TextField()  # autogenerated from content
    content_old_html = models.TextField(blank=True)  # migrated from old db

    class Meta:
        abstract = True
        ordering = ['created_at']
        get_latest_by = 'created_at'


class Quote(FilmUserContent):

    def save(self, *args, **kwargs):
        self.content = strip_tags(self.content)
        self.content_html = kt_utils.bbcode_to_html(self.content)
        super(Quote, self).save(*args, **kwargs)
        self.film.number_of_quotes = self.film.quote_set.count()
        self.film.save(update_fields=['number_of_quotes'])


@receiver(post_delete, sender=Quote)
def delete_quote(sender, instance, **kwargs):
    instance.film.number_of_quotes = instance.film.quote_set.count()
    instance.film.save(update_fields=['number_of_quotes'])


class Trivia(FilmUserContent):
    spoiler = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.content = strip_tags(self.content)
        self.content_html = kt_utils.bbcode_to_html(self.content)
        super(Trivia, self).save(*args, **kwargs)
        self.film.number_of_trivias = self.film.trivia_set.count()
        self.film.save(update_fields=['number_of_trivias'])


@receiver(post_delete, sender=Trivia)
def delete_trivia(sender, instance, **kwargs):
    instance.film.number_of_trivias = instance.film.trivia_set.count()
    instance.film.save(update_fields=['number_of_trivias'])


class Review(FilmUserContent):
    approved = models.BooleanField(default=False)
    snippet = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        self.content = strip_tags(self.content)
        self.content_html = kt_utils.bbcode_to_html(self.content)
        self.snippet = strip_tags(self.content_html)[:500]
        super(Review, self).save(*args, **kwargs)
        self.film.number_of_reviews = self.film.review_set.filter(approved=True).count()
        self.film.save(update_fields=['number_of_reviews'])
        self.created_by.number_of_reviews = Review.objects.filter(created_by=self.created_by, approved=True).count()
        self.created_by.save(update_fields=['number_of_reviews'])

    def __unicode__(self):
        return self.content[:50]


@receiver(post_delete, sender=Review)
def delete_review(sender, instance, **kwargs):
    instance.film.number_of_reviews = instance.film.review_set.filter(approved=True).count()
    instance.film.save(update_fields=['number_of_reviews'])
    instance.created_by.number_of_reviews = Review.objects.filter(created_by=instance.created_by, approved=True).count()
    instance.created_by.save(update_fields=['number_of_reviews'])


class Award(models.Model):
    film = models.ForeignKey(Film)
    artist = models.ForeignKey('Artist', blank=True, null=True)
    name = models.CharField(max_length=250)
    year = models.CharField(max_length=20)
    category = models.CharField(max_length=250)
    note = models.CharField(max_length=250, blank=True)
    created_by = models.ForeignKey(KTUser, blank=True, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super(Award, self).save(*args, **kwargs)
        self.film.number_of_awards = self.film.award_set.count()
        self.film.save(update_fields=['number_of_awards'])

    def __unicode__(self):
        return self.name + ' / ' + self.category


@receiver(post_delete, sender=Award)
def delete_award(sender, instance, **kwargs):
    instance.film.number_of_awards = instance.film.award_set.count()
    instance.film.save(update_fields=['number_of_awards'])


class Link(models.Model):
    name = models.CharField(max_length=250)
    url = models.CharField(max_length=250)
    film = models.ForeignKey(Film, blank=True, null=True, on_delete=models.SET_NULL)
    artist = models.ForeignKey('Artist', blank=True, null=True, on_delete=models.SET_NULL)
    link_domain = models.CharField(max_length=250)
    created_by = models.ForeignKey(KTUser, blank=True, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    LINK_TYPE_OFFICIAL = 'O'
    LINK_TYPE_REVIEWS = 'R'
    LINK_TYPE_INTERVIEWS = 'I'
    LINK_TYPE_OTHER = '-'
    LINK_TYPES = [
        (LINK_TYPE_OFFICIAL, 'Official pages'),
        (LINK_TYPE_REVIEWS, 'Reviews'),
        (LINK_TYPE_INTERVIEWS, 'Interviews'),
        (LINK_TYPE_OTHER, 'Other pages'),
    ]
    link_type = models.CharField(max_length=1, choices=LINK_TYPES, default=LINK_TYPE_OTHER)
    lead = models.TextField(blank=True)
    author = models.ForeignKey(KTUser, blank=True, null=True, on_delete=models.SET_NULL, related_name='authored_link')
    featured = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.link_domain = urlparse(self.url).netloc
        super(Link, self).save(*args, **kwargs)
        if self.film:
            self.film.number_of_links = self.film.link_set.count()
            self.film.save(update_fields=['number_of_links'])
            if self.author:
                self.author.number_of_links = Link.objects.filter(author=self.author).count()
                self.author.save(update_fields=['number_of_links'])

    def __unicode__(self):
        return self.name


@receiver(post_delete, sender=Link)
def delete_link(sender, instance, **kwargs):
    if instance.film:
        instance.film.number_of_links = instance.film.link_set.count()
        instance.film.save(update_fields=['number_of_links'])
        if instance.author:
            instance.author.number_of_links = Link.objects.filter(author=instance.author).count()
            instance.author.save(update_fields=['number_of_links'])


class Artist(models.Model):
    name = models.CharField(max_length=250)
    GENDER_TYPE_MALE = 'M'
    GENDER_TYPE_FEMALE = 'F'
    GENDER_TYPE_UNKNOWN = 'U'
    GENDER_TYPES = [
        (GENDER_TYPE_MALE, 'Male'),
        (GENDER_TYPE_FEMALE, 'Female'),
        (GENDER_TYPE_UNKNOWN, 'Unknown'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_TYPES, default=GENDER_TYPE_UNKNOWN)
    films = models.ManyToManyField(Film, through='FilmArtistRelationship')
    slug_cache = models.CharField(max_length=250, blank=True)
    created_by = models.ForeignKey(KTUser, blank=True, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    number_of_films = models.PositiveIntegerField(default=0)
    number_of_ratings = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(default=0, max_digits=2, decimal_places=1, blank=True, null=True)
    number_of_films_as_actor = models.PositiveIntegerField(default=0)
    number_of_ratings_as_actor = models.PositiveIntegerField(default=0)
    average_rating_as_actor = models.DecimalField(default=0, max_digits=2, decimal_places=1, blank=True, null=True)
    number_of_films_as_director = models.PositiveIntegerField(default=0)
    number_of_ratings_as_director = models.PositiveIntegerField(default=0)
    average_rating_as_director = models.DecimalField(default=0, max_digits=2, decimal_places=1, blank=True, null=True)
    main_picture = models.ForeignKey('Picture', blank=True, null=True, related_name='main_artist_picture', on_delete=models.SET_NULL)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']

    def num_rating(self):
        return sum([f.number_of_ratings for f in self.films.all()])

    def save(self, *args, **kwargs):
        self.slug_cache = slugify(self.name)
        super(Artist, self).save(*args, **kwargs)

    @classmethod
    def get_artist_by_name(cls, name):  # case and more importantly accent sensitive getter
        artist_list = [artist for artist in cls.objects.filter(name=name) if artist.name == name]
        if artist_list:
            return artist_list[0]
        return None

    def calculate_main_picture(self, exclude=None):
        for pic in sorted(self.picture_set.all(), key=lambda pic: (-pic.film.number_of_ratings if pic.film else 0, pic.id)):
            if pic.number_of_artists == 1 and (exclude is None or exclude != pic.id):
                return pic
        return None


class FilmArtistRelationship(models.Model):
    film = models.ForeignKey(Film)
    artist = models.ForeignKey(Artist)
    ROLE_TYPE_DIRECTOR = 'D'
    ROLE_TYPE_ACTOR = 'A'
    ROLE_TYPES = [
        (ROLE_TYPE_DIRECTOR, 'Director'),
        (ROLE_TYPE_ACTOR, 'Actor/actress'),
    ]
    ACTOR_SUBTYPE_FULL = 'F'
    ACTOR_SUBTYPE_VOICE = 'V'
    ACTOR_SUBTYPES = [
        (ACTOR_SUBTYPE_FULL, 'Full'),
        (ACTOR_SUBTYPE_VOICE, 'Voice'),
    ]
    role_type = models.CharField(max_length=1, choices=ROLE_TYPES, default=ROLE_TYPE_DIRECTOR)
    actor_subtype = models.CharField(max_length=1, choices=ACTOR_SUBTYPES, default=ACTOR_SUBTYPE_FULL)
    role_name = models.CharField(max_length=250, blank=True)
    slug_cache = models.CharField(max_length=250, blank=True)
    created_by = models.ForeignKey(KTUser, blank=True, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    main_picture = models.ForeignKey('Picture', blank=True, null=True, related_name='main_role_picture', on_delete=models.SET_NULL)
    is_main_role = models.BooleanField(default=False)

    def __unicode__(self):
        return self.role_type + '[' + self.role_name + ']:' + unicode(self.film) + '/' + unicode(self.artist)

    def save(self, *args, **kwargs):
        self.slug_cache = slugify(self.role_name)
        super(FilmArtistRelationship, self).save(*args, **kwargs)
        ids = []
        slugs = []
        names = []
        for idx, d in enumerate(self.film.directors()[:4]):
            if idx == 3:
                ids.append('')  # indicate that there are more than 3 directors
            else:
                ids.append(unicode(d.id))
                slugs.append(d.slug_cache)
                names.append(d.name)
        if len(ids):
            self.film.directors_cache = ('%s;%s;%s' % (','.join(ids), ','.join(slugs), ','.join(names)))[:250]
            self.film.director_names_cache = ','.join(names)[:250]
        else:
            self.film.directors_cache = ''
            self.film.director_names_cache = ''
        self.film.number_of_actors = FilmArtistRelationship.objects.filter(film_id=self.film, role_type=FilmArtistRelationship.ROLE_TYPE_ACTOR).count()
        self.film.save(update_fields=['directors_cache', 'director_names_cache', 'number_of_actors'])


@receiver(post_delete, sender=FilmArtistRelationship)
def delete_role(sender, instance, **kwargs):
    instance.film.number_of_actors = FilmArtistRelationship.objects.filter(film_id=instance.film, role_type=FilmArtistRelationship.ROLE_TYPE_ACTOR).count()
    instance.film.save(update_fields=['number_of_actors'])


class Biography(models.Model):
    artist = models.ForeignKey(Artist)
    created_by = models.ForeignKey(KTUser, blank=True, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField()  # original w bbcode
    content_html = models.TextField()  # autogenerated from content
    content_old_html = models.TextField(blank=True)  # migrated from old db
    approved = models.BooleanField(default=False)
    snippet = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        self.content = strip_tags(self.content)
        self.content_html = kt_utils.bbcode_to_html(self.content)
        self.snippet = strip_tags(self.content_html)[:500]
        super(Biography, self).save(*args, **kwargs)
        self.created_by.number_of_bios = Biography.objects.filter(created_by=self.created_by, approved=True).count()
        self.created_by.save(update_fields=['number_of_bios'])

    def __unicode__(self):
        return self.content[:50]

    class Meta:
        ordering = ['-created_at']
        get_latest_by = 'created_at'


@receiver(post_delete, sender=Biography)
def delete_biography(sender, instance, **kwargs):
    instance.created_by.number_of_bios = Biography.objects.filter(created_by=instance.created_by, approved=True).count()
    instance.created_by.save(update_fields=['number_of_bios'])


class Keyword(models.Model):
    name = models.CharField(max_length=250)
    KEYWORD_TYPE_COUNTRY = 'C'
    KEYWORD_TYPE_GENRE = 'G'
    KEYWORD_TYPE_MAJOR = 'M'
    KEYWORD_TYPE_OTHER = 'O'
    KEYWORD_TYPES = [
        (KEYWORD_TYPE_COUNTRY, 'Country'),
        (KEYWORD_TYPE_GENRE, 'Genre'),
        (KEYWORD_TYPE_MAJOR, 'Major'),
        (KEYWORD_TYPE_OTHER, 'Other'),
    ]
    keyword_type = models.CharField(max_length=1, choices=KEYWORD_TYPES, default=KEYWORD_TYPE_OTHER)
    films = models.ManyToManyField(Film, through='FilmKeywordRelationship')
    slug_cache = models.CharField(max_length=250, blank=True)
    created_by = models.ForeignKey(KTUser, blank=True, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    old_imdb_name = models.CharField(max_length=250, blank=True)

    def __unicode__(self):
        return self.keyword_type + ':' + self.name

    class Meta:
        ordering = ['keyword_type', 'name']

    def save(self, *args, **kwargs):
        self.slug_cache = slugify(self.name)
        super(Keyword, self).save(*args, **kwargs)

    @classmethod
    def get_keyword_by_name(cls, name, keyword_type):  # case and more importantly accent sensitive getter
        qs = cls.objects.filter(name=name)
        if keyword_type:
            if keyword_type == 'K':
                qs = qs.filter(keyword_type__in=(cls.KEYWORD_TYPE_MAJOR, cls.KEYWORD_TYPE_OTHER))
            else:
                qs = qs.filter(keyword_type=keyword_type)
        keyword_list = [keyword for keyword in qs if keyword.name == name]
        if keyword_list:
            return keyword_list[0]
        return None


class FilmKeywordRelationship(models.Model):
    film = models.ForeignKey(Film)
    keyword = models.ForeignKey(Keyword)
    created_by = models.ForeignKey(KTUser, blank=True, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    spoiler = models.BooleanField(default=False)

    def __unicode__(self):
        return unicode(self.film) + '/' + unicode(self.keyword)

    class Meta:
        unique_together = ['film', 'keyword']


class Sequel(models.Model):
    name = models.CharField(max_length=250)
    SEQUEL_TYPE_SEQUEL = 'S'
    SEQUEL_TYPE_REMAKE = 'R'
    SEQUEL_TYPE_ADAPTATION = 'A'
    SEQUEL_TYPES = [
        (SEQUEL_TYPE_SEQUEL, 'Sequel'),
        (SEQUEL_TYPE_REMAKE, 'Remake'),
        (SEQUEL_TYPE_ADAPTATION, 'Adaptation'),
    ]
    sequel_type = models.CharField(max_length=1, choices=SEQUEL_TYPES, default=SEQUEL_TYPE_SEQUEL)
    films = models.ManyToManyField(Film, through='FilmSequelRelationship')
    slug_cache = models.CharField(max_length=250, blank=True)
    created_by = models.ForeignKey(KTUser, blank=True, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['sequel_type', 'name']

    def all_films(self):
        return self.films.all().order_by('year', 'orig_title', 'id')

    def save(self, *args, **kwargs):
        self.slug_cache = slugify(self.name)
        super(Sequel, self).save(*args, **kwargs)


class FilmSequelRelationship(models.Model):
    film = models.ForeignKey(Film)
    sequel = models.ForeignKey(Sequel)
    serial_number = models.PositiveSmallIntegerField(default=0)  # NOTE: not yet used
    created_by = models.ForeignKey(KTUser, blank=True, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return unicode(self.film) + '/' + unicode(self.sequel)

    class Meta:
        ordering = ['serial_number']


def get_picture_upload_name(instance, filename):
    file_root, file_ext = os.path.splitext(filename)
    random_chunk = ''.join((random.choice(string.ascii_lowercase) for _ in range(8)))
    if instance.film:
        new_file_name = 'p_%s_%s%s' % (unicode(instance.film.id), random_chunk, file_ext)
    elif instance.artist:
        new_file_name = 'pa_%s_%s%s' % (unicode(instance.artist.id), random_chunk, file_ext)
    elif instance.user:
        new_file_name = 'pu_%s_%s%s' % (unicode(instance.user.id), random_chunk, file_ext)
    else:
        new_file_name = 'px_%s%s' % (random_chunk, file_ext)
    hashdir = hashlib.md5(new_file_name).hexdigest()[:3]
    return 'pix/orig/%s/%s' % (hashdir, new_file_name)


class Picture(models.Model):

    img = models.ImageField(upload_to=get_picture_upload_name, height_field='height', width_field='width')
    width = models.PositiveIntegerField(default=0, editable=False)
    height = models.PositiveIntegerField(default=0, editable=False)
    created_by = models.ForeignKey(KTUser, blank=True, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    source_url = models.CharField(max_length=250, blank=True)
    PICTURE_TYPE_POSTER = 'P'
    PICTURE_TYPE_DVD = 'D'
    PICTURE_TYPE_SCREENSHOT = 'S'
    PICTURE_TYPE_OTHER = 'O'
    PICTURE_TYPE_ACTOR_PROFILE = 'A'
    PICTURE_TYPE_USER_PROFILE = 'U'
    PICTURE_TYPES = [
        (PICTURE_TYPE_POSTER, 'Poster'),
        (PICTURE_TYPE_DVD, 'DVD'),
        (PICTURE_TYPE_SCREENSHOT, 'Screenshot'),
        (PICTURE_TYPE_OTHER, 'Other'),
        (PICTURE_TYPE_ACTOR_PROFILE, 'Actor profile'),
        (PICTURE_TYPE_USER_PROFILE, 'User profile'),
    ]
    picture_type = models.CharField(max_length=1, choices=PICTURE_TYPES, default=PICTURE_TYPE_OTHER)
    film = models.ForeignKey(Film, blank=True, null=True, on_delete=models.SET_NULL)
    artists = models.ManyToManyField(Artist, blank=True)
    artist = models.ForeignKey(Artist, blank=True, null=True, on_delete=models.SET_NULL, related_name='actor_profile')
    user = models.ForeignKey(KTUser, blank=True, null=True, on_delete=models.SET_NULL, related_name='user_profile')
    number_of_artists = models.PositiveIntegerField(default=0)

    THUMBNAIL_SIZES = {
        'min': (120, 120),
        'mid': (200, 1000),  # 200 x whatever
        'max': (720, 600),
    }

    @property
    def order_key(self):
        if self.picture_type == self.PICTURE_TYPE_POSTER:
            return 1
        if self.picture_type == self.PICTURE_TYPE_DVD:
            return 2
        return 3

    def get_thumbnail_filename(self, maxwidth, maxheight):
        thumbnail_type = 'tn{w}x{h}'.format(w=maxwidth, h=maxheight)
        path, filename = os.path.split(unicode(self.img))
        file_root, file_ext = os.path.splitext(filename)
        hashdir = path[-3:]
        filedir = settings.MEDIA_ROOT + 'pix/' + thumbnail_type + '/' + hashdir
        filename = filedir + '/' + file_root + '.jpg'
        url = settings.MEDIA_URL + 'pix/' + thumbnail_type + '/' + hashdir + '/' + file_root + '.jpg'
        s3_key = 'pix/' + thumbnail_type + '/' + hashdir + '/' + file_root + '.jpg'
        return filedir, filename, url, s3_key

    def generate_thumbnail(self, maxwidth, maxheight):
        infilename = settings.MEDIA_ROOT + unicode(self.img)
        outfiledir, outfilename, _, _ = self.get_thumbnail_filename(maxwidth, maxheight)
        if not os.path.exists(outfiledir):
            os.makedirs(outfiledir)
        img = Image.open(infilename)
        img.thumbnail((maxwidth, maxheight), Image.ANTIALIAS)
        try:
            img.save(outfilename)
        except IOError:  # cannot write mode P as JPEG
            img.convert('RGB').save(outfilename)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super(Picture, self).save(*args, **kwargs)
        if is_new:
            # upload to s3:
            if not kt_utils.upload_file_to_s3(settings.MEDIA_ROOT + unicode(self.img), unicode(self.img)):
                self.delete()
                raise IOError
            # generate thumbnails and upload to s3:
            for _, (w, h) in self.THUMBNAIL_SIZES.iteritems():
                self.generate_thumbnail(w, h)
                _, outfilename, _, s3_key = self.get_thumbnail_filename(w, h)
                if not kt_utils.upload_file_to_s3(outfilename, s3_key):
                    self.delete()
                    raise IOError
            # delete orig locally:
            try:
                os.remove(settings.MEDIA_ROOT + unicode(self.img))
            except OSError:
                pass
            # delete thumbnails locally:
            for _, (w, h) in self.THUMBNAIL_SIZES.iteritems():
                _, filename, _, _ = self.get_thumbnail_filename(w, h)
                try:
                    os.remove(filename)
                except OSError:
                    pass
        # update number_of_pictures and main_poster for film:
        if self.film:
            self.film.number_of_pictures = self.film.picture_set.count()
            if self.film.main_poster is None and self.picture_type in {self.PICTURE_TYPE_POSTER, self.PICTURE_TYPE_DVD}:
                try:
                    self.film.main_poster = self.film.picture_set.filter(picture_type=self.PICTURE_TYPE_POSTER).order_by('id')[0]
                except IndexError:
                    self.film.main_poster = self.film.picture_set.filter(picture_type=self.PICTURE_TYPE_DVD).order_by('id')[0]
            self.film.save(update_fields=['number_of_pictures', 'main_poster'])

    def crop(self, x, y, w, h):
        orig_name = self.img.name
        orig_width, orig_height = self.width, self.height
        new_name = get_picture_upload_name(self, self.img.name)
        new_local_name = settings.MEDIA_ROOT + new_name
        # download from s3:
        if not kt_utils.download_file_from_s3_with_retry(unicode(self.img), new_local_name):
            raise IOError
        # crop:
        img = Image.open(new_local_name)
        if img.width > img.height:
            zoom = 1.0 * img.width / self.get_width('max')
        else:
            zoom = 1.0 * img.height / self.get_height('max')
        x1, x2 = int(round(zoom * x)), int(round(zoom * (x + w)))
        y1, y2 = int(round(zoom * y)), int(round(zoom * (y + h)))
        img2 = img.crop((x1, y1, x2, y2))
        try:
            img2.save(new_local_name)
        except IOError:  # cannot write mode P as JPEG
            img2.convert('RGB').save(new_local_name)
        self.width = img2.width
        self.height = img2.height
        self.img.name = new_name
        self.save(update_fields=['width', 'height', 'img'])
        # upload to s3:
        if not kt_utils.upload_file_to_s3(settings.MEDIA_ROOT + unicode(self.img), unicode(self.img)):
            # restore original on error:
            self.width = orig_width
            self.height = orig_height
            self.img.name = orig_name
            self.save(update_fields=['width', 'height', 'img'])
            raise IOError
        # generate thumbnails and upload to s3:
        for _, (w, h) in self.THUMBNAIL_SIZES.iteritems():
            self.generate_thumbnail(w, h)
            _, outfilename, _, s3_key = self.get_thumbnail_filename(w, h)
            if not kt_utils.upload_file_to_s3(outfilename, s3_key):
                self.delete()
                raise IOError
        # delete orig locally:
        try:
            os.remove(settings.MEDIA_ROOT + unicode(self.img))
        except OSError:
            pass
        # delete thumbnails locally:
        for _, (w, h) in self.THUMBNAIL_SIZES.iteritems():
            _, filename, _, _ = self.get_thumbnail_filename(w, h)
            try:
                os.remove(filename)
            except OSError:
                pass

    def __unicode__(self):
        return unicode(self.img)

    def get_display_url(self, thumbnail_type):
        if thumbnail_type == 'orig':
            return settings.MEDIA_URL + unicode(self.img)
        _, _, url, _ = self.get_thumbnail_filename(*self.THUMBNAIL_SIZES[thumbnail_type])
        return url

    def get_width(self, thumbnail_type):
        if thumbnail_type == 'orig':
            return self.width
        if self.width * self.THUMBNAIL_SIZES[thumbnail_type][1] > self.height * self.THUMBNAIL_SIZES[thumbnail_type][0]:
            return self.THUMBNAIL_SIZES[thumbnail_type][0]
        else:
            return int(round(1.0 * self.width / self.height * self.THUMBNAIL_SIZES[thumbnail_type][1]))

    def get_height(self, thumbnail_type):
        if thumbnail_type == 'orig':
            return self.height
        if self.width * self.THUMBNAIL_SIZES[thumbnail_type][1] > self.height * self.THUMBNAIL_SIZES[thumbnail_type][0]:
            return int(round(1.0 * self.height / self.width * self.THUMBNAIL_SIZES[thumbnail_type][0]))
        else:
            return self.THUMBNAIL_SIZES[thumbnail_type][1]

    def get_display_urls(self):
        return {
            thumbnail_type: self.get_display_url(thumbnail_type) for thumbnail_type in self.THUMBNAIL_SIZES.keys() + ['orig']
        }

    def get_widths(self):
        return {
            thumbnail_type: self.get_width(thumbnail_type) for thumbnail_type in self.THUMBNAIL_SIZES.keys() + ['orig']
        }

    def get_heights(self):
        return {
            thumbnail_type: self.get_height(thumbnail_type) for thumbnail_type in self.THUMBNAIL_SIZES.keys() + ['orig']
        }

    def get_source_domain(self):
        try:
            return urlparse(self.source_url).netloc
        except:
            return ''

    def get_margin_left(self):
        return int(round((50.0 - 50.0 / self.height * self.width) / 2))

    def get_margin_left_autocomplete(self):
        return int(round((50.0 - 50.0 / self.height * self.width) / 2 * 0.8 - 5))


@receiver(pre_delete, sender=Picture)
def pre_delete_picture(sender, instance, **kwargs):
    '''Update main_poster'''
    if instance.film and instance.film.main_poster == instance:
        try:
            instance.film.main_poster = instance.film.picture_set.filter(picture_type=instance.PICTURE_TYPE_POSTER).exclude(id=instance.id).order_by('id')[0]
        except IndexError:
            try:
                instance.film.main_poster = instance.film.picture_set.filter(picture_type=instance.PICTURE_TYPE_DVD).exclude(id=instance.id).order_by('id')[0]
            except IndexError:
                instance.film.main_poster = None
        instance.film.save(update_fields=['main_poster'])


@receiver(post_delete, sender=Picture)
def delete_picture(sender, instance, **kwargs):
    '''Update number_of_pictures and delete files from s3'''
    if instance.film:
        instance.film.number_of_pictures = instance.film.picture_set.count()
        instance.film.save(update_fields=['number_of_pictures'])
    kt_utils.delete_file_from_s3(unicode(instance.img))
    for _, (w, h) in instance.THUMBNAIL_SIZES.iteritems():
        _, _, _, s3_key = instance.get_thumbnail_filename(w, h)
        kt_utils.delete_file_from_s3(s3_key)


class Message(models.Model):
    sent_by = models.ForeignKey(KTUser, blank=True, null=True, related_name='sent_message', on_delete=models.SET_NULL)
    sent_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField()  # original w bbcode
    content_html = models.TextField()  # autogenerated from content
    content_old_html = models.TextField(blank=True)  # migrated from old db
    owned_by = models.ForeignKey(KTUser, related_name='owned_message', on_delete=models.CASCADE)
    sent_to = models.ManyToManyField(KTUser, blank=True, related_name='received_message')
    private = models.BooleanField(default=True)  # private = only one recipient

    class Meta:
        index_together = [
            ['owned_by', 'sent_at'],
        ]

    def recipients(self):
        return self.sent_to.all().order_by('username', 'id')

    def save(self, *args, **kwargs):
        self.content = strip_tags(self.content)
        self.content_html = kt_utils.bbcode_to_html(self.content)
        super(Message, self).save(*args, **kwargs)

    @classmethod
    def send_message(cls, sent_by, content, recipients):
        if sent_by is None:
            owners = recipients
        else:
            owners = recipients | {sent_by}
        for owner in owners:
            message = Message.objects.create(
                sent_by=sent_by,
                content=content,
                owned_by=owner,
                private=len(recipients)==1,
            )
            for recipient in recipients:
                message.sent_to.add(recipient)
            message.save()
            owner.number_of_messages = Message.objects.filter(owned_by=owner).count()
            owner.save(update_fields=['number_of_messages'])
            for recipient in recipients:
                recipient.number_of_messages = Message.objects.filter(owned_by=recipient).count()
                if recipient.last_message_at is None or recipient.last_message_at < message.sent_at:
                    recipient.last_message_at = message.sent_at
                recipient.save(update_fields=['number_of_messages', 'last_message_at'])
        if sent_by and len(recipients)==1:
            other = list(recipients)[0]
            MessageCountCache.update_cache(owned_by=sent_by, partner=other)
            MessageCountCache.update_cache(owned_by=other, partner=sent_by)


@receiver(post_delete, sender=Message)
def delete_message(sender, instance, **kwargs):
    instance.owned_by.number_of_messages = Message.objects.filter(owned_by=instance.owned_by).count()
    if Message.objects.filter(owned_by=instance.owned_by).exclude(sent_by=instance.owned_by).count() > 0:
        instance.owned_by.last_message_at = Message.objects.filter(owned_by=instance.owned_by).exclude(sent_by=instance.owned_by).latest('sent_at').sent_at
    else:
        instance.owned_by.last_message_at = None
    instance.owned_by.save(update_fields=['number_of_messages', 'last_message_at'])
    # NOTE: recipients are not available here, so MessageCountCache.update_cache lives in view function


class MessageCountCache(models.Model):
    owned_by = models.ForeignKey(KTUser, related_name='owned_message_count', on_delete=models.CASCADE)
    partner = models.ForeignKey(KTUser, related_name='partner_message_count', on_delete=models.CASCADE)
    number_of_messages = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ['owned_by', 'partner']

    @classmethod
    def get_count(cls, owned_by, partner):
        if owned_by == partner:
            return 0
        try:
            return cls.objects.get(owned_by=owned_by, partner=partner).number_of_messages
        except cls.DoesNotExist:
            pass
        return cls.update_cache(owned_by, partner)

    @classmethod
    def update_cache(cls, owned_by, partner):
        if owned_by == partner:
            return 0
        number_of_messages = Message.objects.filter(private=True).filter(owned_by=owned_by).filter(Q(sent_by=partner) | Q(sent_to=partner)).count()
        item, created = cls.objects.get_or_create(owned_by=owned_by, partner=partner)
        item.number_of_messages = number_of_messages
        item.save()
        return number_of_messages


class Wishlist(models.Model):
    film = models.ForeignKey(Film)
    wished_by = models.ForeignKey(KTUser)
    wished_at = models.DateTimeField(auto_now_add=True)
    WISH_TYPE_YES = 'Y'
    WISH_TYPE_NO = 'N'
    WISH_TYPE_GET = 'G'
    WISH_TYPES = [
        (WISH_TYPE_YES, 'Yes'),
        (WISH_TYPE_NO, 'No'),
        (WISH_TYPE_GET, 'Get'),
    ]
    wish_type = models.CharField(max_length=1, choices=WISH_TYPES, default=WISH_TYPE_YES)

    class Meta:
        unique_together = ['film', 'wished_by', 'wish_type']


    def save(self, *args, **kwargs):
        super(Wishlist, self).save(*args, **kwargs)
        if self.wish_type == Wishlist.WISH_TYPE_YES:
            self.wished_by.number_of_wishes_yes = Wishlist.objects.filter(wished_by=self.wished_by, wish_type=Wishlist.WISH_TYPE_YES).count()
            self.wished_by.save(update_fields=['number_of_wishes_yes'])
        elif self.wish_type == Wishlist.WISH_TYPE_NO:
            self.wished_by.number_of_wishes_no = Wishlist.objects.filter(wished_by=self.wished_by, wish_type=Wishlist.WISH_TYPE_NO).count()
            self.wished_by.save(update_fields=['number_of_wishes_no'])
        else:
            self.wished_by.number_of_wishes_get = Wishlist.objects.filter(wished_by=self.wished_by, wish_type=Wishlist.WISH_TYPE_GET).count()
            self.wished_by.save(update_fields=['number_of_wishes_get'])


@receiver(post_delete, sender=Wishlist)
def delete_wish(sender, instance, **kwargs):
    if instance.wish_type == Wishlist.WISH_TYPE_YES:
        instance.wished_by.number_of_wishes_yes = Wishlist.objects.filter(wished_by=instance.wished_by, wish_type=Wishlist.WISH_TYPE_YES).count()
        instance.wished_by.save(update_fields=['number_of_wishes_yes'])
    elif instance.wish_type == Wishlist.WISH_TYPE_NO:
        instance.wished_by.number_of_wishes_no = Wishlist.objects.filter(wished_by=instance.wished_by, wish_type=Wishlist.WISH_TYPE_NO).count()
        instance.wished_by.save(update_fields=['number_of_wishes_no'])
    else:
        instance.wished_by.number_of_wishes_get = Wishlist.objects.filter(wished_by=instance.wished_by, wish_type=Wishlist.WISH_TYPE_GET).count()
        instance.wished_by.save(update_fields=['number_of_wishes_get'])


class TVChannel(models.Model):
    name = models.CharField(max_length=250)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name


class TVFilm(models.Model):
    film = models.ForeignKey(Film)
    channel = models.ForeignKey(TVChannel)
    when = models.DateTimeField()
    created_by = models.ForeignKey(KTUser, blank=True, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)


class UserToplist(models.Model):
    title = models.CharField(max_length=250)
    created_by = models.ForeignKey(KTUser)
    created_at = models.DateTimeField(auto_now_add=True)
    ordered = models.BooleanField(default=True)
    quality = models.BooleanField(default=True)  # if all items have comments, show up more often
    number_of_items = models.PositiveSmallIntegerField()
    TOPLIST_TYPE_FILM = 'F'
    TOPLIST_TYPE_DIRECTOR = 'D'
    TOPLIST_TYPE_ACTOR = 'A'
    TOPLIST_TYPES = [
        (TOPLIST_TYPE_FILM, 'Film'),
        (TOPLIST_TYPE_DIRECTOR, 'Director'),
        (TOPLIST_TYPE_ACTOR, 'Actor'),
    ]
    toplist_type = models.CharField(max_length=1, choices=TOPLIST_TYPES, default=TOPLIST_TYPE_FILM)
    slug_cache = models.CharField(max_length=250, blank=True)

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug_cache = slugify(self.title)
        super(UserToplist, self).save(*args, **kwargs)
        self.created_by.number_of_toplists = UserToplist.objects.filter(created_by=self.created_by).count()
        self.created_by.save(update_fields=['number_of_toplists'])


@receiver(post_delete, sender=UserToplist)
def delete_usertoplist(sender, instance, **kwargs):
    instance.created_by.number_of_toplists = UserToplist.objects.filter(created_by=instance.created_by).count()
    instance.created_by.save(update_fields=['number_of_toplists'])


class UserToplistItem(models.Model):
    usertoplist = models.ForeignKey(UserToplist)
    serial_number = models.PositiveSmallIntegerField(default=0)
    film = models.ForeignKey(Film, blank=True, null=True)
    director = models.ForeignKey(Artist, blank=True, null=True, related_name='director_usertoplist')
    actor = models.ForeignKey(Artist, blank=True, null=True, related_name='actor_usertoplist')
    comment = models.TextField()


class Donation(models.Model):
    given_by = models.ForeignKey(KTUser, blank=True, null=True, on_delete=models.SET_NULL)
    given_at = models.DateTimeField(auto_now_add=True)
    money = models.PositiveIntegerField()
    tshirt = models.BooleanField(default=False)
    comment = models.CharField(max_length=250, blank=True)


class Follow(models.Model):
    who = models.ForeignKey(KTUser, related_name='follows')
    whom = models.ForeignKey(KTUser, related_name='followed_by')
    started_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super(Follow, self).save(*args, **kwargs)
        Recommendation.recalculate_fav_for_user_and_user(self.who, self.whom)


@receiver(post_delete, sender=Follow)
def delete_follow(sender, instance, **kwargs):
    Recommendation.recalculate_fav_for_user_and_user(instance.who, instance.whom)


class PasswordToken(models.Model):
    token = models.CharField(max_length=64, unique=True)
    belongs_to = models.ForeignKey(KTUser)
    valid_until = models.DateTimeField()

    @classmethod
    def get_token(cls, token_value):  # case sensitive getter
        token_list = [token for token in cls.objects.filter(token=token_value) if token.token == token_value]
        if token_list:
            return token_list[0]
        return None


class Change(models.Model):
    created_by = models.ForeignKey(KTUser, blank=True, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=250)
    object = models.CharField(max_length=250)
    state_before = models.TextField(blank=True)
    state_after = models.TextField(blank=True)


class ProfileSegment(models.Model):
    dimension = models.CharField(max_length=250, blank=True, null=True)
    segment = models.PositiveIntegerField()
    effective_number_of_films = models.PositiveIntegerField(default=0)
    ratio_of_films = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ['dimension', 'segment']

    def __unicode__(self):
        return u'%s:%s' % (self.dimension, self.segment)


class UserProfileSegment(models.Model):
    user = models.ForeignKey(KTUser)
    segment = models.ForeignKey(ProfileSegment)
    number_of_votes = models.PositiveIntegerField(default=0)
    relative_number_of_votes = models.PositiveIntegerField(default=0)
    ratio_of_films = models.PositiveIntegerField(default=0)
    score = models.IntegerField(default=0)

    class Meta:
        unique_together = ['user', 'segment']


class SuggestedContent(models.Model):
    created_by = models.ForeignKey(KTUser, blank=True, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    DOMAIN_FILM = 'F'
    DOMAIN_LINK = 'L'
    DOMAINS = [
        (DOMAIN_FILM, 'Film'),
        (DOMAIN_LINK, 'Link'),
    ]
    domain = models.CharField(max_length=1, choices=DOMAINS, default=DOMAIN_FILM)
    content = models.TextField(blank=True)


class OfTheDay(models.Model):
    DOMAIN_FILM = 'F'
    DOMAINS = [
        (DOMAIN_FILM, 'Film'),
    ]
    domain = models.CharField(max_length=1, choices=DOMAINS, default=DOMAIN_FILM)
    day = models.DateField()
    film = models.ForeignKey(Film)
    public = models.BooleanField(default=False)

    class Meta:
        unique_together = ['domain', 'day']


class UserFavourite(models.Model):
    user = models.ForeignKey(KTUser)
    DOMAIN_FILM = 'F'
    DOMAIN_DIRECTOR = 'D'
    DOMAIN_ACTOR = 'A'
    DOMAIN_GENRE = 'G'
    DOMAIN_COUNTRY = 'C'
    DOMAIN_PERIOD = 'P'
    DOMAINS = [
        (DOMAIN_FILM, 'Film'),
        (DOMAIN_DIRECTOR, 'Director'),
        (DOMAIN_ACTOR, 'Actor'),
        (DOMAIN_GENRE, 'Genre'),
        (DOMAIN_COUNTRY, 'Country'),
        (DOMAIN_PERIOD, 'Period'),
    ]
    domain = models.CharField(max_length=1, choices=DOMAINS, default=DOMAIN_FILM)
    fav_id = models.PositiveIntegerField()

    class Meta:
        unique_together = ['user', 'domain', 'fav_id']


class UserUserRating(models.Model):
    user_1 = models.ForeignKey(KTUser, related_name='user_1')
    user_2 = models.ForeignKey(KTUser, related_name='user_2')
    keyword = models.ForeignKey(Keyword, blank=True, null=True)
    last_calculated_at = models.DateTimeField()
    number_of_ratings = models.IntegerField(default=0)
    similarity = models.PositiveSmallIntegerField(blank=True, null=True)
    # TODO: unique index on user_1, user_2, keyword


class FilmFilmRecommendation(models.Model):
    film_1 = models.ForeignKey(Film, related_name='film_1')
    film_2 = models.ForeignKey(Film, related_name='film_2')
    last_calculated_at = models.DateTimeField()
    score = models.IntegerField(default=0)


class EmailCampaign(models.Model):
    title = models.CharField(max_length=250)
    recipients = models.CharField(max_length=250, blank=True, null=True)
    subject = models.CharField(max_length=250)
    html_message = models.TextField(blank=True)
    text_message = models.TextField(blank=True)
    pm_message = models.TextField(blank=True)
    sent_at = models.DateTimeField()


class EmailSend(models.Model):
    user = models.ForeignKey(KTUser, blank=True, null=True, on_delete=models.SET_NULL)
    email_type = models.CharField(max_length=250, blank=True, null=True)
    campaign = models.ForeignKey(EmailCampaign, blank=True, null=True, on_delete=models.SET_NULL)
    email = models.CharField(max_length=250)
    sent_at = models.DateTimeField(auto_now_add=True)
    is_pm = models.BooleanField(default=False)
    is_email = models.BooleanField(default=False)
    is_success = models.BooleanField(default=False)


class EmailBounce(models.Model):
    email = models.CharField(max_length=250)
    bounced_at = models.DateField()


class EmailOpen(models.Model):
    user = models.ForeignKey(KTUser, blank=True, null=True, on_delete=models.SET_NULL)
    email_type = models.CharField(max_length=250, blank=True, null=True)
    campaign = models.ForeignKey(EmailCampaign, blank=True, null=True, on_delete=models.SET_NULL)
    opened_at = models.DateTimeField(auto_now_add=True)


class EmailClick(models.Model):
    user = models.ForeignKey(KTUser, blank=True, null=True, on_delete=models.SET_NULL)
    email_type = models.CharField(max_length=250, blank=True, null=True)
    campaign = models.ForeignKey(EmailCampaign, blank=True, null=True, on_delete=models.SET_NULL)
    clicked_at = models.DateTimeField(auto_now_add=True)
    url = models.CharField(max_length=250)


class EmailUnsubscribe(models.Model):
    user = models.ForeignKey(KTUser, blank=True, null=True, on_delete=models.SET_NULL)
    email_type = models.CharField(max_length=250, blank=True, null=True)
    campaign = models.ForeignKey(EmailCampaign, blank=True, null=True, on_delete=models.SET_NULL)
    unsubscribed_at = models.DateTimeField(auto_now_add=True)


class HourlyActiveUser(models.Model):
    user = models.ForeignKey(KTUser)
    day = models.DateField()
    hour = models.PositiveSmallIntegerField(default=0)
    counter = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ['user', 'day', 'hour']


class DailyActiveUser(models.Model):
    user = models.ForeignKey(KTUser)
    day = models.DateField()
    counter = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ['user', 'day']


class Event(models.Model):
    user = models.ForeignKey(KTUser, blank=True, null=True, on_delete=models.SET_NULL)
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
    film = models.ForeignKey(Film, blank=True, null=True, on_delete=models.SET_NULL)
    topic = models.ForeignKey(Topic, blank=True, null=True, on_delete=models.SET_NULL)
    poll = models.ForeignKey(Poll, blank=True, null=True, on_delete=models.SET_NULL)
    some_id = models.PositiveIntegerField(default=0)
    details = models.CharField(max_length=250, blank=True, null=True)

    def get_details(self):
        if self.details:
            return json.loads(self.details)
        return {}

    def get_comment(self):
        try:
            return Comment.objects.get(id=self.some_id)
        except Comment.DoesNotExist:
            return None


class VapitiVote(models.Model):
    user = models.ForeignKey(KTUser)
    year = models.PositiveIntegerField(default=0, blank=True, null=True)
    vapiti_round = models.PositiveSmallIntegerField(default=0, blank=True, null=True)
    VAPITI_TYPE_GOLD = 'G'
    VAPITI_TYPE_SILVER_MALE = 'M'
    VAPITI_TYPE_SILVER_FEMALE = 'F'
    VAPITI_TYPES = [
        (VAPITI_TYPE_GOLD, 'Gold'),
        (VAPITI_TYPE_SILVER_MALE, 'Silver Male'),
        (VAPITI_TYPE_SILVER_FEMALE, 'Silver Female'),
    ]
    vapiti_type = models.CharField(max_length=1, choices=VAPITI_TYPES, default=VAPITI_TYPE_GOLD)
    serial_number = models.PositiveSmallIntegerField(default=0, blank=True, null=True)
    film = models.ForeignKey(Film)
    artist = models.ForeignKey(Artist, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        unique_together = ['user', 'year', 'vapiti_round', 'vapiti_type', 'serial_number']


class Banner(models.Model):
    published_at = models.DateTimeField(auto_now_add=True)
    where = models.CharField(max_length=32)
    what = models.CharField(max_length=32)
    user = models.ForeignKey(KTUser, blank=True, null=True, on_delete=models.SET_NULL)
    BANNER_STATUS_PUBLISHED = 'P'
    BANNER_STATUS_VIEWED = 'V'
    BANNER_STATUS_CLOSED = 'C'
    BANNER_STATUS_WITHDRAWN = 'W'
    BANNER_STATUSES = [
        (BANNER_STATUS_PUBLISHED, 'Published'),
        (BANNER_STATUS_VIEWED, 'Viewed'),
        (BANNER_STATUS_CLOSED, 'Closed'),
        (BANNER_STATUS_WITHDRAWN, 'Withdrawn'),
    ]
    status = models.CharField(max_length=1, choices=BANNER_STATUSES, default=BANNER_STATUS_PUBLISHED)
    first_viewed_at = models.DateTimeField(blank=True, null=True)
    viewed = models.PositiveSmallIntegerField(default=0)
    closed_at = models.DateTimeField(blank=True, null=True)
    withdrawn_at = models.DateTimeField(blank=True, null=True)


class LinkClick(models.Model):
    url = models.CharField(max_length=250)
    url_domain = models.CharField(max_length=250)
    referer = models.CharField(max_length=250, blank=True)
    user = models.ForeignKey(KTUser, blank=True, null=True, on_delete=models.SET_NULL)
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
    link = models.ForeignKey(Link, blank=True, null=True)
    film = models.ForeignKey(Film, blank=True, null=True)
    artist = models.ForeignKey(Artist, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.url_domain = urlparse(self.url).netloc
        super(LinkClick, self).save(*args, **kwargs)


class ActiveUserCount(models.Model):
    day = models.DateField(primary_key=True)
    dau_count = models.PositiveIntegerField(default=0)
    wau_count = models.PositiveIntegerField(default=0)
    mau_count = models.PositiveIntegerField(default=0)
    new_count = models.PositiveIntegerField(default=0)


class Notification(models.Model):
    target_user = models.ForeignKey(KTUser, related_name='noti_target_user')
    created_at = models.DateTimeField(auto_now_add=True)
    NOTIFICATION_TYPE_COMMENT = 'Co'
    NOTIFICATION_TYPES = [
        (NOTIFICATION_TYPE_COMMENT, 'Comment'),
    ]
    notification_type = models.CharField(max_length=2, choices=NOTIFICATION_TYPES, default=NOTIFICATION_TYPE_COMMENT)
    NOTIFICATION_SUBTYPE_COMMENT_REPLY = 'CoRe'
    NOTIFICATION_SUBTYPE_COMMENT_MENTION = 'CoMe'
    NOTIFICATION_SUBTYPE_COMMENT_ON_FILM_YOU_RATED = 'CoRa'
    NOTIFICATION_SUBTYPE_COMMENT_ON_FILM_YOU_COMMENTED = 'CoCo'
    NOTIFICATION_SUBTYPE_COMMENT_ON_FILM_YOU_WISHED = 'CoWi'
    NOTIFICATION_SUBTYPES = [
        (NOTIFICATION_SUBTYPE_COMMENT_REPLY, 'Comment reply'),
        (NOTIFICATION_SUBTYPE_COMMENT_MENTION, 'Comment mention'),
        (NOTIFICATION_SUBTYPE_COMMENT_ON_FILM_YOU_RATED, 'Comment on film you rated'),
        (NOTIFICATION_SUBTYPE_COMMENT_ON_FILM_YOU_COMMENTED, 'Comment on film you commented'),
        (NOTIFICATION_SUBTYPE_COMMENT_ON_FILM_YOU_WISHED, 'Comment on film you wished'),
    ]
    notification_subtype = models.CharField(max_length=4, choices=NOTIFICATION_SUBTYPES, blank=True)
    film = models.ForeignKey(Film, blank=True, null=True, on_delete=models.SET_NULL)
    topic = models.ForeignKey(Topic, blank=True, null=True, on_delete=models.SET_NULL)
    poll = models.ForeignKey(Poll, blank=True, null=True, on_delete=models.SET_NULL)
    source_user = models.ForeignKey(KTUser, blank=True, null=True, on_delete=models.SET_NULL, related_name='noti_source_user')
    is_read = models.BooleanField(default=False)
    comment = models.ForeignKey(Comment, blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        index_together = [
            ['target_user', 'created_at'],
        ]

    def save(self, *args, **kwargs):
        super(Notification, self).save(*args, **kwargs)
        self.target_user.unread_notification_count = Notification.objects.filter(target_user=self.target_user, is_read=False).count()
        self.target_user.save(update_fields=['unread_notification_count'])

    @property
    def url(self):
        if self.notification_type == 'Co':
            if self.film:
                return reverse('film_comments', args=(self.film.id, self.film.slug_cache))
            if self.topic:
                return reverse('forum', args=(self.topic.id, self.topic.slug_cache))
            if self.poll:
                return reverse('poll', args=(self.poll.id, self.poll.slug_cache))
        return None


@receiver(post_delete, sender=Notification)
def delete_notification(sender, instance, **kwargs):
    instance.target_user.unread_notification_count = Notification.objects.filter(target_user=instance.target_user, is_read=False).count()
    instance.target_user.save(update_fields=['unread_notification_count'])


class UserContribution(KTUser):
    count_film = models.PositiveIntegerField(default=0)
    rank_film = models.PositiveIntegerField(default=0)
    count_role = models.PositiveIntegerField(default=0)
    rank_role = models.PositiveIntegerField(default=0)
    count_keyword = models.PositiveIntegerField(default=0)
    rank_keyword = models.PositiveIntegerField(default=0)
    count_picture = models.PositiveIntegerField(default=0)
    rank_picture = models.PositiveIntegerField(default=0)
    count_trivia = models.PositiveIntegerField(default=0)
    rank_trivia = models.PositiveIntegerField(default=0)
    count_quote = models.PositiveIntegerField(default=0)
    rank_quote = models.PositiveIntegerField(default=0)
    count_review = models.PositiveIntegerField(default=0)
    rank_review = models.PositiveIntegerField(default=0)
    count_link = models.PositiveIntegerField(default=0)
    rank_link = models.PositiveIntegerField(default=0)
    count_biography = models.PositiveIntegerField(default=0)
    rank_biography = models.PositiveIntegerField(default=0)
    count_poll = models.PositiveIntegerField(default=0)
    rank_poll = models.PositiveIntegerField(default=0)
    count_usertoplist = models.PositiveIntegerField(default=0)
    rank_usertoplist = models.PositiveIntegerField(default=0)
