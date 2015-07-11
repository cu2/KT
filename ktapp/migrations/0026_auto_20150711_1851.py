# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0025_auto_20150705_2258'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='quote',
            options={'ordering': ['created_at'], 'get_latest_by': 'created_at'},
        ),
        migrations.AlterModelOptions(
            name='review',
            options={'ordering': ['created_at'], 'get_latest_by': 'created_at'},
        ),
        migrations.AlterModelOptions(
            name='trivia',
            options={'ordering': ['created_at'], 'get_latest_by': 'created_at'},
        ),
    ]
