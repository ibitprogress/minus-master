# -*- coding: utf-8 -*-

from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe

from photos.models import PhotoAlbum, Photo


class PhotoAlbumEditForm(forms.ModelForm):

    class Meta:
        model = PhotoAlbum
        exclude = ('user', 'slug', 'size')


class PhotoEditForm(forms.ModelForm):

    class Meta:
        model = Photo
        exclude = ('date_created', 'image', 'album')


class PhotoAddForm(forms.ModelForm):
    album = forms.ModelChoiceField(queryset=PhotoAlbum.objects,
                                  widget=forms.HiddenInput)

    class Meta:
        model = Photo
        exclude = ('date_created')

    def clean(self):
        cd = self.cleaned_data

        try:
            if cd['image'].size > settings.PHOTO_MAX_SIZE:
                e = forms.ValidationError(mark_safe(\
                u'Розмір файлу не повинен перевищувати: ' + \
                str(settings.PHOTO_MAX_SIZE/1024/1024) + u'МБайт'))
                self._errors['image'] = e.messages
        except:
            pass

        return cd
