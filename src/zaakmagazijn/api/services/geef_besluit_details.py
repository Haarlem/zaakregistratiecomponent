from spyne import ServiceBase, rpc

from ...rgbz.models import (
    Besluit, BesluitInformatieObject, InformatieObject, Zaak
)
from ..stuf import OneToManyRelation, StUFEntiteit
from ..stuf.constants import STUF_XML_NS
from ..stuf.models import BSL_parametersVraagSynchroon, TijdvakGeldigheid
from ..zds.beantwoordvraag import La01Builder, Lv01Builder


# Groep attribuut
class ZaakEntiteit(StUFEntiteit):
    mnemonic = 'ZAK'
    model = Zaak
    field_mapping = (
        # TODO: [KING] Taiga #232 antwoord.object.isUitkomstVan.gerelateerde.zaakIdentificatie staat in de referentie XSD als "identificatie".
        ('identificatie', 'zaakidentificatie'), # Overal is dit 'identificatie' behalve voor geefBesluitDetails?
        ('omschrijving', 'omschrijving'),
        ('toelichting', 'toelichting'),
        # TODO: [TECH] Taiga #233 Resultaat, opschorting en verlenging in geefBesluitDetails Zaak entiteit ontbreken.
        # <ns:resultaat>
        #    <ns:omschrijving stuf:noValue="?" stuf:exact="true">?</ns:omschrijving>
        #    <ns:toelichting stuf:noValue="?" stuf:exact="true">?</ns:toelichting>
        # </ns:resultaat>
        # ('resultaatomschrijving', 'resultaatomschrijving'),
        # ('resultaattoelichting', 'resultaattoelichting'),
        ('startdatum', 'startdatum'),
        ('publicatiedatum', 'publicatiedatum'),
        ('einddatumGepland', 'einddatum_gepland'),
        # <ns:opschorting>
        #    <ns:indicatie stuf:noValue="?" stuf:exact="true">?</ns:indicatie>
        #    <ns:reden stuf:noValue="?" stuf:exact="true">?</ns:reden>
        # </ns:opschorting>
        # <ns:verlenging>
        #    <ns:duur stuf:noValue="?" stuf:exact="true">?</ns:duur>
        #    <ns:reden stuf:noValue="?" stuf:exact="true">?</ns:reden>
        # </ns:verlenging>
    )
    # isVan
    # heeftBetrekkingOp
    # heeftAlsBelangHebbende
    # heeftAlsInitiator
    # heeftAlsDeelzaken
    # heeftAlsHoofdzaak
    # heeft


class BSLZAKEntiteit(StUFEntiteit):
    mnemonic = 'BSLZAK'
    model = Besluit
    field_mapping = []
    gerelateerde = ('zaak', ZaakEntiteit)


# Groep attribuut
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
        ('verzenddatum', 'verzenddatum'),
        ('vertrouwelijkheidAanduiding', 'vertrouwlijkaanduiding'),
        ('auteur', 'auteur'),
        ('status', 'informatieobject_status'),
        ('link', 'enkelvoudiginformatieobject__link'),
        # tijdvakGeldigheid
        # tijdstipRegistratie
        # extraElementen
    )


class BesluitInformatieObjectEntiteit(StUFEntiteit):
    mnemonic = 'BSLEDC'
    model = BesluitInformatieObject
    field_mapping = (
        # Een "samengesteld informatieobject" wordt in "geefBesluitdetails" op
        # geen enkele manier ontsloten volgens het ZDS.
    )
    gerelateerde = ('informatieobject', InformatieObjectEntiteit)


