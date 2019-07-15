from minusstore.models import FileType, MinusAuthor, MinusRecord, MinusCategory, MinusStopWord
from django.contrib import admin
from django.contrib.flatpages.admin import FlatPageAdmin as FlatPageAdminOld
from django.contrib.flatpages.models import FlatPage

from tinymce.widgets import TinyMCE

class FlatPageAdmin(FlatPageAdminOld):
   def formfield_for_dbfield(self, db_field, **kwargs):
       if db_field.name == 'content':
           return db_field.formfield(widget=TinyMCE)
       return super(FlatPageAdmin, self).formfield_for_dbfield(db_field, **kwargs)

class MinusRecordAdmin(admin.ModelAdmin):
    exclude = ('user',)
    list_display = ('title','author', 'user', 'type')
    search_fields = ('title', 'author__name')

class MinusRecordInline(admin.StackedInline):
    model = MinusRecord
    exclude = ('user',)
    extra = 0

class MinusAuthorAdmin(admin.ModelAdmin):
    search_fields = ('name', )
    inlines = (MinusRecordInline,)

class MinusStopWordAdmin(admin.ModelAdmin):
    list_display = ('id','word','blocked')
    list_display_links = ('id',)
    list_editable = ('word','blocked')
        
admin.site.unregister(FlatPage)
admin.site.register(FlatPage, FlatPageAdmin)
admin.site.register(MinusRecord, MinusRecordAdmin)
admin.site.register(MinusAuthor, MinusAuthorAdmin)
admin.site.register(FileType)
admin.site.register(MinusStopWord, MinusStopWordAdmin)
admin.site.register(MinusCategory)
