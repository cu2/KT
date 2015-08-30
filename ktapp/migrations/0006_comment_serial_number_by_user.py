# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0005_auto_20150830_1523'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='serial_number_by_user',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
    ]
