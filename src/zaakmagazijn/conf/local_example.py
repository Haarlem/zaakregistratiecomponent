import os

#
# Any machine specific settings when using development settings.
#

# Automatically figure out the ROOT_DIR and PROJECT_DIR.
DJANGO_PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
ROOT_DIR = os.path.abspath(os.path.join(DJANGO_PROJECT_DIR, os.path.pardir, os.path.pardir))

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

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(levelname)s  %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'zaakmagazijn': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.template': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'zeep.transports': {
            'handlers': ['console'],
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
    }
}

# DMS backend
CMIS_CLIENT_URL = 'http://localhost:8080/alfresco/cmisatom'
CMIS_CLIENT_USER = 'Admin'
CMIS_CLIENT_USER_PASSWORD = 'admin'
