# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-08-02 12:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0096_ktuser_future_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='notification_subtype',
            field=models.CharField(blank=True, choices=[(b'CoRe', b'Comment reply'), (b'CoMe', b'Comment mention')], max_length=4),
        ),
    ]
