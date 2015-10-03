import hashlib
import os
import random
import string
from PIL import Image
from urlparse import urlparse

from django.db import models, connection
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.core.mail import send_mail
from django.db.models import Q
from django.db.models.signals import post_delete
from django.dispatch.dispatcher import receiver
from django.template.defaultfilters import slugify
from django.utils.html import strip_tags

from kt import settings
from ktapp import utils as kt_utils


class KTUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=64, unique=True)
    email = models.EmailField(blank=True, unique=True)
    is_staff = models.BooleanField(default=False)  # admin
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
    email_notification = models.BooleanField(default=True)
    facebook_rating_share = models.BooleanField(default=True)
    added_role = models.PositiveIntegerField(default=0)
    added_artist = models.PositiveIntegerField(default=0)
    added_film = models.PositiveIntegerField(default=0)
    added_tvfilm = models.PositiveIntegerField(default=0)
    added_trivia = models.PositiveIntegerField(default=0)
    REASON_BANNED = 'B'
    REASON_QUIT = 'Q'
    REASON_UNKNOWN = 'U'
    REASONS = [
        (REASON_BANNED, 'Banned'),
        (REASON_QUIT, 'Quit'),
        (REASON_UNKNOWN, 'Unknown'),
    ]
    reason_of_inactivity = models.CharField(max_length=1, choices=REASONS, default=REASON_UNKNOWN)
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
    is_reliable = models.BooleanField(default=False)

    objects = UserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    def email_user(self, subject, message, from_email=settings.DEFAULT_FROM_EMAIL, **kwargs):
        if settings.LOCAL_MAIL:
            print '[SUBJECT] %s' % subject
            print '[FROM] %s' % from_email
            print '[TO] %s' % self.email
            print '[BODY]'
            print message
            print '[/BODY]'
        else:
            send_mail(subject, message, from_email, [self.email], **kwargs)

    def votes(self):
        return self.vote_set.all()

    def get_follows(self):
        return self.follow.all()

    def get_followed_by(self):
        return [u.who for u in self.followed_by.all().select_related('who')]

    def save(self, *args, **kwargs):
        self.slug_cache = slugify(self.username)
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
        for g in self.genres():
            if g.id == 314:
                self.genre_cache_is_music_video = True
            if g.id == 4150:
                self.genre_cache_is_mini = True
            if g.id == 120:
                self.genre_cache_is_short = True
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
        self.user.save()
        Recommendation.recalculate_fav_for_users_and_film(self.user.get_followed_by(), self.film)


