# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0014_auto_20150606_1615'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='serial_number',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
    ]
