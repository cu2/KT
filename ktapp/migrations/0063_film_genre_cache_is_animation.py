# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-02-11 19:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0062_film_number_of_actors'),
    ]

    operations = [
        migrations.AddField(
            model_name='film',
            name='genre_cache_is_animation',
            field=models.BooleanField(default=False),
        ),
    ]
