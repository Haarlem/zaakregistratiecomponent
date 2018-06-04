from .base import *

#
# Standard Django settings.
#

DEBUG = False

ADMINS = ()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'zaakmagazijn',
        'USER': 'jenkins',
        'PASSWORD': 'jenkins',
        'HOST': '',  # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '5435',  # PostgreSQL 9.5 on Jenkins.
        'TEST': {
            'NAME': 'test_%s' % os.getenv('JOB_NAME', default='zaakmagazijn')
        }
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# This should be overwritten with override_settings in test to the appropriate URL.
ZAAKMAGAZIJN_URL = 'bogus.localhost'

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/stable/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

LOGGING['loggers'].update({
    'django': {
        'handlers': ['django'],
        'level': 'WARNING',
        'propagate': True,
    },
})

SKIP_CMIS_TESTS = True

#
# Custom settings
#
INSTALLED_APPS += [
    'django_jenkins',
]

PROJECT_APPS = [app.rsplit('.apps.')[0] for app in INSTALLED_APPS if app.startswith('zaakmagazijn')]

JENKINS_TASKS = (
    'django_jenkins.tasks.run_pylint',
    'django_jenkins.tasks.run_pep8',
)
