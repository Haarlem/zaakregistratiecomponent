import django.dispatch
import logging

from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from auditlog.models import LogEntry

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=LogEntry)
def set_soap_data(sender, instance, **kwargs):
    """
    Signal receiver with an extra, required 'user' kwarg. This method becomes a real (valid) signal receiver when
    it is curried with the actor.
    """
    from auditlog.middleware import threadlocal
    if not hasattr(threadlocal, 'auditlog'):
        return

    try:
        instance.additional_data = threadlocal.auditlog['data']
    except Exception as e:
        logger.exception(e)


service_read = django.dispatch.Signal(providing_args=["instance", ], use_caching=True)

# Monkey patch django-auditlog to include the read action.
LogEntry.Action.READ = 3
LogEntry.Action.choices = (
    (LogEntry.Action.CREATE, _("create")),
    (LogEntry.Action.UPDATE, _("update")),
    (LogEntry.Action.DELETE, _("delete")),
    (LogEntry.Action.READ, _("read")),
)
action_field = LogEntry._meta.get_field('action')
action_field.choices = LogEntry.Action.choices


@receiver(service_read)
def log_read(sender, instance, **kwargs):
    """
    Signal receiver that creates a log entry.

    This signal must be called explicitly, like:

        post_service_read.send(sender=self.__class__, instance=ZaakDocument.objects.get(pk=1))

    """
    from django.contrib.contenttypes.models import ContentType
    from django.utils.encoding import smart_text
    from django.utils.six import integer_types
    from zaakmagazijn.rgbz_mapping.base import ModelProxy

    if isinstance(instance, ModelProxy):
        instance = instance._obj

    pk = LogEntry.objects._get_pk_value(instance)

    attrs = {
        'action': LogEntry.Action.READ,
        'content_type': ContentType.objects.get_for_model(instance),
        'object_pk': pk,
        'object_repr': smart_text(instance),
    }

    if isinstance(pk, integer_types):
        attrs['object_id'] = pk

    get_additional_data = getattr(instance, 'get_additional_data', None)
    if callable(get_additional_data):
        attrs['additional_data'] = get_additional_data()

    LogEntry.objects.create(**attrs)
