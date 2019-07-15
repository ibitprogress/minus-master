from django.contrib import admin
from models import Banner, PlaceHolder

class BannersAdmin(admin.ModelAdmin):
    list_display = ('title','key', 'holder')
    search_fields = ('title','key')

class PlaceHolderAdmin(admin.ModelAdmin):
    list_display = ('title','key')

admin.site.register(Banner, BannersAdmin)
admin.site.register(PlaceHolder, PlaceHolderAdmin)
