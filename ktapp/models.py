from django.db import models
from django.contrib.auth.models import User


class Film(models.Model):
    orig_title = models.CharField(max_length=200)
    other_titles = models.TextField(blank=True)
    year = models.PositiveIntegerField(default=0)
    
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
