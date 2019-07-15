# -*- coding: utf-8
import datetime

from django.test import TestCase
from tddspry.django import DatabaseTestCase
from forum.models import Forum, Thread, Post, Subscription

TEST_FORUM_TITLE = 'Some Nice Forum Title'
TEST_FORUM_SLUG = 'some-nice-forum-title'
TEST_FORUM_DESCRIPTION = 'Some fancy forum description'
TEST_FORUM_TITLE_NEW = 'Some New Nice Forum Title'
TEST_FORUM_SLUG_NEW = 'some-new-nice-forum-title'
TEST_FORUM_DESCRIPTION_NEW = 'Some new fancy forum description'
TEST_THREAD_TITLE = 'Some Nice Thread Title'
TEST_THREAD_LATEST_POST_TIME = datetime.datetime.now()
TEST_THREAD_TITLE_NEW = 'Some New Nice Thread Title'
TEST_POST_BODY = 'Hello, World! Just a testing post'
TEST_POST_BODY_NEW = 'Hello, World! Just a new testing post'

class TestForumModel(DatabaseTestCase):
    
    def test_create(self):
        self.assert_create(Forum, title=TEST_FORUM_TITLE,
                          slug=TEST_FORUM_SLUG,
                          description=TEST_FORUM_DESCRIPTION)

    def test_read(self):
        self.assert_create(Forum, title=TEST_FORUM_TITLE,
                          slug=TEST_FORUM_SLUG,
                          description=TEST_FORUM_DESCRIPTION)
        self.assert_read(Forum, title=TEST_FORUM_TITLE)

    def test_update(self):
        forum_model = self.assert_create(Forum, title=TEST_FORUM_TITLE,
                                      slug=TEST_FORUM_SLUG,
                                      description=TEST_FORUM_DESCRIPTION)
        self.assert_update(forum_model, title=TEST_FORUM_TITLE_NEW,
                          slug=TEST_FORUM_SLUG_NEW,
                          description=TEST_FORUM_DESCRIPTION_NEW)
        self.assert_read(Forum, pk=forum_model.pk)

    def test_delete(self):
        forum_model = self.assert_create(Forum, title=TEST_FORUM_TITLE,
                                          slug=TEST_FORUM_SLUG,
                                          description=TEST_FORUM_DESCRIPTION)
        self.assert_delete(forum_model)


class TestThreadModel(DatabaseTestCase):

    def test_create(self):
        forum_model = self.assert_create(Forum, title=TEST_FORUM_TITLE,
                                      slug=TEST_FORUM_SLUG,
                                      description=TEST_FORUM_DESCRIPTION)
        self.assert_create(Thread, forum=forum_model,
                          title=TEST_THREAD_TITLE,
                          latest_post_time=TEST_THREAD_LATEST_POST_TIME)

    def test_read(self):
        forum_model = self.assert_create(Forum, title=TEST_FORUM_TITLE,
                                      slug=TEST_FORUM_SLUG,
                                      description=TEST_FORUM_DESCRIPTION)
        self.assert_create(Thread, forum=forum_model,
                          title=TEST_THREAD_TITLE,
                          latest_post_time=TEST_THREAD_LATEST_POST_TIME)
        self.assert_read(Thread, title=TEST_THREAD_TITLE)

    def test_update(self):
        forum_model = self.assert_create(Forum, title=TEST_FORUM_TITLE,
                                      slug=TEST_FORUM_SLUG,
                                      description=TEST_FORUM_DESCRIPTION)
        thread_model = self.assert_create(Thread, forum=forum_model,
                                         title=TEST_THREAD_TITLE,
                                         latest_post_time=TEST_THREAD_LATEST_POST_TIME)
        self.assert_update(thread_model, title=TEST_THREAD_TITLE_NEW)
        self.assert_read(Thread, pk=thread_model.pk)

    def test_delete(self):
        forum_model = self.assert_create(Forum, title=TEST_FORUM_TITLE,
                                      slug=TEST_FORUM_SLUG,
                                      description=TEST_FORUM_DESCRIPTION)
        thread_model = self.assert_create(Thread, forum=forum_model,
                                         title=TEST_THREAD_TITLE,
                                         latest_post_time=TEST_THREAD_LATEST_POST_TIME)
        self.assert_delete(thread_model)


