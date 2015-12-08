# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0049_emailcampaign_pm_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='ktuser',
            name='average_rating',
            field=models.DecimalField(default=0, null=True, max_digits=2, decimal_places=1, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ktuser',
            name='bio_snippet',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ktuser',
            name='number_of_film_comments',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ktuser',
            name='number_of_poll_comments',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ktuser',
            name='number_of_ratings_1',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ktuser',
            name='number_of_ratings_2',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ktuser',
            name='number_of_ratings_3',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ktuser',
            name='number_of_ratings_4',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ktuser',
            name='number_of_ratings_5',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ktuser',
            name='number_of_topic_comments',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
    ]
