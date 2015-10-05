# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0034_auto_20151004_0113'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserFavourite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('domain', models.CharField(default=b'F', max_length=1, choices=[(b'F', b'Film'), (b'D', b'Director'), (b'A', b'Actor'), (b'G', b'Genre'), (b'C', b'Country'), (b'P', b'Period')])),
                ('fav_id', models.PositiveIntegerField()),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='userfavourite',
            unique_together=set([('user', 'domain', 'fav_id')]),
        ),
    ]
