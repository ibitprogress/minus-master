# -*- coding: utf-8 -*-
from django.views.generic.list_detail import object_list, object_detail
from django.views.generic.create_update import create_object, update_object,delete_object
from django.core.urlresolvers import reverse
from django.views.decorators.cache import cache_page



from models import NewsItem
from forms import NewsForm

@cache_page(60*5)
def news_index(request):
    news = NewsItem.objects.all().order_by('-pub_date')
    return object_list(
        request,
        queryset = news,
        template_name = 'news/news_index.html',
    )

def news_detail(request, id):
    return object_detail(
        request,
        queryset = NewsItem.objects.all(),
        object_id = id,
        template_name = 'news/news_detail.html',
        )

def news_add(request):
    return create_object(
        request,
        form_class = NewsForm,
        login_required = True,
        template_name = 'news/news_add_edit.html',
        )

def news_edit(request, id):
    return update_object(
        request,
        object_id = id,
        form_class = NewsForm,
        login_required = True,
        extra_context = {'edit':True,},
        template_name = 'news/news_add_edit.html',
        )

def news_delete(request, id):
    return delete_object(
        request,
        model = NewsItem,
        object_id = id,
        post_delete_redirect = reverse('news_index'),
        login_required = True,
        template_name = 'shared/object_delete_confirm.html',
        )

