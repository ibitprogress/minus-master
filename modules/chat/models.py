# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import permalink

# Create your models here.

class ChatRoom(models.Model):
    """holder for chats"""
    user = models.ForeignKey('auth.User',
            related_name='chat_rooms')
    title = models.CharField("Назва",max_length = 50)
    description = models.TextField("Опис", help_text = "В декількох словах, про що йтиме мова", max_length = 200, blank = True, null= True)
    users = []

    def get_absolute_url(self):
        return ('chat_room', [self.id])
    get_absolute_url = permalink(get_absolute_url)

