from django.conf import settings
from django import forms
from django.contrib.auth.models import User
from models import NewsItem
from ck.fields import CKEditor

class NewsForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects,
        widget=forms.HiddenInput)
    class Meta:
        model = NewsItem
        widgets = {
                    'body': CKEditor(ck_attrs={'customConfig' : settings.MEDIA_URL+'js/ckeditor/minusconf.js'})
                }
        exclude = ('pub_date',)

