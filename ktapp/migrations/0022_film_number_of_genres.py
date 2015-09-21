# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0021_auto_20150915_1956'),
    ]

    operations = [
        migrations.AddField(
            model_name='film',
            name='number_of_genres',
            field=models.PositiveSmallIntegerField(default=0),
            preserve_default=True,
        ),
    ]
