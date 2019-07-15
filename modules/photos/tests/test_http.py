# -*- coding: utf-8

from django.conf import settings
from django.test import TestCase

import os.path
from tddspry.django import HttpTestCase

from photos.models import PhotoAlbum, Photo
from django.contrib.contenttypes.models import ContentType

TEST_FILES = os.path.join(settings.MEDIA_ROOT, 'testfiles')
TEST_PHOTO = os.path.join(TEST_FILES,'photo.png')
TEST_PHOTO_BIG = os.path.join(TEST_FILES, 'photo_big.png')


class TestAlbum(HttpTestCase):
    
    fixtures = ['fixtures/test_data.json']

    def test_album_index(self):
        self.go200('album_index')

    def setup(self):
        self.user = self.helper('create_user', 'username', 'password')
        self.login('username', 'password', url='auth_login', formid='id_login')
        self.assert_equal(PhotoAlbum.objects.count() ,0)
        self.go200('album_detail', [self.user.username])
        self.assert_equal(PhotoAlbum.objects.count() ,1)
        #album created when user goes to page

    def teardown(self):
        self.logout(url = 'auth_logout')


    def test_photo_add(self):
        """
        User uploads a photo
        """
        self.go200('photo_add', [self.user.get_profile().get_album_slug()])
        self.showforms()
        self.formclear('id_photo_add')
        self.fv('id_photo_add', 'id_title', 'Some Cool Photo')
        self.fv('id_photo_add', 'id_description', 'Description for photo')
        self.formfile('id_photo_add', 'id_image', TEST_PHOTO)
        self.submit200()
        self.url('photo_detail', [self.user.get_profile().get_album_slug(), 1])
        self.find('Some Cool Photo')

    def test_add_album_for_obj(self):
        """
        User uploads a photo
        """
        self.go200('photo_add', [self.user.get_profile().get_album_slug()])
        self.showforms()
        self.formclear('id_photo_add')
        self.fv('id_photo_add', 'id_title', 'Some Cool Photo')
        self.fv('id_photo_add', 'id_description', 'Description for photo')
        self.formfile('id_photo_add', 'id_image', TEST_PHOTO)
        self.submit200()
        self.url('photo_detail', [self.user.get_profile().get_album_slug(), 1])
        self.find('Some Cool Photo')

    def test_photo_big_add(self):
        """
        User uploads a photo what size is bigger than PHOTO_MAX_SIZE
        """
        self.go200('photo_add', [self.user.get_profile().get_album_slug()])
        self.showforms()
        self.formclear('id_photo_add')
        self.fv('id_photo_add', 'id_title', 'Some Cool Photo')
        self.fv('id_photo_add', 'id_description', 'Description for photo')
        self.formfile('id_photo_add', 'id_image', TEST_PHOTO_BIG)
        self.submit200()
        self.find('Розмір файлу не повинен перевищувати: ' + \
                  str(settings.PHOTO_MAX_SIZE/1024/1024) + 'МБайт')

    def test_photo_edit(self):
        """
        User edits a photo
        """
        self.go200('photo_add', [self.user.get_profile().get_album_slug()])
        self.showforms()
        self.formclear('id_photo_add')
        self.fv('id_photo_add', 'id_title', 'Some Cool Photo')
        self.fv('id_photo_add', 'id_description', 'Description for photo')
        self.formfile('id_photo_add', 'id_image', TEST_PHOTO)
        self.submit200()
        self.url('photo_detail', [self.user.get_profile().get_album_slug(), 1])
        self.find('Some Cool Photo')
        self.go200('photo_edit', [self.user.get_profile().get_album_slug(), 1])
        self.find('Редагування фото')
        self.showforms()
        self.formclear('id_photo_edit')
        self.fv('id_photo_edit', 'id_title', 'Some New Cool Photo')
        self.submit200()
        self.url('photo_detail', [self.user.get_profile().get_album_slug(), 1])
        self.find('Some New Cool Photo')

    def test_photo_delete(self):
        """
        User deletes a photo
        """
        self.go200('photo_add', [self.user.get_profile().get_album_slug()])
        self.showforms()
        self.formclear('id_photo_add')
        self.fv('id_photo_add', 'id_title', 'Some Cool Photo')
        self.fv('id_photo_add', 'id_description', 'Description for photo')
        self.formfile('id_photo_add', 'id_image', TEST_PHOTO)
        self.submit200()
        self.url('photo_detail', [self.user.get_profile().get_album_slug(), 1])
        self.find('Some Cool Photo')
        self.go200('photo_delete', [self.user.get_profile().get_album_slug(), 1])
        self.find('Ви впевненні що хочете видалити фото')
        self.fv('id_photo_delete','__confirm','1')
        self.submit200()
        self.url('album_detail', [self.user.get_profile().get_album_slug()])
        self.go('photo_detail', [self.user.get_profile().get_album_slug(), 1])
        self.code('404')

    def go_to_albums(self):
        self.go200('photo_add', [self.user.get_profile().get_album_slug()])
        self.formclear('id_photo_add')
        self.fv('id_photo_add', 'id_title', 'Some Cool Photo')
        self.fv('id_photo_add', 'id_description', 'Description for photo')
        self.formfile('id_photo_add', 'id_image', TEST_PHOTO)
        self.submit200()
        self.go200('album_detail', self.user.get_profile().get_album_slug()) #by slug
        self.find('Some Cool Photo')
        self.go200('album_detail', self.user.username) #by username
        self.find('Some Cool Photo')
