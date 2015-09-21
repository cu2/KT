# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0024_userprofilesegment_score'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofilesegment',
            name='score',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
