#-*- coding: utf-8 -*-
import re
import os.path
import tempfile
import shutil
from datetime import datetime


from django.contrib.sites.models import Site
from django.core import mail
from django.conf import settings
from django.contrib.auth.models import User
from minusstore.models import MinusRecord, FileType, MinusAuthor
from django.contrib.sites.models import Site

from tddspry.django import TestCase


TEST_NAME = 'Sometestname'
TEST_NAME_NEW = 'Sometestnamenew'
TEST_SURNAME = 'Sometestsurname'
TEST_CITY = 'Sometestcity'
TEST_COUNTRY = 'Sometestcountry'
TEST_FILES = os.path.join(settings.MEDIA_ROOT,'testfiles')
TEST_AUDIO_FILE = os.path.join(TEST_FILES,'04 - jingle bells.mp3')
TEST_AVATAR_JPG = os.path.join(TEST_FILES, 'avatar.jpg')
TEST_AVATAR_PNG = os.path.join(TEST_FILES, 'avatar.png')
TEST_AVATAR_GIF = os.path.join(TEST_FILES, 'avatar.gif')
TEST_AVATAR_WRONG = os.path.join(TEST_FILES, 'dummy.txt')
TEST_AVATAR_CYRILLIC = os.path.join(TEST_FILES, 'аватар.jpg')
TEST_AVATAR_SPACES = os.path.join(TEST_FILES, 'a б c.gif')
TEST_AVATAR_TOOBIG = os.path.join(TEST_FILES, 'avatar_big.png')
TEST_AVATAR_RENAMED = os.path.join(TEST_FILES, 'avatar_renamed.jpg')
TEST_BIRTHDATE = str(datetime.now)
TEST_BIRTHDATE_DAY = '15'
TEST_BIRTHDATE_MONTH = '3'
TEST_BIRTHDATE_YEAR = '1980'
TEST_HIDE_BIRTHDATE = True
TEST_ICQ = '111111111'
TEST_JABBER = 'sometestuid@jabber.org'
TEST_SKYPE = 'sometestskypename'
TEST_WEBSITE = 'sometestsite.com'
TEST_PASSW = "SuperSecur3Passw0rd"
TEST_PASSW_NEW = "SupernewSecur3Passw0rd"
TEST_MAIL = "qtest689@gmail.com"
TEST_MAIL_NEW = "qtest689new@gmail.com"

class TestRegistration(TestCase):
    fixtures = ['fixtures/test_data.json']

    def test_registration(self):
        """
        Trivial user registration case
        """
        self.assert_equal(User.objects.count(), 0)
        self.go200('registration_register')
        self.find('<input id="id_username" type="text" class="required" ' \
             'name="username"')
        self.fv('id_registration',"id_username", TEST_NAME)
        self.fv('id_registration',"id_email", TEST_MAIL)
        self.fv('id_registration', "id_password1", TEST_PASSW)
        self.fv('id_registration', "id_password2", TEST_PASSW)
        self.submit200()
        self.find("Дякуємо")

        self.assert_equal(len(mail.outbox), 1)
        self.assert_equal(User.objects.count(), 1)
        body = mail.outbox[0].body
        match = re.search('.*%s/(.*)' % "activate", body)

        assert match, \
          'Failed to find proper activation link in the mail: %s' % body

        code = match.groups()[0]
        self.go200("registration_activate", args=[code])
        self.go200('registration_complete')
        self.find('завершено')
        user = User.objects.get(username=TEST_NAME)
        self.assert_true(user.is_active, 'User is not activated yet.')

    def test_registration_duplicate_email(self):
        """
        Case when user is trying to register an account with email
        which is already exist in data base
        """
        user = self.helper('create_user', 'username', 'password',
                           email=TEST_MAIL)
        self.go200('registration_register')
        self.find('<input id="id_username" type="text" class="required" ' \
             'name="username"')
        self.fv('id_registration',"id_username", TEST_NAME)
        self.fv('id_registration',"id_email", TEST_MAIL)
        self.fv('id_registration', "id_password1", TEST_PASSW)
        self.fv('id_registration', "id_password2", TEST_PASSW)
        self.submit200()
        self.find("Даний E-Mail вже існує в базі даних.")

    def test_registration_duplicate_username(self):
        """
        Case when user is trying to register an account with username
        which is already exist in data base
        """
        user = self.helper('create_user', 'username', 'password',
                           'email')
        self.go200('registration_register')
        self.find('<input id="id_username" type="text" class="required" ' \
             'name="username"')
        self.fv('id_registration',"id_username", user.username)
        self.fv('id_registration',"id_email", TEST_MAIL)
        self.fv('id_registration', "id_password1", TEST_PASSW)
        self.fv('id_registration', "id_password2", TEST_PASSW)
        self.submit200()
        self.find("A user with that username already exists.")

    def test_registration_different_passwords(self):
        """
        Case when user typed 2 different passwords
        """
        self.go200('registration_register')
        self.find('<input id="id_username" type="text" class="required" ' \
             'name="username"')
        self.fv('id_registration',"id_username", TEST_NAME)
        self.fv('id_registration',"id_email", TEST_MAIL)
        self.fv('id_registration', "id_password1", TEST_PASSW)
        self.fv('id_registration', "id_password2", TEST_PASSW_NEW)
        self.submit200()
        self.find("The two password fields didn")


