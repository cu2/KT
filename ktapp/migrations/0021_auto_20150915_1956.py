# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0020_auto_20150912_1728'),
    ]

    operations = [
        migrations.AlterField(
            model_name='film',
            name='number_of_ratings',
            field=models.PositiveIntegerField(default=0, db_index=True),
            preserve_default=True,
        ),
    ]
