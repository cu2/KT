# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0030_link_link_domain'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='link',
            name='linksite',
        ),
    ]
