from spyne import ServiceBase, rpc

from zaakmagazijn.rgbz_mapping.models import (
    EnkelvoudigDocumentProxy, ZaakDocumentProxy, ZaakProxy
)

from ..stuf import OneToManyRelation, StUFEntiteit
from ..stuf.models import (
    ParametersAntwoordSynchroon, ZAK_parametersVraagSynchroon
)
from ..zds import La01Builder, Lv01Builder


class InformatieObjectEntiteit(StUFEntiteit):
    mnemonic = 'EDC'
    model = EnkelvoudigDocumentProxy
    field_mapping = (
        ('identificatie', 'identificatie'),
        ('dct.omschrijving', 'documenttype__documenttypeomschrijving'),
        ('dct.omschrijvingGeneriek', 'documenttype__documenttypeomschrijving_generiek'),
        ('creatiedatum', 'documentcreatiedatum'),
        ('ontvangstdatum', 'documentontvangstdatum'),
        ('titel', 'documenttitel'),
        ('beschrijving', 'documentbeschrijving'),
        ('formaat', 'documentformaat'),
        ('taal', 'documenttaal'),
        ('versie', 'documentversie'),
        ('status', 'documentstatus'),
        ('verzenddatum', 'documentverzenddatum'),
        ('vertrouwelijkAanduiding', 'vertrouwelijkaanduiding'),
        ('auteur', 'documentauteur'),
        ('link', 'documentlink'),
    )


class ZaakInformatieObjectEntiteit(StUFEntiteit):
    mnemonic = 'ZAKEDC'
    model = ZaakDocumentProxy
    field_mapping = (
        ('registratiedatum', 'registratiedatum'),
        ('titel', 'zaakdocumenttitel'),
        ('beschrijving', 'zaakdocumentbeschrijving'),
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
    model = ZaakProxy
    field_mapping = (
        ('identificatie', 'zaakidentificatie'),
    )
    filter_fields = ('identificatie', )
    input_parameters = ZAK_parametersVraagSynchroon
    output_parameters = ParametersAntwoordSynchroon
    related_fields = (
        OneToManyRelation('heeftRelevant', 'zaakdocument_set', ZaakInformatieObjectEntiteit),
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
