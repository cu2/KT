# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0016_auto_20150908_1711'),
    ]

    operations = [
        migrations.AddField(
            model_name='film',
            name='director_names_cache',
            field=models.CharField(max_length=250, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='film',
            name='genre_names_cache',
            field=models.CharField(max_length=250, blank=True),
            preserve_default=True,
        ),
    ]
