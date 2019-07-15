from django.db import models


class VideoAlbumManager(models.Manager):
    def get_query_set(self):
        return super(VideoAlbumManager, self).get_query_set().filter(videos_count__gt=0)
