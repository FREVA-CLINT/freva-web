# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ResultTag'
        db.create_table(u'history_resulttag', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('result_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['history.Result'])),
            ('type', self.gf('django.db.models.fields.IntegerField')(max_length=2)),
            ('text', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'history', ['ResultTag'])

        # Adding model 'HistoryTag'
        db.create_table(u'history_historytag', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('history_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['history.History'])),
            ('type', self.gf('django.db.models.fields.IntegerField')(max_length=2)),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('uid', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['auth.User'], to_field='username', null=True, db_column='uid')),
        ))
        db.send_create_signal(u'history', ['HistoryTag'])

        # Adding model 'Configuration'
        db.create_table(u'history_configuration', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('history_id', self.gf('django.db.models.fields.related.ForeignKey')(related_name='history_id', to=orm['history.History'])),
            ('parameter_id', self.gf('django.db.models.fields.related.ForeignKey')(related_name='parameter_id', to=orm['plugins.Parameter'])),
            ('md5', self.gf('django.db.models.fields.CharField')(default='', max_length=32)),
            ('value', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('is_default', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'history', ['Configuration'])

        # Adding field 'History.version_details'
        db.add_column(u'history_history', 'version_details',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['plugins.Version']),
                      keep_default=False)

        # Adding field 'History.flag'
        db.add_column(u'history_history', 'flag',
                      self.gf('django.db.models.fields.IntegerField')(default=0, max_length=1),
                      keep_default=False)


        # Changing field 'History.uid'
        db.alter_column(u'history_history', 'uid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], to_field='username', db_column='uid'))
        # Adding index on 'History', fields ['uid']
        db.create_index(u'history_history', ['uid'])


        # Changing field 'History.version'
        db.alter_column(u'history_history', 'version', self.gf('django.db.models.fields.CharField')(max_length=20))
        # Adding field 'Result.preview_file'
        db.add_column(u'history_result', 'preview_file',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)


    def backwards(self, orm):
        # Removing index on 'History', fields ['uid']
        db.delete_index(u'history_history', ['uid'])

        # Deleting model 'ResultTag'
        db.delete_table(u'history_resulttag')

        # Deleting model 'HistoryTag'
        db.delete_table(u'history_historytag')

        # Deleting model 'Configuration'
        db.delete_table(u'history_configuration')

        # Deleting field 'History.version_details'
        db.delete_column(u'history_history', 'version_details_id')

        # Deleting field 'History.flag'
        db.delete_column(u'history_history', 'flag')


        # Changing field 'History.uid'
        db.alter_column(u'history_history', 'uid', self.gf('django.db.models.fields.CharField')(max_length=20))

        # Changing field 'History.version'
        db.alter_column(u'history_history', 'version', self.gf('django.db.models.fields.CharField')(max_length=10))
        # Deleting field 'Result.preview_file'
        db.delete_column(u'history_result', 'preview_file')


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
        u'history.configuration': {
            'Meta': {'object_name': 'Configuration'},
            'history_id': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'history_id'", 'to': u"orm['history.History']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'md5': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '32'}),
            'parameter_id': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'parameter_id'", 'to': u"orm['plugins.Parameter']"}),
            'value': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'history.history': {
            'Meta': {'object_name': 'History'},
            'configuration': ('django.db.models.fields.TextField', [], {}),
            'flag': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slurm_output': ('django.db.models.fields.TextField', [], {}),
            'status': ('django.db.models.fields.IntegerField', [], {'max_length': '1'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'tool': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'uid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'to_field': "'username'", 'db_column': "'uid'"}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'version_details': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': u"orm['plugins.Version']"})
        },
        u'history.historytag': {
            'Meta': {'object_name': 'HistoryTag'},
            'history_id': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['history.History']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'type': ('django.db.models.fields.IntegerField', [], {'max_length': '2'}),
            'uid': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['auth.User']", 'to_field': "'username'", 'null': 'True', 'db_column': "'uid'"})
        },
        u'history.result': {
            'Meta': {'object_name': 'Result'},
            'file_type': ('django.db.models.fields.IntegerField', [], {'max_length': '2'}),
            'history_id': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['history.History']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'output_file': ('django.db.models.fields.TextField', [], {}),
            'preview_file': ('django.db.models.fields.TextField', [], {'default': "''"})
        },
        u'history.resulttag': {
            'Meta': {'object_name': 'ResultTag'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'result_id': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['history.Result']"}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'type': ('django.db.models.fields.IntegerField', [], {'max_length': '2'})
        },
        u'plugins.parameter': {
            'Meta': {'object_name': 'Parameter'},
            'default': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'impact': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '1'}),
            'mandatory': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'parameter_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'parameter_type': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'tool': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'version': ('django.db.models.fields.IntegerField', [], {'max_length': '4'})
        },
        u'plugins.version': {
            'Meta': {'object_name': 'Version'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_version_api': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'internal_version_tool': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'repository': ('django.db.models.fields.TextField', [], {}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'tool': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        }
    }

    complete_apps = ['history']