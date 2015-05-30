import os
import random
import string
from datetime import datetime
from PIL import Image

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.core.mail import send_mail
from django.db.models.signals import post_delete
from django.dispatch.dispatcher import receiver
from django.template.defaultfilters import slugify

from kt import settings


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
    public_gender = models.BooleanField(default=False)
    public_location = models.BooleanField(default=False)
    public_year_of_birth = models.BooleanField(default=False)

    objects = UserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def votes(self):
        return self.vote_set.all()


class Film(models.Model):
    orig_title = models.CharField(max_length=250)
    other_titles = models.TextField(blank=True)
    year = models.PositiveIntegerField(default=0)
    plot_summary = models.TextField(blank=True)
    number_of_comments = models.PositiveIntegerField(default=0)
    last_comment = models.ForeignKey('Comment', blank=True, null=True, related_name='last_film_comment', on_delete=models.SET_NULL)
    artists = models.ManyToManyField('Artist', through='FilmArtistRelationship')
    number_of_ratings_1 = models.PositiveIntegerField(default=0)
    number_of_ratings_2 = models.PositiveIntegerField(default=0)
    number_of_ratings_3 = models.PositiveIntegerField(default=0)
    number_of_ratings_4 = models.PositiveIntegerField(default=0)
    number_of_ratings_5 = models.PositiveIntegerField(default=0)
    number_of_quotes = models.PositiveIntegerField(default=0)
    number_of_trivias = models.PositiveIntegerField(default=0)
    number_of_reviews = models.PositiveIntegerField(default=0)
    keywords = models.ManyToManyField('Keyword', through='FilmKeywordRelationship')
    number_of_keywords = models.PositiveIntegerField(default=0)
    imdb_link = models.CharField(max_length=16, blank=True)
    porthu_link = models.CharField(max_length=16, blank=True)
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

    def __unicode__(self):
        return self.orig_title + ' [' + unicode(self.year) + ']'

    @property
    def film_slug(self):
        if self.other_titles:
            return slugify(self.orig_title) + '-' + slugify(self.other_titles) + '-' + slugify(self.year)
        else:
            return slugify(self.orig_title) + '-' + slugify(self.year)

    def num_specific_rating(self, r):
        if 1 <= r <= 5:
            return getattr(self, 'number_of_ratings_' + str(r))

    def num_rating(self):
        return (self.number_of_ratings_1 +
                self.number_of_ratings_2 +
                self.number_of_ratings_3 +
                self.number_of_ratings_4 +
                self.number_of_ratings_5)
    num_rating.short_description = 'Number of ratings'

    def avg_rating(self):
        if self.num_rating() == 0:
            return None
        return (1.0 * self.number_of_ratings_1 +
                2.0 * self.number_of_ratings_2 +
                3.0 * self.number_of_ratings_3 +
                4.0 * self.number_of_ratings_4 +
                5.0 * self.number_of_ratings_5) / self.num_rating()
    avg_rating.short_description = 'Average rating'

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


class PremierType(models.Model):
    name = models.CharField(max_length=250)

    def __unicode__(self):
        return self.name


class Premier(models.Model):
    film = models.ForeignKey(Film)
    when = models.DateField()
    when_year = models.PositiveIntegerField(blank=True, null=True)
    premier_type = models.ForeignKey(PremierType, blank=True, null=True)

    def __unicode__(self):
        return self.film.orig_title + ': ' + unicode(self.when) + ' [' + unicode(self.premier_type) + ']'

    class Meta:
        ordering = ['when', 'premier_type', 'film']


class Vote(models.Model):
    film = models.ForeignKey(Film)
    user = models.ForeignKey(KTUser)
    rating = models.PositiveSmallIntegerField()
    when = models.DateTimeField(auto_now=True, auto_now_add=True, null=True)

    def __unicode__(self):
        return self.film.orig_title + ' + ' + self.user.username + ' = ' + unicode(self.rating)

    class Meta:
        unique_together = ['film', 'user']

    def save(self, *args, **kwargs):
        super(Vote, self).save(*args, **kwargs)
        self.film.comment_set.filter(created_by=self.user).update(rating=self.rating)


