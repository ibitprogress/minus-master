# -*- coding: utf-8 -*-

import datetime
from django.test import TestCase
from django.conf import settings
from tddspry.django import TestCase
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from users.models import UserProfile
from forum.context_processors import moderator
from forum.models import Forum, Thread, Post

TEST_USERNAME = 'testuser'
TEST_PASSWORD = 'qwerty'
TEST_EMAIL = 'test@mail.com'


class TestModeratorContext(TestCase):
    """
    Cases for testing of moderator context
    """
    fixtures = ['fixtures/test_data.json']

    def test_user_is_authenticated(self):
        """
        Case when user is logged in, but has no moderator atribute
        """
        user = self.helper('create_user', 'username', 'password')
        self.login('username', 'password','auth_login','id_login')
        self.url(settings.LOGIN_REDIRECT_URL)
        request = self.go('/')
        self.assert_false(moderator(request)['moderator'])

    def test_user_is_anonymous(self):
        """
        Case when user is anonymous
        """
        request = self.go('/')
        self.assert_false(moderator(request)['moderator'])

    def test_user_is_moderator(self):
        """
        Case when user is a moderator
        """
        user = self.helper('create_user', 'username', 'password')
        profile = self.assert_read(UserProfile, user=user)
        self.assert_update(user, is_staff=True)
        user = self.assert_read(User,username = 'username')
        self.assert_true(user.is_staff)
        forum = self.assert_create(Forum, title='Some fancy forum',
                                   slug='some-fancy-forum',
                                   description='Bla-bla-bla')
        thread = self.assert_create(Thread, forum=forum,
                                    title='Cool thread')
        post = self.assert_create(Post, author=user, thread=thread,
                                 body='lalala', time=datetime.datetime.now())
        self.login('username', 'password', 'auth_login','id_login')
        self.url(settings.LOGIN_REDIRECT_URL)
        request = self.go200('forum_thread_list', ['some-fancy-forum'])
        self.find('Редагувати')
