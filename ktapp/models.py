from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_delete
from django.dispatch.dispatcher import receiver


class Film(models.Model):
    orig_title = models.CharField(max_length=200)
    other_titles = models.TextField(blank=True)
    year = models.PositiveIntegerField(default=0)
    plot_summary = models.TextField(blank=True)
    number_of_comments = models.PositiveIntegerField(default=0)
    last_comment = models.ForeignKey("Comment", blank=True, null=True, related_name="last_film_comment", on_delete=models.SET_NULL)
    artists = models.ManyToManyField("Artist", through="FilmArtistRelationship")
    number_of_ratings_1 = models.PositiveIntegerField(default=0)
    number_of_ratings_2 = models.PositiveIntegerField(default=0)
    number_of_ratings_3 = models.PositiveIntegerField(default=0)
    number_of_ratings_4 = models.PositiveIntegerField(default=0)
    number_of_ratings_5 = models.PositiveIntegerField(default=0)
    number_of_quotes = models.PositiveIntegerField(default=0)
    number_of_trivias = models.PositiveIntegerField(default=0)
    number_of_reviews = models.PositiveIntegerField(default=0)
    keywords = models.ManyToManyField("Keyword", through="FilmKeywordRelationship")
    number_of_keywords = models.PositiveIntegerField(default=0)
    imdb_link = models.CharField(max_length=16, blank=True)
    porthu_link = models.CharField(max_length=16, blank=True)
    wikipedia_link_en = models.CharField(max_length=200, blank=True)
    wikipedia_link_hu = models.CharField(max_length=200, blank=True)
    imdb_rating = models.PositiveSmallIntegerField(null=True,blank=True)
    imdb_rating_refreshed_at = models.DateTimeField(null=True,blank=True)
    number_of_awards = models.PositiveIntegerField(default=0)
    number_of_links = models.PositiveIntegerField(default=0)
    
    def __unicode__(self):
        return self.orig_title + " [" + unicode(self.year) + "]"
    
    def num_specific_rating(self, r):
        if 1 <= r <= 5:
            return getattr(self, "number_of_ratings_" + str(r))
    
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
        return self.imdb_rating / 10.0


class Vote(models.Model):
    film = models.ForeignKey(Film)
    user = models.ForeignKey(User)
    rating = models.PositiveSmallIntegerField()
    when = models.DateTimeField(auto_now=True, auto_now_add=True)
    
    def __unicode__(self):
        return self.film.orig_title + " + " + self.user.username+ " = " + unicode(self.rating)
    
    class Meta:
        unique_together = ["film", "user"]


class Comment(models.Model):
    DOMAIN_FILM = "F"
    DOMAIN_TOPIC = "T"
    DOMAIN_POLL = "P"
    DOMAINS = [
        (DOMAIN_FILM, "Film"),
        (DOMAIN_TOPIC, "Topic"),
        (DOMAIN_POLL, "Poll"),
    ]
    domain = models.CharField(max_length=1, choices=DOMAINS, default=DOMAIN_FILM)
    film = models.ForeignKey(Film, blank=True, null=True)
    topic = models.ForeignKey("Topic", blank=True, null=True)
    poll = models.ForeignKey("Poll", blank=True, null=True)
    created_by = models.ForeignKey(User)
    created_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    reply_to = models.ForeignKey("self", blank=True, null=True, on_delete=models.SET_NULL)
    
    def __unicode__(self):
        return self.content[:100]
    
    class Meta:
        ordering = ["-created_at"]
        get_latest_by = "created_at"
    
    def save(self, *args, **kwargs):
        """Save comment and update domain object as well"""
        super_kwargs = {key: value for key, value in kwargs.iteritems() if key != "domain"}
        super(Comment, self).save(*args, **super_kwargs)
        kwargs["domain"].number_of_comments = kwargs["domain"].comment_set.count()
        kwargs["domain"].last_comment = kwargs["domain"].comment_set.latest()
        kwargs["domain"].save()


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
    domain.last_comment = domain.comment_set.latest()
    domain.save()


class Topic(models.Model):
    title = models.CharField(max_length=200)
    number_of_comments = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(User)
    created_at = models.DateTimeField(auto_now_add=True)
    last_comment = models.ForeignKey(Comment, blank=True, null=True, related_name="last_topic_comment", on_delete=models.SET_NULL)
    
    def __unicode__(self):
        return self.title
    
    class Meta:
        ordering = ["-last_comment"]


class Poll(models.Model):
    title = models.CharField(max_length=200)
    # NOTE: this is just a placeholder now (for Comment)
    # TODO: extend later with real content
    
    def __unicode__(self):
        return self.title


class FilmUserContent(models.Model):
    film = models.ForeignKey(Film, blank=True, null=True)
    created_by = models.ForeignKey(User)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        abstract = True
        ordering = ["-created_at"]
        get_latest_by = "created_at"


class Quote(FilmUserContent):
    content = models.TextField()
    
    def save(self, *args, **kwargs):
        super(Quote, self).save(*args, **kwargs)
        self.film.number_of_quotes = self.film.quote_set.count()
        self.film.save()


@receiver(post_delete, sender=Quote)
def delete_quote(sender, instance, **kwargs):
    instance.film.number_of_quotes = instance.film.quote_set.count()
    instance.film.save()


