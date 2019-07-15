# -*- coding: utf-8 -*-
from django.test import TestCase
from django.conf import settings
from tddspry.django import TestCase
from django.contrib.auth.models import User

from blurbs.models import GeoCity, GeoRegion, BlurbCategory, Blurb
from blurbs.forms import generate_choices

TEST_TITLE = u"Hello, i'm title або як заголовок"
TEST_TITLE_SLUGIFY = u"hello-im-title-abo-yak-zagolovok"
TEST_CONTENT = "contentcontent"
TEST_USERNAME = 'testuser'
TEST_PASSWORD = 'qwerty'
TEST_EMAIL = 'test@mail.com'
TEST_NAME = 'Sometestname'

class TestBlurbs(TestCase):

    def setup(self):
        self.user = self.helper('create_user')

    def test_crud_cats(self):
        """
        create read update delete
        """
        cat = self.assert_create(BlurbCategory,
                           title = TEST_TITLE,
                           )

        self.assert_read(BlurbCategory,
                           title = TEST_TITLE,
                           slug = TEST_TITLE_SLUGIFY,
                           )

        self.assert_update(cat,
                           title = "t",
                           )
        self.assert_delete(BlurbCategory,
                           title = "t",
                           )


    def test_crud_blurb(self):
        """
        create read update delete
        """
        region = self.assert_create(GeoRegion,
                           title = TEST_TITLE)
        city =self.assert_create(GeoCity,
                           title = TEST_TITLE,
                           region = region
                           )

        category = self.assert_create(BlurbCategory,
                           title = TEST_TITLE,
                           )

        blurb = self.assert_create(Blurb,
                           geocity = city,
                           category = category,
                           buysell = 'B',
                           user=self.user,
                           title = TEST_TITLE,
                           description = TEST_CONTENT
                           )

        self.assert_read(Blurb,
                           geocity = city,
                           georegion = region,
                           category = category,
                           user=self.user,
                           title = TEST_TITLE,
                           description = TEST_CONTENT
                           )

        self.assert_update(Blurb,
                           user=self.user,
                           title = "t",
                           description = "b"
                           )
        self.assert_delete(Blurb,
                           user=self.user,
                           title = "t",
                           description = "b"
                           )

    def test_generate_choices(self):
        cat = self.assert_create(BlurbCategory,
                           title = TEST_TITLE,
                           )
        c = generate_choices(BlurbCategory)
        self.assert_equal(len(c),2)
        self.assert_equal(c[1],(TEST_TITLE_SLUGIFY, TEST_TITLE))
        self.assert_create(BlurbCategory,
                           title = TEST_TITLE+"1",
                           )
        c = generate_choices(BlurbCategory)
        self.assert_equal(len(c),3)

        self.assert_create(BlurbCategory,
                           title = TEST_TITLE+"2",
                           )
        c = generate_choices(BlurbCategory)
        self.assert_equal(len(c),4)
