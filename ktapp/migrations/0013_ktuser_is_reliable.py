# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0012_auto_20150902_2109'),
    ]

    operations = [
        migrations.AddField(
            model_name='ktuser',
            name='is_reliable',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
