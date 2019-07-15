# -*- coding: utf-8 -*-

import os
import shutil
import tempfile
import datetime


from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.management import call_command

from django.test import TestCase #TODO investigate why test fails without it
from tddspry.django import DatabaseTestCase
from minusstore.models import *
from minusstore.utils import up_filename

TEST_FILES = os.path.join(settings.STORAGE_ROOT,'testfiles')
AUDIO_FILE = os.path.join(TEST_FILES,'04 - jingle bells.mp3')
WEIRD_FILE = os.path.join(TEST_FILES,'тест.mp3')
NOTAGS_FILE = os.path.join(TEST_FILES,'notags.mp3')
TEST_FILETYPE = [u'Аудіо',u'тестовий опис','mp3, wav']
TEST_AUTHOR = 'Петро Онищенко'
TEST_TITLE = "Hello guys!"


class TestModels(DatabaseTestCase):
    
    def setup(self):
        super(TestModels, self).setup()
        self.user = self.helper('create_user')
        global TEST_FILE
        TEST_FILE = tempfile.NamedTemporaryFile(dir=TEST_FILES,suffix='.mp3')
        shutil.copy2(AUDIO_FILE, TEST_FILE.name)

        global aut
        aut = self.assert_create(MinusAuthor, name=TEST_AUTHOR)
        global typ
        typ = self.assert_create(FileType,type_name = TEST_FILETYPE[0],
                                    description = TEST_FILETYPE[1], 
                                    filetype = TEST_FILETYPE[2])
        global minus
        minus = self.assert_create(MinusRecord, user=self.user, file=TEST_FILE.name,
                            title = TEST_TITLE, annotation = TEST_FILETYPE[1],
                            lyrics = TEST_FILETYPE[1],
                            author = aut, type = typ
                            )

    def teardown(self):
        try:
            TEST_FILE.close()
        except OSError:
            pass

    def test_db_models(self):
        #read database#
        self.assert_read(MinusRecord, user=self.user, file=TEST_FILE.name, 
                            title = TEST_TITLE, annotation = TEST_FILETYPE[1],
                            lyrics = TEST_FILETYPE[1],
                            author = aut, type = typ)

    def test_author_filetyping(self):
        "basic filetype assigning"
        self.assert_equal(aut.filetypes.count(),1)
        self.assert_equal(aut.filetypes.all()[0], typ)
        minus.delete()
        self.assert_equal(aut.filetypes.count(),0)
        
    def test_filetyping_deeper(self):
        "advanced manipulations with filetypes"
        typ1 = self.assert_create(FileType,type_name = "video",
                                    description = TEST_FILETYPE[1], 
                                    filetype = TEST_FILETYPE[2])
        minus1 = self.assert_create(MinusRecord, user=self.user, file=TEST_FILE.name,
                            title = TEST_TITLE+"1", annotation = TEST_FILETYPE[1],
                            lyrics = TEST_FILETYPE[1],
                            author = aut, type = typ1 
                            )
        minus2 = self.assert_create(MinusRecord, user=self.user, file=TEST_FILE.name,
                            title = TEST_TITLE+"1", annotation = TEST_FILETYPE[1],
                            lyrics = TEST_FILETYPE[1],
                            author = aut, type = typ 
                            )
        self.assert_equal(aut.filetypes.count(),2)
        minus.delete()
        # author has another record of same filetype
        self.assert_equal(aut.filetypes.count(),2)
        self.assert_equal(aut.filetypes.all()[1],typ)
        # but when there is no more files of that type, it should be removed
        minus2.delete()
        self.assert_equal(aut.filetypes.count(),1)
        
        

    def test_arivals_querysets(self):
        minus1 = self.assert_create(MinusRecord, user=self.user, file=TEST_FILE.name,
                            title = TEST_TITLE+"1", annotation = TEST_FILETYPE[1],
                            lyrics = TEST_FILETYPE[1],
                            author = aut, type = typ 
                            )
        minus1.pub_date = datetime.datetime(2008, 1, 3).date()
        minus1.save()
        from minusstore.signals import timed_arivals
        self.assert_equal(len(timed_arivals()), 1)
        self.assert_equal(timed_arivals()[0], minus)
        self.assert_equal(len(timed_arivals("week")), 1)
        self.assert_equal(timed_arivals("week")[0], minus)
        self.assert_equal(len(timed_arivals("two_weeks")), 1)
        self.assert_equal(timed_arivals("two_weeks")[0], minus)
        self.assert_equal(len(timed_arivals("month")), 1)
        self.assert_equal(timed_arivals("month")[0], minus)

    def test_deleted_author(self):
        self.assert_equal(MinusAuthor.objects.count(), 1)
        self.assert_equal(MinusRecord.objects.count(), 1)
        aut.delete()
        self.assert_equal(MinusRecord.objects.count(), 1)
        self.assert_equal(MinusAuthor.objects.count(), 1)
        self.assert_equal(MinusAuthor.objects.all()[0].name, u"Невідомий виконавець")
        self.assert_equal(MinusRecord.objects.all()[0].author,MinusAuthor.objects.all()[0])

    def test_changed_author(self):
        """still trying to catch the bug"""
        minus1 = self.assert_create(MinusRecord, user=self.user, file=TEST_FILE.name,
                            title = TEST_TITLE+"1", annotation = TEST_FILETYPE[1],
                            lyrics = TEST_FILETYPE[1],
                            author = aut, type = typ 
                            )

        minus2 = self.assert_create(MinusRecord, user=self.user, file=TEST_FILE.name,
                            title = TEST_TITLE+"1", annotation = TEST_FILETYPE[1],
                            lyrics = TEST_FILETYPE[1],
                            author = aut, type = typ 
                            )
        newaut = self.assert_create(MinusAuthor, name = "Hello")
        self.assert_equal(MinusAuthor.objects.count(), 2)
        minus.author = newaut
        minus.save()
        self.assert_equal(MinusAuthor.objects.count(), 2)
        self.assert_equal(MinusAuthor.objects.all()[0].name, "Hello")
        minus1.delete()
        self.assert_equal(MinusAuthor.objects.count(), 2)
        self.assert_equal(MinusAuthor.objects.all()[0].name, "Hello")
        minus2.delete()
        self.assert_equal(MinusAuthor.objects.count(), 1)
        self.assert_equal(MinusAuthor.objects.all()[0].name, "Hello")

    def test_collision(self):
        newaut = self.assert_create(MinusAuthor, name = "Hello") #has no records for now
        newaut2 = self.assert_create(MinusAuthor, name = "Hello2") 
        self.assert_equal(MinusAuthor.objects.count(), 3)
        minus.author = newaut
        minus.save()
        self.assert_equal(MinusAuthor.objects.count(), 2) #deleted original not touched unknown


    def test_same_name(self):
        newaut = self.assert_create(MinusAuthor, name = "Hello") #has no records for now

        minus2 = self.assert_create(MinusRecord, user=self.user, file=TEST_FILE.name,
                            title = TEST_TITLE+"1", annotation = TEST_FILETYPE[1],
                            lyrics = TEST_FILETYPE[1],
                            author = newaut, type = typ 
                            )
        # started with different names
        self.assert_equal(MinusAuthor.objects.count(), 2) 
        aut.name = "Hello"
        aut.save()
        self.assert_equal(MinusAuthor.objects.count(), 1) 
        self.assert_equal(MinusAuthor.objects.get(name = "Hello").records_by.count() , 2)

        
        
    def test_filename(self):
        self.assert_true('files' in up_filename(minus, 'file.mp3'))
        
        plus = self.assert_create(MinusPlusRecord,
            user=self.user, file=TEST_FILE.name,
            minus = minus,
            )
        self.assert_true('pluses' in up_filename(plus, 'file.mp3'))

    
    def test_alternative_recs(self):
        self.assert_false(aut.has_alternative())
        minus.alternative = True
        minus.save()
        self.assert_true(aut.has_alternative())
