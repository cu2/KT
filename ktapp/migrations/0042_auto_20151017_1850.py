# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0041_ktuser_is_game_master'),
    ]

    operations = [
        migrations.AddField(
            model_name='biography',
            name='snippet',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='review',
            name='snippet',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
    ]
