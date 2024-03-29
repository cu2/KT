# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-10-08 17:01
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0090_auto_20161229_1815'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserContribution',
            fields=[
                ('ktuser_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('count_film', models.PositiveIntegerField(default=0)),
                ('rank_film', models.PositiveIntegerField(default=0)),
                ('count_role', models.PositiveIntegerField(default=0)),
                ('rank_role', models.PositiveIntegerField(default=0)),
                ('count_keyword', models.PositiveIntegerField(default=0)),
                ('rank_keyword', models.PositiveIntegerField(default=0)),
                ('count_picture', models.PositiveIntegerField(default=0)),
                ('rank_picture', models.PositiveIntegerField(default=0)),
                ('count_trivia', models.PositiveIntegerField(default=0)),
                ('rank_trivia', models.PositiveIntegerField(default=0)),
                ('count_quote', models.PositiveIntegerField(default=0)),
                ('rank_quote', models.PositiveIntegerField(default=0)),
                ('count_review', models.PositiveIntegerField(default=0)),
                ('rank_review', models.PositiveIntegerField(default=0)),
                ('count_link', models.PositiveIntegerField(default=0)),
                ('rank_link', models.PositiveIntegerField(default=0)),
                ('count_biography', models.PositiveIntegerField(default=0)),
                ('rank_biography', models.PositiveIntegerField(default=0)),
                ('count_poll', models.PositiveIntegerField(default=0)),
                ('rank_poll', models.PositiveIntegerField(default=0)),
                ('count_usertoplist', models.PositiveIntegerField(default=0)),
                ('rank_usertoplist', models.PositiveIntegerField(default=0)),
            ],
            options={
                'abstract': False,
            },
            bases=('ktapp.ktuser',),
        ),
    ]
