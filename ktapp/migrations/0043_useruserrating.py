# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0042_auto_20151017_1850'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserUserRating',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_calculated_at', models.DateTimeField()),
                ('number_of_ratings', models.IntegerField(default=0)),
                ('number_of_ratings_11', models.IntegerField(default=0)),
                ('number_of_ratings_12', models.IntegerField(default=0)),
                ('number_of_ratings_13', models.IntegerField(default=0)),
                ('number_of_ratings_14', models.IntegerField(default=0)),
                ('number_of_ratings_15', models.IntegerField(default=0)),
                ('number_of_ratings_21', models.IntegerField(default=0)),
                ('number_of_ratings_22', models.IntegerField(default=0)),
                ('number_of_ratings_23', models.IntegerField(default=0)),
                ('number_of_ratings_24', models.IntegerField(default=0)),
                ('number_of_ratings_25', models.IntegerField(default=0)),
                ('number_of_ratings_31', models.IntegerField(default=0)),
                ('number_of_ratings_32', models.IntegerField(default=0)),
                ('number_of_ratings_33', models.IntegerField(default=0)),
                ('number_of_ratings_34', models.IntegerField(default=0)),
                ('number_of_ratings_35', models.IntegerField(default=0)),
                ('number_of_ratings_41', models.IntegerField(default=0)),
                ('number_of_ratings_42', models.IntegerField(default=0)),
                ('number_of_ratings_43', models.IntegerField(default=0)),
                ('number_of_ratings_44', models.IntegerField(default=0)),
                ('number_of_ratings_45', models.IntegerField(default=0)),
                ('number_of_ratings_51', models.IntegerField(default=0)),
                ('number_of_ratings_52', models.IntegerField(default=0)),
                ('number_of_ratings_53', models.IntegerField(default=0)),
                ('number_of_ratings_54', models.IntegerField(default=0)),
                ('number_of_ratings_55', models.IntegerField(default=0)),
                ('keyword', models.ForeignKey(blank=True, to='ktapp.Keyword', null=True)),
                ('user_1', models.ForeignKey(related_name='user_1', to=settings.AUTH_USER_MODEL)),
                ('user_2', models.ForeignKey(related_name='user_2', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
