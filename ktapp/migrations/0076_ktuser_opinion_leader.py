# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-06-19 15:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0075_ktuser_number_of_followers'),
    ]

    operations = [
        migrations.AddField(
            model_name='ktuser',
            name='opinion_leader',
            field=models.BooleanField(default=False),
        ),
    ]
