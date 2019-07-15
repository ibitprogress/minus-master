from django.contrib import admin

from photos.models import PhotoAlbum, Photo
from django.contrib.contenttypes import generic

class AlbumInline(generic.GenericStackedInline):
    model = PhotoAlbum
    ct_fk_field = 'object_pk'
    readonly_fields = ['user']

class PhotoAdmin(admin.ModelAdmin):
    readonly_fields = ['user']

admin.site.register(PhotoAlbum, PhotoAdmin)
admin.site.register(Photo)
