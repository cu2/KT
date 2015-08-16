# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0002_auto_20150816_0021'),
    ]

    operations = [
        migrations.AddField(
            model_name='film',
            name='main_poster',
            field=models.ForeignKey(related_name='main_poster', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='ktapp.Picture', null=True),
            preserve_default=True,
        ),
    ]
