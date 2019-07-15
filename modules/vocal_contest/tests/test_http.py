# -*- coding: utf-8 -*-
import datetime
import os
import shutil
import tempfile
from django.conf import settings
from django.contrib.flatpages.models import FlatPage
from tddspry.django import TestCase
from vocal_contest.models import VocalContest,\
    VocalContestCategory,\
    VocalContestParticipant,\
    RealVocalContestGuest,\
    RealVocalContestParticipant
from django import forms
import vocal_contest
from vocal_contest import forms as vc_forms

from tddspry.django.helpers import USERNAME, PASSWORD
TEST_TITLE = "Hello, im title чи то я заголовок"
TEST_CONTENT = "contentcontent вміст"
TEST_FILES = os.path.join(settings.STORAGE_ROOT,'testfiles')
AUDIO_FILE = os.path.join(TEST_FILES,'04 - jingle bells.mp3')
NOTAGS_FILE = os.path.join(TEST_FILES,'notags.mp3')

TODAY = datetime.date.today()
TOMORROW = TODAY+\
        datetime.timedelta(days = 1)
YESTERDAY = TODAY-\
        datetime.timedelta(days = 1)
CONT_END = TODAY+\
        datetime.timedelta(days = settings.CONTEST_END_DAYS)
REG_END = TODAY+\
        datetime.timedelta(days = settings.CONTEST_REGISTRATION_END_DAYS)