class TestAuthUser(TestCase):
    """
    Determines test cases for user authentication
    """
    fixtures = ['fixtures/test_data.json']

    def test_login_on_index(self):
        """
        Trying to login via all-pages form
        """
        self.go200('minus')
        self.find('Вхід')
        user = self.helper('create_user', 'username', 'password',
                           email=TEST_MAIL)
        self.fv('login_form', 'id_username', 'username')
        self.fv('login_form', 'id_password', 'password')
        self.submit200()
        self.url('minus/')
        self.notfind('Вхід')
        self.find('username')


    def test_loginpage(self):
        """
        Checking login template and view
        """
        self.go200('auth_login')
        self.find('Вхід')
        user = self.helper('create_user', 'username', 'password',
                           email=TEST_MAIL)
        self.login(TEST_MAIL, 'password', url='auth_login', formid='id_login')
        self.url(settings.LOGIN_REDIRECT_URL)

    def test_logoutpage(self):
        """
        Checking logout template and view
        """
        self.go200('auth_logout')
        self.find('Вихід')
        user = self.helper('create_user', 'username', 'password',
                           email=TEST_MAIL)
        self.login(TEST_MAIL, 'password', url='auth_login', formid='id_login')
        self.logout('auth_logout')
        #self.url('/')

    def test_wrong_password(self):
        """
        Checking case when given password is wrong
        """
        user = self.helper('create_user', 'username', 'password',
                           email=TEST_MAIL)
        self.login(TEST_MAIL, 'wrongpassword', url='auth_login', formid='id_login')
        self.find('спробуйте ще раз')

    def test_loginpage_with_username(self):
        """
        Checking login using username
        """
        self.go200('auth_login')
        self.find('Вхід')
        user = self.helper('create_user', 'username', 'password')
        self.login('username', 'password', url='auth_login', formid='id_login')
        self.url(settings.LOGIN_REDIRECT_URL)

    def test_logoutpage_with_username(self):
        """
        Cheking logout template and view using username
        """
        self.go200('auth_logout')
        self.find('Вихід')
        user = self.helper('create_user', 'username', 'password')
        self.login('username', 'password', url='auth_login', formid='id_login')
        self.logout('auth_logout')
        #self.url('/') done by js

    def test_wrong_password_with_username(self):
        """
        Checking case when given password is wrong using username
        """
        user = self.helper('create_user', 'username', 'password')
        self.login('username', 'wrongpassword', url='auth_login', formid='id_login')
        self.find('спробуйте ще раз')

    def test_authorized_login(self):
        """
        Redirect authorized user from /login/ to /
        """
        user = self.helper('create_user', 'username', 'password')
        self.login('username', 'password', url='auth_login', formid='id_login')
        self.go200('auth_login')
        self.url(settings.LOGIN_REDIRECT_URL)

    def test_authorized_register(self):
        """
        Redirect authorized user from /register/ to /
        """
        user = self.helper('create_user', 'username', 'password')
        self.login('username', 'password', url='auth_login', formid='id_login')
        self.go200('registration_register')
        self.url(settings.LOGIN_REDIRECT_URL)

    def test_login_banned(self):
        user = self.helper('create_user', 'username', 'password', email = TEST_MAIL)
        self.go200('auth_logout')
        user.get_profile().banned = True
        user.get_profile().save()

        self.go200('minus')
        self.find('Вхід')
        self.fv('login_form', 'id_username', 'username')
        self.fv('login_form', 'id_password', 'password')
        self.submit200()
        self.url('quick_login')
        self.find('Вхід')

    def test_ban(self):
        self.assert_equal(len(mail.outbox),0)
        user = self.helper('create_user', 'username', 'password', email = TEST_MAIL)
        moder = self.helper('create_user', 'moder', 'moder', email = 'moder@example.com')
        self.login('moder', 'moder',  url='auth_login', formid='id_login')
        self.go('ban_user', [user.id])
        self.code(404)
        moder.is_staff = True
        moder.save()
        self.go200('ban_user', [user.id])
        #self.go200('user_profile', [user.username])
        self.fv('ban_form', 'id_banned_until', '2020-04-01')
        self.fv('ban_form', 'id_message', 'for fun')
        self.submit200()
        self.url(user.get_profile().get_absolute_url())
        
        user = User.objects.get(id = user.id) #refresh
        self.assert_equal(len(mail.outbox),1)
        self.assert_true('for fun' in mail.outbox[0].message().as_string())
        self.assert_equal(user.get_profile().banned, True)
        

        self.logout('auth_logout')

        self.go200('minus')
        self.find('Вхід')
        self.fv('login_form', 'id_username', 'username')
        self.fv('login_form', 'id_password', 'password')
        self.submit200()
        self.url('quick_login')
        self.find('Вхід')

        user.get_profile().banned_until = datetime.now().date()
        user.get_profile().save()

        self.go200('minus')
        self.find('Вхід')
        self.fv('login_form', 'id_username', 'username')
        self.fv('login_form', 'id_password', 'password')
        self.submit200()
        self.url('minus/')
        self.notfind('Вхід')
        

