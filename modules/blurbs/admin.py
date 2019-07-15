from models import BlurbCategory, Blurb
from django.contrib import admin
from photos.admin import AlbumInline

class BlurbAdmin(admin.ModelAdmin):
    list_display = ('title','user','category','georegion', 'geocity','buysell')
    list_filter = ('category','georegion','buysell')
    search_fields = ['title', 'description']
    inlines = [AlbumInline,]
    readonly_fields = ['user']
admin.site.register(BlurbCategory)
admin.site.register(Blurb, BlurbAdmin)
