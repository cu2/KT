# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0012_donation'),
    ]

    operations = [
        migrations.CreateModel(
            name='Follow',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('who', models.ForeignKey(related_name='follows', to=settings.AUTH_USER_MODEL)),
                ('whom', models.ForeignKey(related_name='followed_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='ktuser',
            name='follow',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, through='ktapp.Follow'),
            preserve_default=True,
        ),
    ]
