from models import NewsItem
from django.contrib import admin

class NewsItemAdmin(admin.ModelAdmin):
    exclude = ('user',)
        
admin.site.register(NewsItem, NewsItemAdmin)

