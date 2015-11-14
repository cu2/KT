# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ktapp', '0045_auto_20151112_0140'),
    ]

    operations = [
        migrations.CreateModel(
            name='FilmFilmRecommendation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_calculated_at', models.DateTimeField()),
                ('score', models.IntegerField(default=0)),
                ('film_1', models.ForeignKey(related_name='film_1', to='ktapp.Film')),
                ('film_2', models.ForeignKey(related_name='film_2', to='ktapp.Film')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
