# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'UserToplistItem'
        db.create_table(u'ktapp_usertoplistitem', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('usertoplist', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ktapp.UserToplist'])),
            ('serial_number', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
            ('film', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ktapp.Film'], null=True, blank=True)),
            ('director', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='director_usertoplist', null=True, to=orm['ktapp.Artist'])),
            ('actor', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='actor_usertoplist', null=True, to=orm['ktapp.Artist'])),
            ('comment', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'ktapp', ['UserToplistItem'])

        # Adding model 'UserToplist'
        db.create_table(u'ktapp_usertoplist', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ktapp.KTUser'], null=True, blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('ordered', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('quality', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('number_of_items', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('toplist_type', self.gf('django.db.models.fields.CharField')(default='F', max_length=1)),
        ))
        db.send_create_signal(u'ktapp', ['UserToplist'])


    def backwards(self, orm):
        # Deleting model 'UserToplistItem'
        db.delete_table(u'ktapp_usertoplistitem')

        # Deleting model 'UserToplist'
        db.delete_table(u'ktapp_usertoplist')


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
        u'ktapp.message': {
            'Meta': {'object_name': 'Message', 'index_together': "[['owned_by', 'sent_at']]"},
            'content': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owned_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'owned_message'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['ktapp.KTUser']"}),
            'private': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'sent_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'sent_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'sent_message'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['ktapp.KTUser']"}),
            'sent_to': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'received_message'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['ktapp.KTUser']"})
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
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ktapp.KTUser']", 'null': 'True', 'blank': 'True'}),
            'film': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ktapp.Film']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'ktapp.review': {
            'Meta': {'ordering': "['-created_at']", 'object_name': 'Review'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ktapp.KTUser']", 'null': 'True', 'blank': 'True'}),
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
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ktapp.KTUser']", 'null': 'True', 'blank': 'True'}),
            'film': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ktapp.Film']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'ktapp.tvchannel': {
            'Meta': {'object_name': 'TVChannel'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        },
        u'ktapp.tvfilm': {
            'Meta': {'object_name': 'TVFilm'},
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ktapp.TVChannel']", 'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ktapp.KTUser']", 'null': 'True', 'blank': 'True'}),
            'film': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ktapp.Film']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'when': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        u'ktapp.usertoplist': {
            'Meta': {'object_name': 'UserToplist'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ktapp.KTUser']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number_of_items': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'ordered': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'quality': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'toplist_type': ('django.db.models.fields.CharField', [], {'default': "'F'", 'max_length': '1'})
        },
        u'ktapp.usertoplistitem': {
            'Meta': {'object_name': 'UserToplistItem'},
            'actor': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'actor_usertoplist'", 'null': 'True', 'to': u"orm['ktapp.Artist']"}),
            'comment': ('django.db.models.fields.TextField', [], {}),
            'director': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'director_usertoplist'", 'null': 'True', 'to': u"orm['ktapp.Artist']"}),
            'film': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ktapp.Film']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'serial_number': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'usertoplist': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ktapp.UserToplist']"})
        },
        u'ktapp.vote': {
            'Meta': {'unique_together': "(['film', 'user'],)", 'object_name': 'Vote'},
            'film': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ktapp.Film']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rating': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ktapp.KTUser']"}),
            'when': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'})
        },
        u'ktapp.wishlist': {
            'Meta': {'object_name': 'Wishlist'},
            'film': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ktapp.Film']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'wish_type': ('django.db.models.fields.CharField', [], {'default': "'Y'", 'max_length': '1'}),
            'wished_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'wished_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ktapp.KTUser']", 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['ktapp']