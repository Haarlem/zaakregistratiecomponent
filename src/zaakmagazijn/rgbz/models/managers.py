from datetime import datetime

from django.db import models, transaction
from django.db.models.constants import LOOKUP_SEP

from ...api.stuf.utils import set_model_value
from ...utils import stuf_datetime
from ..choices import JaNee


class EnkelvoudigInformatieObjectManager(models.Manager):

    @transaction.atomic
    def create_from_cmis_properties(self, properties, zaak, object_id):
        """
        Create an `EnkelvoudigInformatieObject` from CMIS properties.

        :param properties: The CMIS properties as `dict`.
        :param zaak: The `Zaak` object.
        :return: The created `EnkelvoudigInformatieObject` object
        """
        from . import InformatieObjectType, ZaakInformatieObject

        # Remove relational properties, and use them make a `InformatieObjectType`
        informatieobjecttypeomschrijving = properties.pop('zsdms:dct.omschrijving', '')
        # informatieobjectcategorie = properties.pop('zsdms:dct.categorie', '')

        iot, is_created = InformatieObjectType.objects.get_or_create(
            informatieobjecttypeomschrijving=informatieobjecttypeomschrijving,
            # informatieobjectcategorie=informatieobjectcategorie,
            defaults={
                'datum_begin_geldigheid_informatieobjecttype': stuf_datetime.today(),
                # TODO [KING]: De attributen "domein" en "rsin" zijn verplicht in het
                # RGBZ maar bestaan niet bij het InformatieObjectType in ZDS.
                'domein': '?????',
                'rsin': 1,
            }
        )

        edc = self.model(_object_id=object_id)

        for cmis_property, field_name in self.model.CMIS_MAPPING.items():
            if cmis_property not in properties:
                continue

            # If a relational property is still present, the code should be updated.
            assert LOOKUP_SEP not in field_name, \
                'Cannot create {} with relational property: {}'.format(self.model, field_name)

            new_value = properties.get(cmis_property)

            if isinstance(new_value, datetime):
                new_value = stuf_datetime.stuf_date(new_value)

            set_model_value(edc, field_name, new_value)

        edc.informatieobjecttype = iot
        # TODO [KING]: Attribuut "bronorganisatie" is verplicht in het
        # RGBZ maar bestaat niet op het EDC in het ZDS.
        edc.bronorganisatie = 1
        edc.save()

        status = zaak.status_set.get(indicatie_laatst_gezette_status=JaNee.ja)
        ZaakInformatieObject.objects.create(
            zaak=zaak,
            informatieobject=edc,
            # TODO [KING]: Waar komen de ZAKEDC relatie "titel", "beschrijving", "registratiedatum" en "status" vandaan?
            titel=edc.titel,
            beschrijving=edc.beschrijving,
            registratiedatum=stuf_datetime.today(),
            status=status
        )

        return edc