class TestUserProfile(TestCase):
    
    fixtures = ['fixtures/test_data.json']

    def test_userlist(self):
        self.go200('user_list')

    def test_userprofile(self):
        """
        Looking up for some profiles
        """
        user1 = self.helper('create_user', 'username1', 'password')
        user2 = self.helper('create_user', 'username2', 'password')
        self.go200('user_profile', [user1.username])
        self.go200('user_profile', [user2.username])

    def test_userprofile_anonymous(self):
        """
        Looking up a profile with anonymous
        """
        user = self.helper('create_user', 'username', 'password',
                           'email')
        self.login('email', 'password', url='auth_login', formid='id_login')
        self.logout('auth_logout')
        self.go200('user_profile', [user.username])
        self.find(user.username)


    def test_userprofile_edit(self):
        """
        User profile edit form
        """
        user = self.helper('create_user', 'username', 'password',
                           'email')
        self.login('email', 'password', url='auth_login', formid='id_login')
        self.go200('user_editprofile', [user.username])

    def test_userprofile_edit_another(self):
        """
        User's trying to edit another's profile
        """
        user1 = self.helper('create_user', 'username1', 'password')
        user2 = self.helper('create_user', 'username2', 'password')
        self.login('username1', 'password', url='auth_login', formid='id_login')
        self.url(settings.LOGIN_REDIRECT_URL)
        self.go('user_editprofile', [user2.username])
        self.code('404')

    def test_userprofile_submit(self):
        """
        User profile form submit
        """
        user = self.helper('create_user', 'username', 'password')
        self.login('username', 'password', url='auth_login', formid='id_login')
        self.url(settings.LOGIN_REDIRECT_URL)
        self.go200('user_editprofile', [user.username])
        self.showforms()
        self.formclear('id_userprofile')
        self.fv('id_userprofile', 'id_name', TEST_NAME)
        self.fv('id_userprofile', 'id_surname', TEST_SURNAME)
        self.fv('id_userprofile', 'id_city', TEST_CITY)
        self.fv('id_userprofile', 'id_country', TEST_COUNTRY)
        self.fv('id_userprofile', 'id_birthdate_month', TEST_BIRTHDATE_MONTH)
        self.fv('id_userprofile', 'id_birthdate_day', TEST_BIRTHDATE_DAY)
        self.fv('id_userprofile', 'id_birthdate_year', TEST_BIRTHDATE_YEAR)
        self.fv('id_userprofile', 'id_icq', TEST_ICQ)
        self.fv('id_userprofile', 'id_jabber', TEST_JABBER)
        self.fv('id_userprofile', 'id_skype', TEST_SKYPE)
        self.fv('id_userprofile', 'id_website', TEST_WEBSITE)
        self.submit200()
        self.url('user_profile', [user.username])

    def test_userprofile_submit_hidebirthdate(self):
        """
        User profile form submit with hide birthdate
        """
        user = self.helper('create_user', 'username', 'password')
        self.login('username', 'password', url='auth_login', formid='id_login')
        self.url(settings.LOGIN_REDIRECT_URL)
        self.go200('user_editprofile', [user.username])
        self.showforms()
        self.formclear('id_userprofile')
        self.fv('id_userprofile', 'id_name', TEST_NAME)
        self.fv('id_userprofile', 'id_surname', TEST_SURNAME)
        self.fv('id_userprofile', 'id_city', TEST_CITY)
        self.fv('id_userprofile', 'id_country', TEST_COUNTRY)
        self.fv('id_userprofile', 'id_birthdate_month', TEST_BIRTHDATE_MONTH)
        self.fv('id_userprofile', 'id_birthdate_day', TEST_BIRTHDATE_DAY)
        self.fv('id_userprofile', 'id_birthdate_year', TEST_BIRTHDATE_YEAR)
        self.fv('id_userprofile', 'id_hide_birthdate', TEST_HIDE_BIRTHDATE)
        self.fv('id_userprofile', 'id_icq', TEST_ICQ)
        self.fv('id_userprofile', 'id_jabber', TEST_JABBER)
        self.fv('id_userprofile', 'id_skype', TEST_SKYPE)
        self.fv('id_userprofile', 'id_website', TEST_WEBSITE)
        self.submit200()
        self.url('user_profile', [user.username])
        self.notfind('Дата народження:')

    def test_userprofile_edit_anonymous(self):
        """
        Anonymous is trying to edit user profile
        """
        user = self.helper('create_user', 'username', 'password',
                           'email')
        self.login('email', 'password', url='auth_login', formid='id_login')
        self.logout('auth_logout')
        self.go200('users/' + user.username + '/edit')
        self.url(self.build_url('auth_login') + '\?next=/users/' + user.username + '/edit/')

    def test_users_online_none(self):
        """
        There's no any user online
        """
        self.go200('/')
        self.find('Немає жодного')

    def test_users_online(self):
        """
        There's one user at least
        """
        user = self.helper('create_user', 'username', 'password',
                          'email')
        self.login('username', 'password', url='auth_login', formid='id_login')
        self.url(settings.LOGIN_REDIRECT_URL)
        self.find('<a class="dynamic user " title="'+user.username+'" href="' + user.get_absolute_url()\
                  + '">' + user.username)
        


