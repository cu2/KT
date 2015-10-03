# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0027_suggestedcontent'),
    ]

    operations = [
        migrations.CreateModel(
            name='OfTheDay',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('domain', models.CharField(default=b'F', max_length=1, choices=[(b'F', b'Film')])),
                ('day', models.DateField()),
                ('film', models.ForeignKey(to='ktapp.Film')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='oftheday',
            unique_together=set([('domain', 'day')]),
        ),
    ]
