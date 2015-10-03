# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0033_auto_20151003_2045'),
    ]

    operations = [
        migrations.AlterField(
            model_name='suggestedcontent',
            name='domain',
            field=models.CharField(default=b'F', max_length=1, choices=[(b'F', b'Film'), (b'L', b'Link')]),
            preserve_default=True,
        ),
    ]
