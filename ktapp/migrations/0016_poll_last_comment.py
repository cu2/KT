# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0015_comment_serial_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='poll',
            name='last_comment',
            field=models.ForeignKey(related_name='last_poll_comment', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='ktapp.Comment', null=True),
            preserve_default=True,
        ),
    ]
