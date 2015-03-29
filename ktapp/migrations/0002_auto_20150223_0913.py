# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ktuser',
            options={},
        ),
        migrations.RemoveField(
            model_name='ktuser',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='ktuser',
            name='is_admin',
        ),
        migrations.RemoveField(
            model_name='ktuser',
            name='last_name',
        ),
        migrations.AddField(
            model_name='ktuser',
            name='public_gender',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ktuser',
            name='public_location',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ktuser',
            name='public_year_of_birth',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ktuser',
            name='date_joined',
            field=models.DateTimeField(auto_now_add=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ktuser',
            name='email',
            field=models.EmailField(unique=True, max_length=75, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ktuser',
            name='is_active',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ktuser',
            name='is_staff',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ktuser',
            name='username',
            field=models.CharField(unique=True, max_length=64),
            preserve_default=True,
        ),
    ]
