# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0025_auto_20150921_2302'),
    ]

    operations = [
        migrations.AddField(
            model_name='film',
            name='number_of_countries',
            field=models.PositiveSmallIntegerField(default=0),
            preserve_default=True,
        ),
    ]