@receiver(post_delete, sender=Vote)
def delete_vote(sender, instance, **kwargs):
    try:
        instance.film.comment_set.filter(created_by=instance.user).update(rating=None)
    except Film.DoesNotExist:
        pass


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
    created_by = models.ForeignKey(KTUser)
    created_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    reply_to = models.ForeignKey('self', blank=True, null=True, on_delete=models.SET_NULL)
    rating = models.PositiveSmallIntegerField(blank=True, null=True)  # cache for film comments

    def __unicode__(self):
        return self.content[:100]

    class Meta:
        ordering = ['-created_at']
        get_latest_by = 'created_at'

    def save(self, *args, **kwargs):
        """Save comment and update domain object as well"""
        super_kwargs = {key: value for key, value in kwargs.iteritems() if key != 'domain'}
        super(Comment, self).save(*args, **super_kwargs)
        kwargs['domain'].number_of_comments = kwargs['domain'].comment_set.count()
        kwargs['domain'].last_comment = kwargs['domain'].comment_set.latest()
        kwargs['domain'].save()


@receiver(post_delete, sender=Comment)
def delete_comment(sender, instance, **kwargs):
    if instance.domain == Comment.DOMAIN_FILM:
        domain = instance.film
    elif instance.domain == Comment.DOMAIN_TOPIC:
        domain = instance.topic
    elif instance.domain == Comment.DOMAIN_POLL:
        domain = instance.poll
    else:
        return
    domain.number_of_comments = domain.comment_set.count()
    if domain.number_of_comments > 0:
        domain.last_comment = domain.comment_set.latest()
    else:
        domain.last_comment = None
    domain.save()


class Topic(models.Model):
    title = models.CharField(max_length=250)
    number_of_comments = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(KTUser)
    created_at = models.DateTimeField(auto_now_add=True)
    last_comment = models.ForeignKey(Comment, blank=True, null=True, related_name='last_topic_comment', on_delete=models.SET_NULL)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['-last_comment']


class Poll(models.Model):
    title = models.CharField(max_length=250)
    created_by = models.ForeignKey(KTUser, blank=True, null=True)
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

    def __unicode__(self):
        return self.title


class PollChoice(models.Model):
    poll = models.ForeignKey(Poll)
    choice = models.CharField(max_length=250)
    serial_number = models.PositiveSmallIntegerField(default=0)  # TODO: auto number and renumber, when necessary
    number_of_votes = models.PositiveIntegerField(default=0)

    def __unicode__(self):
        return self.choice

    class Meta:
        ordering = ['poll', 'serial_number']


class PollVote(models.Model):
    user = models.ForeignKey(KTUser, blank=True, null=True)
    pollchoice = models.ForeignKey(PollChoice)

    class Meta:
        unique_together = ['user', 'pollchoice']

    def __unicode__(self):
        return u'{}:{}'.format(self.user, self.pollchoice)

    def save(self, *args, **kwargs):
        super(PollVote, self).save(*args, **kwargs)
        self.pollchoice.number_of_votes = self.pollchoice.pollvote_set.count()
        self.pollchoice.save()


