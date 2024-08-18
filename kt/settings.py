# Django settings for kt project.

# set VARIABLES either with default values or with overrides
try:
    import overrides.variables
except:
    VARIABLES = {
        'database_name': 'ktdb_dev',
        'database_user': 'ktadmin',
        'database_password': 'password',
        'database_host': 'db',
        'secret_key': 'secret',
        'aes_key': 'secret1234567890',
    }
else:
    VARIABLES = overrides.variables.VARIABLES

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # get parent dir (i.e. KT project, not KT app)

ROOT_DOMAIN = 'kritikustomeg.org'

DEBUG = True

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': VARIABLES['database_name'],
        'USER': VARIABLES['database_user'],
        'PASSWORD': VARIABLES['database_password'],
        'HOST': VARIABLES['database_host'],
        'PORT': '',
    }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Budapest'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'hu-hu'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
# USE_TZ = True
USE_TZ = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = 'ktapp/media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = 'https://static.kritikustomeg.org/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)


# COMPRESS_PRECOMPILERS = (
#     ('text/jsx', 'browserify -t reactify mobileapp/src/app/index.jsx > {outfile}'),
# )


# Make this unique, and don't share it with anybody.
SECRET_KEY = VARIABLES['secret_key']

AES_KEY = VARIABLES['aes_key']


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': DEBUG,
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.request',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'kt.context_processors.design_version_context',
                'kt.context_processors.number_of_suggested_stuff_for_admins_context',
                'kt.context_processors.settings_context',
            ],
        },
    },
]


MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'kt.middlewares.LoggingMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'kt.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'kt.wsgi.application'


INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'compressor',
    'rest_framework',
    'test_without_migrations',
    'ktapp',
    # 'mobileapp',
)

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGINATE_BY': 10,
}


SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'
SESSION_COOKIE_AGE = 2592000


# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
        },
        'kt_pageview': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'kt_loadtime': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'kt_exception': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'kt_profiler': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    }
}

AUTH_USER_MODEL = 'ktapp.KTUser'
LOGIN_URL = '/bejelentkezes'
LOGIN_REDIRECT_URL = '/'

TEST_RUNNER = 'django.test.runner.DiscoverRunner'


MAX_SEARCH_RESULTS = 10
FIRST_PREMIER_YEAR = 1970

VAPITI_YEAR = 2023
VAPITI_TOPIC_ID = 242
# VAPITI_TOPIC_ID = 0
# VAPITI_EVENT_URL = 'https://www.facebook.com/events/619791135489436/'
VAPITI_EVENT_URL = ''
# VAPITI_EVENT_LOCATION = 'Budapesten az Andersen Pub-ban'
VAPITI_EVENT_LOCATION = ''


# if True (or ENV=='local'), KTUser.email_user() will print the email instead of sending it
LOCAL_MAIL = False


DEFAULT_FROM_EMAIL = None


ENV = 'local'


# import overrides.settings, if there's any
try:
    from overrides.settings import *
except:
    pass
