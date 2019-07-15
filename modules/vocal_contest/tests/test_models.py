# -*- coding: utf-8 -*-
import datetime
import os
import shutil
import tempfile

from django.test import TestCase
from django.conf import settings
from tddspry.django import TestCase
from django.contrib.auth.models import User
from django.db import IntegrityError

from vocal_contest.models import VocalContest,\
    VocalContestCategory,\
    VocalContestParticipant

today = datetime.date.today()
TOMORROW = today+\
        datetime.timedelta(days = 1)
YESTERDAY = today-\
        datetime.timedelta(days = 1)
CONT_END = today+\
        datetime.timedelta(days = settings.CONTEST_END_DAYS)
REG_END = today+\
        datetime.timedelta(days = settings.CONTEST_REGISTRATION_END_DAYS)

TEST_FILES = os.path.join(settings.STORAGE_ROOT,'testfiles')
AUDIO_FILE = os.path.join(TEST_FILES,'04 - jingle bells.mp3')

TEST_TITLE = u"Hello, i'm title або як заголовок"
TEST_TITLE_SLUGIFY = u"hello-im-title-abo-yak-zagolovok"
TEST_CONTENT = "contentcontent"
TEST_USERNAME = 'testuser'
TEST_PASSWORD = 'qwerty'
TEST_EMAIL = 'test@mail.com'
TEST_NAME = 'Sometestname'

class TestBlurbs(TestCase):

    def setup(self):
        self.test_file= tempfile.NamedTemporaryFile(dir=TEST_FILES,suffix='.mp3')
        shutil.copy2(AUDIO_FILE, self.test_file.name)

    
    def teardown(self):
        try:
            self.test_file.close()
        except OSError:
            pass

    def test_crud_contest(self):
        """
        create read update delete
        """
        cont = self.assert_create(VocalContest,
                           title = TEST_TITLE,
                           description = TEST_CONTENT,
                           )

        self.assert_read(VocalContest,
                           title = TEST_TITLE,
                           description = TEST_CONTENT,
                           start_date = today,
                           registration_end_date = REG_END,
                           end_date = CONT_END,
                           )
        self.assert_equal(cont.status(), "open")

        cont = self.assert_update(cont,
                           title = "t",
                           start_date = TOMORROW,
                           registration_end_date = REG_END,
                           end_date = CONT_END,

                           )
        self.assert_equal(cont.status(), "future")

        cont = self.assert_update(cont,
                           start_date = YESTERDAY,
                           registration_end_date = YESTERDAY,
                           end_date = CONT_END,

                           )
        self.assert_equal(cont.status(), "closed")
        cont = self.assert_update(cont,
                           start_date = YESTERDAY,
                           registration_end_date = YESTERDAY,
                           end_date = today,

                           )
        self.assert_equal(cont.status(), "closed")

        cont = self.assert_update(cont,
                           start_date = YESTERDAY,
                           registration_end_date = YESTERDAY,
                           end_date = today,

                           )
        self.assert_equal(cont.status(), "closed")

        cont = self.assert_update(cont,
                           start_date = YESTERDAY,
                           registration_end_date = YESTERDAY,
                           end_date = YESTERDAY,

                           )
        self.assert_equal(cont.status(), "finished")
        self.assert_delete(VocalContest,
                           title = "t",
                           )



    def test_crud_cats(self):
        """
        create read update delete
        """
        cont = self.assert_create(VocalContest,
                           title = TEST_TITLE,
                           description = TEST_CONTENT,
                           )

        cat = self.assert_create(VocalContestCategory,
                           title = TEST_TITLE,
                           contest = cont,
                           )

        self.assert_read(VocalContestCategory,
                           title = TEST_TITLE,
                           )

        self.assert_update(cat,
                           title = "t",
                           description = TEST_CONTENT,
                           )

        self.assert_delete(VocalContestCategory,
                           title = "t",
                           )

    def test_crud_participation(self):
        cont = self.assert_create(VocalContest,
                           title = TEST_TITLE,
                           description = TEST_CONTENT,
                           )

        cat1 = self.assert_create(VocalContestCategory,
                           title = TEST_TITLE,
                           contest = cont,
                           )

        cat2 = self.assert_create(VocalContestCategory,
                           title = TEST_TITLE,
                           contest = cont,
                           )
        user = self.helper('create_user')

        
        partic = self.assert_create(VocalContestParticipant,
                            user = user,
                            title = TEST_TITLE,
                            category = cat1,
                            file = self.test_file.name,
                            description = TEST_CONTENT
                            )

        partic = self.assert_update(VocalContestParticipant,
                            user = user,
                            contest = cont,
                            title = TEST_TITLE+"ASAS",
                            category = cat2,
                            file = self.test_file.name,
                            description = TEST_CONTENT
                            )

        self.assert_delete(VocalContestParticipant,
                            user = user,
                            contest = cont,
                            title = TEST_TITLE+"ASAS",
                            category = cat2,
                            file = self.test_file.name,
                            description = TEST_CONTENT
                            )
        

    def test_managers(self):
        self.assert_equal(VocalContest.objects.get_current(), None)

        cont1 = self.assert_create(VocalContest,
                   title = TEST_TITLE,
                   description = TEST_CONTENT,
                   )

        cont2 = self.assert_create(VocalContest,
                   start_date = YESTERDAY,
                   registration_end_date = YESTERDAY,
                   end_date = YESTERDAY,
                   )

        cont3 = self.assert_create(VocalContest,
                   start_date = REG_END,
                   registration_end_date = REG_END,
                   end_date = CONT_END,
                   )

        # current contest is that one which is already started 
        # or ended last
        self.assert_equal(VocalContest.objects.get_current(), cont1)
        cont1.delete()
        self.assert_equal(VocalContest.objects.get_current(), cont2)

        cat1 = self.assert_create(VocalContestCategory,
                           title = TEST_TITLE,
                           contest = cont2,
                           )

        cat2 = self.assert_create(VocalContestCategory,
                           title = TEST_TITLE,
                           contest = cont3,
                           )

        cat3 = self.assert_create(VocalContestCategory,
                           title = TEST_TITLE,
                           contest = cont2,
                           )

        cat4 = self.assert_create(VocalContestCategory,
                           title = TEST_TITLE,
                           contest = cont3,
                           )


        self.assert_equal(list(VocalContestCategory.objects.get_cats(VocalContest.objects.get_current())),
            [cat1, cat3])
