import logging
import re

from django.conf import settings

from ..api.stuf.choices import (
    BerichtcodeChoices, ClientFoutChoices, ServerFoutChoices
)
from ..api.stuf.faults import StUFFault
from .models import Application

logger = logging.getLogger(__name__)


def handle_authorization(ctx):
    if settings.ZAAKMAGAZIJN_OPEN_ACCESS:
        return

    # Check body to be present
    if len(ctx.in_object) == 0:
        raise StUFFault(ServerFoutChoices.stuf058)

    pattern = '\{([^\}]+)?\}?([\w]+)'
    ns, method = re.search(pattern, ctx.method_request_string).groups()
    for obj in ctx.in_object:
        # Check stuurgegevens to be present
        try:
            zender = obj.stuurgegevens.zender
            ontvanger = obj.stuurgegevens.ontvanger
        except AttributeError as e:
            raise StUFFault(ServerFoutChoices.stuf058)

        # Check if we are the intended recipient
        if ontvanger.applicatie != settings.ZAAKMAGAZIJN_SYSTEEM.get('applicatie'):
            raise StUFFault(ClientFoutChoices.stuf010)

        # Check if the sender exists
        try:
            allow = Application.objects.can_access(zender.applicatie, method)
        except Application.DoesNotExist:
            raise StUFFault(ClientFoutChoices.stuf013)

        # Check if the sender is allowed this function
        if not allow:
            logger.info('Disallow application "{}" access to "{}".'.format(
                zender.applicatie, method))
            raise StUFFault(ClientFoutChoices.stuf052)

        logger.debug('Allow application "{}" access to "{}".'.format(
            zender.applicatie, method))
