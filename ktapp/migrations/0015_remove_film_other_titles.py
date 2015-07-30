# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0014_auto_20150730_1939'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='film',
            name='other_titles',
        ),
    ]
