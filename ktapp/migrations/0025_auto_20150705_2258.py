# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0024_passwordtoken'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ktuser',
            name='public_gender',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ktuser',
            name='public_location',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ktuser',
            name='public_year_of_birth',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
