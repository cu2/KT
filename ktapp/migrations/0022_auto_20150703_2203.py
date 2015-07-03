# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0021_biography'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='comment',
            index_together=set([('created_at',), ('domain', 'created_at')]),
        ),
    ]
