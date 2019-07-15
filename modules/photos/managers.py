from django.db import models


class AlbumManager(models.Manager):
    def get_query_set(self):
        return super(AlbumManager, self).get_query_set().filter(size__gt=0)