class TestAvatarUpload(TestCase):
    """
    Tests for different cases with avatar upload
    """
    fixtures = ['fixtures/test_data.json']

    def test_avatar_upload(self):
        """
        Trivial avatar uploading case
        """
        user = self.helper('create_user', 'username', 'password')
        self.login('username', 'password', url='auth_login', formid='id_login')
        self.url(settings.LOGIN_REDIRECT_URL)
        self.go200('user_editprofile', [user.username])
        self.find('Аватар')
        self.showforms()
        self.formclear('id_userprofile')
        self.formfile('id_userprofile', 'avatar', TEST_AVATAR_JPG)
        self.submit200()
        self.url('user_profile', [user.username])
        self.find(user.username)

    def test_avatar_upload_cyrillic(self):
        """
        Trivial avatar with cyrillic uploading case
        """
        user = self.helper('create_user', 'username', 'password')
        self.login('username', 'password', url='auth_login', formid='id_login')
        self.url(settings.LOGIN_REDIRECT_URL)
        self.go200('user_editprofile', [user.username])
        self.find('Аватар')
        self.showforms()
        self.formclear('id_userprofile')
        self.formfile('id_userprofile', 'avatar', TEST_AVATAR_CYRILLIC)
        self.submit200()
        self.url('user_profile', [user.username])
        self.find(user.username)

    def test_avatar_upload_spaces(self):
        """
        Trivial avatar with spaces in name uploading case
        """
        user = self.helper('create_user', 'username', 'password')
        self.login('username', 'password', url='auth_login', formid='id_login')
        self.url(settings.LOGIN_REDIRECT_URL)
        self.go200('user_editprofile', [user.username])
        self.find('Аватар')
        self.showforms()
        self.formclear('id_userprofile')
        self.formfile('id_userprofile', 'avatar', TEST_AVATAR_SPACES)
        self.submit200()
        self.url('user_profile', [user.username])
        self.find(user.username)

    def test_avatar_upload_gif(self):
        """
        Trivial avatar in gif format uploading case
        """
        user = self.helper('create_user', 'username', 'password')
        self.login('username', 'password', url='auth_login', formid='id_login')
        self.url(settings.LOGIN_REDIRECT_URL)
        self.go200('user_editprofile', [user.username])
        self.find('Аватар')
        self.showforms()
        self.formclear('id_userprofile')
        self.formfile('id_userprofile', 'avatar', TEST_AVATAR_GIF)
        self.submit200()
        self.url('user_profile', [user.username])
        self.find(user.username)

    def test_avatar_upload_png(self):
        """
        Trivial avatar in png format uploading case
        """
        user = self.helper('create_user', 'username', 'password')
        self.login('username', 'password', url='auth_login', formid='id_login')
        self.url(settings.LOGIN_REDIRECT_URL)
        self.go200('user_editprofile', [user.username])
        self.find('Аватар')
        self.showforms()
        self.formclear('id_userprofile')
        self.formfile('id_userprofile', 'avatar', TEST_AVATAR_PNG)
        self.submit200()
        self.url('user_profile', [user.username])
        self.find(user.username)

    def test_avatar_upload_big(self):
        """
        Test validation for too big image file
        """
        user = self.helper('create_user', 'username', 'password')
        self.login('username', 'password', url='auth_login', formid='id_login')
        self.url(settings.LOGIN_REDIRECT_URL)
        self.go200('user_editprofile', [user.username])
        self.find('Аватар')
        self.showforms()
        self.formclear('id_userprofile')
        self.formfile('id_userprofile', 'avatar', TEST_AVATAR_TOOBIG)
        self.submit200()
        self.find('Розмір файлу не повинен')

    def test_avatar_upload_wrong(self):
        """
        Wrong file uploading case
        """
        user = self.helper('create_user', 'username', 'password')
        self.login('username', 'password', url='auth_login', formid='id_login')
        self.url(settings.LOGIN_REDIRECT_URL)
        self.go200('user_editprofile', [user.username])
        self.find('Аватар')
        self.showforms()
        self.formclear('id_userprofile')
        self.formfile('id_userprofile', 'avatar', TEST_AVATAR_WRONG)
        self.submit200()
        self.find('Upload a valid image.')

    def test_avatar_upload_renamed(self):
        """
        Wrong file renamed to image uploading case
        """
        user = self.helper('create_user', 'username', 'password')
        self.login('username', 'password', url='auth_login', formid='id_login')
        self.url(settings.LOGIN_REDIRECT_URL)
        self.go200('user_editprofile', [user.username])
        self.find('Аватар')
        self.showforms()
        self.formclear('id_userprofile')
        self.formfile('id_userprofile', 'avatar', TEST_AVATAR_RENAMED)
        self.submit200()
        self.find('Upload a valid image.')


