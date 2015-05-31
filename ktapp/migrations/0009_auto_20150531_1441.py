# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0008_auto_20150531_0149'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wishlist',
            name='wish_type',
            field=models.CharField(default=b'Y', max_length=1, choices=[(b'Y', b'Yes'), (b'N', b'No'), (b'G', b'Get')]),
            preserve_default=True,
        ),
    ]
