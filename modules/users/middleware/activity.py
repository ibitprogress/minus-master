# -*- coding: utf-8 -*-

from django.conf import settings

from datetime import datetime
import re

from users.models import UserActivity

compiled_lists = {}


class LastActivity(object):

    def process_request(self, request):
        if not request.user.is_authenticated():
            return
        urls_module = __import__(settings.ROOT_URLCONF, {}, {}, [''])
        skip_list = getattr(urls_module, 'skip_last_activity_date', None)
        skipped_path = request.path
        if skipped_path.startswith('/'):
            skipped_path = skipped_path[1:]
        if skip_list is not None:
            for expression in skip_list:
                compiled_version = None
                if not compiled_lists.has_key(expression):
                    compiled_lists[expression] = re.compile(expression)
                compiled_version = compiled_lists[expression]
                if compiled_version.search(skipped_path):
                    return
        activity = None
        try:
            activity = request.user.useractivity
        except:
            activity = UserActivity()
            activity.user = request.user
            activity.last_activity_date = datetime.now()
            activity.last_activity_ip = request.META['REMOTE_ADDR']
            activity.save()
        activity.last_activity_date = datetime.now()
        activity.last_activity_ip = request.META['REMOTE_ADDR']
        activity.save()
