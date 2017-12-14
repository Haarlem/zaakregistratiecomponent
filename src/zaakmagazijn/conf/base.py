import os

import django.db.models.options as options
from django.core.urlresolvers import reverse_lazy

from zaakmagazijn.rgbz.choices import Rolomschrijving, RolomschrijvingGeneriek

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
DJANGO_PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
BASE_DIR = os.path.abspath(os.path.join(DJANGO_PROJECT_DIR, os.path.pardir, os.path.pardir))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'o^3*o8_zj*@tml&!plx#8d_zs1v@0#$3j#))&igcx*k%gwnrd$'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [

    # Note: contenttypes should be first, see Django ticket #10827
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Optional applications.
    'django.contrib.admin',

    # External applications.
    'axes',
    'sniplates',
    'hijack',
    'compat',  # Part of hijack
    'hijack_admin',

    # Project applications.
    'zaakmagazijn.accounts',
    'zaakmagazijn.utils',
    'zaakmagazijn.apiauth',
    'zaakmagazijn.api',
    'zaakmagazijn.rsgb',
    'zaakmagazijn.rgbz',
    'zaakmagazijn.async',
    'zaakmagazijn.cmis',

    # Contrib
    'zaakmagazijn.contrib.idgenerator',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'zaakmagazijn.urls'

# List of callables that know how to import templates from various sources.
RAW_TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(DJANGO_PROJECT_DIR, 'templates'),
            os.path.join(DJANGO_PROJECT_DIR, 'api/tests/files'),

        ],
        'APP_DIRS': False,  # conflicts with explicity specifying the loaders
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'zaakmagazijn.utils.context_processors.settings',
            ],
            'loaders': RAW_TEMPLATE_LOADERS
        },
    },
]

WSGI_APPLICATION = 'zaakmagazijn.wsgi.application'

# Database: Defined in target specific settings files.
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'nl-nl'

TIME_ZONE = 'Europe/Amsterdam'

USE_I18N = True

USE_L10N = True

USE_TZ = True

USE_THOUSAND_SEPARATOR = True

# Translations
LOCALE_PATHS = (
    os.path.join(DJANGO_PROJECT_DIR, 'conf', 'locale'),
)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(DJANGO_PROJECT_DIR, 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
]

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

MEDIA_URL = '/media/'

FIXTURE_DIRS = (
    os.path.join(DJANGO_PROJECT_DIR, 'fixtures'),
)

DEFAULT_FROM_EMAIL = 'zaakmagazijn@example.com'

