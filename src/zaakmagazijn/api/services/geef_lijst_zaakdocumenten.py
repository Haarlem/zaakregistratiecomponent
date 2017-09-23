from spyne import ServiceBase, rpc

from zaakmagazijn.rgbz.models import (
    InformatieObject, Zaak, ZaakInformatieObject
)

from ..stuf import OneToManyRelation, StUFEntiteit
from ..stuf.models import ZAK_parametersVraagSynchroon
from ..zds import La01Builder, Lv01Builder


class InformatieObjectEntiteit(StUFEntiteit):
    mnemonic = 'EDC'
    model = InformatieObject
    field_mapping = (
        ('identificatie', 'informatieobjectidentificatie'),
        ('dct.omschrijving', 'informatieobjecttype__informatieobjecttypeomschrijving'),
        ('dct.omschrijvingGeneriek', 'informatieobjecttype__informatieobjecttypeomschrijving_generiek'),
        ('creatiedatum', 'creatiedatum'),
        ('ontvangstdatum', 'ontvangstdatum'),
        ('titel', 'titel'),
        ('beschrijving', 'beschrijving'),
        ('formaat', 'enkelvoudiginformatieobject__formaat'),
        ('taal', 'enkelvoudiginformatieobject__taal'),
        ('versie', 'versie'),
        ('status', 'informatieobject_status'),
        ('verzenddatum', 'verzenddatum'),
        ('vertrouwelijkheidAanduiding', 'vertrouwlijkaanduiding'),
        ('auteur', 'auteur'),
        ('link', 'enkelvoudiginformatieobject__link'),
    )


class ZaakInformatieObjectEntiteit(StUFEntiteit):
    mnemonic = 'ZAKEDC'
    model = ZaakInformatieObject
    field_mapping = (
        ('registratiedatum', 'registratiedatum'),
        ('titel', 'titel'),
        ('beschrijving', 'beschrijving'),
    )
    gerelateerde = ('informatieobject', InformatieObjectEntiteit)
    fields = (
        'gerelateerde',
        'registratiedatum',
        'titel',
        'beschrijving',
    )


class ZaakDocumentLijstEntiteit(StUFEntiteit):
    mnemonic = 'ZAK'
    model = Zaak
    field_mapping = (
        ('identificatie', 'zaakidentificatie'),
    )
    filter_fields = ('identificatie', )
    input_parameters = ZAK_parametersVraagSynchroon
    related_fields = (
        OneToManyRelation('heeftRelevant', 'zaakinformatieobject_set', ZaakInformatieObjectEntiteit),
    )
    fields = (
        'identificatie',
        'heeftRelevant',
    )


input_builder = Lv01Builder(ZaakDocumentLijstEntiteit, 'GeefLijstZaakdocumenten')
output_builder = La01Builder(ZaakDocumentLijstEntiteit, 'GeefLijstZaakdocumenten')


class GeefLijstZaakdocumenten(ServiceBase):
    """
    De "geef Lijst Zaakdocumenten"-service biedt ZSC's de mogelijkheid om een
    lijst met referenties op te vragen naar DOCUMENTen behorende bij een
    lopende zaak middels een vraag-/antwoordinteractie.

    De ZSC krijgt in deze interactie de hoedanigheid van DSC. In het
    antwoordbericht staan alle ZAAKDOCUMENTEN (de relatie tussen ZAAK en
    DOCUMENT) die bekend zijn bij het ZS.

    Zie: ZDS 1.2, paragraaf 4.3.1
    """
    input_model = input_builder.create_model()
    output_model = output_builder.create_model()

    @rpc(input_model, _body_style="bare", _out_message_name="geefLijstZaakdocumenten_ZakLa01", _returns=output_model)
    def geefLijstZaakdocumenten_ZakLv01(ctx, data):

        # Eisen aan ZS:
        #
        # * Het ZS is de authentieke bron voor de relatie ZAAKDOCUMENT;
        # * Het ZS retourneert alle voor hem bekende ZAAKDOCUMENT relaties in
        #   het antwoordbericht.

        # Interactie tussen DSC en ZS:
        #
        # Tussen DSC en ZS is een vraag-/antwoordinteractie.

        return output_builder.create_data(data, GeefLijstZaakdocumenten.output_model)
