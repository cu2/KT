# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0018_auto_20150614_1219'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='owned_by',
            field=models.ForeignKey(related_name='owned_message', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
    ]
