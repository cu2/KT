# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0029_auto_20151003_1644'),
    ]

    operations = [
        migrations.AddField(
            model_name='link',
            name='link_domain',
            field=models.CharField(default='', max_length=250),
            preserve_default=False,
        ),
    ]
