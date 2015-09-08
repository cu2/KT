# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0014_auto_20150903_1012'),
    ]

    operations = [
        migrations.AddField(
            model_name='film',
            name='genres_cache',
            field=models.CharField(max_length=250, blank=True),
            preserve_default=True,
        ),
    ]
