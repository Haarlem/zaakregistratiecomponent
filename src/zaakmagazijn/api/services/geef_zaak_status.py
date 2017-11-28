from spyne import ServiceBase, rpc

from zaakmagazijn.rgbz_mapping.models import (
    StatusProxy, StatusTypeProxy, ZaakProxy
)

from ..stuf import OneToManyRelation, StUFEntiteit
from ..stuf.models import (
    ParametersAntwoordSynchroon, ZAK_parametersVraagSynchroon
)
from ..zds import La01Builder, Lv01Builder


class StatusTypeEntiteit(StUFEntiteit):
    mnemonic = 'STT'
    model = StatusTypeProxy
    field_mapping = (
        ('zkt.omschrijving', 'zaaktype__zaaktypeomschrijving'),
        ('volgnummer', 'volgnummer'),
        ('omschrijving', 'omschrijving'),
    )
    required_fields = (
        'zkt.omschrijving',
    )


class StatusEntiteit(StUFEntiteit):
    mnemonic = 'ZAKSTT'
    model = StatusProxy
    field_mapping = (
        ('toelichting', 'toelichting'),
        ('datumStatusGezet', 'datum_status_gezet'),
        ('indicatieLaatsteStatus', 'indicatie_laatst_gezette_status'),
    )
    filter_fields = ('indicatieLaatsteStatus', )  # Should be fixed on J
    gerelateerde = ('status_type', StatusTypeEntiteit)
    fields = (
        'gerelateerde',
        'toelichting',
        'datumStatusGezet',
        'indicatieLaatsteStatus',
    )
    required_fields = (
        'toelichting',
    )


class ZaakEntiteit(StUFEntiteit):
    mnemonic = 'ZAK'
    model = ZaakProxy
    field_mapping = (
        ('identificatie', 'zaakidentificatie'),
    )
    filter_fields = ('identificatie', )
    related_fields = (
        OneToManyRelation('heeft', 'status_set', StatusEntiteit),
    )
    input_parameters = ZAK_parametersVraagSynchroon
    output_parameters = ParametersAntwoordSynchroon
    fields = (
        'identificatie',
        'heeft',
    )


input_builder = Lv01Builder(ZaakEntiteit, 'GeefZaakStatus')
output_builder = La01Builder(ZaakEntiteit, 'GeefZaakStatus')


class GeefZaakstatus(ServiceBase):
    """
    De "Geef Zaakstatus"-service biedt ZSC's de mogelijkheid om de meest
    actuele status van een lopende zaak op te vragen middels een
    vraag-/antwoordinteractie.

    Zie: ZDS 1.2, paragraaf 4.1.1
    """
    input_model = input_builder.create_model()
    output_model = output_builder.create_model()

    @rpc(input_model, _body_style="bare", _out_message_name="geefZaakstatus_ZakLa01", _returns=output_model)
    def geefZaakstatus_ZakLv01(ctx, data):
        """
        Opvragen meest actuele status van een lopende zaak.
        """

        # Eisen aan ZS:
        #
        # Het ZS retourneert alle attributen die gespecificeerd zijn in het
        # antwoordbericht en waarnaar de ZSC vraagt in het vraagbericht.
        # Eventueel kan het ZS hierbij gebruik maken van het attribuut
        # StUF:noValue, zie StUF 03.01 paragraaf 3.4

        # Interactie tussen ZSC en ZS:
        #
        # Tussen ZSC en ZS is een vraag-/antwoordinteractie.

        return output_builder.create_data(data, GeefZaakstatus.output_model)
