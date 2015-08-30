# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0006_comment_serial_number_by_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='ktuser',
            name='number_of_comments',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
    ]
