from django import forms
from django.contrib.auth.models import User

from models import ChatRoom


class RoomCreateForm(forms.ModelForm):
    
    user = forms.ModelChoiceField(queryset=User.objects, widget=forms.HiddenInput)
    class Meta:
        model = ChatRoom
