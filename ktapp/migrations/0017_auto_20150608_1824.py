# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0016_poll_last_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='content_html',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='comment',
            name='content_old_html',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
    ]
