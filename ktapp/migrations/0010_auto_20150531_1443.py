# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0009_auto_20150531_1441'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='wishlist',
            unique_together=set([]),
        ),
    ]
