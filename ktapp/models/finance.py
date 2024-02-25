from django.db import models


class Donation(models.Model):
    given_by = models.ForeignKey('KTUser', blank=True, null=True, on_delete=models.SET_NULL)
    given_at = models.DateField()
    money = models.PositiveIntegerField()
    tshirt = models.BooleanField(default=False)
    comment = models.CharField(max_length=250, blank=True)

    def __unicode__(self):
        return '{}HUF @ {}'.format(self.money, self.given_at)


class ServerCost(models.Model):
    year = models.PositiveIntegerField()
    actual_cost = models.PositiveIntegerField(blank=True, null=True)
    planned_cost = models.PositiveIntegerField(blank=True, null=True)
    opening_balance = models.IntegerField(blank=True, null=True)
    actual_cost_estimated = models.BooleanField(default=False)

    def __unicode__(self):
        if self.actual_cost:
            cost = '{}HUF'.format(self.actual_cost)
        else:
            cost = '{}HUF*'.format(self.planned_cost)
        return '{} @ {}'.format(cost, self.year)
