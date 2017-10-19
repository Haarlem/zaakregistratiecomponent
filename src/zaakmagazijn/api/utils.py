import uuid

from django.conf import settings

from ..rgbz.models import EnkelvoudigInformatieObject
from .stuf.choices import ServerFoutChoices


def create_unique_id():
    gemeente_code = settings.ZAAKMAGAZIJN_GEMEENTE_CODE
    assert len(gemeente_code) == 4, 'Gemeentecode should always be 4 characters long'

    return '{}{}'.format(gemeente_code, str(uuid.uuid4()))


def get_enkelvoudig_informatie_object_or_fault(identificatie: str) -> EnkelvoudigInformatieObject:
    """
    Retrieve the EnkelvoudigInformatieObject belonging to :param:`identificatie`, or
    raise the appropriate StUFFault.
    """
    from .stuf.faults import StUFFault

    eio = EnkelvoudigInformatieObject.objects.filter(informatieobjectidentificatie=identificatie).first()
    if eio is None:
        raise StUFFault(
            ServerFoutChoices.stuf064,
            stuf_details='Gerefereerde zaakdocument is niet aanwezig'
        )

    if not eio.zaakinformatieobject_set.exists():
        raise StUFFault(
            ServerFoutChoices.stuf064,
            stuf_details='Gerefereerde document is wel aanwezig maar geen zaakdocument'
        )

    return eio
