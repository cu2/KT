from django.db import models


class HourlyActiveUser(models.Model):
    user = models.ForeignKey('KTUser')
    day = models.DateField()
    hour = models.PositiveSmallIntegerField(default=0)
    counter = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ['user', 'day', 'hour']


class DailyActiveUser(models.Model):
    user = models.ForeignKey('KTUser')
    day = models.DateField()
    counter = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ['user', 'day']


class ActiveUserCount(models.Model):
    day = models.DateField(primary_key=True)
    dau_count = models.PositiveIntegerField(default=0)
    wau_count = models.PositiveIntegerField(default=0)
    mau_count = models.PositiveIntegerField(default=0)
    new_count = models.PositiveIntegerField(default=0)