class BesluitEntiteit(StUFEntiteit):
    mnemonic = 'BSL'
    model = Besluit
    field_mapping = [  # Per ZDS 1.2 pg 43
        ('identificatie', 'identificatie'),
        ('datumBeslissing', 'besluitdatum'),
        ('toelichting', 'besluittoelichting'),
        ('ingangsdatumWerking', 'ingangsdatum'),
        ('einddatumWerking', 'vervaldatum'),
        ('vervalreden', 'vervalreden'),
        ('datumPublicatie', 'publicatiedatum'),
        ('datumVerzending', 'verzenddatum'),
        ('datumUiterlijkeReactie', 'uiterlijke_reactiedatum'),
        ('bst.omschrijving', 'besluittype__besluittypeomschrijving'),
        ('bst.omschrijvingGeneriek', 'besluittype__besluittypeomschrijving_generiek'),
        ('bst.categorie', 'besluittype__besluitcategorie'),
        ('bst.reactietermijn', 'besluittype__reactietermijn'),
        ('bst.publicatieIndicatie', 'besluittype__publicatie_indicatie'),
        ('bst.publicatieTekst', 'besluittype__publicatietekst'),
        ('bst.publicatieTermijn', 'besluittype__publicatietermijn'),
    ]
    filter_fields = ('identificatie', )
    input_parameters = BSL_parametersVraagSynchroon
    fields = (
        'identificatie',
        'bst.omschrijving',
        'bst.omschrijvingGeneriek',
        'bst.categorie',
        'bst.reactietermijn',
        'bst.publicatieIndicatie',
        'bst.publicatieTekst',
        'bst.publicatieTermijn',
        'datumBeslissing',
        'toelichting',
        'ingangsdatumWerking',
        'einddatumWerking',
        'vervalreden',
        'datumPublicatie',
        'datumVerzending',
        'datumUiterlijkeReactie',
        'tijdvakGeldigheid',
        # TODO: [KING] Taiga #230 object.tijdstipRegistratie in geefBesluitDetails heeft geen RGBZ mapping.
        'isUitkomstVan',
        'isVastgelegdIn',
    )
    related_fields = (
        OneToManyRelation('isVastgelegdIn', 'besluitinformatieobject_set', BesluitInformatieObjectEntiteit),
        OneToManyRelation('isUitkomstVan', 'self', BSLZAKEntiteit, min_occurs=1, max_occurs=1),
    )
    begin_geldigheid = 'besluittype__datum_begin_geldigheid_besluittype'
    eind_geldigheid = 'besluittype__datum_einde_geldigheid_besluittype'


input_builder = Lv01Builder(BesluitEntiteit, 'GeefBesluitDetails')
output_builder = La01Builder(BesluitEntiteit, 'GeefBesluitDetailsAntwoord')


class GeefBesluitDetails(ServiceBase):
    """
    De "geef Besluitdetails"-service biedt ZSC's de mogelijkheid om attributen
    van een besluit en gerelateerde objecten behorende bij een lopende zaak op
    te vragen middels een vraag-/antwoordinteractie.

    Zie: ZDS 1.2, paragraaf 4.1.10
    """
    input_model = input_builder.create_model()
    output_model = output_builder.create_model()

    @rpc(input_model, _body_style="bare", _out_message_name="geefBesluitdetails_BslLa01", _returns=output_model)
    def geefBesluitdetails_BslLv01(ctx, data):
        """
        Opvragen meest actuele gegevens van een besluit behorende bij een zaak.
        """

        # Eisen aan ZS:
        #
        # Het ZS retourneert alle attributen waarnaar de ZSC vraagt in het
        # vraagbericht. Eventueel kan het ZS hierbij gebruik maken van het
        # attribuut StUF:noValue, zie StUF 03.01 paragraaf 3.4

        # Interactie tussen ZSC en ZS:
        #
        # Tussen ZSC en ZS is een vraag-/antwoordinteractie.
        #
        # De ZSC mag niet naar andere elementen/attributen vragen dan
        # gespecificeerd in het antwoordbericht, tenzij het ZS het RGBZ
        # volledig ondersteunt (zie verder).

        data = output_builder.create_data(data, GeefBesluitDetails.output_model)
        return data
