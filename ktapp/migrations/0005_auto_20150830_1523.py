# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0004_change'),
    ]

    operations = [
        migrations.AddField(
            model_name='ktuser',
            name='latest_comments',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ktuser',
            name='latest_votes',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
    ]
