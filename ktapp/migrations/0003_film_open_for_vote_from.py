# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0002_auto_20150719_1905'),
    ]

    operations = [
        migrations.AddField(
            model_name='film',
            name='open_for_vote_from',
            field=models.DateField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
