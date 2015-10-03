# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0028_auto_20151003_1202'),
    ]

    operations = [
        migrations.AddField(
            model_name='film',
            name='genre_cache_is_mini',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='film',
            name='genre_cache_is_music_video',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='film',
            name='genre_cache_is_short',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
