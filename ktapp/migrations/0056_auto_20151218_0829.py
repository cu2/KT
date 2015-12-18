# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-18 08:29
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0055_auto_20151218_0829'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='sent_to',
            field=models.ManyToManyField(blank=True, related_name='received_message', to=settings.AUTH_USER_MODEL),
        ),
    ]
