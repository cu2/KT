# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0018_auto_20150911_2041'),
    ]

    operations = [
        migrations.AddField(
            model_name='artist',
            name='average_rating',
            field=models.DecimalField(default=0, null=True, max_digits=2, decimal_places=1, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='artist',
            name='average_rating_as_actor',
            field=models.DecimalField(default=0, null=True, max_digits=2, decimal_places=1, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='artist',
            name='average_rating_as_director',
            field=models.DecimalField(default=0, null=True, max_digits=2, decimal_places=1, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='artist',
            name='number_of_ratings',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='artist',
            name='number_of_ratings_as_actor',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='artist',
            name='number_of_ratings_as_director',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
    ]
