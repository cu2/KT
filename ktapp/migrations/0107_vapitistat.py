# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2024-03-21 17:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0106_auto_20240219_1127'),
    ]

    operations = [
        migrations.CreateModel(
            name='VapitiStat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.PositiveSmallIntegerField()),
                ('vapiti_round', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('vapiti_type', models.CharField(choices=[(b'G', b'Gold'), (b'M', b'Silver Male'), (b'F', b'Silver Female')], max_length=1)),
                ('user_count', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('film_count', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('artist_count', models.PositiveSmallIntegerField(blank=True, null=True)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='vapitistat',
            unique_together=set([('year', 'vapiti_round', 'vapiti_type')]),
        ),
    ]