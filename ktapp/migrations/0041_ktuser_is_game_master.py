# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0040_auto_20151017_1534'),
    ]

    operations = [
        migrations.AddField(
            model_name='ktuser',
            name='is_game_master',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
