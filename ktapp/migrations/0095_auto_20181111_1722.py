# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-11-11 17:22
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0094_ktuser_validated_email_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='IgnoreUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('when', models.DateTimeField(auto_now_add=True)),
                ('ignore_pm', models.BooleanField(default=False)),
                ('ignore_comment', models.BooleanField(default=False)),
                ('who', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('whom', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='ignoreuser',
            unique_together=set([('who', 'whom')]),
        ),
    ]