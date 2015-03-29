# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0002_auto_20150223_0913'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='filmkeywordrelationship',
            unique_together=set([('film', 'keyword')]),
        ),
    ]
