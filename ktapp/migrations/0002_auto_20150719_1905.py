# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='filmkeywordrelationship',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 7, 19, 19, 5, 52, 652178), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='filmkeywordrelationship',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='filmsequelrelationship',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 7, 19, 19, 5, 57, 880226), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='filmsequelrelationship',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
    ]
