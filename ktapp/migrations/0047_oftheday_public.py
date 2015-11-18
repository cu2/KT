# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0046_filmfilmrecommendation'),
    ]

    operations = [
        migrations.AddField(
            model_name='oftheday',
            name='public',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
