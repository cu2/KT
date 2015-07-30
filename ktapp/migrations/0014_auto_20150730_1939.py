# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0013_remove_premier_when_year'),
    ]

    operations = [
        migrations.AddField(
            model_name='film',
            name='second_title',
            field=models.CharField(max_length=250, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='film',
            name='third_title',
            field=models.CharField(max_length=250, blank=True),
            preserve_default=True,
        ),
    ]
