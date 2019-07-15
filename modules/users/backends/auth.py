from django.conf import settings
from django.contrib.auth.models import User
import datetime
from django.contrib.auth.backends import ModelBackend


class EmailOrUsernameModelBackend(ModelBackend):
    """
    Implements an authorization with email instead of login
    """

    def authenticate(self, username=None, password=None):
        if '@' in username:
            kwargs = {'email': username}
        else:
            kwargs = {'username': username}
        try:
            user = User.objects.get(**kwargs)
            if user.check_password(password):
                if user.get_profile().banned:
                    profile = user.get_profile()
                    if datetime.date.today() < profile.banned_until:
                        return None
                    else:
                        profile.banned = False
                        profile.save()
                        return user
                else:
                    return user
        except User.DoesNotExist:
            return None

