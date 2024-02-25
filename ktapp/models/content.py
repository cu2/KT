import datetime
import hashlib
import os
import random
import string
from PIL import Image
from urlparse import urlparse

from django.conf import settings
from django.db import models
from django.core.urlresolvers import reverse
from django.db.models.signals import post_delete, pre_delete
from django.dispatch.dispatcher import receiver
from django.template.defaultfilters import slugify

from ktapp import utils as kt_utils


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
    vapiti_year = models.PositiveIntegerField(blank=True, null=True)
    slug_cache = models.CharField(max_length=250, blank=True)
    created_by = models.ForeignKey('KTUser', blank=True, null=True, on_delete=models.SET_NULL)
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
        return 'https://{}{}'.format(
            settings.ROOT_DOMAIN,
            reverse('film_main', args=(self.id, self.slug_cache)),
        )

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
    created_by = models.ForeignKey('KTUser', blank=True, null=True, on_delete=models.SET_NULL)
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
    created_by = models.ForeignKey('KTUser', blank=True, null=True, on_delete=models.SET_NULL)
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
    created_by = models.ForeignKey('KTUser', blank=True, null=True, on_delete=models.SET_NULL)
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
    created_by = models.ForeignKey('KTUser', blank=True, null=True, on_delete=models.SET_NULL)
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
    created_by = models.ForeignKey('KTUser', blank=True, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['sequel_type', 'name']

    def all_films(self):
        return [
            fs.film
            for fs in FilmSequelRelationship.objects.filter(
                sequel=self,
            ).select_related('film').order_by(
                'film__year', 'serial_number', 'film__orig_title', 'film__id',
            )
        ]

    def save(self, *args, **kwargs):
        self.slug_cache = slugify(self.name)
        super(Sequel, self).save(*args, **kwargs)


class FilmSequelRelationship(models.Model):
    film = models.ForeignKey(Film)
    sequel = models.ForeignKey(Sequel)
    serial_number = models.PositiveSmallIntegerField(default=0)
    created_by = models.ForeignKey('KTUser', blank=True, null=True, on_delete=models.SET_NULL)
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
    created_by = models.ForeignKey('KTUser', blank=True, null=True, on_delete=models.SET_NULL)
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
    user = models.ForeignKey('KTUser', blank=True, null=True, on_delete=models.SET_NULL, related_name='user_profile')
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


class Award(models.Model):
    film = models.ForeignKey(Film)
    artist = models.ForeignKey('Artist', blank=True, null=True)
    name = models.CharField(max_length=250)
    year = models.CharField(max_length=20)
    category = models.CharField(max_length=250)
    note = models.CharField(max_length=250, blank=True)
    created_by = models.ForeignKey('KTUser', blank=True, null=True, on_delete=models.SET_NULL)
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
