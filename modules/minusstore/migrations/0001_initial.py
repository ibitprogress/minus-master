# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'FileType'
        db.create_table('minusstore_filetype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type_name', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('display_name', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('filetype', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal('minusstore', ['FileType'])

        # Adding model 'MinusCategory'
        db.create_table('minusstore_minuscategory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('display_name', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
        ))
        db.send_create_signal('minusstore', ['MinusCategory'])

        # Adding model 'MinusAuthor'
        db.create_table('minusstore_minusauthor', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('minusstore', ['MinusAuthor'])

        # Adding M2M table for field filetypes on 'MinusAuthor'
        db.create_table('minusstore_minusauthor_filetypes', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('minusauthor', models.ForeignKey(orm['minusstore.minusauthor'], null=False)),
            ('filetype', models.ForeignKey(orm['minusstore.filetype'], null=False))
        ))
        db.create_unique('minusstore_minusauthor_filetypes', ['minusauthor_id', 'filetype_id'])

        # Adding model 'MinusRecord'
        db.create_table('minusstore_minusrecord', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='uploaded_records', to=orm['auth.User'])),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=2048, null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('is_folk', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(related_name='records_by', to=orm['minusstore.MinusAuthor'])),
            ('arrangeuathor', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('annotation', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('thematics', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('tempo', self.gf('django.db.models.fields.CharField')(default='normal', max_length=10)),
            ('staff', self.gf('django.db.models.fields.CharField')(default='solo', max_length=10)),
            ('gender', self.gf('django.db.models.fields.CharField')(default='all', max_length=10)),
            ('is_childish', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_amateur', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_ritual', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('lyrics', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('plusrecord', self.gf('django.db.models.fields.URLField')(max_length=2048, null=True, blank=True)),
            ('times_downloaded', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('pub_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('length', self.gf('django.db.models.fields.TimeField')(default=datetime.time(0, 0))),
            ('bitrate', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('filesize', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('embed_video', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='matched_records', to=orm['minusstore.FileType'])),
            ('rating_votes', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, blank=True)),
            ('rating_score', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
        ))
        db.send_create_signal('minusstore', ['MinusRecord'])

        # Adding M2M table for field categories on 'MinusRecord'
        db.create_table('minusstore_minusrecord_categories', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('minusrecord', models.ForeignKey(orm['minusstore.minusrecord'], null=False)),
            ('minuscategory', models.ForeignKey(orm['minusstore.minuscategory'], null=False))
        ))
        db.create_unique('minusstore_minusrecord_categories', ['minusrecord_id', 'minuscategory_id'])

        # Adding model 'MinusStats'
        db.create_table('minusstore_minusstats', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('rate', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('minus', self.gf('django.db.models.fields.related.ForeignKey')(related_name='downloads', to=orm['minusstore.MinusRecord'])),
        ))
        db.send_create_signal('minusstore', ['MinusStats'])

        # Adding model 'MinusWeekStats'
        db.create_table('minusstore_minusweekstats', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('rate', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('minus', self.gf('django.db.models.fields.related.ForeignKey')(related_name='weekly_downloads', to=orm['minusstore.MinusRecord'])),
        ))
        db.send_create_signal('minusstore', ['MinusWeekStats'])

        # Adding model 'CommentNotify'
        db.create_table('minusstore_commentnotify', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('comment', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['comments.Comment'], unique=True)),
            ('minus', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['minusstore.MinusRecord'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('is_seen', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('minusstore', ['CommentNotify'])


    def backwards(self, orm):
        
        # Deleting model 'FileType'
        db.delete_table('minusstore_filetype')

        # Deleting model 'MinusCategory'
        db.delete_table('minusstore_minuscategory')

        # Deleting model 'MinusAuthor'
        db.delete_table('minusstore_minusauthor')

        # Removing M2M table for field filetypes on 'MinusAuthor'
        db.delete_table('minusstore_minusauthor_filetypes')

        # Deleting model 'MinusRecord'
        db.delete_table('minusstore_minusrecord')

        # Removing M2M table for field categories on 'MinusRecord'
        db.delete_table('minusstore_minusrecord_categories')

        # Deleting model 'MinusStats'
        db.delete_table('minusstore_minusstats')

        # Deleting model 'MinusWeekStats'
        db.delete_table('minusstore_minusweekstats')

        # Deleting model 'CommentNotify'
        db.delete_table('minusstore_commentnotify')


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
        'comments.comment': {
            'Meta': {'ordering': "('submit_date',)", 'object_name': 'Comment', 'db_table': "'django_comments'"},
            'comment': ('django.db.models.fields.TextField', [], {'max_length': '3000'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'content_type_set_for_comment'", 'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_removed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'object_pk': ('django.db.models.fields.TextField', [], {}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'submit_date': ('django.db.models.fields.DateTimeField', [], {'default': 'None'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'comment_comments'", 'null': 'True', 'to': "orm['auth.User']"}),
            'user_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'user_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'user_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'minusstore.commentnotify': {
            'Meta': {'object_name': 'CommentNotify'},
            'comment': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['comments.Comment']", 'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_seen': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'minus': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['minusstore.MinusRecord']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'minusstore.filetype': {
            'Meta': {'ordering': "['type_name']", 'object_name': 'FileType'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'filetype': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type_name': ('django.db.models.fields.CharField', [], {'max_length': '15'})
        },
        'minusstore.minusauthor': {
            'Meta': {'ordering': "['name']", 'object_name': 'MinusAuthor'},
            'filetypes': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'authors_have'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['minusstore.FileType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'minusstore.minuscategory': {
            'Meta': {'ordering': "['name']", 'object_name': 'MinusCategory'},
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '15'})
        },
        'minusstore.minusrecord': {
            'Meta': {'ordering': "['-pub_date']", 'object_name': 'MinusRecord'},
            'annotation': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'arrangeuathor': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'records_by'", 'to': "orm['minusstore.MinusAuthor']"}),
            'bitrate': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'records_in_category'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['minusstore.MinusCategory']"}),
            'embed_video': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '2048', 'null': 'True', 'blank': 'True'}),
            'filesize': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'gender': ('django.db.models.fields.CharField', [], {'default': "'all'", 'max_length': '10'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_amateur': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_childish': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_folk': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_ritual': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'length': ('django.db.models.fields.TimeField', [], {'default': 'datetime.time(0, 0)'}),
            'lyrics': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'plusrecord': ('django.db.models.fields.URLField', [], {'max_length': '2048', 'null': 'True', 'blank': 'True'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'rating_score': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'rating_votes': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'}),
            'staff': ('django.db.models.fields.CharField', [], {'default': "'solo'", 'max_length': '10'}),
            'tempo': ('django.db.models.fields.CharField', [], {'default': "'normal'", 'max_length': '10'}),
            'thematics': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'times_downloaded': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'matched_records'", 'to': "orm['minusstore.FileType']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'uploaded_records'", 'to': "orm['auth.User']"})
        },
        'minusstore.minusstats': {
            'Meta': {'object_name': 'MinusStats'},
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'minus': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'downloads'", 'to': "orm['minusstore.MinusRecord']"}),
            'rate': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'minusstore.minusweekstats': {
            'Meta': {'object_name': 'MinusWeekStats'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'minus': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'weekly_downloads'", 'to': "orm['minusstore.MinusRecord']"}),
            'rate': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['minusstore']
