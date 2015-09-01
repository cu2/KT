# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0009_ktuser_number_of_ratings'),
    ]

    operations = [
        migrations.AddField(
            model_name='film',
            name='directors_cache',
            field=models.CharField(max_length=250, blank=True),
            preserve_default=True,
        ),
    ]
