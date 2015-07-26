# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0010_auto_20150725_1913'),
    ]

    operations = [
        migrations.AlterField(
            model_name='film',
            name='year',
            field=models.PositiveIntegerField(default=0, null=True, blank=True),
            preserve_default=True,
        ),
    ]
