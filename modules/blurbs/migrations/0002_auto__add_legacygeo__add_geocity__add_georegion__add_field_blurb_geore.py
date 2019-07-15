# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'LegacyGeo'
        db.create_table(u'geo', (
            ('id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('area_id', self.gf('django.db.models.fields.IntegerField')()),
            ('region_id', self.gf('django.db.models.fields.IntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=765)),
            ('type', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('blurbs', ['LegacyGeo'])

        # Adding model 'GeoCity'
        db.create_table('blurbs_geocity', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('region', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['blurbs.GeoRegion'])),
            ('is_city', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('blurbs', ['GeoCity'])

        # Adding model 'GeoRegion'
        db.create_table('blurbs_georegion', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal('blurbs', ['GeoRegion'])

        # Adding field 'Blurb.georegion'
        db.add_column('blurbs_blurb', 'georegion', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['blurbs.GeoRegion'], null=True, blank=True), keep_default=False)

        # Adding field 'Blurb.geocity'
        db.add_column('blurbs_blurb', 'geocity', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['blurbs.GeoCity'], null=True, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting model 'LegacyGeo'
        db.delete_table(u'geo')

        # Deleting model 'GeoCity'
        db.delete_table('blurbs_geocity')

        # Deleting model 'GeoRegion'
        db.delete_table('blurbs_georegion')

        # Deleting field 'Blurb.georegion'
        db.delete_column('blurbs_blurb', 'georegion_id')

        # Deleting field 'Blurb.geocity'
        db.delete_column('blurbs_blurb', 'geocity_id')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'blurbs.blurb': {
            'Meta': {'ordering': "('-pub_date',)", 'object_name': 'Blurb'},
            'buysell': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['blurbs.BlurbCategory']", 'blank': 'True'}),
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['blurbs.BlurbCity']", 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '1000', 'blank': 'True'}),
            'geocity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['blurbs.GeoCity']", 'null': 'True', 'blank': 'True'}),
            'georegion': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['blurbs.GeoRegion']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'blurbs.blurbcategory': {
            'Meta': {'object_name': 'BlurbCategory'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '60', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '60'})
        },
        'blurbs.blurbcity': {
            'Meta': {'object_name': 'BlurbCity'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '60', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '60'})
        },
        'blurbs.geocity': {
            'Meta': {'object_name': 'GeoCity'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_city': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['blurbs.GeoRegion']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'blurbs.georegion': {
            'Meta': {'object_name': 'GeoRegion'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'blurbs.legacygeo': {
            'Meta': {'object_name': 'LegacyGeo', 'db_table': "u'geo'"},
            'area_id': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '765'}),
            'region_id': ('django.db.models.fields.IntegerField', [], {}),
            'type': ('django.db.models.fields.IntegerField', [], {})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['blurbs']
