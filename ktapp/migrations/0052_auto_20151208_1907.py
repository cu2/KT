# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0051_auto_20151208_0847'),
    ]

    operations = [
        migrations.CreateModel(
            name='DailyActiveUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('day', models.DateField()),
                ('counter', models.PositiveIntegerField(default=0)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HourlyActiveUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('day', models.DateField()),
                ('hour', models.PositiveSmallIntegerField(default=0)),
                ('counter', models.PositiveIntegerField(default=0)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='hourlyactiveuser',
            unique_together=set([('user', 'day', 'hour')]),
        ),
        migrations.AlterUniqueTogether(
            name='dailyactiveuser',
            unique_together=set([('user', 'day')]),
        ),
    ]
