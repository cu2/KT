# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0010_auto_20150531_1443'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='wishlist',
            unique_together=set([('film', 'wished_by', 'wish_type')]),
        ),
    ]
