# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0023_auto_20150921_2152'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofilesegment',
            name='score',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
    ]
