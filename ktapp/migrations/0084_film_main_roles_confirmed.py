# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-10-17 00:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0083_filmartistrelationship_is_main_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='film',
            name='main_roles_confirmed',
            field=models.BooleanField(default=False),
        ),
    ]
