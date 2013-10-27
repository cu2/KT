from django.db import models
from django.contrib.auth.models import User


class Film(models.Model):
    orig_title = models.CharField(max_length=200)
    other_titles = models.TextField(blank=True)
    year = models.PositiveIntegerField(default=0)
    plot_summary = models.TextField(blank=True)
    last_comment = models.ForeignKey("Comment", blank=True, null=True, related_name="last_film_comment")
    
    def __unicode__(self):
        return self.orig_title + " [" + unicode(self.year) + "]"
    
    def avg_rating(self):
        return 4.0  # TODO: implement this
    avg_rating.short_description = 'Average rating'


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
    reply_to = models.ForeignKey("self", blank=True, null=True)
    
    def __unicode__(self):
        return self.content[:100]
    
    class Meta:
        ordering = ["-created_at"]


class Topic(models.Model):
    title = models.CharField(max_length=200)
    number_of_comments = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(User)
    created_at = models.DateTimeField(auto_now_add=True)
    last_comment = models.ForeignKey(Comment, blank=True, null=True, related_name="last_topic_comment")
    
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