class Trivia(FilmUserContent):
    content = models.TextField()
    
    def save(self, *args, **kwargs):
        super(Trivia, self).save(*args, **kwargs)
        self.film.number_of_trivias = self.film.trivia_set.count()
        self.film.save()


@receiver(post_delete, sender=Trivia)
def delete_trivia(sender, instance, **kwargs):
    instance.film.number_of_trivias = instance.film.trivia_set.count()
    instance.film.save()


class Review(FilmUserContent):
    content = models.TextField()
    
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
    artist = models.ForeignKey("Artist", blank=True, null=True)
    name = models.CharField(max_length=250)
    year = models.CharField(max_length=20)
    category = models.CharField(max_length=250)
    note = models.CharField(max_length=250, blank=True)
    
    def save(self, *args, **kwargs):
        super(Award, self).save(*args, **kwargs)
        self.film.number_of_awards = self.film.award_set.count()
        self.film.save()
    
    def __unicode__(self):
        return self.name + " / " + self.category


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
    created_by = models.ForeignKey(User)
    created_at = models.DateTimeField(auto_now_add=True)
    LINK_TYPE_OFFICIAL = "O"
    LINK_TYPE_REVIEWS = "R"
    LINK_TYPE_INTERVIEWS = "I"
    LINK_TYPE_OTHER = "-"
    LINK_TYPES = [
        (LINK_TYPE_OFFICIAL, "Official pages"),
        (LINK_TYPE_REVIEWS, "Reviews"),
        (LINK_TYPE_INTERVIEWS, "Interviews"),
        (LINK_TYPE_OTHER, "Other pages"),
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
    name = models.CharField(max_length=200)
    GENDER_TYPE_MALE = "M"
    GENDER_TYPE_FEMALE = "F"
    GENDER_TYPE_UNKNOWN = "U"
    GENDER_TYPES = [
        (GENDER_TYPE_MALE, "Male"),
        (GENDER_TYPE_FEMALE, "Female"),
        (GENDER_TYPE_UNKNOWN, "Unknown"),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_TYPES, default=GENDER_TYPE_UNKNOWN)
    films = models.ManyToManyField(Film, through="FilmArtistRelationship")
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        ordering = ["name"]


class FilmArtistRelationship(models.Model):
    film = models.ForeignKey(Film)
    artist = models.ForeignKey(Artist)
    ROLE_TYPE_DIRECTOR = "D"
    ROLE_TYPE_ACTOR = "A"
    ROLE_TYPES = [
        (ROLE_TYPE_DIRECTOR, "Director"),
        (ROLE_TYPE_ACTOR, "Actor/actress"),
    ]
    ACTOR_SUBTYPE_FULL = "F"
    ACTOR_SUBTYPE_VOICE = "V"
    ACTOR_SUBTYPE_DUB = "D"
    ACTOR_SUBTYPES = [
        (ACTOR_SUBTYPE_FULL, "Full"),
        (ACTOR_SUBTYPE_VOICE, "Voice"),
        (ACTOR_SUBTYPE_DUB, "Dub"),
    ]
    role_type = models.CharField(max_length=1, choices=ROLE_TYPES, default=ROLE_TYPE_DIRECTOR)
    actor_subtype = models.CharField(max_length=1, choices=ACTOR_SUBTYPES, default=ACTOR_SUBTYPE_FULL)
    role_name = models.CharField(max_length=200, blank=True)
    
    def __unicode__(self):
        return self.role_type + "[" + self.role_name + "]:" + unicode(self.film) + "/" + unicode(self.artist)


class Keyword(models.Model):
    name = models.CharField(max_length=200)
    KEYWORD_TYPE_COUNTRY = "C"
    KEYWORD_TYPE_GENRE = "G"
    KEYWORD_TYPE_MAJOR = "M"
    KEYWORD_TYPE_OTHER = "O"
    KEYWORD_TYPES = [
        (KEYWORD_TYPE_COUNTRY, "Country"),
        (KEYWORD_TYPE_GENRE, "Genre"),
        (KEYWORD_TYPE_MAJOR, "Major"),
        (KEYWORD_TYPE_OTHER, "Other"),
    ]
    keyword_type = models.CharField(max_length=1, choices=KEYWORD_TYPES, default=KEYWORD_TYPE_OTHER)
    films = models.ManyToManyField(Film, through="FilmKeywordRelationship")
    
    def __unicode__(self):
        return self.keyword_type + ":" + self.name
    
    class Meta:
        ordering = ["keyword_type", "name"]


class FilmKeywordRelationship(models.Model):
    film = models.ForeignKey(Film)
    keyword = models.ForeignKey(Keyword)
    
    def __unicode__(self):
        return unicode(self.film) + "/" + unicode(self.keyword)
    
    def save(self, *args, **kwargs):
        super(FilmKeywordRelationship, self).save(*args, **kwargs)
        self.film.number_of_keywords = self.film.keyword_set.count()
        self.film.save()


@receiver(post_delete, sender=FilmKeywordRelationship)
def delete_filmkeyword(sender, instance, **kwargs):
    instance.film.number_of_keywords = instance.film.keyword_set.count()
    instance.film.save()
