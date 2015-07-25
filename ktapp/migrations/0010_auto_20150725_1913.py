# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0009_usertoplist_slug_cache'),
    ]

    operations = [
        migrations.AlterField(
            model_name='filmartistrelationship',
            name='actor_subtype',
            field=models.CharField(default=b'F', max_length=1, choices=[(b'F', b'Full'), (b'V', b'Voice')]),
            preserve_default=True,
        ),
    ]
