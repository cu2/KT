# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-12-10 15:41
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0088_ktuser_unread_notification_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='comment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ktapp.Comment'),
        ),
    ]