@receiver(post_delete, sender=Vote)
def delete_vote(sender, instance, **kwargs):
    try:
        instance.film.comment_set.filter(created_by=instance.user).update(rating=None)
    except Film.DoesNotExist:
        pass
    instance.user.latest_votes = ','.join([unicode(v.id) for v in instance.user.vote_set.all().order_by('-when', '-id')[:100]])
    instance.user.number_of_ratings = instance.user.vote_set.count()
    instance.user.save()
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

    def __unicode__(self):
        return self.content[:100]

    class Meta:
        ordering = ['-created_at']
        get_latest_by = 'created_at'
        index_together = [
            ['created_at'],
            ['domain', 'created_at'],
            ['created_by', 'serial_number_by_user', 'created_at'],
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
            kwargs['domain'].save()
            self.created_by.latest_comments = ','.join([unicode(c.id) for c in self.created_by.comment_set.all().order_by('-created_at', '-id')[:100]])
            self.created_by.number_of_comments = self.created_by.comment_set.count()
            self.created_by.save()

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
        domain_object.save()


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
    domain.save()
    for idx, remaining_comment in enumerate(Comment.objects.filter(created_by=instance.created_by).order_by('created_at', 'id')):
        remaining_comment.serial_number_by_user = idx + 1
        remaining_comment.save()
    instance.created_by.latest_comments = ','.join([unicode(c.id) for c in instance.created_by.comment_set.all().order_by('-created_at', '-id')[:100]])
    instance.created_by.number_of_comments = instance.created_by.comment_set.count()
    instance.created_by.save()


class Topic(models.Model):
    title = models.CharField(max_length=250)
    number_of_comments = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(KTUser, blank=True, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    last_comment = models.ForeignKey(Comment, blank=True, null=True, related_name='last_topic_comment', on_delete=models.SET_NULL)
    slug_cache = models.CharField(max_length=250, blank=True)
    closed_until = models.DateTimeField(blank=True, null=True)

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
        self.pollchoice.save()
        self.pollchoice.poll.number_of_votes = sum([pc.number_of_votes for pc in self.pollchoice.poll.pollchoice_set.all()])
        users = set()
        for pc in self.pollchoice.poll.pollchoice_set.all():
            for pv in PollVote.objects.filter(pollchoice=pc):
                users.add(pv.user)
        self.pollchoice.poll.number_of_people = len(users)
        self.pollchoice.poll.save()


@receiver(post_delete, sender=PollVote)
def delete_pollvote(sender, instance, **kwargs):
    instance.pollchoice.number_of_votes = instance.pollchoice.pollvote_set.count()
    instance.pollchoice.save()
    instance.pollchoice.poll.number_of_votes = sum([pc.number_of_votes for pc in instance.pollchoice.poll.pollchoice_set.all()])
    users = set()
    for pc in instance.pollchoice.poll.pollchoice_set.all():
        for pv in PollVote.objects.filter(pollchoice=pc):
            users.add(pv.user)
    instance.pollchoice.poll.number_of_people = len(users)
    instance.pollchoice.poll.save()


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
        self.film.save()


@receiver(post_delete, sender=Quote)
def delete_quote(sender, instance, **kwargs):
    instance.film.number_of_quotes = instance.film.quote_set.count()
    instance.film.save()


class Trivia(FilmUserContent):
    spoiler = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.content = strip_tags(self.content)
        self.content_html = kt_utils.bbcode_to_html(self.content)
        super(Trivia, self).save(*args, **kwargs)
        self.film.number_of_trivias = self.film.trivia_set.count()
        self.film.save()


@receiver(post_delete, sender=Trivia)
def delete_trivia(sender, instance, **kwargs):
    instance.film.number_of_trivias = instance.film.trivia_set.count()
    instance.film.save()


class Review(FilmUserContent):
    approved = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.content = strip_tags(self.content)
        self.content_html = kt_utils.bbcode_to_html(self.content)
        super(Review, self).save(*args, **kwargs)
        self.film.number_of_reviews = self.film.review_set.filter(approved=True).count()
        self.film.save()

    def __unicode__(self):
        return self.content[:50]


@receiver(post_delete, sender=Review)
def delete_review(sender, instance, **kwargs):
    instance.film.number_of_reviews = instance.film.review_set.filter(approved=True).count()
    instance.film.save()


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
        self.film.save()

    def __unicode__(self):
        return self.name + ' / ' + self.category


@receiver(post_delete, sender=Award)
def delete_award(sender, instance, **kwargs):
    instance.film.number_of_awards = instance.film.award_set.count()
    instance.film.save()


class LinkSite(models.Model):
    name = models.CharField(max_length=250)
    url = models.CharField(max_length=250)

    def __unicode__(self):
        return self.name


class Link(models.Model):
    name = models.CharField(max_length=250)
    url = models.CharField(max_length=250)
    film = models.ForeignKey(Film)
    linksite = models.ForeignKey(LinkSite, blank=True, null=True, on_delete=models.SET_NULL)
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

    def save(self, *args, **kwargs):
        self.link_domain = urlparse(self.url).netloc
        super(Link, self).save(*args, **kwargs)
        self.film.number_of_links = self.film.link_set.count()
        self.film.save()

    def __unicode__(self):
        return self.name


@receiver(post_delete, sender=Link)
def delete_link(sender, instance, **kwargs):
    instance.film.number_of_links = instance.film.link_set.count()
    instance.film.save()


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
        self.film.save()


class Biography(models.Model):
    artist = models.ForeignKey(Artist)
    created_by = models.ForeignKey(KTUser, blank=True, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField()  # original w bbcode
    content_html = models.TextField()  # autogenerated from content
    content_old_html = models.TextField(blank=True)  # migrated from old db
    approved = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.content = strip_tags(self.content)
        self.content_html = kt_utils.bbcode_to_html(self.content)
        super(Biography, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.content[:50]

    class Meta:
        ordering = ['-created_at']
        get_latest_by = 'created_at'


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
    new_file_name = 'p_%s_%s%s' % (unicode(instance.film.id), random_chunk, file_ext)
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
    PICTURE_TYPES = [
        (PICTURE_TYPE_POSTER, 'Poster'),
        (PICTURE_TYPE_DVD, 'DVD'),
        (PICTURE_TYPE_SCREENSHOT, 'Screenshot'),
        (PICTURE_TYPE_OTHER, 'Other'),
    ]
    picture_type = models.CharField(max_length=1, choices=PICTURE_TYPES, default=PICTURE_TYPE_OTHER)
    film = models.ForeignKey(Film)
    artists = models.ManyToManyField(Artist, blank=True)

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
        return filedir, filename, url

    def generate_thumbnail(self, maxwidth, maxheight):
        infilename = settings.MEDIA_ROOT + unicode(self.img)
        outfiledir, outfilename, _ = self.get_thumbnail_filename(maxwidth, maxheight)
        if not os.path.exists(outfiledir):
            os.makedirs(outfiledir)
        img = Image.open(infilename)
        img.thumbnail((maxwidth, maxheight), Image.ANTIALIAS)
        img.save(outfilename)

    def save(self, *args, **kwargs):
        super(Picture, self).save(*args, **kwargs)
        self.film.number_of_pictures = self.film.picture_set.count()
        if self.picture_type in {self.PICTURE_TYPE_POSTER, self.PICTURE_TYPE_DVD}:
            try:
                self.film.main_poster = self.film.picture_set.filter(picture_type=self.PICTURE_TYPE_POSTER).order_by('id')[0]
            except IndexError:
                self.film.main_poster = self.film.picture_set.filter(picture_type=self.PICTURE_TYPE_DVD).order_by('id')[0]
        self.film.save()
        for _, (w, h) in self.THUMBNAIL_SIZES.iteritems():
            self.generate_thumbnail(w, h)

    def __unicode__(self):
        return unicode(self.img)

    def get_display_url(self, thumbnail_type):
        if thumbnail_type == 'orig':
            return settings.MEDIA_URL + unicode(self.img)
        _, _, url = self.get_thumbnail_filename(*self.THUMBNAIL_SIZES[thumbnail_type])
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


@receiver(post_delete, sender=Picture)
def delete_picture(sender, instance, **kwargs):
    '''Update number_of_pictures and delete files'''
    instance.film.number_of_pictures = instance.film.picture_set.count()
    if instance.picture_type in {instance.PICTURE_TYPE_POSTER, instance.PICTURE_TYPE_DVD}:
        try:
            instance.film.main_poster = instance.film.picture_set.filter(picture_type=instance.PICTURE_TYPE_POSTER).order_by('id')[0]
        except IndexError:
            try:
                instance.film.main_poster = instance.film.picture_set.filter(picture_type=instance.PICTURE_TYPE_DVD).order_by('id')[0]
            except IndexError:
                instance.film.main_poster = None
    instance.film.save()
    try:
        os.remove(settings.MEDIA_ROOT + unicode(instance.img))
    except OSError:
        pass
    for _, (w, h) in instance.THUMBNAIL_SIZES.iteritems():
        _, filename, _ = instance.get_thumbnail_filename(w, h)
        try:
            os.remove(filename)
        except OSError:
            pass


class Message(models.Model):
    sent_by = models.ForeignKey(KTUser, blank=True, null=True, related_name='sent_message', on_delete=models.SET_NULL)
    sent_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField()  # original w bbcode
    content_html = models.TextField()  # autogenerated from content
    content_old_html = models.TextField(blank=True)  # migrated from old db
    owned_by = models.ForeignKey(KTUser, related_name='owned_message', on_delete=models.CASCADE)
    sent_to = models.ManyToManyField(KTUser, blank=True, null=True, related_name='received_message')
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
            owner.save()
            for recipient in recipients:
                recipient.number_of_messages = Message.objects.filter(owned_by=recipient).count()
                if recipient.last_message_at is None or recipient.last_message_at < message.sent_at:
                    recipient.last_message_at = message.sent_at
                recipient.save()
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
    instance.owned_by.save()
    # recipients are not available here, so MessageCountCache.update_cache lives in view function


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
        elif self.wish_type == Wishlist.WISH_TYPE_NO:
            self.wished_by.number_of_wishes_no = Wishlist.objects.filter(wished_by=self.wished_by, wish_type=Wishlist.WISH_TYPE_NO).count()
        else:
            self.wished_by.number_of_wishes_get = Wishlist.objects.filter(wished_by=self.wished_by, wish_type=Wishlist.WISH_TYPE_GET).count()
        self.wished_by.save()


@receiver(post_delete, sender=Wishlist)
def delete_wish(sender, instance, **kwargs):
    if instance.wish_type == Wishlist.WISH_TYPE_YES:
        instance.wished_by.number_of_wishes_yes = Wishlist.objects.filter(wished_by=instance.wished_by, wish_type=Wishlist.WISH_TYPE_YES).count()
    elif instance.wish_type == Wishlist.WISH_TYPE_NO:
        instance.wished_by.number_of_wishes_no = Wishlist.objects.filter(wished_by=instance.wished_by, wish_type=Wishlist.WISH_TYPE_NO).count()
    else:
        instance.wished_by.number_of_wishes_get = Wishlist.objects.filter(wished_by=instance.wished_by, wish_type=Wishlist.WISH_TYPE_GET).count()
    instance.wished_by.save()


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
        self.created_by.save()


@receiver(post_delete, sender=UserToplist)
def delete_usertoplist(sender, instance, **kwargs):
    instance.created_by.number_of_toplists = UserToplist.objects.filter(created_by=instance.created_by).count()
    instance.created_by.save()


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
    DOMAINS = [
        (DOMAIN_FILM, 'Film'),
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

    class Meta:
        unique_together = ['domain', 'day']
