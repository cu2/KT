# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-08-02 13:00
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0097_auto_20190802_1242'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subscribed_at', models.DateTimeField(auto_now_add=True)),
                ('subscription_type', models.CharField(choices=[(b'S', b'Subscribe'), (b'I', b'Ignore')], default=b'S', max_length=1)),
                ('film', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ktapp.Film')),
                ('poll', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ktapp.Poll')),
                ('topic', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ktapp.Topic')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterField(
            model_name='notification',
            name='notification_subtype',
            field=models.CharField(blank=True, choices=[(b'CoRe', b'Comment reply'), (b'CoMe', b'Comment mention'), (b'CoFS', b'Comment on film you subscribed to'), (b'CoTS', b'Comment on topic you subscribed to'), (b'CoPS', b'Comment on poll you subscribed to')], max_length=4),
        ),
    ]