# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0048_emailbounce_emailcampaign_emailclick_emailopen_emailsend'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailcampaign',
            name='pm_message',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
    ]
