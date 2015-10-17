# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0039_link_featured'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='comment',
            index_together=set([('created_by', 'serial_number_by_user', 'created_at'), ('created_at',), ('film', 'serial_number'), ('topic', 'serial_number'), ('domain', 'created_at')]),
        ),
    ]
