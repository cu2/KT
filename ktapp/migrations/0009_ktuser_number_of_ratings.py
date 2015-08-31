# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0008_auto_20150830_1911'),
    ]

    operations = [
        migrations.AddField(
            model_name='ktuser',
            name='number_of_ratings',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
    ]
