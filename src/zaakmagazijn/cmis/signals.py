"""
Signal handlers voor ZS-DMS interactie.
"""
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from zaakmagazijn.rgbz.models import Zaak

from .client import default_client as client


@receiver(post_save, sender=Zaak, dispatch_uid='cmis.creeer_zaakfolder')
def creeer_zaakfolder(signal, instance, **kwargs):
    # only create the folder in the DMS if it's a newly created object
    if not kwargs['created'] or kwargs['raw']:
        return

    transaction.on_commit(
        lambda: client.creeer_zaakfolder(instance),
        using=kwargs['using']
    )