class FilmUserContent(models.Model):
    film = models.ForeignKey(Film, blank=True, null=True)
    created_by = models.ForeignKey(KTUser, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']
        get_latest_by = 'created_at'


class Quote(FilmUserContent):
    content = models.TextField()  # original w bbcode
    content_html = models.TextField()  # autogenerated from content
    content_old_html = models.TextField(blank=True)  # migrated from old db

    def save(self, *args, **kwargs):
        super(Quote, self).save(*args, **kwargs)
        self.film.number_of_quotes = self.film.quote_set.count()
        self.film.save()


@receiver(post_delete, sender=Quote)
def delete_quote(sender, instance, **kwargs):
    instance.film.number_of_quotes = instance.film.quote_set.count()
    instance.film.save()


class Trivia(FilmUserContent):
    content = models.TextField()  # original w bbcode
    content_html = models.TextField()  # autogenerated from content
    content_old_html = models.TextField(blank=True)  # migrated from old db

    def save(self, *args, **kwargs):
        super(Trivia, self).save(*args, **kwargs)
        self.film.number_of_trivias = self.film.trivia_set.count()
        self.film.save()


@receiver(post_delete, sender=Trivia)
def delete_trivia(sender, instance, **kwargs):
    instance.film.number_of_trivias = instance.film.trivia_set.count()
    instance.film.save()


class Review(FilmUserContent):
    content = models.TextField()  # original w bbcode
    content_html = models.TextField()  # autogenerated from content
    content_old_html = models.TextField(blank=True)  # migrated from old db
    approved = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        super(Review, self).save(*args, **kwargs)
        self.film.number_of_reviews = self.film.review_set.count()
        self.film.save()

    def __unicode__(self):
        return self.content[:50]


@receiver(post_delete, sender=Review)
def delete_review(sender, instance, **kwargs):
    instance.film.number_of_reviews = instance.film.review_set.count()
    instance.film.save()


class Award(models.Model):
    film = models.ForeignKey(Film)
    artist = models.ForeignKey('Artist', blank=True, null=True)
    name = models.CharField(max_length=250)
    year = models.CharField(max_length=20)
    category = models.CharField(max_length=250)
    note = models.CharField(max_length=250, blank=True)

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
    linksite = models.ForeignKey(LinkSite, blank=True, null=True)
    created_by = models.ForeignKey(KTUser)
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

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']


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
    ACTOR_SUBTYPE_DUB = 'D'
    ACTOR_SUBTYPES = [
        (ACTOR_SUBTYPE_FULL, 'Full'),
        (ACTOR_SUBTYPE_VOICE, 'Voice'),
        (ACTOR_SUBTYPE_DUB, 'Dub'),
    ]
    role_type = models.CharField(max_length=1, choices=ROLE_TYPES, default=ROLE_TYPE_DIRECTOR)
    actor_subtype = models.CharField(max_length=1, choices=ACTOR_SUBTYPES, default=ACTOR_SUBTYPE_FULL)
    role_name = models.CharField(max_length=250, blank=True)

    def __unicode__(self):
        return self.role_type + '[' + self.role_name + ']:' + unicode(self.film) + '/' + unicode(self.artist)


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

    def __unicode__(self):
        return self.keyword_type + ':' + self.name

    class Meta:
        ordering = ['keyword_type', 'name']


class FilmKeywordRelationship(models.Model):
    film = models.ForeignKey(Film)
    keyword = models.ForeignKey(Keyword)

    def __unicode__(self):
        return unicode(self.film) + '/' + unicode(self.keyword)

    class Meta:
        unique_together = ['film', 'keyword']

    def save(self, *args, **kwargs):
        super(FilmKeywordRelationship, self).save(*args, **kwargs)
        self.film.number_of_keywords = self.film.keyword_set.count()
        self.film.save()


@receiver(post_delete, sender=FilmKeywordRelationship)
def delete_filmkeyword(sender, instance, **kwargs):
    instance.film.number_of_keywords = instance.film.keyword_set.count()
    instance.film.save()


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

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['sequel_type', 'name']

    def all_films(self):
        return self.films.all()


class FilmSequelRelationship(models.Model):
    film = models.ForeignKey(Film)
    sequel = models.ForeignKey(Sequel)
    serial_number = models.PositiveSmallIntegerField(default=0)  # TODO: auto number and renumber, when necessary

    def __unicode__(self):
        return unicode(self.film) + '/' + unicode(self.sequel)

    class Meta:
        ordering = ['serial_number']


def get_picture_upload_name(instance, filename):
    file_root, file_ext = os.path.splitext(filename)
    yearmonth = datetime.now().strftime('%Y%m')
    random_chunk = ''.join((random.choice(string.ascii_lowercase) for _ in range(8)))
    return ''.join(['pix/orig/', yearmonth,
                    '/p_', unicode(instance.film.id), '_', random_chunk, file_ext])


class Picture(models.Model):

    img = models.ImageField(upload_to=get_picture_upload_name, height_field='height', width_field='width')
    width = models.PositiveIntegerField(default=0, editable=False)
    height = models.PositiveIntegerField(default=0, editable=False)
    created_by = models.ForeignKey(KTUser)
    created_at = models.DateTimeField(auto_now_add=True)
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
        'mid': (720, 480),
    }

    def get_thumbnail_filename(self, thumbnail_type):
        path, filename = os.path.split(unicode(self.img))
        file_root, file_ext = os.path.splitext(filename)
        yearmonth = path[-6:]
        filedir = settings.MEDIA_ROOT + 'pix/' + thumbnail_type + '/' + yearmonth
        filename = filedir + '/' + file_root + '.jpg'
        url = settings.MEDIA_URL + 'pix/' + thumbnail_type + '/' + yearmonth + '/' + file_root + '.jpg'
        return filedir, filename, url

    def generate_thumbnail(self, thumbnail_type, maxwidth, maxheight=None):
        if maxheight is None:
            maxheight = maxwidth
        infilename = settings.MEDIA_ROOT + unicode(self.img)
        outfiledir, outfilename, _ = self.get_thumbnail_filename(thumbnail_type)
        if not os.path.exists(outfiledir):
            os.makedirs(outfiledir)
        img = Image.open(infilename)
        img.thumbnail((maxwidth, maxheight), Image.ANTIALIAS)
        img.save(outfilename)

    def save(self, *args, **kwargs):
        super(Picture, self).save(*args, **kwargs)
        self.film.number_of_pictures = self.film.picture_set.count()
        self.film.save()
        self.generate_thumbnail('min', *self.THUMBNAIL_SIZES['min'])
        self.generate_thumbnail('mid', *self.THUMBNAIL_SIZES['mid'])

    def __unicode__(self):
        return unicode(self.img)

    def get_display_url(self, thumbnail_type):
        if thumbnail_type == 'orig':
            return settings.MEDIA_URL + unicode(self.img)
        _, _, url = self.get_thumbnail_filename(thumbnail_type)
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

    # TODO: implement this in a better way (these are shortcuts for template)
    def get_display_url_min(self):
        return self.get_display_url('min')

    def get_display_url_mid(self):
        return self.get_display_url('mid')

    def get_width_min(self):
        return self.get_width('min')

    def get_width_mid(self):
        return self.get_width('mid')

    def get_height_min(self):
        return self.get_height('min')

    def get_height_mid(self):
        return self.get_height('mid')


