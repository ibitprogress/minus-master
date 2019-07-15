# Django settings for minus.lviv.ua project.

import os.path
import sys

# Setting PROJECT_ROOT variable
PROJECT_ROOT = os.path.normpath(os.path.dirname(__file__))

# Adding modules directory to python path
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'modules'))

DEBUG = True
TEMPLATE_DEBUG = DEBUG
DATABASE_SUPPORTS_TRANSACTIONS = True #for testing purposes

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'minus.db'
    }
}


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Kiev'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'uk-ua'
USE_L10N = True
SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT,'static')
STORAGE_ROOT = MEDIA_ROOT

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/static/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'lyo^@z+xkheq7sga285rvqq*pmhu&*b=-@3r5abgqhl=u!=7*e'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'users.middleware.activity.LastActivity',
    'users.middleware.redirects.AuthorizedRedirects',
    'django.contrib.messages.middleware.MessageMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.contrib.messages.context_processors.messages',
    'forum.context_processors.moderator',
    'sape.django.context_processors.sape',
    'minusstore.context_processors.pjax',
)

ROOT_URLCONF = 'minus.urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT, 'templates'),
)

INSTALLED_APPS = (
    'admin_tools',
    'admin_tools.theming',
    'admin_tools.menu',
    'admin_tools.dashboard',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.flatpages',
    'django.contrib.markup',
    'django.contrib.sessions',
    'django.contrib.comments',
    'django.contrib.messages',
    'django_nose',
    'forum',
    'sape.django',
    'minusstore',
    'messages',
    'registration',
    'users',
    'photos',
    'django_inlines',
    'djangoratings',
    'voting',
    'gencal',
    'pagination',
    'friends',
    'videos',
    'albums',
    'haystack',
    'pytils',
    'ck',
    'tinymce',
    'links',
    'captcha',
    'chunks',
    'jchat',
    'chat',
    'delivery',
    'banners',
    'news',
    'blurbs',
    'vocal_contest',
    'tastypie',
    'hitcount',
    'radio',
    'south',
    #'debug_toolbar',
)
INTERNAL_IPS = ('127.0.0.1',)
HAYSTACK_SITECONF = 'minus.search_sites'
HAYSTACK_SEARCH_ENGINE = 'whoosh'
HAYSTACK_WHOOSH_PATH = os.path.join(PROJECT_ROOT, 'search')
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 20

CACHE_BACKEND = "dummy://"
CACHE_MIDDLEWARE_SECONDS = 600
CACHE_MIDDLEWARE_KEY_PREFIX = 'minus'
CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True

SKIP_SOUTH_TESTS = True
SOUTH_TESTS_MIGRATE = False

FILE_UPLOAD_MAX_MEMORY_SIZE = 0 #have to do this because of reading idv3tags
MAX_FILE_SIZE = 50*1024*1024 #25 Mb


# Registration
ACCOUNT_ACTIVATION_DAYS = 3
# Authorization
AUTHENTICATION_BACKENDS = (
    'users.backends.auth.EmailOrUsernameModelBackend',
)
# Users settings
AUTH_PROFILE_MODULE = 'users.userprofile'

LOGIN_URL = '/login/'
LOGOUT_URL = '/logout/'
LOGIN_REDIRECT_URL = '/'

FORUM_BASE = '/forum'

# Avatar settings
AVATAR_WIDTH = 100
AVATAR_HEIGHT = 130
AVATAR_SMALL_WIDTH = 50
AVATAR_SMALL_HEIGHT = 65

AVATAR_MAX_SIZE = 200*1024 #200 Kb
# Photos settings
PHOTO_THUMB_WIDTH = 120
PHOTO_THUMB_HEIGHT = 120
PHOTO_WIDTH = 640
PHOTO_HEIGHT = 480
PHOTO_THUMB_SUFFIX = '_th'
PHOTO_MAX_SIZE = 2*1024*1024 #2 Mb
PHOTO_ALBUM_LIMIT = 10*1024*1024 #10 Mb

# How many top rated objects to show with top_rated tag.
TOP_RATED_LIMIT = 10

# Authenticated user will be redirected to
# LOGIN_REDIRECT_URL from these patterns.
AUTH_USER_DISALLOWED_URLS = (
    '/login/',
    '/register/',
)

# For embeding
INLINES_START_TAG = '{{'
INLINES_END_TAG = '}}'

#uncomment if we use different users for shell/run
#FILE_UPLOAD_PERMISSIONS = 0666

#Links settings
FRIENDLINK_MODERATOR_EMAIL = 'rmetelsky@gmail.com'

#TinyMCE settings
TINYMCE_DEFAULT_CONFIG = {
    'plugins': "table,spellchecker,paste,searchreplace",
    'theme': "advanced",
    'cleanup_on_startup': True,
    'custom_undo_redo_levels': 10,
    'skin': 'o2k7',
    'theme_advanced_toolbar_location': 'top',
    'theme_advanced_buttons1_add': 'forecolor,backcolor,forecolorpicker,backcolorpicker,fontselect,fontsizeselect'
}

TINYMCE_SPELLCHECKER = True

SAPE_DATABASE = os.path.join(PROJECT_ROOT, 'sape/links.db')
SAPE_USER = '7c3733475075d6b6761c51ce674d6208'
SAPE_HOST = 'minus.lviv.ua'

TEST_RUNNER = 'tddspry.django.runner.TestSuiteRunner'

TEST_DISABLED_APPS = ('south', )
SANITY_TAGS = "p blockquote span:style font:color:size ul li ol i strike strong b em u a:href pre br img:src code"

CONTEST_END_DAYS = 30
CONTEST_REGISTRATION_END_DAYS = 14

HITCOUNT_KEEP_HIT_ACTIVE = { 'days': 7 }
HITCOUNT_HITS_PER_IP_LIMIT = 0
HITCOUNT_EXCLUDE_USER_GROUP = ( 'Editor', )

ADMIN_TOOLS_INDEX_DASHBOARD = 'minus.dashboard.CustomIndexDashboard'
ADMIN_TOOLS_APP_INDEX_DASHBOARD = 'minus.dashboard.CustomAppIndexDashboard'

RADIO_URL = "http://minus.lviv.ua:8001/minusradio"
# Try to loading settings from ``settings_local.py`` file 
try:
    from settings_local import *
except ImportError, e:
    sys.stderr.write('settings_local.py not found. Using default settings\n')
    sys.stderr.write('%s: %s\n\n' % (e.__class__.__name__, e))
