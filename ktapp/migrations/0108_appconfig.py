# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2024-08-18 16:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0107_vapitistat'),
    ]

    operations = [
        migrations.CreateModel(
            name='AppConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vapiti_year', models.PositiveIntegerField()),
                ('vapiti_topic_id', models.PositiveIntegerField()),
            ],
        ),
    ]
