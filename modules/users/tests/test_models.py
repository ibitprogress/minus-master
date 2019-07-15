# -*- coding: utf-8 -*-

from math import sqrt
import datetime
import os.path
import tempfile
import shutil
from mock import Mock

from django.test import TestCase
from django.conf import settings
from tddspry.django import DatabaseTestCase
from django.contrib.auth.models import User


from users.models import UserProfile, UserRating, StaffTicket
from voting.models import Vote

from registration.models import RegistrationProfile
from photos.models import PhotoAlbum

TEST_ACTIVATION_KEY = 'ab' * 20
TEST_USERNAME = 'testuser'
TEST_USERNAME_NEW = 'testusernew'
TEST_PASSWORD = 'qwerty'
TEST_PASSWORD_NEW = 'qwertynew'
TEST_EMAIL = 'test@mail.com'
TEST_EMAIL_NEW = 'testnew@mail.com'
TEST_CITY = 'Sometestcity'
TEST_COUNTRY = 'Sometestcountry'
TEST_FILES = os.path.join(settings.MEDIA_ROOT,'testfiles')
TEST_AVATAR_JPG = os.path.join(TEST_FILES, 'avatar.jpg')
TEST_AVATAR_PNG = os.path.join(TEST_FILES, 'avatar.png')
TEST_AVATAR_GIF = os.path.join(TEST_FILES, 'avatar.gif')
TEST_AVATAR_WRONG = os.path.join(TEST_FILES, 'dummy.txt')
TEST_AVATAR_CYRILLIC = os.path.join(TEST_FILES, 'аватар.jpg')
TEST_AVATAR_SPACES = os.path.join(TEST_FILES, 'a б c.gif')
TEST_AVATAR_TOOBIG = os.path.join(TEST_FILES, 'avatar_big.png')
TEST_AVATAR_RENAMED = os.path.join(TEST_FILES, 'avatar_renamed.jpg')
TEST_BIRTHDATE = datetime.date.today()
TEST_HIDE_BIRTHDATE = True
TEST_ICQ = '111111111'
TEST_JABBER = 'sometestuid@jabber.org'
TEST_SKYPE = 'sometestskypename'
TEST_WEBSITE = 'sometestsite.com'


class TestRegistrationProfile(DatabaseTestCase):

    def test_create(self):
        self.assert_create(RegistrationProfile,
                           user=self.helper('create_user'),
                           activation_key=TEST_ACTIVATION_KEY)

    def test_read(self):
        user = self.helper('create_user')
        self.assert_create(RegistrationProfile,
                           user=user,
                           activation_key=TEST_ACTIVATION_KEY)
        self.assert_read(RegistrationProfile,
                         user=user,
                           activation_key=TEST_ACTIVATION_KEY)

    def test_delete(self):
        regprofile = self.assert_create(RegistrationProfile,
                                        user=self.helper('create_user'),
                                        activation_key=TEST_ACTIVATION_KEY)
        self.assert_delete(regprofile)


