# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0022_auto_20150703_2203'),
    ]

    operations = [
        migrations.AddField(
            model_name='ktuser',
            name='core_member',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ktuser',
            name='validated_email',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
