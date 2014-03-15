# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'KTUser'
        db.create_table(u'ktapp_ktuser', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('last_login', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('is_superuser', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('username', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('is_staff', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('date_joined', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('gender', self.gf('django.db.models.fields.CharField')(default='U', max_length=1)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
            ('year_of_birth', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal(u'ktapp', ['KTUser'])

        # Adding M2M table for field groups on 'KTUser'
        m2m_table_name = db.shorten_name(u'ktapp_ktuser_groups')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('ktuser', models.ForeignKey(orm[u'ktapp.ktuser'], null=False)),
            ('group', models.ForeignKey(orm[u'auth.group'], null=False))
        ))
        db.create_unique(m2m_table_name, ['ktuser_id', 'group_id'])

        # Adding M2M table for field user_permissions on 'KTUser'
        m2m_table_name = db.shorten_name(u'ktapp_ktuser_user_permissions')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('ktuser', models.ForeignKey(orm[u'ktapp.ktuser'], null=False)),
            ('permission', models.ForeignKey(orm[u'auth.permission'], null=False))
        ))
        db.create_unique(m2m_table_name, ['ktuser_id', 'permission_id'])

        # Adding model 'Film'
        db.create_table(u'ktapp_film', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('orig_title', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('other_titles', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('year', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('plot_summary', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('number_of_comments', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('last_comment', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='last_film_comment', null=True, on_delete=models.SET_NULL, to=orm['ktapp.Comment'])),
            ('number_of_ratings_1', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('number_of_ratings_2', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('number_of_ratings_3', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('number_of_ratings_4', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('number_of_ratings_5', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('number_of_quotes', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('number_of_trivias', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('number_of_reviews', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('number_of_keywords', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('imdb_link', self.gf('django.db.models.fields.CharField')(max_length=16, blank=True)),
            ('porthu_link', self.gf('django.db.models.fields.CharField')(max_length=16, blank=True)),
            ('wikipedia_link_en', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('wikipedia_link_hu', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('imdb_rating', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('imdb_rating_refreshed_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('number_of_awards', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('number_of_links', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('number_of_pictures', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('main_premier', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('main_premier_year', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'ktapp', ['Film'])

        # Adding model 'PremierType'
        db.create_table(u'ktapp_premiertype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=250)),
        ))
        db.send_create_signal(u'ktapp', ['PremierType'])

        # Adding model 'Premier'
        db.create_table(u'ktapp_premier', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('film', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ktapp.Film'])),
            ('when', self.gf('django.db.models.fields.DateField')()),
            ('premier_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ktapp.PremierType'], null=True, blank=True)),
        ))
        db.send_create_signal(u'ktapp', ['Premier'])

        # Adding model 'Vote'
        db.create_table(u'ktapp_vote', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('film', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ktapp.Film'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ktapp.KTUser'])),
            ('rating', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('when', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'ktapp', ['Vote'])

        # Adding unique constraint on 'Vote', fields ['film', 'user']
        db.create_unique(u'ktapp_vote', ['film_id', 'user_id'])

        # Adding model 'Comment'
        db.create_table(u'ktapp_comment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('domain', self.gf('django.db.models.fields.CharField')(default='F', max_length=1)),
            ('film', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ktapp.Film'], null=True, blank=True)),
            ('topic', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ktapp.Topic'], null=True, blank=True)),
            ('poll', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ktapp.Poll'], null=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ktapp.KTUser'])),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('reply_to', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ktapp.Comment'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('rating', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'ktapp', ['Comment'])

        # Adding model 'Topic'
        db.create_table(u'ktapp_topic', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('number_of_comments', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ktapp.KTUser'])),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_comment', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='last_topic_comment', null=True, on_delete=models.SET_NULL, to=orm['ktapp.Comment'])),
        ))
        db.send_create_signal(u'ktapp', ['Topic'])

        # Adding model 'Poll'
        db.create_table(u'ktapp_poll', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=250)),
        ))
        db.send_create_signal(u'ktapp', ['Poll'])

        # Adding model 'Quote'
        db.create_table(u'ktapp_quote', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('film', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ktapp.Film'], null=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ktapp.KTUser'])),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('content', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'ktapp', ['Quote'])

        # Adding model 'Trivia'
        db.create_table(u'ktapp_trivia', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('film', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ktapp.Film'], null=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ktapp.KTUser'])),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('content', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'ktapp', ['Trivia'])

        # Adding model 'Review'
        db.create_table(u'ktapp_review', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('film', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ktapp.Film'], null=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ktapp.KTUser'])),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('content', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'ktapp', ['Review'])

        # Adding model 'Award'
        db.create_table(u'ktapp_award', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('film', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ktapp.Film'])),
            ('artist', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ktapp.Artist'], null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('year', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('note', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
        ))
        db.send_create_signal(u'ktapp', ['Award'])

        # Adding model 'LinkSite'
        db.create_table(u'ktapp_linksite', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=250)),
        ))
        db.send_create_signal(u'ktapp', ['LinkSite'])

        # Adding model 'Link'
        db.create_table(u'ktapp_link', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('film', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ktapp.Film'])),
            ('linksite', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ktapp.LinkSite'], null=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ktapp.KTUser'])),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('link_type', self.gf('django.db.models.fields.CharField')(default='-', max_length=1)),
            ('lead', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'ktapp', ['Link'])

        # Adding model 'Artist'
        db.create_table(u'ktapp_artist', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('gender', self.gf('django.db.models.fields.CharField')(default='U', max_length=1)),
        ))
        db.send_create_signal(u'ktapp', ['Artist'])

        # Adding model 'FilmArtistRelationship'
        db.create_table(u'ktapp_filmartistrelationship', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('film', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ktapp.Film'])),
            ('artist', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ktapp.Artist'])),
            ('role_type', self.gf('django.db.models.fields.CharField')(default='D', max_length=1)),
            ('actor_subtype', self.gf('django.db.models.fields.CharField')(default='F', max_length=1)),
            ('role_name', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
        ))
        db.send_create_signal(u'ktapp', ['FilmArtistRelationship'])

        # Adding model 'Keyword'
        db.create_table(u'ktapp_keyword', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('keyword_type', self.gf('django.db.models.fields.CharField')(default='O', max_length=1)),
        ))
        db.send_create_signal(u'ktapp', ['Keyword'])

        # Adding model 'FilmKeywordRelationship'
        db.create_table(u'ktapp_filmkeywordrelationship', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('film', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ktapp.Film'])),
            ('keyword', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ktapp.Keyword'])),
        ))
        db.send_create_signal(u'ktapp', ['FilmKeywordRelationship'])

        # Adding model 'Sequel'
        db.create_table(u'ktapp_sequel', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('sequel_type', self.gf('django.db.models.fields.CharField')(default='S', max_length=1)),
        ))
        db.send_create_signal(u'ktapp', ['Sequel'])

        # Adding model 'FilmSequelRelationship'
        db.create_table(u'ktapp_filmsequelrelationship', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('film', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ktapp.Film'])),
            ('sequel', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ktapp.Sequel'])),
            ('serial_number', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
        ))
        db.send_create_signal(u'ktapp', ['FilmSequelRelationship'])

        # Adding model 'Picture'
        db.create_table(u'ktapp_picture', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('img', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('width', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('height', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ktapp.KTUser'])),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('source_url', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('picture_type', self.gf('django.db.models.fields.CharField')(default='O', max_length=1)),
            ('film', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ktapp.Film'])),
        ))
        db.send_create_signal(u'ktapp', ['Picture'])

        # Adding M2M table for field artists on 'Picture'
        m2m_table_name = db.shorten_name(u'ktapp_picture_artists')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('picture', models.ForeignKey(orm[u'ktapp.picture'], null=False)),
            ('artist', models.ForeignKey(orm[u'ktapp.artist'], null=False))
        ))
        db.create_unique(m2m_table_name, ['picture_id', 'artist_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'Vote', fields ['film', 'user']
        db.delete_unique(u'ktapp_vote', ['film_id', 'user_id'])

        # Deleting model 'KTUser'
        db.delete_table(u'ktapp_ktuser')

        # Removing M2M table for field groups on 'KTUser'
        db.delete_table(db.shorten_name(u'ktapp_ktuser_groups'))

        # Removing M2M table for field user_permissions on 'KTUser'
        db.delete_table(db.shorten_name(u'ktapp_ktuser_user_permissions'))

        # Deleting model 'Film'
        db.delete_table(u'ktapp_film')

        # Deleting model 'PremierType'
        db.delete_table(u'ktapp_premiertype')

        # Deleting model 'Premier'
        db.delete_table(u'ktapp_premier')

        # Deleting model 'Vote'
        db.delete_table(u'ktapp_vote')

        # Deleting model 'Comment'
        db.delete_table(u'ktapp_comment')

        # Deleting model 'Topic'
        db.delete_table(u'ktapp_topic')

        # Deleting model 'Poll'
        db.delete_table(u'ktapp_poll')

        # Deleting model 'Quote'
        db.delete_table(u'ktapp_quote')

        # Deleting model 'Trivia'
        db.delete_table(u'ktapp_trivia')

        # Deleting model 'Review'
        db.delete_table(u'ktapp_review')

        # Deleting model 'Award'
        db.delete_table(u'ktapp_award')

        # Deleting model 'LinkSite'
        db.delete_table(u'ktapp_linksite')

        # Deleting model 'Link'
        db.delete_table(u'ktapp_link')

        # Deleting model 'Artist'
        db.delete_table(u'ktapp_artist')

        # Deleting model 'FilmArtistRelationship'
        db.delete_table(u'ktapp_filmartistrelationship')

        # Deleting model 'Keyword'
        db.delete_table(u'ktapp_keyword')

        # Deleting model 'FilmKeywordRelationship'
        db.delete_table(u'ktapp_filmkeywordrelationship')

        # Deleting model 'Sequel'
        db.delete_table(u'ktapp_sequel')

        # Deleting model 'FilmSequelRelationship'
        db.delete_table(u'ktapp_filmsequelrelationship')

        # Deleting model 'Picture'
        db.delete_table(u'ktapp_picture')

        # Removing M2M table for field artists on 'Picture'
        db.delete_table(db.shorten_name(u'ktapp_picture_artists'))


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'ktapp.artist': {
            'Meta': {'ordering': "['name']", 'object_name': 'Artist'},
            'films': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['ktapp.Film']", 'through': u"orm['ktapp.FilmArtistRelationship']", 'symmetrical': 'False'}),
            'gender': ('django.db.models.fields.CharField', [], {'default': "'U'", 'max_length': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        },
        u'ktapp.award': {
            'Meta': {'object_name': 'Award'},
            'artist': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ktapp.Artist']", 'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'film': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ktapp.Film']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'year': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        u'ktapp.comment': {
            'Meta': {'ordering': "['-created_at']", 'object_name': 'Comment'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ktapp.KTUser']"}),
            'domain': ('django.db.models.fields.CharField', [], {'default': "'F'", 'max_length': '1'}),
            'film': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ktapp.Film']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'poll': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ktapp.Poll']", 'null': 'True', 'blank': 'True'}),
            'rating': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'reply_to': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ktapp.Comment']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'topic': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ktapp.Topic']", 'null': 'True', 'blank': 'True'})
        },
        u'ktapp.film': {
            'Meta': {'object_name': 'Film'},
            'artists': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['ktapp.Artist']", 'through': u"orm['ktapp.FilmArtistRelationship']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imdb_link': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'imdb_rating': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'imdb_rating_refreshed_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'keywords': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['ktapp.Keyword']", 'through': u"orm['ktapp.FilmKeywordRelationship']", 'symmetrical': 'False'}),
            'last_comment': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'last_film_comment'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['ktapp.Comment']"}),
            'main_premier': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'main_premier_year': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'number_of_awards': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'number_of_comments': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'number_of_keywords': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'number_of_links': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'number_of_pictures': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'number_of_quotes': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'number_of_ratings_1': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'number_of_ratings_2': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'number_of_ratings_3': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'number_of_ratings_4': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'number_of_ratings_5': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'number_of_reviews': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'number_of_trivias': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'orig_title': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'other_titles': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'plot_summary': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'porthu_link': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'sequels': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['ktapp.Sequel']", 'through': u"orm['ktapp.FilmSequelRelationship']", 'symmetrical': 'False'}),
            'wikipedia_link_en': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'wikipedia_link_hu': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'year': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        u'ktapp.filmartistrelationship': {
            'Meta': {'object_name': 'FilmArtistRelationship'},
            'actor_subtype': ('django.db.models.fields.CharField', [], {'default': "'F'", 'max_length': '1'}),
            'artist': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ktapp.Artist']"}),
            'film': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ktapp.Film']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'role_name': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'role_type': ('django.db.models.fields.CharField', [], {'default': "'D'", 'max_length': '1'})
        },
        u'ktapp.filmkeywordrelationship': {
            'Meta': {'object_name': 'FilmKeywordRelationship'},
            'film': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ktapp.Film']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keyword': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ktapp.Keyword']"})
        },
        u'ktapp.filmsequelrelationship': {
            'Meta': {'ordering': "['serial_number']", 'object_name': 'FilmSequelRelationship'},
            'film': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ktapp.Film']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sequel': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ktapp.Sequel']"}),
            'serial_number': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'})
        },
        u'ktapp.keyword': {
            'Meta': {'ordering': "['keyword_type', 'name']", 'object_name': 'Keyword'},
            'films': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['ktapp.Film']", 'through': u"orm['ktapp.FilmKeywordRelationship']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keyword_type': ('django.db.models.fields.CharField', [], {'default': "'O'", 'max_length': '1'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        },
        u'ktapp.ktuser': {
            'Meta': {'object_name': 'KTUser'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'default': "'U'", 'max_length': '1'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'year_of_birth': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        u'ktapp.link': {
            'Meta': {'object_name': 'Link'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ktapp.KTUser']"}),
            'film': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ktapp.Film']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lead': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'link_type': ('django.db.models.fields.CharField', [], {'default': "'-'", 'max_length': '1'}),
            'linksite': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ktapp.LinkSite']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        },
        u'ktapp.linksite': {
            'Meta': {'object_name': 'LinkSite'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        },
        u'ktapp.picture': {
            'Meta': {'object_name': 'Picture'},
            'artists': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['ktapp.Artist']", 'symmetrical': 'False', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ktapp.KTUser']"}),
            'film': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ktapp.Film']"}),
            'height': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'img': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'picture_type': ('django.db.models.fields.CharField', [], {'default': "'O'", 'max_length': '1'}),
            'source_url': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'width': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        u'ktapp.poll': {
            'Meta': {'object_name': 'Poll'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        },
        u'ktapp.premier': {
            'Meta': {'ordering': "['when', 'premier_type', 'film']", 'object_name': 'Premier'},
            'film': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ktapp.Film']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'premier_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ktapp.PremierType']", 'null': 'True', 'blank': 'True'}),
            'when': ('django.db.models.fields.DateField', [], {})
        },
        u'ktapp.premiertype': {
            'Meta': {'object_name': 'PremierType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        },
        u'ktapp.quote': {
            'Meta': {'ordering': "['-created_at']", 'object_name': 'Quote'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ktapp.KTUser']"}),
            'film': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ktapp.Film']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'ktapp.review': {
            'Meta': {'ordering': "['-created_at']", 'object_name': 'Review'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ktapp.KTUser']"}),
            'film': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ktapp.Film']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'ktapp.sequel': {
            'Meta': {'ordering': "['sequel_type', 'name']", 'object_name': 'Sequel'},
            'films': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['ktapp.Film']", 'through': u"orm['ktapp.FilmSequelRelationship']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'sequel_type': ('django.db.models.fields.CharField', [], {'default': "'S'", 'max_length': '1'})
        },
        u'ktapp.topic': {
            'Meta': {'ordering': "['-last_comment']", 'object_name': 'Topic'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ktapp.KTUser']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_comment': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'last_topic_comment'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['ktapp.Comment']"}),
            'number_of_comments': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        },
        u'ktapp.trivia': {
            'Meta': {'ordering': "['-created_at']", 'object_name': 'Trivia'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ktapp.KTUser']"}),
            'film': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ktapp.Film']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'ktapp.vote': {
            'Meta': {'unique_together': "(['film', 'user'],)", 'object_name': 'Vote'},
            'film': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ktapp.Film']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rating': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ktapp.KTUser']"}),
            'when': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['ktapp']