class TestUserProfile(DatabaseTestCase):

    def test_create(self):
        """
        Checking whether UserProfile is creating automatically
        with User creation.
        """
        self.assert_create(User, username=TEST_USERNAME,
                          password=TEST_PASSWORD, email=TEST_EMAIL)
        user = User.objects.get(id=1)
        self.assert_read(UserProfile, user=user)


    def test_read(self):
        """
        Checking whether UserProfile and User models are
        accessible after creation
        """
        self.assert_create(User, username=TEST_USERNAME,
                          password=TEST_PASSWORD, email=TEST_EMAIL)
        user = User.objects.get(id=1)
        self.assert_read(User, username=user.username)
        self.assert_read(UserProfile, user=user)

    def test_delete(self):
        """
        Checking deleting User and UserProfile models
        """
        user_model = self.assert_create(User, username=TEST_USERNAME,
                          password=TEST_PASSWORD, email=TEST_EMAIL)
        user = User.objects.get(id=1)
        userprofile_model = self.assert_read(UserProfile,
                                             user=user)
        self.assert_equal(UserProfile.objects.count(), 1)
        self.assert_delete(user_model)
        # Profile should be deleted automatically
        self.assert_equal(UserProfile.objects.count(), 0)

    def test_update(self):
        """
        Checking update of models
        """
        user = self.assert_create(User, username=TEST_USERNAME,
                          password=TEST_PASSWORD, email=TEST_EMAIL)
        userprofile_model = self.assert_read(UserProfile,
                                             user=user)
        self.assert_update(userprofile_model, user=user,
                          country=TEST_COUNTRY, birthdate=TEST_BIRTHDATE,
                          icq=TEST_ICQ, jabber=TEST_JABBER, skype=TEST_SKYPE,
                          website=TEST_WEBSITE )

    def test_update_hide_birthdate(self):
        """
        Checking update of models with checking out hide birthdate
        """
        user = self.assert_create(User, username=TEST_USERNAME,
                          password=TEST_PASSWORD, email=TEST_EMAIL)
        userprofile_model = self.assert_read(UserProfile,
                                             user=user)
        self.assert_update(userprofile_model, user=user,
                           country=TEST_COUNTRY, birthdate=TEST_BIRTHDATE,
                           hide_birthdate=TEST_HIDE_BIRTHDATE, icq=TEST_ICQ,
                           jabber=TEST_JABBER, skype=TEST_SKYPE,
                           website=TEST_WEBSITE)

    def test_state(self):
        user = self.assert_create(User, username=TEST_USERNAME,
                          password=TEST_PASSWORD, email=TEST_EMAIL)
        userprofile_model = self.assert_read(UserProfile,
                                             user=user)
        self.assert_false(userprofile_model.is_versed())
        user.date_joined = datetime.datetime(2010,1,1)
        user.save()
        userprofile_model = self.assert_read(UserProfile,
                                             user=user)
        self.assert_true(userprofile_model.is_versed())
        



class TestAvatarStore(DatabaseTestCase):
    """
    Test cases with storing avatar file in database
    """

    def setup(self):
        super(TestAvatarStore, self).setup()
        global TEST_AVATAR
        TEST_AVATAR = tempfile.NamedTemporaryFile(dir=TEST_FILES,
                                                suffix='.jpg')
        shutil.copy2(TEST_AVATAR_JPG, TEST_AVATAR.name)

    def teardown(self):
        try:
            TEST_AVATAR.close()
        except OSError:
            pass

    def test_userprofile_avatar_read(self):
        """
        Reading user profile model with avatar
        """
        self.assert_create(User, username=TEST_USERNAME,
                          password=TEST_PASSWORD, email=TEST_EMAIL)
        user = User.objects.get(id=1)
        userprofile_model = self.assert_read(UserProfile, user=user)
        self.assert_update(userprofile_model, user=user,
                           country=TEST_COUNTRY, avatar=TEST_AVATAR.name,
                           birthdate=TEST_BIRTHDATE, hide_birthdate=TEST_HIDE_BIRTHDATE,
                           icq=TEST_ICQ, jabber=TEST_JABBER, skype=TEST_SKYPE,
                           website=TEST_WEBSITE)
        self.assert_read(UserProfile, user=user,
                         country=TEST_COUNTRY, avatar=TEST_AVATAR.name,
                         birthdate=TEST_BIRTHDATE, icq=TEST_ICQ,
                         jabber=TEST_JABBER, skype=TEST_SKYPE,
                         website=TEST_WEBSITE)

    def test_userprofile_avatar_update(self):
        """
        Updating user profile model with avatar
        """
        self.assert_create(User, username=TEST_USERNAME,
                          password=TEST_PASSWORD, email=TEST_EMAIL)
        user = User.objects.get(id=1)
        userprofile_model = self.assert_read(UserProfile, user=user)
        self.assert_update(userprofile_model, user=user,
                           city=TEST_CITY,
                           country=TEST_COUNTRY, avatar=TEST_AVATAR.name,
                           birthdate=TEST_BIRTHDATE, hide_birthdate=TEST_HIDE_BIRTHDATE,
                           icq=TEST_ICQ, jabber=TEST_JABBER, skype=TEST_SKYPE,
                           website=TEST_WEBSITE)

    def test_userprofile_avatar_delete(self):
        """
        Deleting user profile model with avatar
        """
        self.assert_create(User, username=TEST_USERNAME,
                          password=TEST_PASSWORD, email=TEST_EMAIL)
        user = User.objects.get(id=1)
        userprofile_model = self.assert_read(UserProfile, user=user)
        self.assert_update(userprofile_model, user=user,
                            city=TEST_CITY,
                           country=TEST_COUNTRY, avatar=TEST_AVATAR.name,
                           birthdate=TEST_BIRTHDATE, hide_birthdate=TEST_HIDE_BIRTHDATE,
                           icq=TEST_ICQ, jabber=TEST_JABBER, skype=TEST_SKYPE,
                           website=TEST_WEBSITE)
        self.assert_delete(userprofile_model)