class TestVC(TestCase):
    fixtures = ['fixtures/test_data.json']
    
    def setup(self):
        vc_forms.VocalContestParticipantForm.category = \
            forms.ModelChoiceField(queryset = VocalContestCategory.objects.all())
        vocal_contest.forms.VocalContestParticipantForm = vc_forms.VocalContestParticipantForm

        self.test_file= tempfile.NamedTemporaryFile(dir=TEST_FILES,suffix='.mp3')
        shutil.copy2(AUDIO_FILE, self.test_file.name)

        self.user = self.helper('create_user')
        self.contest = self.assert_create(VocalContest,
                           title = TEST_TITLE,
                           description = TEST_CONTENT,
                           )

        self.cat1 = self.assert_create(VocalContestCategory,
                           title = TEST_TITLE+"1",
                           contest = self.contest,
                           )

        self.cat2 = self.assert_create(VocalContestCategory,
                           title = TEST_TITLE+"2",
                           contest = self.contest,
                           )
        

    def teardown(self):
        try:
            self.test_file.close()
        except OSError:
            pass
        VocalContestParticipant.objects.all().delete()


    def test_contest_status(self):
        self.assert_equal(self.contest.start_date, TODAY)
        self.go200('news_index')
        self.find('Конкурс вокалістів')
        self.find('Відкрито реєстрацію')
        self.contest.start_date = TOMORROW
        self.contest.save()
        self.go200('news_index')
        self.notfind('Конкурс вокалістів')
        self.contest.start_date = YESTERDAY
        self.contest.save()
        self.go200('news_index')
        self.find('Конкурс вокалістів')
        self.find('Відкрито реєстрацію')
        self.contest.start_date = YESTERDAY
        self.contest.registration_end_date = TODAY
        self.contest.save()
        self.go200('news_index')
        self.find('Конкурс вокалістів')
        self.find('Відкрито реєстрацію')
        self.contest.start_date = YESTERDAY
        self.contest.registration_end_date = YESTERDAY
        self.contest.save()
        self.go200('news_index')
        self.find('Конкурс вокалістів')
        self.find('Реєстрацію завершено')
        self.contest.start_date = YESTERDAY
        self.contest.registration_end_date = YESTERDAY
        self.contest.end_date = YESTERDAY
        self.contest.save()
        self.go200('news_index')
        self.find('Конкурс вокалістів')
        self.find('Результати')

    def test_contest_participate(self):
        self.go200('vocal_contest_index')
        self.find('Прийняти участь')

        self.login(USERNAME, PASSWORD, url = 'auth_login', formid = 'id_login')
        self.go200('vocal_contest_participate')
        self.fv('vocal_contest_participate', 'title', 'c'+TEST_TITLE)
        self.fv('vocal_contest_participate', 'category', str(self.cat1.id))
        self.fv('vocal_contest_participate', 'description', TEST_CONTENT)
        self.formfile('vocal_contest_participate', 'file', AUDIO_FILE)
        self.submit200()
        self.assert_equal(VocalContestParticipant.objects.count(), 1)
        vcp = self.assert_read(VocalContestParticipant,
            user = self.user,
            title = "c"+TEST_TITLE)
        self.assert_equal(vcp.file.name.split('/')[-1], "04-jingle-bells.mp3")
        self.url('vocal_contest_participant_detail', [vcp.id])
        self.find('c'+TEST_TITLE)

    def test_contest_participate_twice(self):
        self.login(USERNAME, PASSWORD, url = 'auth_login', formid = 'id_login')
        self.go200('vocal_contest_participate')
        self.fv('vocal_contest_participate', 'title', 'c'+TEST_TITLE)
        self.fv('vocal_contest_participate', 'category', str(self.cat1.id))
        self.fv('vocal_contest_participate', 'description', TEST_CONTENT)
        self.formfile('vocal_contest_participate', 'file', AUDIO_FILE)
        self.submit200()
        self.assert_equal(VocalContestParticipant.objects.count(), 1)

        self.go200('vocal_contest_participate')
        self.fv('vocal_contest_participate', 'title', 'c2'+TEST_TITLE)
        self.fv('vocal_contest_participate', 'category', str(self.cat2.id))
        self.fv('vocal_contest_participate', 'description', TEST_CONTENT)
        self.formfile('vocal_contest_participate', 'file', AUDIO_FILE)
        self.submit200()
        self.assert_equal(VocalContestParticipant.objects.count(), 2)

        self.go200('vocal_contest_participate')
        self.fv('vocal_contest_participate', 'title', 'c3'+TEST_TITLE)
        self.fv('vocal_contest_participate', 'category', str(self.cat2.id))
        self.fv('vocal_contest_participate', 'description', TEST_CONTENT)
        self.formfile('vocal_contest_participate', 'file', AUDIO_FILE)
        self.submit200()
        self.assert_equal(VocalContestParticipant.objects.count(), 2)
        self.url('vocal_contest_participate')
        self.find('errorlist')
        self.find('c2'+TEST_TITLE)

    def test_contest_participate_ended(self):
        self.contest.registration_end_date = YESTERDAY
        self.contest.save()
        self.go200('vocal_contest_participate')
        self.url('vocal_contest_index')

    def test_participate_fill_tag(self):
        self.go200('vocal_contest_index')
        self.find('Прийняти участь')

        tag_title = 'Jingle Bells'
        self.login(USERNAME, PASSWORD, url = 'auth_login', formid = 'id_login')
        self.go200('vocal_contest_participate')
        self.showforms()
        self.fv('vocal_contest_participate', 'category', str(self.cat1.id))
        self.formfile('vocal_contest_participate', 'file', AUDIO_FILE)
        self.submit200()
        self.assert_equal(VocalContestParticipant.objects.count(), 1)
        vcp = self.assert_read(VocalContestParticipant, user = self.user, title = tag_title)
        self.url('vocal_contest_participant_detail', [vcp.id])
        self.find(tag_title)

        self.go200('vocal_contest_participate')
        self.fv('vocal_contest_participate', 'category', str(self.cat2.id))
        self.formfile('vocal_contest_participate', 'file', NOTAGS_FILE)
        self.submit200()
        self.assert_equal(VocalContestParticipant.objects.count(), 2)
        vcp = self.assert_read(VocalContestParticipant, user = self.user, title = 'notags')
        self.url('vocal_contest_participant_detail', [vcp.id])
        self.find('notags')


    def test_contest_participate_delete(self):
        vc1 = self.assert_create(VocalContestParticipant, 
            user = self.user,
            contest = self.contest,
            category = self.cat1,
            file = self.test_file.name,
            title = "part1_1")

        self.helper('create_user','u','p')
        self.login('u', 'p', url = 'auth_login', formid = 'id_login')
        self.go('vocal_contest_participant_delete', [vc1.id])
        self.code(404)
        self.logout()
        self.login(USERNAME, PASSWORD,url = 'auth_login', formid = 'id_login')
        self.go200('vocal_contest_participant_delete', [vc1.id])
        self.fv('object_delete', '__confirm__', '1')
        self.submit200()
        self.url('vocal_contest_index')
        self.assert_equal(VocalContestParticipant.objects.count(), 0)


    def test_contest_participate_ended(self):
        self.login(USERNAME, PASSWORD, url = 'auth_login', formid = 'id_login')
        self.contest.registration_end_date = YESTERDAY
        self.contest.save()
        self.go200('vocal_contest_participate')
        self.url('vocal_contest_index')


    def test_show_contest_parts(self):
        self.assert_create(VocalContestParticipant, 
            user = self.user,
            contest = self.contest,
            category = self.cat1,
            file = self.test_file.name,
            title = "part1_1")

        self.assert_create(VocalContestParticipant, 
            user = self.user,
            contest = self.contest,
            category = self.cat1,
            file = self.test_file.name,
            title = "part1_2")

        self.assert_create(VocalContestParticipant, 
            user = self.user,
            contest = self.contest,
            category = self.cat2,
            file = self.test_file.name,
            title = "part2_1")
        
        self.go200('vocal_contest_filter', ['1','date'])
        self.find('part1_1')
        self.find('part1_2')
        self.notfind('part2_1')

        # should show the same. First category is default and date ordering
        self.go200('vocal_contest_index' )
        self.find('part1_1')
        self.find('part1_2')
        self.notfind('part2_1')

        self.go200('vocal_contest_filter', ['2','rate'])
        self.notfind('part1_1')
        self.notfind('part1_2')
        self.find('part2_1')

    def test_show_voting(self):
        """
        only after registration is ended and for versed users
        also no voting for own objects
        """
        self.login(USERNAME, PASSWORD, url = 'auth_login', formid = 'id_login')
        alteruser = self.helper('create_user', 'u','p')
        self.assert_create(VocalContestParticipant, 
            user = alteruser,
            contest = self.contest,
            category = self.cat1,
            file = self.test_file.name,
            title = "part1_1")
        self.go200('vocal_contest_index')
        self.find('part1_1')
        self.notfind('upvote')
        self.user.date_joined = datetime.datetime(2010,2,2)
        self.user.save()
        self.go200('vocal_contest_index')
        self.notfind('upvote')
        self.contest.registration_end_date = YESTERDAY
        self.contest.save()
        self.go200('vocal_contest_index')
        self.find('upvote')
        self.user.date_joined = datetime.datetime.today()
        self.user.save()
        self.go200('vocal_contest_index')
        self.notfind('upvote')
        alteruser.date_joined = datetime.datetime(2010,2,2)
        alteruser.save()
        self.logout()
        self.login('u', 'p', url = 'auth_login', formid = 'id_login')
        self.go200('vocal_contest_index')
        self.notfind('upvote')


    def test_agreement_page(self):
        self.login(USERNAME, PASSWORD, url = 'auth_login', formid = 'id_login')
        fp = self.assert_create(FlatPage, title = "Agreement", content = "<p>Do you agree to sell your soul to us?</p>")
        self.contest.rules = fp
        self.contest.save()
        self.go200('vocal_contest_participate')
        self.find('Agreement')
        self.find('Do you agree')
        self.fv('agreement_form', '__confirm__', "1")
        self.submit200()
        self.notfind('Agreement')
        self.notfind('Do you agree')
        self.assert_equal(VocalContestCategory.objects.get_cats().count(), 2)
        self.showforms()
        self.fv('vocal_contest_participate', 'title', 'c'+TEST_TITLE)
        self.fv('vocal_contest_participate', 'category', '1')
        self.fv('vocal_contest_participate', 'description', TEST_CONTENT)
        self.formfile('vocal_contest_participate', 'file', AUDIO_FILE)
        self.submit200()
        self.assert_equal(VocalContestParticipant.objects.count(), 1)
        self.contest.rules = None
        self.contest.save()
    
    def test_contest_archive(self):
        self.contest.start_date = YESTERDAY
        self.contest.registration_end_date = YESTERDAY
        self.contest.end_date = YESTERDAY
        self.contest.save()
        self.assert_equal(self.contest.status(), 'finished')
        self.go200('news_index')
        self.find('Результати')
        self.assert_create(VocalContest, title = 't',
            description = 'd')
        self.go200('news_index')
        self.find('Відкрито реєстрацію')
        self.find('Архів')
        self.showlinks()
        self.find('Архів конкурсів')
        self.go200('vocal_contest_archive')
        self.find(TEST_TITLE)


    def test_real_contest_participate(self):
        """not working"""
        self.login(USERNAME, PASSWORD, url = 'auth_login', formid = 'id_login')
        self.contest.is_real = True
        self.contest.save()
        self.go200('news_index')
        self.find('Оф-лайн конкурс вокалістів')
        self.find('Відкрито реєстрацію')

        self.go200('vocal_contest_participate')
        self.fv('vocal_contest_participate', 'category', '1')
        self.submit200()
        self.assert_equal(RealVocalContestParticipant.objects.count(), 1)

    def test_real_contest_guest(self):
        """not working"""
        self.login(USERNAME, PASSWORD, url = 'auth_login', formid = 'id_login')
        self.contest.is_real = True
        self.contest.save()
        self.go200('news_index')
        self.find('Оф-лайн конкурс вокалістів')
        self.find('Відкрито реєстрацію')
        self.find('Гостей')

        self.go200('vocal_contest_guest')
        self.fv('vocal_contest_guest', 'places', '3')
        self.submit200()
        self.assert_equal(RealVocalContestGuest.objects.count(), 1)
        self.go200('news_index')
        self.find('Гостей: 3')

