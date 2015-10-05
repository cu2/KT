# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0036_ktuser_bio'),
    ]

    operations = [
        migrations.AddField(
            model_name='ktuser',
            name='fav_period',
            field=models.CharField(max_length=250, null=True, blank=True),
            preserve_default=True,
        ),
    ]
