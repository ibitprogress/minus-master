# -*- coding: utf-8 -*-
from django.test import TestCase
from django.conf import settings
from tddspry.django import TestCase
from django.contrib.auth.models import User

from news.models import NewsItem

TEST_TITLE = "Hello, i'm title"
TEST_CONTENT = "contentcontent"
TEST_USERNAME = 'testuser'
TEST_PASSWORD = 'qwerty'
TEST_EMAIL = 'test@mail.com'
TEST_NAME = 'Sometestname'

class TestNews(TestCase):

    def setup(self):
        self.user = self.helper('create_user')

    def test_crud(self):
        """
        create read update delete
        """
        new = self.assert_create(NewsItem,
                           user=self.user,
                           title = TEST_TITLE,
                           body = TEST_CONTENT
                           )

        self.assert_read(NewsItem,
                           user=self.user,
                           title = TEST_TITLE,
                           body = TEST_CONTENT
                           )

        self.assert_update(new,
                           user=self.user,
                           title = "t",
                           body = "b"
                           )
        self.assert_delete(NewsItem,
                           user=self.user,
                           title = "t",
                           body = "b"
                           )


