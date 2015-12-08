# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0050_auto_20151208_0843'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ktuser',
            name='average_rating',
            field=models.DecimalField(default=None, null=True, max_digits=2, decimal_places=1, blank=True),
            preserve_default=True,
        ),
    ]
