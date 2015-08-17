# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'UserProfile'
        db.create_table('user_profile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(related_name='profile', unique=True, to=orm['auth.User'])),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal(u'user_profile', ['UserProfile'])

        # Adding model 'Relationship'
        db.create_table(u'user_profile_relationship', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('from_person', self.gf('django.db.models.fields.related.ForeignKey')(related_name='from_people', to=orm['user_profile.UserProfile'])),
            ('to_person', self.gf('django.db.models.fields.related.ForeignKey')(related_name='to_people', to=orm['user_profile.UserProfile'])),
            ('status', self.gf('django.db.models.fields.IntegerField')()),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'user_profile', ['Relationship'])

        # Adding unique constraint on 'Relationship', fields ['from_person', 'to_person', 'status']
        db.create_unique(u'user_profile_relationship', ['from_person_id', 'to_person_id', 'status'])

        # Adding model 'LikeProfile'
        db.create_table(u'user_profile_likeprofile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('from_like', self.gf('django.db.models.fields.related.ForeignKey')(related_name='from_likeprofile', to=orm['user_profile.UserProfile'])),
            ('to_like', self.gf('django.db.models.fields.related.ForeignKey')(related_name='to_likeprofile', to=orm['user_profile.UserProfile'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'user_profile', ['LikeProfile'])

        # Adding unique constraint on 'LikeProfile', fields ['from_like', 'to_like']
        db.create_unique(u'user_profile_likeprofile', ['from_like_id', 'to_like_id'])

        # Adding model 'Request'
        db.create_table(u'user_profile_request', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('emitter', self.gf('django.db.models.fields.related.ForeignKey')(related_name='from_request', to=orm['user_profile.UserProfile'])),
            ('receiver', self.gf('django.db.models.fields.related.ForeignKey')(related_name='to_request', to=orm['user_profile.UserProfile'])),
            ('status', self.gf('django.db.models.fields.IntegerField')()),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'user_profile', ['Request'])

        # Adding unique constraint on 'Request', fields ['emitter', 'receiver', 'status']
        db.create_unique(u'user_profile_request', ['emitter_id', 'receiver_id', 'status'])


    def backwards(self, orm):
        # Removing unique constraint on 'Request', fields ['emitter', 'receiver', 'status']
        db.delete_unique(u'user_profile_request', ['emitter_id', 'receiver_id', 'status'])

        # Removing unique constraint on 'LikeProfile', fields ['from_like', 'to_like']
        db.delete_unique(u'user_profile_likeprofile', ['from_like_id', 'to_like_id'])

        # Removing unique constraint on 'Relationship', fields ['from_person', 'to_person', 'status']
        db.delete_unique(u'user_profile_relationship', ['from_person_id', 'to_person_id', 'status'])

        # Deleting model 'UserProfile'
        db.delete_table('user_profile')

        # Deleting model 'Relationship'
        db.delete_table(u'user_profile_relationship')

        # Deleting model 'LikeProfile'
        db.delete_table(u'user_profile_likeprofile')

        # Deleting model 'Request'
        db.delete_table(u'user_profile_request')


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
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'publications.publication': {
            'Meta': {'object_name': 'Publication'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'is_response_from': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'responses'", 'null': 'True', 'to': u"orm['publications.Publication']"}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'to_publication'", 'to': u"orm['user_profile.UserProfile']"}),
            'writer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'from_publication'", 'to': u"orm['user_profile.UserProfile']"})
        },
        u'user_profile.likeprofile': {
            'Meta': {'unique_together': "(('from_like', 'to_like'),)", 'object_name': 'LikeProfile'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'from_like': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'from_likeprofile'", 'to': u"orm['user_profile.UserProfile']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'to_like': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'to_likeprofile'", 'to': u"orm['user_profile.UserProfile']"})
        },
        u'user_profile.relationship': {
            'Meta': {'unique_together': "(('from_person', 'to_person', 'status'),)", 'object_name': 'Relationship'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'from_person': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'from_people'", 'to': u"orm['user_profile.UserProfile']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {}),
            'to_person': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'to_people'", 'to': u"orm['user_profile.UserProfile']"})
        },
        u'user_profile.request': {
            'Meta': {'unique_together': "(('emitter', 'receiver', 'status'),)", 'object_name': 'Request'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'emitter': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'from_request'", 'to': u"orm['user_profile.UserProfile']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'receiver': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'to_request'", 'to': u"orm['user_profile.UserProfile']"}),
            'status': ('django.db.models.fields.IntegerField', [], {})
        },
        u'user_profile.userprofile': {
            'Meta': {'object_name': 'UserProfile', 'db_table': "'user_profile'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'likeprofiles': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'likesToMe'", 'symmetrical': 'False', 'through': u"orm['user_profile.LikeProfile']", 'to': u"orm['user_profile.UserProfile']"}),
            'publications': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'publications_to'", 'symmetrical': 'False', 'through': u"orm['publications.Publication']", 'to': u"orm['user_profile.UserProfile']"}),
            'relationships': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'related_to'", 'symmetrical': 'False', 'through': u"orm['user_profile.Relationship']", 'to': u"orm['user_profile.UserProfile']"}),
            'requests': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'requestsToMe'", 'symmetrical': 'False', 'through': u"orm['user_profile.Request']", 'to': u"orm['user_profile.UserProfile']"}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'profile'", 'unique': 'True', 'to': u"orm['auth.User']"})
        }
    }

    complete_apps = ['user_profile']