# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import ktapp.models
import django.utils.timezone
from django.conf import settings


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
                ('username', models.CharField(unique=True, max_length=64)),
                ('email', models.EmailField(unique=True, max_length=75, blank=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('date_joined', models.DateTimeField(auto_now_add=True)),
                ('gender', models.CharField(default=b'U', max_length=1, choices=[(b'M', b'Male'), (b'F', b'Female'), (b'U', b'Unknown')])),
                ('location', models.CharField(max_length=250, null=True, blank=True)),
                ('year_of_birth', models.PositiveIntegerField(default=0)),
                ('public_gender', models.BooleanField(default=True)),
                ('public_location', models.BooleanField(default=True)),
                ('public_year_of_birth', models.BooleanField(default=True)),
                ('slug_cache', models.CharField(max_length=250, blank=True)),
                ('validated_email', models.BooleanField(default=False)),
                ('core_member', models.BooleanField(default=False)),
                ('i_county_id', models.SmallIntegerField(default=-1)),
                ('email_notification', models.BooleanField(default=True)),
                ('facebook_rating_share', models.BooleanField(default=True)),
                ('added_role', models.PositiveIntegerField(default=0)),
                ('added_artist', models.PositiveIntegerField(default=0)),
                ('added_film', models.PositiveIntegerField(default=0)),
                ('added_tvfilm', models.PositiveIntegerField(default=0)),
                ('added_trivia', models.PositiveIntegerField(default=0)),
                ('reason_of_inactivity', models.CharField(default=b'U', max_length=1, choices=[(b'B', b'Banned'), (b'Q', b'Quit'), (b'U', b'Unknown')])),
                ('old_permissions', models.CharField(max_length=250, null=True, blank=True)),
                ('ip_at_registration', models.CharField(max_length=250, null=True, blank=True)),
                ('ip_at_last_login', models.CharField(max_length=250, null=True, blank=True)),
                ('last_message_at', models.DateTimeField(null=True, blank=True)),
                ('last_message_checking_at', models.DateTimeField(null=True, blank=True)),
                ('old_tv_settings', models.CharField(max_length=250, null=True, blank=True)),
                ('last_activity_at', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Artist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=250)),
                ('gender', models.CharField(default=b'U', max_length=1, choices=[(b'M', b'Male'), (b'F', b'Female'), (b'U', b'Unknown')])),
                ('slug_cache', models.CharField(max_length=250, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
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
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('artist', models.ForeignKey(blank=True, to='ktapp.Artist', null=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Biography',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('content', models.TextField()),
                ('content_html', models.TextField()),
                ('content_old_html', models.TextField(blank=True)),
                ('approved', models.BooleanField(default=False)),
                ('artist', models.ForeignKey(to='ktapp.Artist')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['-created_at'],
                'get_latest_by': 'created_at',
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
                ('content_html', models.TextField()),
                ('content_old_html', models.TextField(blank=True)),
                ('rating', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('serial_number', models.PositiveIntegerField(default=0)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['-created_at'],
                'get_latest_by': 'created_at',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Donation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('given_at', models.DateTimeField(auto_now_add=True)),
                ('money', models.PositiveIntegerField()),
                ('tshirt', models.BooleanField(default=False)),
                ('comment', models.CharField(max_length=250, blank=True)),
                ('given_by', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Film',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('orig_title', models.CharField(max_length=250)),
                ('second_title', models.CharField(max_length=250, blank=True)),
                ('third_title', models.CharField(max_length=250, blank=True)),
                ('year', models.PositiveIntegerField(default=0, null=True, blank=True)),
                ('plot_summary', models.TextField(blank=True)),
                ('number_of_comments', models.PositiveIntegerField(default=0)),
                ('number_of_ratings_1', models.PositiveIntegerField(default=0)),
                ('number_of_ratings_2', models.PositiveIntegerField(default=0)),
                ('number_of_ratings_3', models.PositiveIntegerField(default=0)),
                ('number_of_ratings_4', models.PositiveIntegerField(default=0)),
                ('number_of_ratings_5', models.PositiveIntegerField(default=0)),
                ('number_of_ratings', models.PositiveIntegerField(default=0)),
                ('average_rating', models.DecimalField(default=0, null=True, max_digits=2, decimal_places=1, blank=True)),
                ('number_of_quotes', models.PositiveIntegerField(default=0)),
                ('number_of_trivias', models.PositiveIntegerField(default=0)),
                ('number_of_reviews', models.PositiveIntegerField(default=0)),
                ('number_of_keywords', models.PositiveIntegerField(default=0)),
                ('imdb_link', models.CharField(max_length=16, blank=True)),
                ('porthu_link', models.PositiveIntegerField(default=0, null=True, blank=True)),
                ('wikipedia_link_en', models.CharField(max_length=250, blank=True)),
                ('wikipedia_link_hu', models.CharField(max_length=250, blank=True)),
                ('imdb_rating', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('imdb_rating_refreshed_at', models.DateTimeField(null=True, blank=True)),
                ('number_of_awards', models.PositiveIntegerField(default=0)),
                ('number_of_links', models.PositiveIntegerField(default=0)),
                ('number_of_pictures', models.PositiveIntegerField(default=0)),
                ('main_premier', models.DateField(null=True, blank=True)),
                ('main_premier_year', models.PositiveIntegerField(null=True, blank=True)),
                ('slug_cache', models.CharField(max_length=250, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('open_for_vote_from', models.DateField(null=True, blank=True)),
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
                ('actor_subtype', models.CharField(default=b'F', max_length=1, choices=[(b'F', b'Full'), (b'V', b'Voice')])),
                ('role_name', models.CharField(max_length=250, blank=True)),
                ('slug_cache', models.CharField(max_length=250, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('artist', models.ForeignKey(to='ktapp.Artist')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
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
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('spoiler', models.BooleanField(default=False)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
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
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('film', models.ForeignKey(to='ktapp.Film')),
            ],
            options={
                'ordering': ['serial_number'],
            },
            bases=(models.Model,),
        ),
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
        migrations.CreateModel(
            name='Keyword',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=250)),
                ('keyword_type', models.CharField(default=b'O', max_length=1, choices=[(b'C', b'Country'), (b'G', b'Genre'), (b'M', b'Major'), (b'O', b'Other')])),
                ('slug_cache', models.CharField(max_length=250, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('old_imdb_name', models.CharField(max_length=250, blank=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
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
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
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
                ('content_html', models.TextField()),
                ('content_old_html', models.TextField(blank=True)),
                ('private', models.BooleanField(default=True)),
                ('owned_by', models.ForeignKey(related_name='owned_message', to=settings.AUTH_USER_MODEL)),
                ('sent_by', models.ForeignKey(related_name='sent_message', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('sent_to', models.ManyToManyField(related_name='received_message', null=True, to=settings.AUTH_USER_MODEL, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PasswordToken',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('token', models.CharField(unique=True, max_length=64)),
                ('valid_until', models.DateTimeField()),
                ('belongs_to', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
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
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
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
                ('slug_cache', models.CharField(max_length=250, blank=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('last_comment', models.ForeignKey(related_name='last_poll_comment', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='ktapp.Comment', null=True)),
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
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
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
                ('content_html', models.TextField()),
                ('content_old_html', models.TextField(blank=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('film', models.ForeignKey(to='ktapp.Film')),
            ],
            options={
                'ordering': ['created_at'],
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
                ('content_html', models.TextField()),
                ('content_old_html', models.TextField(blank=True)),
                ('approved', models.BooleanField(default=False)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('film', models.ForeignKey(to='ktapp.Film')),
            ],
            options={
                'ordering': ['created_at'],
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
                ('slug_cache', models.CharField(max_length=250, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
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
                ('slug_cache', models.CharField(max_length=250, blank=True)),
                ('closed_until', models.DateTimeField(null=True, blank=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
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
                ('content_html', models.TextField()),
                ('content_old_html', models.TextField(blank=True)),
                ('spoiler', models.BooleanField(default=False)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('film', models.ForeignKey(to='ktapp.Film')),
            ],
            options={
                'ordering': ['created_at'],
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
                ('when', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('channel', models.ForeignKey(to='ktapp.TVChannel')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('film', models.ForeignKey(to='ktapp.Film')),
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
                ('slug_cache', models.CharField(max_length=250, blank=True)),
                ('created_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
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
                ('when', models.DateTimeField(auto_now=True, auto_now_add=True, null=True)),
                ('shared_on_facebook', models.BooleanField(default=False)),
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
                ('wish_type', models.CharField(default=b'Y', max_length=1, choices=[(b'Y', b'Yes'), (b'N', b'No'), (b'G', b'Get')])),
                ('film', models.ForeignKey(to='ktapp.Film')),
                ('wished_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='wishlist',
            unique_together=set([('film', 'wished_by', 'wish_type')]),
        ),
        migrations.AlterUniqueTogether(
            name='vote',
            unique_together=set([('film', 'user')]),
        ),
        migrations.AddField(
            model_name='premier',
            name='premier_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='ktapp.PremierType', null=True),
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
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='ktapp.LinkSite', null=True),
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
        migrations.AlterUniqueTogether(
            name='filmkeywordrelationship',
            unique_together=set([('film', 'keyword')]),
        ),
        migrations.AddField(
            model_name='film',
            name='artists',
            field=models.ManyToManyField(to='ktapp.Artist', through='ktapp.FilmArtistRelationship'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='film',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
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
        migrations.AlterIndexTogether(
            name='comment',
            index_together=set([('created_at',), ('domain', 'created_at')]),
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
        migrations.AddField(
            model_name='ktuser',
            name='follow',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, through='ktapp.Follow'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ktuser',
            name='groups',
            field=models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of his/her group.', verbose_name='groups'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ktuser',
            name='user_permissions',
            field=models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions'),
            preserve_default=True,
        ),
    ]
