"""
This file was generated with the customdashboard management command, it
contains the two classes for the main dashboard and app index dashboard.
You can customize these classes as you want.

To activate your index dashboard add the following to your settings.py::
    ADMIN_TOOLS_INDEX_DASHBOARD = 'minus.dashboard.CustomIndexDashboard'

And to activate the app index dashboard::
    ADMIN_TOOLS_APP_INDEX_DASHBOARD = 'minus.dashboard.CustomAppIndexDashboard'
"""
from collections import Counter #python 2.7 only!

from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from admin_tools.dashboard import modules, Dashboard, AppIndexDashboard
from admin_tools.utils import get_admin_site_name
from django.contrib.admin.models import LogEntry
from django.db.models import exceptions


class RecentModelsList(modules.ModelList):
    def init_with_context(self,context):
        log = LogEntry.objects.filter(user = context['request'].user)[:100]
        objects = []
        for e in log:
            try:
                m = e.get_edited_object()
                #can be done more clean way
                objects.append(m.__class__.__module__+'.'+m.__class__.__name__) 
            except exceptions.ObjectDoesNotExist:
                pass
        #order items by frequency.
        self.models = [e[0] for e in Counter(objects).most_common(10)]
        super(RecentModelsList, self).init_with_context(context)


class CustomIndexDashboard(Dashboard):
    """
    Custom index dashboard for minus.
    """
    def init_with_context(self, context):
        site_name = get_admin_site_name(context)
        # append a link list module for "quick links"
        # Recentl models
        

        self.children.append(RecentModelsList(_("Most used")))
          
        # append an app list module for "Applications"
        self.children.append(modules.AppList(
            _('Applications'),
            exclude=('django.contrib.*',),
        ))

        # append an app list module for "Administration"
        self.children.append(modules.AppList(
            _('Administration'),
            models=('django.contrib.*',),
        ))

        self.children.append(modules.LinkList(
            _('Quick links'),
            layout='inline',
            draggable=True,
            deletable=True,
            collapsible=True,
            children=[
                [_('Return to site'), '/'],
                [_('Moderator information'), '/moderator/'],
                [_('Radio'), 'http://minus.lviv.ua:8001/admin/listmounts.xsl'],
                [_('Change password'),
                 reverse('%s:password_change' % site_name)],
                [_('Log out'), reverse('%s:logout' % site_name)],
            ]
        ))
        
        # append a recent actions module
        self.children.append(modules.RecentActions(_('Recent Actions'), 1))

        # append another link list module for "support".
        self.children.append(modules.LinkList(
            _('Support'),
            children=[
                {
                    'title': _('Django documentation'),
                    'url': 'http://docs.djangoproject.com/',
                    'external': True,
                },
                {
                    'title': _('Django "django-users" mailing list'),
                    'url': 'http://groups.google.com/group/django-users',
                    'external': True,
                },
                {
                    'title': _('Django irc channel'),
                    'url': 'irc://irc.freenode.net/django',
                    'external': True,
                },
            ]
        ))


class CustomAppIndexDashboard(AppIndexDashboard):
    """
    Custom app index dashboard for minus.
    """

    # we disable title because its redundant with the model list module
    title = ''

    def __init__(self, *args, **kwargs):
        AppIndexDashboard.__init__(self, *args, **kwargs)

        # append a model list module and a recent actions module
        self.children += [
            modules.ModelList(self.app_title, self.models),
            modules.RecentActions(
                _('Recent Actions'),
                include_list=self.get_app_content_types(),
                limit=5
            )
        ]

    def init_with_context(self, context):
        """
        Use this method if you need to access the request context.
        """
        return super(CustomAppIndexDashboard, self).init_with_context(context)
