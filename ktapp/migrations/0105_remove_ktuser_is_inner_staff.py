# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2024-02-08 21:18
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0104_auto_20240208_1930'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ktuser',
            name='is_inner_staff',
        ),
    ]
