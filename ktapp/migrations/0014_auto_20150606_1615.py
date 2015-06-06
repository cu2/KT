# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0013_auto_20150531_1848'),
    ]

    operations = [
        migrations.AddField(
            model_name='artist',
            name='slug_cache',
            field=models.CharField(max_length=250, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='film',
            name='slug_cache',
            field=models.CharField(max_length=250, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='filmartistrelationship',
            name='slug_cache',
            field=models.CharField(max_length=250, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='keyword',
            name='slug_cache',
            field=models.CharField(max_length=250, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ktuser',
            name='slug_cache',
            field=models.CharField(max_length=250, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='poll',
            name='slug_cache',
            field=models.CharField(max_length=250, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='sequel',
            name='slug_cache',
            field=models.CharField(max_length=250, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='topic',
            name='slug_cache',
            field=models.CharField(max_length=250, blank=True),
            preserve_default=True,
        ),
    ]
