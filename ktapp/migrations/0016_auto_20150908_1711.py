# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0015_film_genres_cache'),
    ]

    operations = [
        migrations.CreateModel(
            name='Recommendation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fav_number_of_ratings', models.PositiveIntegerField(default=0)),
                ('fav_average_rating', models.DecimalField(default=None, null=True, max_digits=2, decimal_places=1, blank=True)),
                ('film', models.ForeignKey(to='ktapp.Film')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='recommendation',
            unique_together=set([('film', 'user')]),
        ),
    ]
