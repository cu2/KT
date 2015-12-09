# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0052_auto_20151208_1907'),
    ]

    operations = [
        migrations.AddField(
            model_name='ktuser',
            name='number_of_vapiti_votes',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ktuser',
            name='vapiti_weight',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
    ]
