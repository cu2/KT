# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0004_keyword_old_imdb_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='filmkeywordrelationship',
            name='spoiler',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
