# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0031_remove_link_linksite'),
    ]

    operations = [
        migrations.DeleteModel(
            name='LinkSite',
        ),
    ]