class TestRecordsList(TestCase):
    """
    Tests for list of created records by user
    in his/her profile.
    """
    fixtures = ['fixtures/test_data.json']

    def test_no_records(self):
        """
        Case when user has no records
        """
        user = self.helper('create_user', 'username', 'password')
        self.login('username', 'password', url='auth_login', formid='id_login')
        self.url(settings.LOGIN_REDIRECT_URL)
        self.assert_equal(MinusRecord.objects.count(),0)
        self.go200('user_profile', [user.username])
        self.notfind('Залиті мінусовки')

    def test_records_exist(self):
        """
        Case when at least 1 record exist
        """
        self.superuser = self.helper('create_superuser', 'superusername', 'password')
        self.login_to_admin('superusername', 'password')
        self.assert_create(FileType, type_name="audio", filetype = "mp3,mid")
        self.logout('auth_logout')
        user = self.helper('create_user', 'username', 'password')
        self.login('username', 'password', url='auth_login', formid='id_login')
        self.url(settings.LOGIN_REDIRECT_URL)
        self.go200('minus_upload')
        self.find('Завантажити мінусовку')
        self.find('Файл')
        self.formfile('minus_upload', 'file', TEST_AUDIO_FILE)
        self.submit200()
        self.assert_not_equal(user.uploaded_records.count(),0)
        self.go200('user_profile', [user.username])
        self.find('Останні залиті мінусовки')
