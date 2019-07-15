# -*- coding: utf-8 -*-
from blurbs.models import LegacyGeo, GeoRegion, GeoCity
from django.core.management.base import NoArgsCommand


regions = ((1, 'АР Крим'),
    (2, 'Вінницька область'),
    (3, 'Волинська область'),
    (4, 'Дніпропетровська область'),
    (5, 'Донецька область'),
    (6, 'Житомирська область'),
    (7, 'Закарпатська область'),
    (8, 'Запорізька область'),
    (9, 'Івано-Франківська область'),
    (10, 'Київська область'),
    (11, 'Кіровоградська область'),
    (12, 'Луганська область'),
    (13, 'Львівська область'),
    (14, 'Миколаївська область'),
    (15, 'Одеська область '),
    (16, 'Полтавська область'),
    (17, 'Рівненська область'),
    (18, 'Сумська область'),
    (19, 'Тернопільська область'),
    (20, 'Харківська область '),
    (21, 'Херсонська область'),
    (22, 'Хмельницька область'),
    (23, 'Черкаська область'),
    (24, 'Чернівецька область'),
    (25, 'Чернігівська область'))
    

class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        for region in regions:
            GeoRegion.objects.get_or_create(id = region[0], title = region[1])
        for city in LegacyGeo.objects.filter(type__lte = 2):
            r = GeoRegion.objects.get(id = city.area_id)
            if city.type == 1: is_city = True
            else: is_city = False
            c = GeoCity.objects.create(title = city.name, region = r, is_city = is_city)
            print c


