from django.core.exceptions import ImproperlyConfigured

from .base import *

# Helper function
missing_environment_vars = []


def getenv(key, default=None, required=False, split=False):
    val = os.getenv(key, default)
    if required and val is None:
        missing_environment_vars.append(key)
    if split and val:
        val = val.split(',')
    return val


#
# Standard Django settings.
#
DEBUG = getenv('DEBUG', False)

ADMINS = getenv('ADMINS', split=True)
MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'USER': getenv('DATABASE_USER', 'postgres'),
        'NAME': getenv('DATABASE_NAME', 'postgres'),
        'PASSWORD': getenv('DATABASE_PASSWORD', ''),
        'HOST': getenv('DATABASE_HOST', 'db'),
        'PORT': getenv('DATABASE_PORT', '5432'),
    }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = getenv('ALLOWED_HOSTS', '*', split=True)

#
# Additional Django settings
#

# Disable security measures for development
SESSION_COOKIE_SECURE = getenv('SESSION_COOKIE_SECURE', False)
SESSION_COOKIE_HTTPONLY = getenv('SESSION_COOKIE_HTTPONLY', False)
CSRF_COOKIE_SECURE = getenv('CSRF_COOKIE_SECURE', False)

#
# Custom settings
#
ENVIRONMENT = 'docker'

#
# Zaakmagazijn settings
#
ZAAKMAGAZIJN_GEMEENTE_CODE =  getenv('ZAAKMAGAZIJN_GEMEENTE_CODE', '0000')
ZAAKMAGAZIJN_MAX_CONTENT_LENGTH = int(getenv('ZAAKMAGAZIJN_MAX_CONTENT_LENGTH', 40 * 1024 * 1024))  # 40mb
ZAAKMAGAZIJN_OPEN_ACCESS = getenv('ZAAKMAGAZIJN_OPEN_ACCESS', True)
ZAAKMAGAZIJN_DEFAULT_MAX_NR_RESULTS = int(getenv('ZAAKMAGAZIJN_DEFAULT_MAX_NR_RESULTS', 15))

# Identificatie van systeem
ZAAKMAGAZIJN_SYSTEEM = {
    'organisatie': getenv('ZAAKMAGAZIJN_SYSTEEM_ORGANISATIE', 'ORG'),
    'applicatie': getenv('ZAAKMAGAZIJN_SYSTEEM_APPLICATIE', 'TTA'),
    'administratie': getenv('ZAAKMAGAZIJN_SYSTEEM_ADMINISTRATIE', ''),
    'gebruiker': getenv('ZAAKMAGAZIJN_SYSTEEM_GEBRUIKER', ''),
}

ZAAKMAGAZIJN_ZAAK_ID_GENERATOR = getenv('ZAAKMAGAZIJN_ZAAK_ID_GENERATOR', 'zaakmagazijn.api.utils.create_unique_id')
# Alternatives:
# 'zaakmagazijn.contrib.idgenerator.utils.create_incremental_year_id'
# 'zaakmagazijn.contrib.idgenerator.utils.create_incremental_year_with_org_id'

ZAAKMAGAZIJN_DOCUMENT_ID_GENERATOR = getenv('ZAAKMAGAZIJN_DOCUMENT_ID_GENERATOR', 'zaakmagazijn.api.utils.create_unique_id')
ZAAKMAGAZIJN_BESLUIT_ID_GENERATOR = getenv('ZAAKMAGAZIJN_BESLUIT_ID_GENERATOR', 'zaakmagazijn.api.utils.create_unique_id')

ZAAKMAGAZIJN_REFERENCE_WSDL = getenv('ZAAKMAGAZIJN_REFERENCE_WSDL', True)

ZAAKMAGAZIJN_URL = getenv('ZAAKMAGAZIJN_URL', None, required=True)

# CMIS Client settings
CMIS_ZAKEN_TYPE_ENABLED = getenv('CMIS_ZAKEN_TYPE_ENABLED', False)
CMIS_UPLOAD_TO = getenv('CMIS_UPLOAD_TO', 'zaakmagazijn.cmis.utils.upload_to')
# Alternatives:
# 'zaakmagazijn.cmis.utils.upload_to_date_based'
CMIS_CLIENT_CLASS = getenv('CMIS_CLIENT_CLASS', 'zaakmagazijn.cmis.client.CMISDMSClient')
CMIS_CLIENT_URL = getenv('CMIS_CLIENT_URL', 'http://localhost:8080/alfresco/cmisatom')
CMIS_CLIENT_USER = getenv('CMIS_CLIENT_USER', 'Admin')
CMIS_CLIENT_USER_PASSWORD = getenv('CMIS_CLIENT_USER_PASSWORD', 'admin')
CMIS_SENDER_PROPERTY = getenv('CMIS_SENDER_PROPERTY', None)  # Example: 'hlm:zender'


# Override settings with local settings.
try:
    from .local import *
except ImportError:
    pass


if missing_environment_vars:
    raise ImproperlyConfigured(
        'These environment variables are required but missing: {}'.format(', '.join(missing_environment_vars)))
