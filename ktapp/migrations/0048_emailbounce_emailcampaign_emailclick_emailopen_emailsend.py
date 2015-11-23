# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0047_oftheday_public'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailBounce',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.CharField(max_length=250)),
                ('bounced_at', models.DateTimeField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EmailCampaign',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=250)),
                ('recipients', models.CharField(max_length=250, null=True, blank=True)),
                ('subject', models.CharField(max_length=250)),
                ('html_message', models.TextField(blank=True)),
                ('text_message', models.TextField(blank=True)),
                ('sent_at', models.DateTimeField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EmailClick',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email_type', models.CharField(max_length=250, null=True, blank=True)),
                ('clicked_at', models.DateTimeField(auto_now_add=True)),
                ('url', models.CharField(max_length=250)),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='ktapp.EmailCampaign', null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EmailOpen',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email_type', models.CharField(max_length=250, null=True, blank=True)),
                ('opened_at', models.DateTimeField(auto_now_add=True)),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='ktapp.EmailCampaign', null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EmailSend',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email_type', models.CharField(max_length=250, null=True, blank=True)),
                ('email', models.CharField(max_length=250)),
                ('sent_at', models.DateTimeField(auto_now_add=True)),
                ('is_pm', models.BooleanField(default=False)),
                ('is_email', models.BooleanField(default=False)),
                ('is_success', models.BooleanField(default=False)),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='ktapp.EmailCampaign', null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
