# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2024-02-07 16:00
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0100_servercost'),
    ]

    operations = [
        migrations.DeleteModel(
            name='TVFilm',
        ),
        migrations.DeleteModel(
            name='TVChannel',
        ),
        migrations.RemoveField(
            model_name='ktuser',
            name='added_tvfilm',
        ),
        migrations.RemoveField(
            model_name='ktuser',
            name='old_tv_settings',
        ),
    ]
