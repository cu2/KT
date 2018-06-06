# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-07 00:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0092_ktuser_last_uur_calculation_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='ktuser',
            name='signed_privacy_policy',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='ktuser',
            name='signed_privacy_policy_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='ktuser',
            name='email_notification',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='ktuser',
            name='subscribed_to_campaigns',
            field=models.BooleanField(default=False),
        ),
    ]
