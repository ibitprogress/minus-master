import time

from django.core.management.base import NoArgsCommand
from django.contrib.auth.models import User
from users.models import UserProfile, UserRating, create_rating


class Command(NoArgsCommand):
    """recount ratings for all active users
    (quite performance-expensive)"""
        
    def handle_noargs(self, **options):
        users = User.objects.all()
        for u in users:
            create_rating(User, instance = u)
            print "Counted rating for %s" % u


