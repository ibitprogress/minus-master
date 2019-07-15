# -*- coding: utf-8 -*-

from django import forms

from forum.models import Thread, Post
from ck.fields import CKEditor

class CreateThreadForm(forms.Form):
    title = forms.CharField(label="Заголовок", max_length=100)
    body = forms.CharField(label="", widget=CKEditor(ck_attrs={'customConfig' : '/static/js/ckeditor/minusconf.js'}))
    subscribe = forms.BooleanField(label="Я хочу отримувати листи про нові повідомлення\
                                   в цій темі на мій e-mail", required=False)


class ReplyForm(forms.Form):
    body = forms.CharField(label="", widget=CKEditor(ck_attrs={'customConfig' : '/static/js/ckeditor/minusconf.js'}))
    subscribe = forms.BooleanField(label="Я хочу отримувати листи про нові повідомлення\
                                   в цій темі на мій e-mail", required=False)


class ThreadEditForm(forms.ModelForm):
    body = forms.CharField(label="", widget=CKEditor(ck_attrs={'customConfig' : '/static/js/ckeditor/minusconf.js'}))

    class Meta:
        model = Thread
        exclude = ('posts', 'views', 'latest_post_time')


class PostEditForm(forms.ModelForm):
    body = forms.CharField(label="", widget=CKEditor(ck_attrs={'customConfig' : '/static/js/ckeditor/minusconf.js'}))

    class Meta:
        model = Post
        exclude = ('thread', 'author', 'time')
