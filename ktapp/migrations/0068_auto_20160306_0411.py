# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-03-06 04:11
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0067_auto_20160306_0353'),
    ]

    operations = [
        migrations.RunSQL(
            ('CREATE FULLTEXT INDEX fulltext_idx_slug_cache ON ktapp_ktuser (slug_cache)',),
            ('DROP INDEX fulltext_idx_slug_cache ON ktapp_ktuser',),
        ),
    ]
