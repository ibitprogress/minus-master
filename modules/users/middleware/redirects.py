from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.conf import settings


class AuthorizedRedirects(object):
    """
    Checks whether a user is authenticated and redirects
    from non usable views for authenticated user
    """
    
    def process_request(self, request):
        if request.user.is_authenticated():
            try:
                if request.path in settings.AUTH_USER_DISALLOWED_URLS:
                    return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
            except:
                pass
        pass
