# -*- coding: utf-8 -*-
from tddspry.django import TestCase
from news.models import NewsItem


from tddspry.django.helpers import USERNAME, PASSWORD
TEST_TITLE = "Hello, im title чи то я заголовок"
TEST_CONTENT = "contentcontent вміст"

class TestNews(TestCase):
    fixtures = ['fixtures/test_data.json']
    
    def setup(self):
        self.user = self.helper('create_user')
        self.moder = self.helper('create_user', username = 'moder', password = 'moder')
        self.moder.is_staff = True
        self.moder.save()

    def test_site_crud_news(self):
        self.login('moder', 'moder', url='auth_login', formid='id_login')
        self.go200('minus_index')
        self.go200('news_add')
        self.fv('news_add', 'title', TEST_TITLE)
        self.fv('news_add', 'body', TEST_CONTENT)
        self.submit200()
        self.assert_read(NewsItem,
                           title = TEST_TITLE,
                           body = TEST_CONTENT
                           )
        self.go200('news_edit', [1])
        self.fv('news_add', 'title', TEST_TITLE+"1")
        self.fv('news_add', 'body', TEST_CONTENT+"1")
        self.submit200()
        self.assert_read(NewsItem,
                           title = TEST_TITLE+"1",
                           body = TEST_CONTENT+"1"
                           )
        self.go200('news_delete', [1])
        self.fv('object_delete', '__confirm__', 1)
        self.submit200()
        self.url('news_index')
        self.assert_equal(NewsItem.objects.count(), 0)

    def test_show_news(self):
        self.login(USERNAME, PASSWORD,url='auth_login', formid='id_login')
        self.assert_create(NewsItem,
                           user=self.moder,
                           title = TEST_TITLE+"1",
                           body = TEST_CONTENT+"1",
                           allow_comments = False
                           )

        self.assert_create(NewsItem,
                           user=self.moder,
                           title = TEST_TITLE+"2",
                           body = TEST_CONTENT+"2"
                           )

        self.go200('news_index')
        self.find(TEST_TITLE+"1")
        self.find(TEST_TITLE+"2")
        self.find(TEST_CONTENT+"1")
        self.find(TEST_CONTENT+"2")
        self.go200('news_detail',[1])
        self.find(TEST_TITLE+"1")
        self.notfind('коментар') #comments are disabled
        self.go200('news_detail',[2])
        self.find(TEST_TITLE+"2")
        self.find('коментар') #comments are enabled

    def test_some_permissions(self):
        self.assert_create(NewsItem,
                           user=self.moder,
                           title = TEST_TITLE+"1",
                           body = TEST_CONTENT+"1",
                           allow_comments = False
                           )
        self.login('moder', 'moder', url='auth_login', formid='id_login')
        self.go200('news_index')
        self.find('Додати новину')
        self.find(TEST_TITLE+"1")
        self.find('Редагувати')
        self.go200('news_detail',[1])
        self.find('Редагувати')
        self.logout()
        self.login(USERNAME, PASSWORD, url='auth_login', formid='id_login')
        self.go200('news_index')
        self.notfind('Додати новину')
        self.find(TEST_TITLE+"1")
        self.notfind('Редагувати')
        self.go200('news_detail',[1])
        self.notfind('Редагувати')
