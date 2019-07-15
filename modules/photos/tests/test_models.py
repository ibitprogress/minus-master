# -*- coding: utf-8 -*-

from django.contrib.contenttypes.models import ContentType
from django.conf import settings

import os.path
import tempfile
import shutil

from datetime import datetime
from tddspry.django import DatabaseTestCase

from photos.models import PhotoAlbum, Photo
from albums.models import create_album_for

TEST_FILES = os.path.join(settings.MEDIA_ROOT, 'testfiles')
TEST_PHOTO = os.path.join(TEST_FILES,'photo.png')
SLUG  = 'albom-testusername1'


class TestPhotoAlbum(DatabaseTestCase):
    
    def test_create(self):
        user = self.helper('create_user')
        create_album_for(user.get_profile(), user, PhotoAlbum)
        self.assert_read(PhotoAlbum, slug=SLUG)

    def test_update(self):
        user = self.helper('create_user')
        create_album_for(user.get_profile(), user, PhotoAlbum)
        album = self.assert_read(PhotoAlbum, slug=SLUG)
        self.assert_update(album, name='Super puper album')
        self.assert_read(PhotoAlbum, name='Super puper album',
                        slug=SLUG)

    def test_delete(self):
        user = self.helper('create_user')
        create_album_for(user.get_profile(), user, PhotoAlbum)
        album = self.assert_read(PhotoAlbum, slug=SLUG)
        self.assert_delete(album)

class TestPhoto(DatabaseTestCase):

    def setup(self):
        user = self.helper('create_user')
        create_album_for(user.get_profile(), user, PhotoAlbum)
        super(TestPhoto, self).setup()
        global TEST_PHOTO_COPY
        TEST_PHOTO_COPY = tempfile.NamedTemporaryFile(dir=TEST_FILES,
                                                      suffix='.png')
        shutil.copy2(TEST_PHOTO, TEST_PHOTO_COPY.name)

    def teardown(self):
        try:
            TEST_PHOTO_COPY.close()
        except OSError:
            pass

    def test_create(self):
        album = self.assert_read(PhotoAlbum, slug=SLUG)
        self.assert_create(Photo, title='Some cool photo',
                          description='Description for some cool photo',
                          date_created=datetime.now(), album=album,
                          image=TEST_PHOTO_COPY.name)
        self.assert_read(Photo, title='Some cool photo')

    def test_update(self):
        album = self.assert_read(PhotoAlbum, slug=SLUG)
        photo = self.assert_create(Photo, title='Some cool photo',
                                  description='Description for some cool photo',
                                  date_created=datetime.now(), album=album,
                                  image=TEST_PHOTO_COPY.name)
        self.assert_update(photo, title='Some new cool photo')
        self.assert_read(Photo, title='Some new cool photo')

    def test_delete(self):
        album = self.assert_read(PhotoAlbum, slug=SLUG)
        photo = self.assert_create(Photo, title='Some cool photo',
                                  description='Description for some cool photo',
                                  date_created=datetime.now(), album=album,
                                  image=TEST_PHOTO_COPY.name)
        self.assert_delete(photo)
