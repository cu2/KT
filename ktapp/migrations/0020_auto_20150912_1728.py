# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0019_auto_20150912_1723'),
    ]

    operations = [
        migrations.AddField(
            model_name='artist',
            name='number_of_films',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='artist',
            name='number_of_films_as_actor',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='artist',
            name='number_of_films_as_director',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
    ]
