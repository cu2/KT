# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0012_auto_20150726_1152'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='premier',
            name='when_year',
        ),
    ]
