from .base import *

#
# Standard Django settings.
#

DEBUG = True
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

ADMINS = ()
MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'zaakmagazijn',
        'USER': 'zaakmagazijn',
        'PASSWORD': 'zaakmagazijn',
        'HOST': '',  # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',  # Set to empty string for default.
    }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

LOGGING['loggers'].update({
    'zaakmagazijn': {
        'handlers': ['console'],
        'level': 'DEBUG',
        'propagate': True,
    },
    'django': {
        'handlers': ['console'],
        'level': 'INFO',
        'propagate': True,
    },
    'django.db.backends': {
        'handlers': ['django'],
        'level': 'INFO',
        'propagate': False,
    },
    'performance': {
        'handlers': ['console'],
        'level': 'INFO',
        'propagate': True,
    },
    'zeep.transports': {
        'level': 'WARNING',
        'propagate': True,
    },
    'spyne': {
        'handlers': ['console'],
        'level': 'WARNING',
        'propagate': True,
    },
    'cmislib': {
        'handlers': ['console'],
        'level': 'WARNING',
        'propagate': True,
    }
})

#
# Additional Django settings
#

# Disable security measures for development
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = False
CSRF_COOKIE_SECURE = False

#
# Custom settings
#
ENVIRONMENT = 'development'

#
# Library settings
#

# Django debug toolbar
INSTALLED_APPS += [
    'debug_toolbar',
    'django_extensions',
]
MIDDLEWARE_CLASSES += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]
INTERNAL_IPS = ('127.0.0.1',)
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False
}

ZAAKMAGAZIJN_URL = 'http://localhost:8000'

# Override settings with local settings.
try:
    from .local import *
except ImportError:
    pass
