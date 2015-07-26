# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0011_auto_20150726_1125'),
    ]

    operations = [
        migrations.AlterField(
            model_name='film',
            name='porthu_link',
            field=models.PositiveIntegerField(default=0, null=True, blank=True),
            preserve_default=True,
        ),
    ]
