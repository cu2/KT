# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0032_delete_linksite'),
    ]

    operations = [
        migrations.AddField(
            model_name='link',
            name='artist',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='ktapp.Artist', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='link',
            name='author',
            field=models.ForeignKey(related_name='authored_link', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='link',
            name='film',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='ktapp.Film', null=True),
            preserve_default=True,
        ),
    ]
