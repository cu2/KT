# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0006_vote_shared_on_facebook'),
    ]

    operations = [
        migrations.AddField(
            model_name='topic',
            name='closed_until',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
