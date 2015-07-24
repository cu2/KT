# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0007_topic_closed_until'),
    ]

    operations = [
        migrations.AddField(
            model_name='trivia',
            name='spoiler',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
