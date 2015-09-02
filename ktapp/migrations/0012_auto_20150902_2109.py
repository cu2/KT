# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0011_auto_20150902_1833'),
    ]

    operations = [
        migrations.AddField(
            model_name='ktuser',
            name='number_of_toplists',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ktuser',
            name='number_of_wishes_get',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ktuser',
            name='number_of_wishes_no',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ktuser',
            name='number_of_wishes_yes',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
    ]
