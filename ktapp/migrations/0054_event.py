# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0053_auto_20151209_2132'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('event_datetime', models.DateTimeField(auto_now_add=True)),
                ('event_type', models.CharField(default=b'NV', max_length=2, choices=[(b'NV', b'New vote'), (b'CV', b'Change vote'), (b'DV', b'Delete vote'), (b'AW', b'Add to wishlist'), (b'RW', b'Remove from wishlist'), (b'NC', b'New comment'), (b'EC', b'Edit comment'), (b'SU', b'Signup'), (b'EP', b'Edit profile'), (b'FO', b'Follow'), (b'UF', b'Unfollow'), (b'PV', b'Poll vote')])),
                ('some_id', models.PositiveIntegerField(default=0)),
                ('details', models.CharField(max_length=250, null=True, blank=True)),
                ('film', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='ktapp.Film', null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
