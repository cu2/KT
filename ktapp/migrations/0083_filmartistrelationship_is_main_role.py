# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-10-16 12:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0082_auto_20161007_1953'),
    ]

    operations = [
        migrations.AddField(
            model_name='filmartistrelationship',
            name='is_main_role',
            field=models.BooleanField(default=False),
        ),
    ]