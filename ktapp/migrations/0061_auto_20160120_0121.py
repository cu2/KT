# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-20 01:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0060_auto_20160102_1251'),
    ]

    operations = [
        migrations.AddField(
            model_name='artist',
            name='main_picture',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='main_artist_picture', to='ktapp.Picture'),
        ),
        migrations.AddField(
            model_name='filmartistrelationship',
            name='main_picture',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='main_role_picture', to='ktapp.Picture'),
        ),
    ]
