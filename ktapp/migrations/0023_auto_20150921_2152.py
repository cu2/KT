# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0022_film_number_of_genres'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProfileSegment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dimension', models.CharField(max_length=250, null=True, blank=True)),
                ('segment', models.PositiveIntegerField()),
                ('effective_number_of_films', models.PositiveIntegerField(default=0)),
                ('ratio_of_films', models.PositiveIntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserProfileSegment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number_of_votes', models.PositiveIntegerField(default=0)),
                ('relative_number_of_votes', models.PositiveIntegerField(default=0)),
                ('ratio_of_films', models.PositiveIntegerField(default=0)),
                ('segment', models.ForeignKey(to='ktapp.ProfileSegment')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='userprofilesegment',
            unique_together=set([('user', 'segment')]),
        ),
        migrations.AlterUniqueTogether(
            name='profilesegment',
            unique_together=set([('dimension', 'segment')]),
        ),
    ]
