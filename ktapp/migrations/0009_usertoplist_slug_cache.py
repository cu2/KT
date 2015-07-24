# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0008_trivia_spoiler'),
    ]

    operations = [
        migrations.AddField(
            model_name='usertoplist',
            name='slug_cache',
            field=models.CharField(max_length=250, blank=True),
            preserve_default=True,
        ),
    ]
