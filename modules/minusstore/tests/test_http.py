#-*- coding: utf-8 -*-
import os, sys
import datetime
import shutil
import tempfile
from mutagen.mp3 import MP3

from django.utils.encoding import smart_str
from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase #weird %)
from django.core.management import call_command

from tddspry.django import TestCase
from tddspry.django.helpers import USERNAME, PASSWORD

from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType

from hitcount.models import HitCount, Hit
from minusstore.models import MinusRecord, FileType, MinusAuthor, MinusCategory, MinusStats, MinusWeekStats, MinusPlusRecord, MinusStopWord
from albums.models import Audio, AudioAlbum
 
TEST_FILES = os.path.join(settings.STORAGE_ROOT,'testfiles')
AUDIO_FILE = os.path.join(TEST_FILES,'04 - jingle bells.mp3')
DUMMY_FILE = os.path.join(TEST_FILES,'dummy.txt')
NOTAGS_FILE = os.path.join(TEST_FILES,'notags.mp3')
MIDI_FILE = os.path.join(TEST_FILES,'midifile.mid')
AUDIO_1251_FILE = os.path.join(TEST_FILES, '_Orysjamiks.mp3')
#YOUTUBE_URL = "http://www.youtube.com/watch?v=2LBBpcFgvHU"
YOUTUBE_URL = "http://www.youtube.com/watch?feature=player_embedded&v=Zn2Ob5PepsU"
YOUTUBE_EMBED = """<object style="height: 344px; width: 425px"><param name="movie" value="http://www.youtube.com/v/2LBBpcFgvHU"><param name="allowFullScreen" value="true"><param name="allowScriptAccess" value="always"><embed src="http://www.youtube.com/v/2LBBpcFgvHU" type="application/x-shockwave-flash" allowfullscreen="true" allowScriptAccess="always" width="425" height="344"></object>"""
CR = r'\<div id="content"\>(.|\n)*(%s)(.|\n)*\</div\>' #content regexp
STOPWORDS = u"гурт дует тріо супер порно мінус"

