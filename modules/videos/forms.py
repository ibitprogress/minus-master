# -*- coding: utf-8 -*-

from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe

from videos.models import VideoAlbum, Video


class VideoAlbumEditForm(forms.ModelForm):

    class Meta:
        model = VideoAlbum
        exclude = ('user', 'slug', 'videos_count')


class VideoEditForm(forms.ModelForm):

    class Meta:
        model = Video
        exclude = ('date_created', 'embed_video', 'video_album')


class VideoAddForm(forms.ModelForm):
    video_album = forms.ModelChoiceField(queryset=VideoAlbum.objects,
                                  widget=forms.HiddenInput)

    class Meta:
        model = Video
        exclude = ('date_created')

    def clean(self):
        cd = self.cleaned_data
        try:
            if cd['embed_video']:
                code = cd['embed_video']        #here we define type of video
                if code.find('youtube.com') != -1:      #string search!
                    cd['embed_video'] = \
                    settings.INLINES_START_TAG+\
                    " youtube "\
                    + code \
                    + settings.INLINES_END_TAG      # actually more efficent
                                                    # validation goes in
                                                    # django_inlines 
                                                    # here we just find-out                          
                                                    # the type of embed
                else:
                    cd['embed_video'] = ''
                    e = forms.ValidationError(mark_safe(u"Невірний код вставки відео")) 
                    self._errors['embed_video'] = e.messages
        except:
            pass

        return cd
