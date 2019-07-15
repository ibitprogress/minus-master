# -*- coding: utf-8 -*-
from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import truncatewords_html

class NewsItem(models.Model):
    """news on site. so typical"""
    user = models.ForeignKey(User)
    title = models.CharField("Заголовок",
        max_length = 150)
    preview = models.TextField("Вступна частина",
        help_text = "Показується на загальній сторінці, якщо порожня — покажеться початок тексту новини",
        blank = True,
        null = True)
    body = models.TextField("Текст",
        help_text = "Показується після кнопки «читати далі»",
        blank = True)
    allow_comments = models.BooleanField("Дозволити коментарі",
        default = True)
    pub_date = models.DateTimeField(default=datetime.now,
                                       editable=True)
    def __unicode__(self):
        return self.title
    
    def get_preview(self):
        if not self.preview:
            return truncatewords_html(self.body, 50)
        else:
            return self.preview


    class Meta:
        ordering = ('-pub_date',)
        verbose_name = u'Новина'
        verbose_name_plural = u'Новини на сайті'
            
    @models.permalink
    def get_absolute_url(self):
        return ('news_detail', [str(self.id)])