class TestMinusUploads(TestCase ):
    fixtures = ['fixtures/test_data.json']
    def setup(self):
        self.superuser = self.helper('create_superuser')
        self.user = self.helper('create_user','u','p')
        self.login_to_admin(USERNAME,PASSWORD)
        self.type = self.assert_create(FileType, type_name="audio", filetype = "mp3,mid")
        cat = self.assert_create(MinusCategory, name= "onecat")
        cat = self.assert_create(MinusCategory, name= "twocat")
        for word in STOPWORDS.split():
            MinusStopWord.objects.create(word = word)
        p = MinusStopWord.objects.get(word = u'порно')
        p.blocked = True
        p.save()

    def teardown(self):
        for object in MinusRecord.objects.all():
            try:
                object.delete()
            except MinusRecord.DoesNotExist:
                pass

    def test_successfull_upload(self):
        """upload mp3 and guess tags"""
        self.go200('minus_upload')
        self.assert_equal(MinusRecord.objects.count(),0)
        self.assert_equal(MinusAuthor.objects.count(),0)
        self.find('Завантажити мінусовку')
        self.find('Файл')
        self.formfile('minus_upload', 'file', AUDIO_FILE)
        self.submit200()
        self.assert_equal(MinusAuthor.objects.count(),1)
        self.assert_equal(MinusRecord.objects.count(),1)
        minus = MinusRecord.objects.all()[0]
        self.url('minus_detail', [minus.author, minus.id])
        self.assert_equal(minus.author.name,"Richard Cheese")
        self.assert_equal(minus.title,"Jingle Bells")
        self.assert_equal(minus.length,datetime.time(0,1,10))
        self.assert_equal(minus.bitrate, 195)
        self.assert_equal(minus.user, self.superuser)

    def test_edit(self):
        """ edit record"""
        self.go200('minus_upload')
        self.formfile('minus_upload', 'file', AUDIO_FILE)
        self.submit200()
        self.go200('minus_edit', [self.superuser, 1])
        self.find("Richard")
        self.formfile('minus_upload', 'file', MIDI_FILE )
        self.fv('minus_upload', 'author', "brams")
        self.fv('minus_upload', 'title', "midifile")
        self.submit200()
        minus = MinusRecord.objects.all()[0]
        self.assert_equal(minus.author.name,"Brams")
        self.assert_equal(minus.title,u"midifile")
        self.assert_equal(minus.user, self.superuser)
        self.go200('minus_edit', [self.superuser, 1])
        self.fv('minus_upload', 'author', "kirams")
        self.fv('minus_upload', 'add_category', 'yuppie')
        self.submit200()
        minus = MinusRecord.objects.all()[0]
        self.url('minus_detail', [minus.author, minus.id])
        self.assert_equal(minus.author.name,"Kirams")

    def test_edit_prems(self):
        self.go200('minus_upload')
        self.formfile('minus_upload', 'file', AUDIO_FILE)
        self.fv('minus_upload', 'categories', 'onecat')
        self.submit200()
        un = 'usr'
        pw = '111'
        self.logout('auth_logout')
        user = self.helper("create_user", un, pw)
        self.login(un, pw, url='auth_login', formid='id_login')
        self.go('minus_edit', [self.superuser, 1])
        self.code(404)
        self.go('minus_edit', [user, 1])
        self.code(404)
        self.logout('auth_logout')
        user.is_staff = True
        user.save()
        self.login(un, pw, url='auth_login', formid='id_login')
        self.go('minus_edit', [user, 1])
        self.code(200)
        self.fv('minus_upload', 'author', "brams")
        self.fv('minus_upload', 'add_category', 'yuppie')
        self.submit200()
        minus = MinusRecord.objects.all()[0]
        self.assert_equal(minus.author.name, "Brams")
        self.assert_equal(minus.user, self.superuser)
        self.assert_equal(MinusAuthor.objects.count(),1)    #authors without recs
                                                            #should be deleted
        self.assert_equal(MinusAuthor.objects.all()[0].name,"Brams")
        self.assert_equal(MinusCategory.objects.count(),2)    #authors without recs
        self.assert_equal(MinusCategory.objects.all()[1].name,"yuppie")

    def test_delete(self):
        self.go200('minus_upload')
        self.formfile('minus_upload', 'file', AUDIO_FILE)
        self.fv('minus_upload', 'categories', 'onecat')
        self.submit200()
        self.go200('minus_delete', [self.superuser, 1])
        self.fv('id_photo_delete', '__confirm__', '1')
        self.submit200()
        self.url('minus_author_by_letter', "R")
        self.assert_equal(MinusRecord.objects.count(),0)
        self.assert_equal(MinusAuthor.objects.count(),0)
        self.assert_equal(MinusCategory.objects.count(),0)

    def test_up_assign_categories(self):
        """testing issues when categories was not added"""
        self.go200('minus_upload')
        self.formfile('minus_upload', 'file', AUDIO_FILE)
        self.fv('minus_upload', 'categories', 'onecat')
        self.submit200()
        minus = MinusRecord.objects.all()[0]
        self.url('minus_detail', [minus.author, minus.id])
        self.assert_equal(minus.categories.count(), 1)
        self.assert_equal(minus.categories.all()[0].name, 'onecat')

    def test_up_add_category(self):
        """add custom category"""
        self.go200('minus_upload')
        self.formfile('minus_upload', 'file', AUDIO_FILE)
        self.fv('minus_upload', 'add_category', 'yuppie')
        self.submit200()
        minus = MinusRecord.objects.all()[0]
        self.url('minus_detail', [minus.author, minus.id])
        self.assert_equal(minus.categories.count(), 1)
        self.assert_equal(minus.categories.all()[0].name, 'yuppie')
        self.assert_equal(MinusCategory.objects.count(), 3)

    def test_category_mixed(self):
        """add custom and select from existing"""
        self.go200('minus_upload')
        self.formfile('minus_upload', 'file', AUDIO_FILE)
        self.fv('minus_upload', 'categories', 'onecat')
        self.fv('minus_upload', 'add_category', 'yuppie')
        self.submit200()
        minus = MinusRecord.objects.all()[0]
        self.assert_equal(minus.categories.count(), 2)
        self.assert_equal(minus.categories.all()[0].name, 'onecat')
        self.assert_equal(minus.categories.all()[1].name, 'yuppie')

    def test_category_mixed_on_edit(self):
        """There were some issues with it"""
        self.go200('minus_upload')
        self.formfile('minus_upload', 'file', AUDIO_FILE)
        self.fv('minus_upload', 'categories', 'onecat')
        self.submit200()
        minus = MinusRecord.objects.all()[0]
        self.assert_equal(minus.categories.count(), 1)
        self.go200('minus_edit', [self.superuser, minus.id])
        self.fv('minus_upload', 'add_category', 'yuppie')
        self.submit200()
        self.assert_equal(minus.categories.count(), 2)
        self.assert_equal(minus.categories.all()[0].name, 'onecat')
        self.assert_equal(minus.categories.all()[1].name, 'yuppie')

    def test_folk_up(self):
        'upload folk reccord.'
        self.go200('minus_upload')
        self.formfile('minus_upload', 'file', AUDIO_FILE)
        self.fv('minus_upload', 'is_folk', True)
        self.submit200()
        minus = MinusRecord.objects.all()[0]
        self.url('minus_detail', [minus.author, minus.id])
        self.assert_equal(minus.is_folk, True)
        self.assert_equal(minus.author.name,u"Народна")
        self.assert_equal(minus.title,"Jingle Bells")
        self.assert_equal(minus.user, self.superuser)


    def test_upload_wrong_file(self):
        """upload unallowed file"""
        self.go200('minus_upload')
        self.assert_equal(MinusRecord.objects.count(),0)
        self.assert_equal(MinusAuthor.objects.count(),0)
        self.formfile('minus_upload', 'file', DUMMY_FILE)
        self.submit200()
        self.find('Невідомий тип файлу')
        self.assert_equal(MinusRecord.objects.count(),0)
        self.assert_equal(MinusAuthor.objects.count(),0)
        
    def test_upload_wrong_file(self):
        """upload not-tagged mp3"""
        self.go200('minus_upload')
        self.assert_equal(MinusRecord.objects.count(),0)
        self.assert_equal(MinusAuthor.objects.count(),0)
        self.formfile('minus_upload', 'file', NOTAGS_FILE)
        self.submit200()
        self.assert_equal(MinusRecord.objects.count(),1)
        self.assert_equal(MinusAuthor.objects.count(),1)
        minus = MinusRecord.objects.all()[0]
        self.assert_equal(minus.title, 'notags')
        self.assert_equal(unicode(minus.author), u'Невідомий Виконавець')

    def test_upload_non_audio(self):
        "tags should be guessed from filename"
        self.go200('minus_upload')
        self.formfile('minus_upload', 'file', MIDI_FILE)
        self.submit200()
        self.assert_equal(MinusRecord.objects.count(),1)
        minus = MinusRecord.objects.all()[0]
        self.assert_equal(minus.title, "midifile")
        self.assert_equal(unicode(minus.author), u'Невідомий Виконавець')

    def test_file_too_large(self):
        "upload large file"
        oldmax = settings.MAX_FILE_SIZE
        settings.MAX_FILE_SIZE = 1
        self.go200('minus_upload')
        self.formfile('minus_upload', 'file', AUDIO_FILE)
        self.submit200()
        settings.MAX_FILE_SIZE = oldmax 
        self.find("повинен не перевищувати")
        self.assert_equal(MinusRecord.objects.count(),0)
        self.assert_equal(MinusAuthor.objects.count(),0)

    def test_upload_1251(self):
        "different encodings. issue #32"
        self.go200('minus_upload')
        self.formfile('minus_upload', 'file', AUDIO_1251_FILE)
        self.submit200()
        self.find("Мандри")


    def test_upload_nofile(self):
        self.go200('minus_upload')
        self.fv('minus_upload', 'author', 'hello') 
        self.submit200()
        self.find("Додайте будьласка файл")

    def test_upload_similar_file(self):
        "if files are similar, do not upload them"
        self.go200('minus_upload')
        self.formfile('minus_upload', 'file', AUDIO_FILE)
        self.submit200()
        self.go200('minus_upload')
        self.formfile('minus_upload', 'file', AUDIO_FILE)
        self.submit200()
        self.url('minus_upload')
        self.find("Файл вже присутній у базі")
        self.assert_equal(MinusRecord.objects.count(),1)
        minus = MinusRecord.objects.all()[0]
        minus.file.name = "Changed.mp3"     # we asume that this
        minus.save()                        # file is different
        self.go200('minus_upload')
        self.formfile('minus_upload', 'file', AUDIO_FILE)
        self.submit200()
        self.notfind("Файл вже присутній у базі")

    def test_embed_ok(self):
        """various right embeding of video"""
        self.go200('minus_upload')
        self.formfile('minus_upload', 'file', AUDIO_FILE)
        self.fv('minus_upload', 'id_embed_video', YOUTUBE_URL) 
        self.submit200()
        self.notfind("Невірний")
        self.show()
        self.find("youtube_video")
        self.find("<object width")
        self.go200('minus_upload')
        self.formfile('minus_upload', 'file', NOTAGS_FILE)
        self.fv('minus_upload', 'id_embed_video', YOUTUBE_EMBED) 
        self.submit200()
        self.notfind("Невірний")
        self.show()
        self.find("<object width")

    def test_embed_bad(self):
        "wrong embeds"
        self.go200('minus_upload')
        self.formfile('minus_upload', 'file', AUDIO_FILE)
        self.fv('minus_upload', 'id_embed_video',"blabla") 
        self.submit200()
        self.find("Невірний")

        self.formfile('minus_upload', 'file', AUDIO_FILE)
        self.fv('minus_upload', 'id_embed_video',"youtube blabla") 
        self.submit200()
        self.find("Невірний")

        self.formfile('minus_upload', 'file', AUDIO_FILE)
        self.fv('minus_upload', 'id_embed_video',"<object>Nasty thing</object>") 
        self.submit200()
        self.find("Невірний")

        self.formfile('minus_upload', 'file', AUDIO_FILE)
        self.fv('minus_upload', 'id_embed_video', 'youtube.com') #superhacker detected
        self.submit200()
        self.notfind("Невірний")
        self.notfind("youtube_video")  #but no fun at the end

    def test_agreement_page(self):
        f = FlatPage.objects.create(title = 'f',
            url = '/rules/', 
            content = 'rulerule')
        self.go200('minus_upload')
        self.find('rulerule')
        self.fv('agreement_form', '__confirm__', 1)
        self.submit200()
        self.notfind('rulerule')
        self.find('Файл')

    def test_change_user(self):
        """User in Post-data can be changed"""
        self.go200('minus_upload')
        self.formfile('minus_upload', 'file', AUDIO_FILE)
        
        self.config("readonly_controls_writeable", 1)
        self.fv('minus_upload', 'user', '2')
        self.submit200()
        self.config("readonly_controls_writeable", 0)
        minus = MinusRecord.objects.all()[0]
        self.url('minus_detail', [minus.author, minus.id])
        self.assert_equal(minus.user, self.superuser)
    

    def test_plusrecord(self):
        """uploading pluses"""
        self.go200('minus_upload')
        self.find('Завантажити плюсовку')
        self.go200('minus_plus_upload')
        self.formfile('minus_plus_upload', 'file', AUDIO_FILE)
        self.submit200()
        self.url('minus_by_user',[self.superuser.username])
        self.assert_equal(MinusPlusRecord.objects.count(), 1)
        self.go200('minus_upload')
        self.formfile('minus_upload', 'file', AUDIO_FILE)
        self.submit200()
        m = MinusRecord.objects.all()[0]
        p = MinusPlusRecord.objects.all()[0]
        self.assert_equal(p.minus , m)

    def test_plusrecors_delete(self):
        """uploading pluses, seenig FlatPage, deleting"""
        f = FlatPage.objects.create(title = 'f',
            url = '/minus/upload/plus/done/',
            content = 'flapi')
        self.go200('minus_plus_upload')
        self.formfile('minus_plus_upload', 'file', AUDIO_FILE)
        self.submit200()
        self.url('minus_plus_upload_done')
        self.find('flapi')
        self.go200('minus_plus_upload')
        self.formfile('minus_plus_upload', 'file', AUDIO_FILE)
        self.submit200()
        self.assert_equal(MinusPlusRecord.objects.count(), 2)
        self.go200('minus_upload')
        self.formfile('minus_upload', 'file', AUDIO_FILE)
        self.submit200()
        self.find('Плюс')
        m = MinusRecord.objects.all()[0]
        p = MinusPlusRecord.objects.all()[0]
        self.assert_equal(p.minus , m)
        self.assert_equal(MinusPlusRecord.objects.count(), 1)
        self.go200('plus_delete', [p.id])
        self.fv('object_delete','__confirm__', 1)
        self.submit200()
        self.assert_equal(MinusPlusRecord.objects.count(), 0)


    def test_plusrecords_on_edit(self):
        """
        on changing plusrecords, old one should be detached
        and deleted
        """
        self.go200('minus_plus_upload')
        self.formfile('minus_plus_upload', 'file', AUDIO_FILE)
        self.submit200()
        self.go200('minus_upload')
        self.formfile('minus_upload', 'file', AUDIO_FILE)
        self.submit200()
        self.go200('minus_plus_upload')
        self.formfile('minus_plus_upload', 'file', AUDIO_FILE)
        self.submit200()
        self.assert_equal(MinusPlusRecord.objects.count(), 2)
        self.go200('minus_edit', [self.superuser, 1])
        self.fv('minus_upload', 'author', "brams")
        self.submit200()
        self.find('Плюс')
        self.assert_equal(MinusPlusRecord.objects.count(), 1)


    def test_plusrecords_on_delete(self):
        self.go200('minus_plus_upload')
        self.formfile('minus_plus_upload', 'file', AUDIO_FILE)
        self.submit200()
        self.go200('minus_upload')
        self.formfile('minus_upload', 'file', AUDIO_FILE)
        self.submit200()
        self.go200('minus_delete', [self.superuser, 1])
        self.fv('id_photo_delete', '__confirm__', '1')
        self.submit200()



    def test_moderator_uploads_plusrecord(self):
        """plus should be attached to minus.user not to moderator"""
        self.go200('minus_plus_upload_user',[self.user.id])
        self.formfile('minus_plus_upload', 'file', AUDIO_FILE)
        self.submit200()
        self.logout('auth_logout')
        self.login('u', 'p', url='auth_login', formid='id_login')
        self.go200('minus_upload')
        self.showforms()
        self.formfile('minus_upload', 'file', AUDIO_FILE)
        self.submit200()
        plus = MinusPlusRecord.objects.all()[0]
        minus = MinusRecord.objects.all()[0]
        self.assert_equal(plus.user, self.user)
        self.assert_equal(minus.user, self.user)
        self.assert_equal(plus.minus, minus)
        

    def test_author_validation(self):
        """Remove stop-words from names"""
        self.go200('minus_upload')
        self.formfile('minus_upload', 'file', AUDIO_FILE)
        self.fv('minus_upload', 'author', 'Дует Співаки')
        self.submit200()
        #self.assert_equal(smart_str(MinusAuthor.objects.all()[0].name), smart_str('Співаки'))
        MinusAuthor.objects.get(name = smart_str('Співаки'))

    def test_track_validation(self):
        """Remove stop-words from titles """
        self.go200('minus_upload')
        self.formfile('minus_upload', 'file', AUDIO_FILE)
        self.fv('minus_upload', 'title', 'мінус тест')
        self.submit200()
        MinusRecord.objects.get(title = u'Тест')

        self.go200('minus_upload')
        self.formfile('minus_upload', 'file', AUDIO_FILE)
        self.fv('minus_upload', 'title', 'порно тест')
        self.submit200()
        self.url('minus_upload')
        self.assert_equal(MinusRecord.objects.count(), 1) # no new record


    def test_author_name_surname(self):
        """
        Often users misplace song author's name and surname
        so we can automagically place it right
        """
        self.assert_create(MinusAuthor, name = 'Гаврилів Петро')
        wrongaut = self.assert_create(MinusAuthor,
                name = 'Гаврилів Петро і Маша Распутіна')

        TEST_FILE = tempfile.NamedTemporaryFile(dir=TEST_FILES,suffix='.mp3')
        shutil.copy2(AUDIO_FILE, TEST_FILE.name)
        self.assert_create(MinusRecord, user=self.user,
                file=TEST_FILE.name,
                title = "first",
                author = wrongaut, type = self.type
                )
        self.assert_create(MinusRecord, user=self.user,
                file=TEST_FILE.name,
                title = "second",
                author = wrongaut, type = self.type
                )
        #wrong author has two records

        self.go200('minus_upload')
        self.formfile('minus_upload', 'file', AUDIO_FILE)
        self.fv('minus_upload', 'title', 'ourecord')
        self.fv('minus_upload', 'author', 'Петро Гаврилів')
        self.submit200()
        self.assert_equal(MinusAuthor.objects.count(),2)
        self.assert_equal(MinusAuthor.objects.get(name = \
                smart_str('Гаврилів Петро')).\
                records_by.all()[0].title, 'ourecord')


    def test_filling_idv3tags(self):
        self.go200('minus_upload')
        self.formfile('minus_upload', 'file', AUDIO_FILE)
        self.fv('minus_upload', 'title', 'Test Idv3')
        self.fv('minus_upload', 'author', 'Петро Гаврилів')
        self.submit200()

        minus = MinusRecord.objects.get(title = 'Test Idv3')
        mp3info = MP3(minus.file.path)
        self.assert_equal(mp3info['TPE1'].text[0], u'Петро Гаврилів')
        self.assert_equal(mp3info['TIT2'].text[0], u'Test Idv3')
        self.assert_equal(mp3info['COMM::\'ukr\''].text[0], u'Звантажено з minus.lviv.ua')
        self.assert_equal(mp3info['TALB'].text[0], u"Записи користувача " + minus.user.get_profile().fullname())
        
        

        



        

        


