import os

from django.conf import settings


def on_jenkins():
    return 'JOB_NAME' in os.environ


def should_skip_cmis_tests():
    return getattr(settings, 'SKIP_CMIS_TESTS', False)
