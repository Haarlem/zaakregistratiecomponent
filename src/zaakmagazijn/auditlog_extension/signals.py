import logging

from django.db.models.signals import pre_save
from django.dispatch import receiver

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