class TestMinusDisplays(TestCase):
    fixtures = ['fixtures/test_data.json']
    def setup(self):
        self.user = self.helper('create_user')

        self.assert_create(MinusAuthor, name="Test0")
        self.assert_create(MinusAuthor, name="Test1")
        typ = self.assert_create(FileType, type_name="audio", filetype = "mp3,wav")
        typ2 = self.assert_create(FileType, type_name="midi", filetype = "mid,kar")

        cat = self.assert_create(MinusCategory, name= "tst")
        for i in xrange(10): 
            self.assert_create(MinusRecord, 
                        title = "test"+str(i),
                        author = MinusAuthor.objects.get(name = "Test"+str(i%2)), #two authors
                        file = NOTAGS_FILE,
                        user = self.user,
                        type = typ,
                        )
        mid = self.assert_create(MinusRecord,title = "midi_rec",
                        author = MinusAuthor.objects.get(name = "Test0"),
                        type = typ2,
                        user = self.user,
                        file = MIDI_FILE,
                        alternative = True
                        )

        mid.categories = [cat]
        mid.save()


    def _test_minus_index(self):
        """
        TODO: Remake me for templatetag

        minuses index page
        displays items in order of arival
        """
        self.assert_equal(MinusRecord.objects.count(),11)
        self.go200('minus_index')
        for i in xrange(10):
            self.find('test'+str(i))

    def test_by_author(self):
        """
        display minuses by author
        """
        self.assert_equal(MinusRecord.objects.count(),11)
        self.go200('minus_by_author', ['Test0'])
        self.find(CR % 'Test0')
        for i in xrange(10):
            if i % 2 == 0:
                self.find(CR % ('test'+str(i)))
            else:
                self.notfind(CR % ('test'+str(i)))
        self.find(CR % "midi_rec")

    def test_by_type(self):
        "filter minuses by type"
        self.go200('minus_by_type',  ['audio'])
        for i in xrange(10):
            self.find(CR % ('test'+str(i)))
        self.notfind(CR % 'midi_rec')
        
        self.go200('minus_by_type', ['midi'])
        for i in xrange(10):
            self.notfind(CR % ('test'+str(i)))
        self.find(CR % 'midi_rec')

    def test_authors_index(self):
        "display available minus-authors"
        self.go200('minus_author_index')
        self.find("Test0")
        self.find("Test1")

    def test_difficult_author_names(self):
        "authors with long and difficult names"
        names = ["Кириличний", "007", "Чиж & Ко.", "_CraZy Bastards-yea!_"]
        for name in names:
            author = self.assert_create(MinusAuthor, name = name)
            mod_url = author.get_absolute_url()
            vi_url = reverse('minus_by_author', args=[name])
            self.assert_equal(mod_url, vi_url)

    def test_minus_detail_page(self):
        "detail page"
        self.go200('minus_detail', ["Test0", "1"])
        self.find('test0')
        #TODO test display of fields

    def test_time_archives(self):
        "archives by year, month, day"
        now = datetime.datetime.now()
        oldrec = MinusRecord.objects.get(id=1)
        newrecs = MinusRecord.objects.filter(id__gt=1)
        olddate = datetime.datetime(2009,02,23,1,1,1,1)
        oldrec.pub_date =  olddate
        oldrec.save()
        self.go200('minus_archive_year', [olddate.year])
        
        self.find(str(CR % oldrec.title))
        for rec in newrecs:
            self.notfind(CR % rec.title)
        self.go200('minus_archive_year', [now.year])
        self.notfind(CR % oldrec.title)
        for rec in newrecs:
            self.find(CR % rec.title)

        self.go200('minus_archive_month', [olddate.year, olddate.month])
        self.find(oldrec.title)
        for rec in newrecs:
            self.notfind( CR % rec.title)

        print now.year, now.month
        self.go200('minus_archive_month', [now.year, now.month])
        self.notfind(CR % oldrec.title)
        for rec in newrecs:
            self.find(CR % rec.title)

        self.go200('minus_archive_day', [olddate.year, olddate.month, olddate.day])
        self.find(CR % oldrec.title)
        for rec in newrecs:
            self.notfind(CR % rec.title)
        self.go200('minus_archive_day', [now.year, now.month, now.day])
        self.notfind(CR % oldrec.title)
        for rec in newrecs:
            self.find(CR % rec.title)



    def test_authors_by_letter(self):
        "filter artists by letter"
        self.assert_create(MinusAuthor, name="ьщачло")
        self.assert_create(MinusAuthor, name="0test11")
        self.assert_equal(MinusAuthor.objects.count(),4)
        self.go200('minus_author_by_letter', ['T'])
        self.find(CR % 'Test0')
        self.find(CR % 'Test1')
        self.notfind(CR % 'ьщачло')
        self.go200('minus_author_by_letter', [u'ь'])
        self.notfind(CR % 'Test1')
        self.find(CR % 'ьщачло')
        self.go200('minus_author_by_letter', ['0-9'])
        self.notfind(CR % 'Test1')
        self.notfind(CR % 'ьщачло')
        self.find(CR % '0test11')

        self.go200('minus_author_by_letter', [u'0-9'])
        self.notfind(CR % 'Test1')
        self.notfind(CR % 'ьщачло')
        self.find(CR % '0test11')

    def test_minus_by_user(self):
        altuser = self.helper('create_user', username = 'bla')
        mid = MinusRecord.objects.get(title = "midi_rec")
        mid.user = altuser
        mid.save()
        self.go200('minus_by_user', [self.user.username])
        for i in xrange(10):
            self.find(CR % ('test'+str(i)))
        self.notfind(CR % 'midi_rec')


    def test_ajax_responses(self):
        self.go200('minus_by_author_ajax', ['Test0','','',''])
        for i in xrange(10):
            if i % 2 == 0:
                self.find('test'+str(i))
        self.find("midi_rec")

        self.go200('minus_by_author_ajax', ['Test0','audio','',''])
        for i in xrange(10):
            if i % 2 == 0:
                self.find('test'+str(i))
        self.notfind("midi_rec")

        self.go200('minus_by_author_ajax', ['Test0','midi','',''])
        for i in xrange(10):
            if i % 2 == 0:
                self.notfind('test'+str(i))
        self.find("midi_rec")

        self.go200('minus_by_author_ajax', ['Test0','midi','m',''])
        for i in xrange(10):
            if i % 2 == 0:
                self.notfind('test'+str(i))
        self.find("midi_rec")

        self.go200('minus_by_author_ajax', ['Test0','midi','z',''])
        for i in xrange(10):
            if i % 2 == 0:
                self.notfind('test'+str(i))
        self.notfind("midi_rec")

        self.go200('minus_by_author_ajax', ['Test0','','','regular'])
        self.notfind("midi_rec")

        self.go200('minus_by_author_ajax', ['Test0','','','alternative'])
        self.find("midi_rec")

    def test_downloads(self):
        """Stats for downloading files"""
        min = MinusRecord.objects.get(id = 1)
        self.assert_equal(min.rating.score , 0)

        self.login(USERNAME, PASSWORD, url='auth_login', formid='id_login')
        self.go('minus_download', ["Test0", 1])
        min = MinusRecord.objects.get(id = 1)

        hits = HitCount.objects.get(content_type = ContentType.objects.get_for_model(min),
            object_pk= min.pk)
        self.assert_equal(hits.hits, 1)
        self.assert_equal(min.rating.score , 1)
        stat = MinusStats.objects.get(minus = min, date = datetime.date.today())
        self.assert_equal(stat.rate, 1)
        #stats must be counted for one day

        self.go('minus_download', ["Test0", 1])
        min = MinusRecord.objects.get(id = 1)
        hits = HitCount.objects.get(content_type = ContentType.objects.get_for_model(min),
            object_pk= min.pk)
        self.assert_equal(hits.hits, 1)
        self.assert_equal(min.rating.score , 1)
        stat = MinusStats.objects.get(minus = min, date = datetime.date.today())
        self.assert_equal(stat.rate, 1)
        # second time, same result
        stat.date = datetime.date.today() - datetime.timedelta(days=1)
        stat.save()

        self.logout('auth_logout')
        user = self.helper('create_user', 'u','n', 'm@example.com')
        self.login('u', 'n', url='auth_login', formid='id_login')

        self.go('minus_download', ["Test0", 1])
        min = MinusRecord.objects.get(id = 1)
        hits = HitCount.objects.get(content_type = ContentType.objects.get_for_model(min),
            object_pk= min.pk)
        self.assert_equal(hits.hits, 2)
        self.assert_equal(min.rating.score , 2)
        stat = MinusStats.objects.get(minus = min, date = datetime.date.today())
        self.assert_equal(stat.rate, 1) #and now we have a new stat
        self.go('minus_download', ["Test0", 1])
        stat = MinusStats.objects.get(minus = min, date = datetime.date.today())
        
        stat.date = datetime.date.today() - datetime.timedelta(days=8)
        stat.save()
        self.go('minus_download', ["Test0", 1])
        call_command('generate_stats')
        wstat = MinusWeekStats.objects.get(minus = min)
        wstat.rate = 1 #other stat with  is outside of our week
        
    def test_commenting(self):
        un = 'usr'
        pw = '111'
        user = self.helper("create_user", un, pw)
        self.login(un,pw,url='auth_login', formid='id_login')
        # different user comments
        self.go200('minus_detail', ["Test0", "1"])
        self.fv('comment_form', 'comment', 'hello comment')
        self.submit200()
        self.find('hello comment')

        from minusstore.models import CommentNotify
        self.assert_equal(CommentNotify.objects.count(), 1)

        self.logout('auth_logout')

        #owner comments
        self.login(USERNAME, PASSWORD, url='auth_login', formid='id_login')
        self.go200('minus_detail', ["Test0", "1"])
        self.fv('comment_form', 'comment', 'hello owner')
        self.submit200()
        self.find('hello owner')

        self.assert_equal(CommentNotify.objects.count(), 1)
        
        self.go200('comments_for', [USERNAME])
        self.find('hello comment')
        self.notfind('hello owner')
        from django.contrib.comments.models import Comment
        Comment.objects.all()[0].delete()

        self.go200('comments_for', [USERNAME])
        self.notfind('hello comment')




