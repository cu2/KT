# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0010_film_directors_cache'),
    ]

    operations = [
        migrations.CreateModel(
            name='MessageCountCache',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number_of_messages', models.PositiveIntegerField(default=0)),
                ('owned_by', models.ForeignKey(related_name='owned_message_count', to=settings.AUTH_USER_MODEL)),
                ('partner', models.ForeignKey(related_name='partner_message_count', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='messagecountcache',
            unique_together=set([('owned_by', 'partner')]),
        ),
        migrations.AddField(
            model_name='ktuser',
            name='number_of_messages',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
    ]
