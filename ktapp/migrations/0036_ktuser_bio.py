# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0035_auto_20151005_2054'),
    ]

    operations = [
        migrations.AddField(
            model_name='ktuser',
            name='bio',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
    ]