class TestMinusAlbumsMoving(TestCase):
    fixtures = ['fixtures/test_data.json']
    def setup(self):


        global TEST_FILE
        TEST_FILE = tempfile.NamedTemporaryFile(dir=TEST_FILES,suffix='.mp3')
        shutil.copy2(AUDIO_FILE, TEST_FILE.name)
        global TEST_NOTAGS_FILE
        TEST_NOTAGS_FILE = tempfile.NamedTemporaryFile(dir=TEST_FILES,suffix='.mp3')
        shutil.copy2(NOTAGS_FILE, TEST_NOTAGS_FILE.name)

        self.user = self.helper('create_user')
        aut = self.assert_create(MinusAuthor, name="Test0")
        typ = self.assert_create(FileType, type_name="audio", filetype = "mp3,wav")
        cat = self.assert_create(MinusCategory, name= "tst")
        
        self.minus = self.assert_create(MinusRecord, 
                    title = "test",
                    author = aut,
                    file = TEST_NOTAGS_FILE.name,
                    user = self.user,
                    type = typ,
        )

        album = self.assert_create(AudioAlbum,
                user = self.user,
                name = 'tstalbum',
                slug = 'tstalbum',
        )

        self.audiorec = self.assert_create(Audio,
                user = self.user,
                album = album,
                file = TEST_FILE.name
        )
        self.login(USERNAME, PASSWORD, url='auth_login', formid='id_login')

    def teardown(self):
        try:
            TEST_FILE.close()
            TEST_NOTAGS_FILE.close()
        except OSError:
            pass

    def test_audio_to_minus(self):
        self.assert_equal(MinusRecord.objects.count(), 1)
        self.assert_equal(Audio.objects.count(), 1)
        self.go200('audiorec_to_minus', [self.audiorec.id])
        self.fv('id_convert', '__confirm__', '1')
        self.submit200()
        self.assert_equal(MinusRecord.objects.count(), 2)
        self.assert_equal(Audio.objects.count(), 0)
        newmin = MinusRecord.objects.get(id = 2)
        self.assert_true('files' in newmin.file.name)
        self.url('minus_edit', [self.user.username,newmin.id ])
        self.fv('minus_upload', 'title', 'audiorecord')
        self.submit200()
        self.url('minus_detail', [newmin.author, newmin.id])


    def test_minus_to_audio(self):
        self.assert_equal(MinusRecord.objects.count(), 1)
        self.assert_equal(Audio.objects.count(), 1)
        self.go200('minus_to_audiorec', [self.minus.id])
        self.fv('id_convert', '__confirm__', '1')
        self.submit200()
        self.assert_equal(MinusRecord.objects.count(), 0)
        self.assert_equal(Audio.objects.count(), 2)
        newaudiorec = Audio.objects.get(id = 2)
        self.assert_true('uploads' in newaudiorec.file.name)
        self.url('show_object_detail',['audio',newaudiorec.user.username,newaudiorec.album.slug, newaudiorec.id])
        
        
        
