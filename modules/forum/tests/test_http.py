# -*- coding: utf-8 -*-

import datetime
from tddspry.django import TestCase

from django.conf import settings
from django.contrib.sites.models import Site
from forum.models import Forum, Thread, Post, Subscription
from users.models import UserProfile


class TestForumViews(TestCase):
    """
    Tests for forum views
    """
    fixtures = ['fixtures/test_data.json']

    def setup(self):
        global user, forum, thread
        user = self.helper('create_user', 'username', 'password')
        forum = self.assert_create(Forum, title='Some fancy forum',
                                   slug='some-fancy-forum',
                                   description='Bla-bla-bla')
        thread = self.assert_create(Thread, forum=forum,
                                    title='Cool thread')
        post = self.assert_create(Post, author=user, thread=thread,
                                  body='lalala',
                                  time=datetime.datetime.now())
        
    def test_index(self):
        """
        Forum index view
        """
        self.go200('forum_index')
        self.find('Some fancy forum')
        
    def test_thread_list(self):
        """
        Thread list view
        """
        self.go200('forum_thread_list', [forum.slug])
        self.find('Cool thread')
        
    def test_thread(self):
        """
        Thread view
        """
        self.go200('forum_view_thread', [thread.id])
        self.find('lalala')
        
    def test_subscriptions_anonymous(self):
        """
        Test subscriptions view when user is 
        anonymous
        """
        self.go200('forum_index')
        self.notfind('Оновити підписки')
        self.go200('forum_subscriptions')
        self.url(self.build_url('auth_login')+'.*')
        
    def test_subscriptions(self):
        """
        Test subscriptions view
        """
        self.helper('create_user', 'testuser', 'password')
        self.login('testuser', 'password', 'auth_login','id_login')
        self.url(settings.LOGIN_REDIRECT_URL)
        self.go200('forum_index')
        self.find('Оновити підписки')
        self.go200('forum_subscriptions')
        self.find('Ви не підписані на жодну з тем')
        
    def test_new_thread(self):
        """
        Test new thread view
        """
        self.helper('create_user', 'testuser', 'password')
        self.login('testuser', 'password', 'auth_login','id_login')
        self.url(settings.LOGIN_REDIRECT_URL)
        self.go200('forum_new_thread', [forum.slug])
        self.showforms()
        self.formclear('id_newthread')
        self.fv('id_newthread', 'id_title', 'Some cool new thread')
        self.fv('id_newthread', 'id_body', 'Hello world!')
        self.submit200()
        self.go200('forum_thread_list', [forum.slug])
        self.find('Some cool new thread')
        self.go200('forum_view_thread', [2])
        self.find('Hello world!')
        
    def test_new_thread_anonymous(self):
        """
        Test new thread view for anonymous
        """
        self.go200('forum_thread_list', [forum.slug])
        self.find('Для створення нових тем — будь-ласка авторизуйтесь.')
        self.go200('forum_new_thread', [forum.slug])
        self.url(settings.LOGIN_REDIRECT_URL+'.*')
        
    def test_thread_reply(self):
        """
        Test thread reply view
        """
        self.helper('create_user', 'testuser', 'password')
        self.login('testuser', 'password', 'auth_login','id_login')
        self.url(settings.LOGIN_REDIRECT_URL)
        self.go200('forum_reply_thread', [thread.id])
        self.showforms()
        self.formclear('id_forum_reply')
        self.fv('id_forum_reply', 'id_body', 'Boom shak a lak')
        self.submit200()
        self.go200('forum_view_thread', [thread.id])
        self.find('Boom shak a lak')
        
    def test_thread_reply_anonymous(self):
        """
        Test thread reply view for anonymous
        """
        self.go200('forum_view_thread', [thread.id])
        self.find('Будь-ласка авторизуйтесь для того щоб залишати повідомлення.')
        self.go200('forum_reply_thread', [thread.id])
        self.url(settings.LOGIN_REDIRECT_URL+'.*')
        
    def test_moderator_edit_thread(self):
        """
        Thread edit view for moderators
        """
        moderator = self.helper('create_user', 'moder', 'password')
        moderator_profile = self.assert_read(UserProfile,
                                              user=moderator)
        self.assert_update(moderator, is_staff=True)
        self.login('moder', 'password', 'auth_login','id_login')
        self.url(settings.LOGIN_REDIRECT_URL)
        self.go200('forum_thread_list', [forum.slug])
        self.find('Редагувати тему')
