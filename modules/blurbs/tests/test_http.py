# -*- coding: utf-8 -*-
from tddspry.django import TestCase
from blurbs.models import BlurbCategory, Blurb , GeoCity, GeoRegion


from tddspry.django.helpers import USERNAME, PASSWORD
TEST_TITLE = "Hello, im title чи то я заголовок"
TEST_TITLE_SLUGIFY = "hello-im-title-chy-to-ya-zagolovok"
TEST_CONTENT = "contentcontent вміст"
TEST_CONTENT_SLUGIFY = "contentcontent-vmist"

class TestBlurbs(TestCase):

    def setup(self):
        self.user = self.helper('create_user')
        self.cat = self.assert_create(BlurbCategory, title = TEST_TITLE)
        self.region = self.assert_create(GeoRegion, title = "region"+TEST_TITLE)
        self.city = self.assert_create(GeoCity, title = "city"+TEST_TITLE, region = self.region)
        self.login(USERNAME, PASSWORD, url = 'auth_login', formid = 'id_login')

    def test_site_crud_blurbs(self):
        self.go200('blurb_add')
        self.fv('blurb_add', 'title', TEST_TITLE)
        self.fv('blurb_add', 'description', TEST_CONTENT)
        self.fv('blurb_add', 'buysell', 'B')
        self.fv('blurb_add','georegion', str(self.region.id)) #cities are loaded via js :(
        self.fv('blurb_add','category', str(self.cat.id))
        self.submit200()

        self.url('blurb_detail', [TEST_TITLE_SLUGIFY,'B','1'])
        self.assert_read(Blurb,
            title = TEST_TITLE,
            description = TEST_CONTENT,
            buysell = 'B',
            user = self.user)
        self.find(TEST_TITLE)
        self.find(TEST_CONTENT)

        self.go200('blurb_edit', [1])
        self.fv('blurb_add', 'title', TEST_TITLE+"1")
        self.fv('blurb_add', 'description', TEST_CONTENT+"1")
        self.fv('blurb_add', 'buysell', 'S')
        self.fv('blurb_add','geocity', str(self.city.id)) #on edit they should be preloaded
        self.submit200()
        self.assert_read(Blurb,
            title = TEST_TITLE+"1",
            description = TEST_CONTENT+"1",
            buysell = 'S',
            user = self.user)

        self.url('blurb_detail', [TEST_TITLE_SLUGIFY,'S',1])

        self.go200('blurb_delete', [1])
        self.fv('object_delete', '__confirm__', 1)
        self.submit200()
        self.url('blurbs_filter')

    def test_not_allow_empty(self):
        self.assert_equal(BlurbCategory.objects.count() , 1)
        self.go200('blurb_add')
        self.fv('blurb_add', 'title', TEST_TITLE)
        self.fv('blurb_add', 'description', TEST_CONTENT)
        self.fv('blurb_add', 'buysell', 'B')
        self.submit200()
        self.go200('blurb_add')
        self.assert_equal(Blurb.objects.count() , 0)
        self.assert_equal(BlurbCategory.objects.count() , 1)

    def test_0filtering(self):
        """
        different filtering combinations
        """
        cat2 = self.assert_create(BlurbCategory, 
            title = TEST_CONTENT)
        city2 = self.assert_create(GeoCity, 
            title = TEST_CONTENT,
            region = self.region)

        self.assert_create(Blurb,
            title = TEST_TITLE+" SELL 1",
            description = TEST_CONTENT,
            buysell = 'B',
            user = self.user,
            geocity = self.city,
            category = self.cat
            )
        
        self.assert_create(Blurb,
            title = TEST_TITLE+" SELL 2",
            description = TEST_CONTENT,
            buysell = 'S',
            user = self.user,
            geocity = self.city,
            category = self.cat
            )
        self.assert_create(Blurb,
            title = TEST_TITLE+" SELL 3",
            description = TEST_CONTENT,
            buysell = 'S',
            user = self.user,
            geocity = city2,
            category = self.cat
            )

        self.assert_create(Blurb,
            title = TEST_TITLE+" SELL 4",
            description = TEST_CONTENT,
            buysell = 'S',
            user = self.user,
            geocity = self.city,
            category = cat2
            )

        self.go200('blurbs_filter')
        self.find("SELL 1")
        self.find("SELL 2")
        self.find("SELL 3")
        self.find("SELL 4")
        self.fv('blurbs_filter', 'buysell', 'S')

        self.submit200()
        self.notfind("SELL 1")
        self.find("SELL 2")
        self.find("SELL 3")
        self.find("SELL 4")

        self.fv('blurbs_filter', 'buysell', 'B')
        self.fv('blurbs_filter', 'georegion', str(self.region.id))
        self.submit200()
        self.find("SELL 1")
        self.notfind("SELL 2")
        self.notfind("SELL 3")
        self.notfind("SELL 4")

        self.fv('blurbs_filter', 'buysell', 'A')
        self.assert_equal(GeoCity.objects.count(),2)
        self.fv('blurbs_filter', 'geocity', str(self.city.id))
        self.submit200()
        self.find("SELL 1")
        self.find("SELL 2")
        self.notfind("SELL 3")
        self.find("SELL 4")

        self.fv('blurbs_filter', 'buysell', 'B')
        self.fv('blurbs_filter', 'geocity', str(self.city.id))
        self.submit200()
        self.find("SELL 1")
        self.notfind("SELL 2")
        self.notfind("SELL 3")
        self.notfind("SELL 4")

        self.fv('blurbs_filter', 'buysell', 'S')
        self.fv('blurbs_filter', 'geocity', str(self.city.id))
        self.submit200()
        self.notfind("SELL 1")
        self.find("SELL 2")
        self.notfind("SELL 3")
        self.find("SELL 4")

        self.fv('blurbs_filter', 'buysell', 'S')
        self.fv('blurbs_filter', 'geocity', str(city2.id))
        self.submit200()
        self.notfind("SELL 1")
        self.notfind("SELL 2")
        self.find("SELL 3")
        self.notfind("SELL 4")

        self.fv('blurbs_filter', 'buysell', 'A')
        self.fv('blurbs_filter', 'geocity', '')
        self.fv('blurbs_filter', 'georegion', '')
        self.fv('blurbs_filter', 'category', self.cat.slug)
        self.submit200()
        self.find("SELL 1")
        self.find("SELL 2")
        self.find("SELL 3")
        self.notfind("SELL 4")

        self.fv('blurbs_filter', 'buysell', 'A')
        self.fv('blurbs_filter', 'category', cat2.slug)
        self.submit200()
        self.notfind("SELL 1")
        self.notfind("SELL 2")
        self.notfind("SELL 3")
        self.find("SELL 4")

        self.fv('blurbs_filter', 'buysell', 'B')
        self.fv('blurbs_filter', 'georegion', str(self.region.id))
        self.fv('blurbs_filter', 'category', self.cat.slug)
        self.submit200()
        self.find("SELL 1")
        self.notfind("SELL 2")
        self.notfind("SELL 3")
        self.notfind("SELL 4")

        self.fv('blurbs_filter', 'buysell', 'S')
        self.fv('blurbs_filter', 'georegion', str(self.region.id))
        self.fv('blurbs_filter', 'geocity', str(self.city.id))
        self.fv('blurbs_filter', 'category', self.cat.slug)
        self.submit200()
        self.notfind("SELL 1")
        self.find("SELL 2")
        self.notfind("SELL 3")
        self.notfind("SELL 4")

        self.fv('blurbs_filter', 'buysell', 'S')
        self.fv('blurbs_filter', 'georegion', str(self.region.id))
        self.fv('blurbs_filter', 'geocity', str(self.city.id))
        self.fv('blurbs_filter', 'category', self.cat.slug)
        self.fv('blurbs_filter', 'unseen', True)
        self.submit200()
        self.notfind("SELL 1")
        self.notfind("SELL 2")
        self.notfind("SELL 3")
        self.notfind("SELL 4")
 
        self.assert_create(Blurb,
            title = TEST_TITLE+" SELL 5",
            description = TEST_CONTENT,
            buysell = 'S',
            user = self.user,
            geocity = self.city,
            category = self.cat
            )
        self.fv('blurbs_filter', 'buysell', 'S')
        self.fv('blurbs_filter', 'georegion', str(self.region.id))
        self.fv('blurbs_filter', 'geocity', str(self.city.id))
        self.fv('blurbs_filter', 'category', self.cat.slug)
        self.fv('blurbs_filter', 'unseen', True)
        self.submit200()
        self.notfind("SELL 1")
        self.notfind("SELL 2")
        self.notfind("SELL 3")
        self.notfind("SELL 4")
        self.find("SELL 5")


    def test_my_blurbs(self):
        self.go200('blurbs_by_user', [self.user.username])
        self.find('немає')
        self.go200('blurb_add')
        self.fv('blurb_add', 'title', TEST_TITLE)
        self.fv('blurb_add', 'description', TEST_CONTENT)
        self.fv('blurb_add', 'buysell', 'B')
        self.fv('blurb_add','georegion', str(self.region.id)) #cities are loaded via js :(
        self.fv('blurb_add','category', str(self.cat.id))
        self.submit200()
        self.go200('blurbs_by_user', [self.user])
        self.find(TEST_TITLE)
        self.find(TEST_CONTENT)

    
    def test_add_blurb_twice(self):
        """dont allow to add two similar blurbs"""
        self.go200('blurb_add')
        self.fv('blurb_add', 'title', TEST_TITLE)
        self.fv('blurb_add', 'description', TEST_CONTENT)
        self.fv('blurb_add', 'buysell', 'B')
        self.fv('blurb_add','georegion', str(self.region.id)) #cities are loaded via js :(
        self.fv('blurb_add','category', str(self.cat.id))
        self.submit200()
        self.url('blurb_detail', [TEST_TITLE_SLUGIFY,'B','1']) 

        self.go200('blurb_add')
        self.fv('blurb_add', 'title', TEST_TITLE)
        self.fv('blurb_add', 'description', TEST_CONTENT)
        self.fv('blurb_add', 'buysell', 'B')
        self.fv('blurb_add','georegion', str(self.region.id)) #cities are loaded via js :(
        self.fv('blurb_add','category', str(self.cat.id))
        self.submit200()
        self.url('blurb_add') 
        self.find('існує')

        self.fv('blurb_add', 'title', TEST_TITLE)
        self.fv('blurb_add', 'description', 'hello man')
        self.fv('blurb_add', 'buysell', 'B')
        self.fv('blurb_add','georegion', str(self.region.id)) #cities are loaded via js :(
        self.fv('blurb_add','category', str(self.cat.id))
        self.submit200()

        self.url('blurb_detail', [TEST_TITLE_SLUGIFY,'B','2']) 
