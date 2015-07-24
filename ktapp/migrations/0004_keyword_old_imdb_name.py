# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0003_film_open_for_vote_from'),
    ]

    operations = [
        migrations.AddField(
            model_name='keyword',
            name='old_imdb_name',
            field=models.CharField(max_length=250, blank=True),
            preserve_default=True,
        ),
    ]
