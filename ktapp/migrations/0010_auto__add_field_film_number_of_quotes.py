# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Film.number_of_quotes'
        db.add_column(u'ktapp_film', 'number_of_quotes',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Film.number_of_quotes'
        db.delete_column(u'ktapp_film', 'number_of_quotes')


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
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
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
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'ktapp.comment': {
            'Meta': {'ordering': "['-created_at']", 'object_name': 'Comment'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'domain': ('django.db.models.fields.CharField', [], {'default': "'F'", 'max_length': '1'}),
            'film': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ktapp.Film']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'poll': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ktapp.Poll']", 'null': 'True', 'blank': 'True'}),
            'reply_to': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ktapp.Comment']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'topic': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ktapp.Topic']", 'null': 'True', 'blank': 'True'})
        },
        u'ktapp.film': {
            'Meta': {'object_name': 'Film'},
            'artists': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['ktapp.Artist']", 'through': u"orm['ktapp.FilmArtistRelationship']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_comment': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'last_film_comment'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['ktapp.Comment']"}),
            'number_of_comments': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'number_of_quotes': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'number_of_ratings_1': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'number_of_ratings_2': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'number_of_ratings_3': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'number_of_ratings_4': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'number_of_ratings_5': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'orig_title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'other_titles': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'plot_summary': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'year': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        u'ktapp.filmartistrelationship': {
            'Meta': {'object_name': 'FilmArtistRelationship'},
            'actor_subtype': ('django.db.models.fields.CharField', [], {'default': "'F'", 'max_length': '1'}),
            'artist': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ktapp.Artist']"}),
            'film': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ktapp.Film']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'role_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'role_type': ('django.db.models.fields.CharField', [], {'default': "'D'", 'max_length': '1'})
        },
        u'ktapp.poll': {
            'Meta': {'object_name': 'Poll'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'ktapp.quote': {
            'Meta': {'ordering': "['-created_at']", 'object_name': 'Quote'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'film': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ktapp.Film']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'ktapp.topic': {
            'Meta': {'ordering': "['-last_comment']", 'object_name': 'Topic'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_comment': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'last_topic_comment'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['ktapp.Comment']"}),
            'number_of_comments': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'ktapp.vote': {
            'Meta': {'unique_together': "(['film', 'user'],)", 'object_name': 'Vote'},
            'film': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ktapp.Film']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rating': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'when': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['ktapp']