class FakeList(list):
    """List that sometimes behaves as queryset"""
    def __init__(self, *arg):
        super(FakeList, self).__init__(*arg)
        self.count = Mock()
        self.count.return_value = len(self)

    def aggregate(self,*args):
        sum = 0
        for obj in self:
            sum += obj.rating.score
        return {'rating_score__sum':sum}


class TestUserRatings(DatabaseTestCase):
    """docstring for TestUserRatings"""
    def setup(self):
        super(TestUserRatings, self).setup()
        self.user = self.assert_create(User, username=TEST_USERNAME,
                          password=TEST_PASSWORD, email=TEST_EMAIL)
        self.mn = Mock()
        self.mn.rating.score = 15
        import users
        import minusstore
        from minusstore.models import MinusRecord
        self.oldvode = users.models.Vote
        self.oldminus = MinusRecord
        users.models.Vote = Mock()
        users.models.Vote.objects.get_score = Mock()
        users.models.Vote.objects.get_score.return_value = {'score':10}
        users.models.MinusRecord = Mock()
        users.models.MinusRecord.mocked = True
        users.models.MinusRecord.objects.filter = Mock()
        users.models.MinusRecord.objects.filter.return_value = FakeList([self.mn, self.mn])

    def teardown(self):
        import users
        import minusstore
        from minusstore.models import MinusRecord
        users.models.Vote = self.oldvode 
        MinusRecord = self.oldminus 
        MinusRecord.objects.filter = self.oldminus.objects.filter
        reload(users)
        reload(minusstore)

    def test_created(self):
        self.assert_equal(UserRating.objects.count(), 1)
        
    def test_read(self):
        self.assert_read(UserRating, user = self.user)

    def test_counts(self):
        import users
        r = UserRating.objects.get(user = self.user)
        r.count_rating()
        self.assert_equal(r.average_minus_rating, 15) #two recs with rating of 15

        #vote(10) +  average rating(15) + count of uploaded recs (2)
        self.assert_equal(r.rating, int(10*(sqrt(15+15)+10)))
        self.mn.rating.score = 1
        r.count_rating()
        self.assert_equal(r.rating, int(10*(sqrt(1+1)+10))) 
        users.models.MinusRecord.objects.filter.return_value = FakeList([self.mn, self.mn]*10)
        r.count_rating()
        self.assert_equal(r.rating, int(10*(sqrt(20)+10)))

        

class TestStaffTickets(DatabaseTestCase):
    def setup(self):
        self.user = self.assert_create(User, username=TEST_USERNAME,
                          password=TEST_PASSWORD, email=TEST_EMAIL)
    def test_create(self):
        """mostly we are interested only in creation of tickets"""
        self.assert_create(StaffTicket, user = self.user, content_object = self.user,
            message = "MASSAGE")

    def test_notify_staff_on_names_match(self):
        user2 = self.assert_create(User, username=TEST_USERNAME+"2",
                          password=TEST_PASSWORD, email=TEST_EMAIL)
        self.user.first_name = "Andrew"
        self.user.last_name = "Meakovski"
        self.user.save()
        self.assert_equal(StaffTicket.objects.count(), 0)
        user2.first_name = "Andrew"
        user2.last_name = "Meakovski"
        user2.save()
        # notification about same names
        self.assert_equal(StaffTicket.objects.count(), 1)
        
