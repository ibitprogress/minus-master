# -*- coding: utf-8 -*-
import os
from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase #weird %)
from django.core.management import call_command

from tddspry.django import TestCase
from tddspry.django.helpers import USERNAME, PASSWORD

 
from albums.models import Audio, AudioAlbum
from albums.views import models

TEST_FILES = os.path.join(settings.STORAGE_ROOT,'testfiles')
AUDIO_FILE = os.path.join(TEST_FILES,'04 - jingle bells.mp3')

class TestAlbums(TestCase):
    
    def setup(self):
        self.user = self.helper('create_user')
        self.login(USERNAME, PASSWORD, url='auth_login', formid='id_login')
        self.type = 'audio'
        self.model = Audio
        self.albummodel = AudioAlbum


    def test_crud(self):
        self.assert_equal(self.model.objects.count(),0)
        self.assert_equal(self.albummodel.objects.count(),0)
        self.go200('up_object', [self.type, self.user.username ])
        fnm= self.type+'_add' #form name
        self.fv(fnm, 'title', 'testtt')
        self.fv(fnm, 'description', 'descrr')
        self.formfile(fnm,'file', AUDIO_FILE)
        self.submit200()

        self.assert_equal(self.model.objects.count(),1)
        #album created automagically
        self.assert_equal(self.albummodel.objects.count(),1)

        album = self.albummodel.objects.all()[0]
        self.go200('show_objects_album',[self.type, self.user.username,album.slug])
        self.go200('show_album',[self.type, self.user.username, album.slug])
        self.find('testtt')
        self.find('descrr')

        self.go200('edit_object', [self.type, self.model.objects.all()[0].pk])
        self.fv(fnm,'title', 'edited')
        self.submit200()

        self.go200('show_objects_album',[self.type,  self.user.username, album.slug])
        self.find('edited')

        self.go200('remove_object',[self.type,  self.user.username, self.model.objects.all()[0].pk])

        self.fv('object_delete', '__confirm__', 1)
        self.submit200()
        self.assert_equal(self.model.objects.count(),0)

    def test_crud_album(self):
        self.go200('create_album' , [self.type, self.user.username])
        fnma= self.type+'_album_add' #form name
        fnm= self.type+'_add' #form name
        self.fv(fnma, 'name', 'atesttt')
        self.fv(fnma, 'description', 'adescrr')
        self.submit200()

        self.assert_equal(self.albummodel.objects.count(),1)
        self.assert_equal(self.albummodel.objects.all()[0].slug, 'atesttt')

        self.go200('up_object', [self.type, self.user.username])
        self.fv(fnm, 'title', 'testtt')
        self.fv(fnm, 'description', 'descrr')
        self.fv(fnm, 'album', 'atesttt')
        self.formfile(fnm,'file', AUDIO_FILE)
        self.submit200()
        self.assert_equal(self.model.objects.count(),1)
        self.assert_equal(self.albummodel.objects.count(),1)
        self.assert_equal(self.model.objects.all()[0].album, self.albummodel.objects.all()[0])

        self.go200('show_album',[self.type, self.user.username, self.albummodel.objects.all()[0].slug])
        self.go200('up_object_to_album', [self.type, self.user.username, self.albummodel.objects.all()[0].slug])
        self.fv(fnm, 'title', 'testtt')
        self.fv(fnm, 'description', 'descrr')
        self.formfile(fnm,'file', AUDIO_FILE)
        self.submit200()

        self.assert_equal(self.model.objects.count(),2)
        self.assert_equal(self.albummodel.objects.count(),1)
        self.assert_equal(self.model.objects.all()[1].album, self.albummodel.objects.all()[0])

        self.go200('edit_album',[self.type, self.user.username, self.albummodel.objects.all()[0].pk])
        self.fv(fnma, 'name', 'newname')
        self.submit200()
        self.assert_equal(self.albummodel.objects.all()[0].slug, 'newname') #slug changed
        self.go200('show_album',[self.type, self.user.username, self.albummodel.objects.all()[0].slug])
        self.find('newname')

        self.go200('remove_album',[self.type, self.user.username, self.albummodel.objects.all()[0].pk])
        self.fv('object_delete', '__confirm__', 1)
        self.submit200()
        self.assert_equal(self.albummodel.objects.count(),0)

    def test_allow_download(self):
        self.go200('up_object', [self.type, self.user.username ])
        fnm= self.type+'_add' #form name
        self.fv(fnm, 'title', 'testtt')
        self.fv(fnm, 'description', 'descrr')
        self.fv(fnm, 'downloadable', True)
        self.formfile(fnm,'file', AUDIO_FILE)
        self.submit200()
        
        album = self.albummodel.objects.all()[0]
        self.go200('show_album',[self.type, self.user.username,album.slug])
        self.find('testtt')
        self.find('Звантажити запис')

        self.go200('edit_object', [self.type,  1])
        fnm= self.type+'_add' #form name
        self.fv(fnm, 'downloadable', False)
        self.submit200()
        
        album = self.albummodel.objects.all()[0]
        self.go200('show_album',[self.type, self.user.username,album.slug])
        self.find('testtt')
        self.notfind('Звантажити запис')
        self.go200('show_object_detail',[self.type, self.user.username,album.slug, 1])
        self.find('testtt')
        self.notfind('Звантажити запис')
