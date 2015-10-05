# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0037_ktuser_fav_period'),
    ]

    operations = [
        migrations.AddField(
            model_name='ktuser',
            name='bio_html',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
    ]
