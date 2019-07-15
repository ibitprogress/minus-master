from django.contrib.auth.models import User


def moderator(request):
    """
    Returns a boolean respectively to user rang
    """
    try:
        user = User.objects.get(pk=request.user.pk)
        if user.is_staff:
            return {'moderator': True}
    except:
        pass
    return {'moderator': False}
