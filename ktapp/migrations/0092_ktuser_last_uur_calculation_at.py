# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2018-01-25 18:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0091_usercontribution'),
    ]

    operations = [
        migrations.AddField(
            model_name='ktuser',
            name='last_uur_calculation_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
