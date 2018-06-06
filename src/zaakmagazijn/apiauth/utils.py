import logging
import re

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from ..api.stuf.choices import ClientFoutChoices, ServerFoutChoices
from ..api.stuf.faults import StUFFault
from ..api.stuf.utils import get_systeem
from .models import Application

logger = logging.getLogger(__name__)


def handle_authorization(ctx):
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

        system_dict = get_systeem(ontvanger)

        # Check if we are the intended recipient (not required)
        if ontvanger is not None:
            # Application is required, the rest is optional but should match
            # if provided!
            for key, request_value in ontvanger.as_dict().items():
                system_val = system_dict.get(key)
                if (request_value or key == 'applicatie') and request_value != system_val:
                    raise StUFFault(
                        ClientFoutChoices.stuf010,
                        _('Ontvangende {} "{}" uit verzoek komt niet overeen met "{}".').format(
                            key, request_value, system_val
                        ))

        from auditlog.middleware import threadlocal
        if hasattr(threadlocal, 'auditlog'):
            threadlocal.auditlog['data'] = {
                'functie': method,
                'zender': zender.as_dict() if zender else None,
            }

        # If we have open access, we don't need to check the sender.
        if settings.ZAAKMAGAZIJN_OPEN_ACCESS:
            continue

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