class TestPostModel(DatabaseTestCase):

    def test_create(self):
        forum_model = self.assert_create(Forum, title=TEST_FORUM_TITLE,
                                      slug=TEST_FORUM_SLUG,
                                      description=TEST_FORUM_DESCRIPTION)
        thread_model = self.assert_create(Thread, forum=forum_model,
                                      title=TEST_THREAD_TITLE,
                                      latest_post_time=TEST_THREAD_LATEST_POST_TIME)
        author = self.helper('create_user')
        self.assert_create(Post, thread=thread_model, author=author,
                          body=TEST_POST_BODY, time=TEST_THREAD_LATEST_POST_TIME)

    def test_read(self):
        forum_model = self.assert_create(Forum, title=TEST_FORUM_TITLE,
                                      slug=TEST_FORUM_SLUG,
                                      description=TEST_FORUM_DESCRIPTION)
        thread_model = self.assert_create(Thread, forum=forum_model,
                                      title=TEST_THREAD_TITLE,
                                      latest_post_time=TEST_THREAD_LATEST_POST_TIME)
        author = self.helper('create_user')
        self.assert_create(Post, thread=thread_model, author=author,
                          body=TEST_POST_BODY, time=TEST_THREAD_LATEST_POST_TIME)
        self.assert_read(Post, body=TEST_POST_BODY)

    def test_update(self):
        forum_model = self.assert_create(Forum, title=TEST_FORUM_TITLE,
                                      slug=TEST_FORUM_SLUG,
                                      description=TEST_FORUM_DESCRIPTION)
        thread_model = self.assert_create(Thread, forum=forum_model,
                                      title=TEST_THREAD_TITLE,
                                      latest_post_time=TEST_THREAD_LATEST_POST_TIME)
        author = self.helper('create_user')
        post_model = self.assert_create(Post, thread=thread_model, author=author,
                                  body=TEST_POST_BODY, time=TEST_THREAD_LATEST_POST_TIME)
        self.assert_update(post_model, body=TEST_POST_BODY_NEW)
        self.assert_read(Post, pk=post_model.pk)

    def test_delete(self):
        forum_model = self.assert_create(Forum, title=TEST_FORUM_TITLE,
                                      slug=TEST_FORUM_SLUG,
                                      description=TEST_FORUM_DESCRIPTION)
        thread_model = self.assert_create(Thread, forum=forum_model,
                                      title=TEST_THREAD_TITLE,
                                      latest_post_time=TEST_THREAD_LATEST_POST_TIME)
        author = self.helper('create_user')
        post_model = self.assert_create(Post, thread=thread_model, author=author,
                                  body=TEST_POST_BODY, time=TEST_THREAD_LATEST_POST_TIME)
        self.assert_delete(post_model)


class TestSubscriptionModel(DatabaseTestCase):

    def test_create(self):
        forum_model = self.assert_create(Forum, title=TEST_FORUM_TITLE,
                                      slug=TEST_FORUM_SLUG,
                                      description=TEST_FORUM_DESCRIPTION)
        thread_model = self.assert_create(Thread, forum=forum_model,
                                      title=TEST_THREAD_TITLE,
                                      latest_post_time=TEST_THREAD_LATEST_POST_TIME)
        author = self.helper('create_user')
        self.assert_create(Subscription, author=author, thread=thread_model)

    def test_read(self):
        forum_model = self.assert_create(Forum, title=TEST_FORUM_TITLE,
                                      slug=TEST_FORUM_SLUG,
                                      description=TEST_FORUM_DESCRIPTION)
        thread_model = self.assert_create(Thread, forum=forum_model,
                                      title=TEST_THREAD_TITLE,
                                      latest_post_time=TEST_THREAD_LATEST_POST_TIME)
        author = self.helper('create_user')
        self.assert_create(Subscription, author=author, thread=thread_model)
        self.assert_read(Subscription, author=author, thread=thread_model)

    def test_update(self):
        forum_model = self.assert_create(Forum, title=TEST_FORUM_TITLE,
                                      slug=TEST_FORUM_SLUG,
                                      description=TEST_FORUM_DESCRIPTION)
        thread_model = self.assert_create(Thread, forum=forum_model,
                                      title=TEST_THREAD_TITLE,
                                      latest_post_time=TEST_THREAD_LATEST_POST_TIME)
        thread_model2 = self.assert_create(Thread, forum=forum_model,
                                      title=TEST_THREAD_TITLE_NEW,
                                      latest_post_time=TEST_THREAD_LATEST_POST_TIME)
        author = self.helper('create_user')
        subscription_model = self.assert_create(Subscription, author=author,
                                                thread=thread_model)
        self.assert_update(subscription_model, thread=thread_model2)

    def test_delete(self):
        forum_model = self.assert_create(Forum, title=TEST_FORUM_TITLE,
                                      slug=TEST_FORUM_SLUG,
                                      description=TEST_FORUM_DESCRIPTION)
        thread_model = self.assert_create(Thread, forum=forum_model,
                                      title=TEST_THREAD_TITLE,
                                      latest_post_time=TEST_THREAD_LATEST_POST_TIME)
        author = self.helper('create_user')
        subscription_model = self.assert_create(Subscription, author=author,
                                                thread=thread_model)
        self.assert_delete(subscription_model)
