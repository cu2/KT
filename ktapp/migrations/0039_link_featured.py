# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0038_ktuser_bio_html'),
    ]

    operations = [
        migrations.AddField(
            model_name='link',
            name='featured',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
