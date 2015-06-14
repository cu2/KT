# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0017_auto_20150608_1824'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='content_html',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='message',
            name='content_old_html',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
    ]
