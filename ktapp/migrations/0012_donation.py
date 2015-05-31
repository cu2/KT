# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0011_auto_20150531_1443'),
    ]

    operations = [
        migrations.CreateModel(
            name='Donation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('given_at', models.DateTimeField(auto_now_add=True)),
                ('money', models.PositiveIntegerField()),
                ('tshirt', models.BooleanField(default=False)),
                ('comment', models.CharField(max_length=250, blank=True)),
                ('given_by', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