@receiver(post_delete, sender=Picture)
def delete_picture(sender, instance, **kwargs):
    """Update number_of_pictures and delete files"""
    instance.film.number_of_pictures = instance.film.picture_set.count()
    instance.film.save()
    try:
        os.remove(settings.MEDIA_ROOT + unicode(instance.img))
    except OSError:
        pass
    _, filename, _ = instance.get_thumbnail_filename('min')
    try:
        os.remove(filename)
    except OSError:
        pass
    _, filename, _ = instance.get_thumbnail_filename('mid')
    try:
        os.remove(filename)
    except OSError:
        pass


class Message(models.Model):
    sent_by = models.ForeignKey(KTUser, blank=True, null=True, related_name='sent_message', on_delete=models.SET_NULL)
    sent_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    owned_by = models.ForeignKey(KTUser, blank=True, null=True, related_name='owned_message', on_delete=models.SET_NULL)
    sent_to = models.ManyToManyField(KTUser, blank=True, null=True, related_name='received_message')
    private = models.BooleanField(default=True)  # private = only one recipient

    class Meta:
        index_together = [
            ['owned_by', 'sent_at'],
        ]


class Wishlist(models.Model):
    film = models.ForeignKey(Film, blank=True, null=True)
    wished_by = models.ForeignKey(KTUser, blank=True, null=True)
    wished_at = models.DateTimeField(auto_now_add=True)
    WISH_TYPE_YES = 'Y'
    WISH_TYPE_NO = 'N'
    WISH_TYPES = [
        (WISH_TYPE_YES, 'Yes'),
        (WISH_TYPE_NO, 'No'),
    ]
    wish_type = models.CharField(max_length=1, choices=WISH_TYPES, default=WISH_TYPE_YES)


class TVChannel(models.Model):
    name = models.CharField(max_length=250)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name


class TVFilm(models.Model):
    film = models.ForeignKey(Film, blank=True, null=True)
    channel = models.ForeignKey(TVChannel, blank=True, null=True)
    when = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(KTUser, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class UserToplist(models.Model):
    title = models.CharField(max_length=250)
    created_by = models.ForeignKey(KTUser, blank=True, null=True)
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

    def __unicode__(self):
        return self.title


class UserToplistItem(models.Model):
    usertoplist = models.ForeignKey(UserToplist)
    serial_number = models.PositiveSmallIntegerField(default=0)  # TODO: auto number and renumber, when necessary
    film = models.ForeignKey(Film, blank=True, null=True)
    director = models.ForeignKey(Artist, blank=True, null=True, related_name='director_usertoplist')
    actor = models.ForeignKey(Artist, blank=True, null=True, related_name='actor_usertoplist')
    comment = models.TextField()
