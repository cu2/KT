# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-02-21 15:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0064_auto_20160211_1954'),
    ]

    operations = [
        migrations.AddField(
            model_name='film',
            name='genre_cache_is_docu',
            field=models.BooleanField(default=False),
        ),
    ]
