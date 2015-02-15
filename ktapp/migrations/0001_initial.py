# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import ktapp.models
import django.utils.timezone
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='KTUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', unique=True, max_length=30, verbose_name='username', validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username.', 'invalid')])),
                ('first_name', models.CharField(max_length=30, verbose_name='first name', blank=True)),
                ('last_name', models.CharField(max_length=30, verbose_name='last name', blank=True)),
                ('email', models.EmailField(max_length=75, verbose_name='email address', blank=True)),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('gender', models.CharField(default=b'U', max_length=1, choices=[(b'M', b'Male'), (b'F', b'Female'), (b'U', b'Unknown')])),
                ('location', models.CharField(max_length=250, null=True, blank=True)),
                ('year_of_birth', models.PositiveIntegerField(default=0)),
                ('is_admin', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of his/her group.', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Artist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=250)),
                ('gender', models.CharField(default=b'U', max_length=1, choices=[(b'M', b'Male'), (b'F', b'Female'), (b'U', b'Unknown')])),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Award',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=250)),
                ('year', models.CharField(max_length=20)),
                ('category', models.CharField(max_length=250)),
                ('note', models.CharField(max_length=250, blank=True)),
                ('artist', models.ForeignKey(blank=True, to='ktapp.Artist', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('domain', models.CharField(default=b'F', max_length=1, choices=[(b'F', b'Film'), (b'T', b'Topic'), (b'P', b'Poll')])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('content', models.TextField()),
                ('rating', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('created_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'get_latest_by': 'created_at',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Film',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('orig_title', models.CharField(max_length=250)),
                ('other_titles', models.TextField(blank=True)),
                ('year', models.PositiveIntegerField(default=0)),
                ('plot_summary', models.TextField(blank=True)),
                ('number_of_comments', models.PositiveIntegerField(default=0)),
                ('number_of_ratings_1', models.PositiveIntegerField(default=0)),
                ('number_of_ratings_2', models.PositiveIntegerField(default=0)),
                ('number_of_ratings_3', models.PositiveIntegerField(default=0)),
                ('number_of_ratings_4', models.PositiveIntegerField(default=0)),
                ('number_of_ratings_5', models.PositiveIntegerField(default=0)),
                ('number_of_quotes', models.PositiveIntegerField(default=0)),
                ('number_of_trivias', models.PositiveIntegerField(default=0)),
                ('number_of_reviews', models.PositiveIntegerField(default=0)),
                ('number_of_keywords', models.PositiveIntegerField(default=0)),
                ('imdb_link', models.CharField(max_length=16, blank=True)),
                ('porthu_link', models.CharField(max_length=16, blank=True)),
                ('wikipedia_link_en', models.CharField(max_length=250, blank=True)),
                ('wikipedia_link_hu', models.CharField(max_length=250, blank=True)),
                ('imdb_rating', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('imdb_rating_refreshed_at', models.DateTimeField(null=True, blank=True)),
                ('number_of_awards', models.PositiveIntegerField(default=0)),
                ('number_of_links', models.PositiveIntegerField(default=0)),
                ('number_of_pictures', models.PositiveIntegerField(default=0)),
                ('main_premier', models.DateField(null=True, blank=True)),
                ('main_premier_year', models.PositiveIntegerField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FilmArtistRelationship',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('role_type', models.CharField(default=b'D', max_length=1, choices=[(b'D', b'Director'), (b'A', b'Actor/actress')])),
                ('actor_subtype', models.CharField(default=b'F', max_length=1, choices=[(b'F', b'Full'), (b'V', b'Voice'), (b'D', b'Dub')])),
                ('role_name', models.CharField(max_length=250, blank=True)),
                ('artist', models.ForeignKey(to='ktapp.Artist')),
                ('film', models.ForeignKey(to='ktapp.Film')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FilmKeywordRelationship',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('film', models.ForeignKey(to='ktapp.Film')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FilmSequelRelationship',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('serial_number', models.PositiveSmallIntegerField(default=0)),
                ('film', models.ForeignKey(to='ktapp.Film')),
            ],
            options={
                'ordering': ['serial_number'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Keyword',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=250)),
                ('keyword_type', models.CharField(default=b'O', max_length=1, choices=[(b'C', b'Country'), (b'G', b'Genre'), (b'M', b'Major'), (b'O', b'Other')])),
                ('films', models.ManyToManyField(to='ktapp.Film', through='ktapp.FilmKeywordRelationship')),
            ],
            options={
                'ordering': ['keyword_type', 'name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Link',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=250)),
                ('url', models.CharField(max_length=250)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('link_type', models.CharField(default=b'-', max_length=1, choices=[(b'O', b'Official pages'), (b'R', b'Reviews'), (b'I', b'Interviews'), (b'-', b'Other pages')])),
                ('lead', models.TextField(blank=True)),
                ('created_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('film', models.ForeignKey(to='ktapp.Film')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LinkSite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=250)),
                ('url', models.CharField(max_length=250)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sent_at', models.DateTimeField(auto_now_add=True)),
                ('content', models.TextField()),
                ('private', models.BooleanField(default=True)),
                ('owned_by', models.ForeignKey(related_name='owned_message', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('sent_by', models.ForeignKey(related_name='sent_message', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('sent_to', models.ManyToManyField(related_name='received_message', null=True, to=settings.AUTH_USER_MODEL, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Picture',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('img', models.ImageField(height_field=b'height', width_field=b'width', upload_to=ktapp.models.get_picture_upload_name)),
                ('width', models.PositiveIntegerField(default=0, editable=False)),
                ('height', models.PositiveIntegerField(default=0, editable=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('source_url', models.CharField(max_length=250, blank=True)),
                ('picture_type', models.CharField(default=b'O', max_length=1, choices=[(b'P', b'Poster'), (b'D', b'DVD'), (b'S', b'Screenshot'), (b'O', b'Other')])),
                ('artists', models.ManyToManyField(to='ktapp.Artist', blank=True)),
                ('created_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('film', models.ForeignKey(to='ktapp.Film')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Poll',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=250)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('nominated_by', models.CharField(max_length=250, null=True, blank=True)),
                ('open_from', models.DateTimeField(null=True, blank=True)),
                ('open_until', models.DateTimeField(null=True, blank=True)),
                ('state', models.CharField(default=b'W', max_length=1, choices=[(b'W', b'Waiting for approval'), (b'A', b'Approved'), (b'O', b'Open'), (b'C', b'Closed')])),
                ('number_of_comments', models.PositiveIntegerField(default=0)),
                ('number_of_votes', models.PositiveIntegerField(default=0)),
                ('number_of_people', models.PositiveIntegerField(default=0)),
                ('created_by', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PollChoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('choice', models.CharField(max_length=250)),
                ('serial_number', models.PositiveSmallIntegerField(default=0)),
                ('number_of_votes', models.PositiveIntegerField(default=0)),
                ('poll', models.ForeignKey(to='ktapp.Poll')),
            ],
            options={
                'ordering': ['poll', 'serial_number'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PollVote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pollchoice', models.ForeignKey(to='ktapp.PollChoice')),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Premier',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('when', models.DateField()),
                ('film', models.ForeignKey(to='ktapp.Film')),
            ],
            options={
                'ordering': ['when', 'premier_type', 'film'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PremierType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=250)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Quote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('content', models.TextField()),
                ('created_by', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('film', models.ForeignKey(blank=True, to='ktapp.Film', null=True)),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
                'get_latest_by': 'created_at',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('content', models.TextField()),
                ('created_by', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('film', models.ForeignKey(blank=True, to='ktapp.Film', null=True)),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
                'get_latest_by': 'created_at',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Sequel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=250)),
                ('sequel_type', models.CharField(default=b'S', max_length=1, choices=[(b'S', b'Sequel'), (b'R', b'Remake'), (b'A', b'Adaptation')])),
                ('films', models.ManyToManyField(to='ktapp.Film', through='ktapp.FilmSequelRelationship')),
            ],
            options={
                'ordering': ['sequel_type', 'name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=250)),
                ('number_of_comments', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('last_comment', models.ForeignKey(related_name='last_topic_comment', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='ktapp.Comment', null=True)),
            ],
            options={
                'ordering': ['-last_comment'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Trivia',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('content', models.TextField()),
                ('created_by', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('film', models.ForeignKey(blank=True, to='ktapp.Film', null=True)),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
                'get_latest_by': 'created_at',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TVChannel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=250)),
                ('active', models.BooleanField(default=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TVFilm',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('when', models.DateTimeField(null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('channel', models.ForeignKey(blank=True, to='ktapp.TVChannel', null=True)),
                ('created_by', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('film', models.ForeignKey(blank=True, to='ktapp.Film', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserToplist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=250)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('ordered', models.BooleanField(default=True)),
                ('quality', models.BooleanField(default=True)),
                ('number_of_items', models.PositiveSmallIntegerField()),
                ('toplist_type', models.CharField(default=b'F', max_length=1, choices=[(b'F', b'Film'), (b'D', b'Director'), (b'A', b'Actor')])),
                ('created_by', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserToplistItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('serial_number', models.PositiveSmallIntegerField(default=0)),
                ('comment', models.TextField()),
                ('actor', models.ForeignKey(related_name='actor_usertoplist', blank=True, to='ktapp.Artist', null=True)),
                ('director', models.ForeignKey(related_name='director_usertoplist', blank=True, to='ktapp.Artist', null=True)),
                ('film', models.ForeignKey(blank=True, to='ktapp.Film', null=True)),
                ('usertoplist', models.ForeignKey(to='ktapp.UserToplist')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rating', models.PositiveSmallIntegerField()),
                ('when', models.DateTimeField(auto_now=True, auto_now_add=True)),
                ('film', models.ForeignKey(to='ktapp.Film')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Wishlist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('wished_at', models.DateTimeField(auto_now_add=True)),
                ('wish_type', models.CharField(default=b'Y', max_length=1, choices=[(b'Y', b'Yes'), (b'N', b'No')])),
                ('film', models.ForeignKey(blank=True, to='ktapp.Film', null=True)),
                ('wished_by', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='vote',
            unique_together=set([('film', 'user')]),
        ),
        migrations.AddField(
            model_name='premier',
            name='premier_type',
            field=models.ForeignKey(blank=True, to='ktapp.PremierType', null=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='pollvote',
            unique_together=set([('user', 'pollchoice')]),
        ),
        migrations.AlterIndexTogether(
            name='message',
            index_together=set([('owned_by', 'sent_at')]),
        ),
        migrations.AddField(
            model_name='link',
            name='linksite',
            field=models.ForeignKey(blank=True, to='ktapp.LinkSite', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='filmsequelrelationship',
            name='sequel',
            field=models.ForeignKey(to='ktapp.Sequel'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='filmkeywordrelationship',
            name='keyword',
            field=models.ForeignKey(to='ktapp.Keyword'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='film',
            name='artists',
            field=models.ManyToManyField(to='ktapp.Artist', through='ktapp.FilmArtistRelationship'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='film',
            name='keywords',
            field=models.ManyToManyField(to='ktapp.Keyword', through='ktapp.FilmKeywordRelationship'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='film',
            name='last_comment',
            field=models.ForeignKey(related_name='last_film_comment', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='ktapp.Comment', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='film',
            name='sequels',
            field=models.ManyToManyField(to='ktapp.Sequel', through='ktapp.FilmSequelRelationship'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='comment',
            name='film',
            field=models.ForeignKey(blank=True, to='ktapp.Film', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='comment',
            name='poll',
            field=models.ForeignKey(blank=True, to='ktapp.Poll', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='comment',
            name='reply_to',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='ktapp.Comment', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='comment',
            name='topic',
            field=models.ForeignKey(blank=True, to='ktapp.Topic', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='award',
            name='film',
            field=models.ForeignKey(to='ktapp.Film'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='artist',
            name='films',
            field=models.ManyToManyField(to='ktapp.Film', through='ktapp.FilmArtistRelationship'),
            preserve_default=True,
        ),
    ]
