# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2023-07-24 17:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0099_film_vapiti_year'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServerCost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.PositiveIntegerField()),
                ('actual_cost', models.PositiveIntegerField(blank=True, null=True)),
                ('planned_cost', models.PositiveIntegerField(blank=True, null=True)),
                ('opening_balance', models.IntegerField(blank=True, null=True)),
                ('actual_cost_estimated', models.BooleanField(default=False)),
            ],
        ),
    ]