LOGGING_DIR = os.path.join(BASE_DIR, 'log')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(levelname)s %(name)s %(module)s %(process)d %(thread)d  %(message)s'
        },
        'timestamped': {
            'format': '%(asctime)s %(levelname)s %(name)s  %(message)s'
        },
        'simple': {
            'format': '%(levelname)s  %(message)s'
        },
        'performance': {
            'format': '%(asctime)s %(process)d | %(thread)d | %(message)s',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'timestamped'
        },
        'django': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGGING_DIR, 'django.log'),
            'formatter': 'verbose',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 10
        },
        'project': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGGING_DIR, 'zaakmagazijn.log'),
            'formatter': 'verbose',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 10
        },
        'performance': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGGING_DIR, 'performance.log'),
            'formatter': 'performance',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 10
        },
    },
    'loggers': {
        'zaakmagazijn': {
            'handlers': ['project'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['django'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.template': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    }
}

#
# Additional Django settings
#

# Custom user model
AUTH_USER_MODEL = 'accounts.User'

# Allow logging in with both username+password and email+password
AUTHENTICATION_BACKENDS = [
    'zaakmagazijn.accounts.backends.UserModelEmailBackend',
    'django.contrib.auth.backends.ModelBackend'
]

#
# Custom settings
#
PROJECT_NAME = 'zaakmagazijn'
ENVIRONMENT = None
SHOW_ALERT = True
options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('mnemonic',)

#
# Library settings
#

# Django-axes
AXES_LOGIN_FAILURE_LIMIT = 30  # Default: 3
AXES_LOCK_OUT_AT_FAILURE = True  # Default: True
AXES_USE_USER_AGENT = False  # Default: False
AXES_COOLOFF_TIME = 1  # One hour

# Django-hijack (and Django-hijack-admin)
HIJACK_LOGIN_REDIRECT_URL = '/admin/'
HIJACK_LOGOUT_REDIRECT_URL = reverse_lazy('admin:accounts_user_changelist')
HIJACK_REGISTER_ADMIN = False
# This is a CSRF-security risk.
# See: http://django-hijack.readthedocs.io/en/latest/configuration/#allowing-get-method-for-hijack-views
HIJACK_ALLOW_GET_REQUESTS = True

#
# Zaakmagazijn settings
#

# Prefix for identification codes.
ZAAKMAGAZIJN_GEMEENTE_CODE = '0000'

# Max amount of bytes that the WSGI server can process in 1 request.
#
# Since attachments are bas64 encoded twice and thus increase in size
# the maximum file content size is max_content_length/(8/6)/(8/6) (~23 mb in our case)
# (excluding any other payload)
ZAAKMAGAZIJN_MAX_CONTENT_LENGTH = 40 * 1024 * 1024  # 40mb

# Allow everyone or use the authentication scheme.
ZAAKMAGAZIJN_OPEN_ACCESS = True

# Based on XSD parametersVraag -> maximumAantal
ZAAKMAGAZIJN_DEFAULT_MAX_NR_RESULTS = 15

# Indentificatie van systeem
ZAAKMAGAZIJN_SYSTEEM = {
    'organisatie': 'ORG',
    'applicatie': 'TTA',
    'administratie': '',
    'gebruiker': '',
}

ZAAKMAGAZIJN_ZAAK_ID_GENERATOR = 'zaakmagazijn.api.utils.create_unique_id'
# ZAAKMAGAZIJN_ZAAK_ID_GENERATOR = 'zaakmagazijn.contrib.idgenerator.utils.create_incremental_year_id'

# Absolute URL of the Zaakmagazijn. Used in the WSDL and should not be altered.
ZAAKMAGAZIJN_ZDS_URL = '/static/schema/'
ZAAKMAGAZIJN_ZDS_PATH = os.path.join(BASE_DIR, 'zds', 'ZDS 1.2 2017 Q1 Resolved')

# Whether soap/wsdl/schema locations in the WSDL should be rewritten on-the-fly to
# the proper locations or if the original schema's should be used.
ZAAKMAGAZIJN_REFERENCE_WSDL = True

# Use the workaround for the StUF testplatform.
ZAAKMAGAZIJN_STUF_TESTPLATFORM = False

# Schema's are distributed as static files.
STATICFILES_DIRS = list(STATICFILES_DIRS) + [
    ('schema', os.path.join(ZAAKMAGAZIJN_ZDS_PATH)),
]

# Toelichtingen, en omschrijvingen die automatisch worden ingevuld bij het
# aanmaken van het Relatietype Rol, voor een Zaak.
#
# Relatietype Rol wordt als volgt gevuld:
# - De key wordt gebruikt voor: Attribuutsoort Rolomschrijving,
# - 'generiek' wordt gebruikt voor: Attribuutsoort Rolomschrijving generiek,
# - 'toelichting wordt gebruikt voor: Attribuutsoort Roltoelichting

# Let op: Als je deze waardes wijzigt, zorg ervoor dat je ook een migratie schrijft
# omdat op deze waardes ook gefilterd wordt. (Mogelijk ook een TODO ;)

ZAAKMAGAZIJN_ROLOMSCHRIJVINGEN = {
    Rolomschrijving.adviseur: {
        'generiek': RolomschrijvingGeneriek.adviseur,
        'toelichting': 'Kennis in dienst stellen van de behandeling van (een deel van) een zaak'
    },
    Rolomschrijving.belanghebbende: {
        'generiek': RolomschrijvingGeneriek.belanghebbende,
        'toelichting': 'Vanuit eigen en objectief belang rechtstreeks betrokken zijn bij of '
                       'geïnformeerd willen worden over de behandeling en/of de uitkomst van '
                       'een zaak'
    },
    Rolomschrijving.behandelaar: {
        'generiek': RolomschrijvingGeneriek.behandelaar,
        'toelichting': 'De vakinhoudelijke behandeling doen van (een deel van) een zaak'
    },
    Rolomschrijving.beslisser: {
        'generiek': RolomschrijvingGeneriek.beslisser,
        'toelichting': 'Nemen van besluiten die voor de uitkomst van een zaak noodzakelijk zijn'
    },
    Rolomschrijving.initiator: {
        'generiek': RolomschrijvingGeneriek.initiator,
        'toelichting': 'Aanleiding geven tot de start van een zaak'
    },
    Rolomschrijving.klantcontacter: {
        'generiek': RolomschrijvingGeneriek.klantcontacter,
        'toelichting': 'Het eerste aanspreekpunt zijn voor vragen van burgers en bedrijven '
                       'in het kader van de dienstverlening door de organisatie aan burgers '
                       'en bedrijven. Nb. Met betrekking tot het zaakgericht werken betreft '
                       'dit veelal het verzorgen van de intake van een vraag naar een product '
                       'of dienst, het informeren over de voortgang van de behandeling van de '
                       'zaak en het leveren van de uitkomst van de zaak.'
    },
    Rolomschrijving.zaakcoordinator: {
        'generiek': RolomschrijvingGeneriek.zaakcoordinator,
        'toelichting': 'Er voor zorg dragen dat de behandeling van de zaak in samenhang '
                       'uitgevoerd wordt conform de daarover gemaakte afspraken',
    }
}

# CMIS Client settings
CMIS_ZAKEN_TYPE_ENABLED = False
CMIS_UPLOAD_TO = 'zaakmagazijn.cmis.utils.upload_to'
# CMIS_UPLOAD_TO = 'zaakmagazijn.cmis.utils.upload_to_date_based'
CMIS_CLIENT_CLASS = 'zaakmagazijn.cmis.client.CMISDMSClient'
CMIS_CLIENT_URL = 'http://localhost:8080/alfresco/cmisatom'
CMIS_CLIENT_USER = 'Admin'
CMIS_CLIENT_USER_PASSWORD = 'admin'

# Use a property to store the sender information
CMIS_SENDER_PROPERTY = None
