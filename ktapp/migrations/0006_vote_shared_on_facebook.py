# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0005_filmkeywordrelationship_spoiler'),
    ]

    operations = [
        migrations.AddField(
            model_name='vote',
            name='shared_on_facebook',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
