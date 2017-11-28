import logging

from spyne import ServiceBase, rpc

from ...rgbz.models import Besluit, BesluitInformatieObject, InformatieObject
from ..stuf import OneToManyRelation, StUFEntiteit
from ..stuf.models import BSL_parametersVraagSynchroon, Bv03Bericht
from ..stuf.utils import get_bv03_stuurgegevens
from ..zds import Lk01Builder
from ..zds.kennisgevingsberichten import process_update

logger = logging.getLogger(__name__)


class InformatieObjectEntiteit(StUFEntiteit):
    mnemonic = 'EDC'
    model = InformatieObject

    field_mapping = (
        ('identificatie', 'informatieobjectidentificatie'),
        ('titel', 'titel'),
        ('dct.omschrijving', 'informatieobjecttype__informatieobjecttypeomschrijving')
    )
    fields = (
        'identificatie',
        'dct.omschrijving',
        'titel',
    )
    matching_fields = (
        'identificatie'
    )


class BesluitInformatieObjectEntiteit(StUFEntiteit):
    mnemonic = 'BSLEDC'
    model = BesluitInformatieObject
    field_mapping = ()
    gerelateerde = ('informatieobject', InformatieObjectEntiteit)
    fields = (
        'gerelateerde',
    )
    matching_fields = (
        'gerelateerde'
    )


class BesluitEntiteit(StUFEntiteit):
    mnemonic = 'BSL'
    model = Besluit
    field_mapping = (  # Per ZDS 1.2 pg 40
        ('identificatie', 'identificatie'),
        ('bst.omschrijving', 'besluittype__besluittypeomschrijving'),
        ('datumBeslissing', 'besluitdatum'),
        ('ingangsdatumWerking', 'ingangsdatum'),
        ('einddatumWerking', 'vervaldatum'),
        ('vervalreden', 'vervalreden'),
        ('datumPublicatie', 'publicatiedatum'),
        ('datumVerzending', 'verzenddatum'),
        ('datumUiterlijkeReactie', 'uiterlijke_reactiedatum'),
        ('toelichting', 'besluittoelichting'),
    )
    filter_fields = ('identificatie', )
    input_parameters = BSL_parametersVraagSynchroon
    related_fields = (
        OneToManyRelation('isVastgelegdIn', 'is_vastgelegd_in', BesluitInformatieObjectEntiteit),
    )
    fields = (
        'identificatie',
        'bst.omschrijving',
        'datumBeslissing',
        'toelichting',
        'ingangsdatumWerking',
        'einddatumWerking',
        'vervalreden',
        'datumPublicatie',
        'datumVerzending',
        'datumUiterlijkeReactie',
        'isVastgelegdIn',
    )
    matching_fields = (
        'identificatie',
        'datumBeslissing',
    )


input_builder = Lk01Builder(BesluitEntiteit, 'UpdateBesluit', update=True)


class UpdateBesluit(ServiceBase):
    """
    De Update Besluit service biedt ZSC's de mogelijkheid om de attributen van
    een besluit te wijzigen.

    Zie: ZDS 1.2, paragraaf 4.1.8
    """
    input_model = input_builder.create_model()
    output_model = Bv03Bericht

    @rpc(input_model, _body_style="bare", _out_message_name="{http://www.egem.nl/StUF/StUF0301}Bv03Bericht", _returns=output_model)
    def updateBesluit_BslLk01(ctx, data):
        """
        Een besluit dat relevant is voor een lopende zaak is gewijzigd.
        """

        # Eisen aan ZS:
        #
        # Het ZS verwerkt berichten asynchroon en direct ("near realtime");

        process_update(BesluitEntiteit, data)

        return {
            'stuurgegevens': get_bv03_stuurgegevens(data),
        }
