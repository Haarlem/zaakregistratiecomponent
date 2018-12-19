from django.db import transaction

from spyne import ServiceBase, rpc

from zaakmagazijn.rgbz_mapping.models import (
    EnkelvoudigDocumentProxy, ZaakDocumentProxy, ZaakProxy
)

from ...cmis.client import default_client as dms_client
from ..stuf import OneToManyRelation, StUFEntiteit
from ..stuf.models import Bv03Bericht  # , TijdvakGeldigheid
from ..stuf.utils import get_bv03_stuurgegevens
from ..zds import Lk01Builder
from ..zds.kennisgevingsberichten import process_create


class ZaakEntiteit(StUFEntiteit):
    mnemonic = 'ZAK'
    model = ZaakProxy
    field_mapping = (
        ('identificatie', 'zaakidentificatie'),
        ('omschrijving', 'omschrijving'),
    )
    matching_fields = (
        'identificatie',
        'omschrijving',
    )


class ZaakInformatieObjectEntiteit(StUFEntiteit):
    mnemonic = 'EDCZAK'
    model = ZaakDocumentProxy
    gerelateerde = ('zaak', ZaakEntiteit)
    field_mapping = ()  # Intentionally left blank

    begin_geldigheid = 'begin_geldigheid'
    eind_geldigheid = 'eind_geldigheid'
    begin_relatie = 'begin_relatie'
    eind_relatie = 'begin_relatie'
    tijdstip_registratie = 'tijdstip_registratie'


class EnkelvoudigDocumentEntiteit(StUFEntiteit):
    mnemonic = 'EDC'
    model = EnkelvoudigDocumentProxy
    field_mapping = (
        ('identificatie', 'identificatie'),
        ('dct.omschrijving', 'documenttype__documenttypeomschrijving'),
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
        ('inhoud', '_inhoud'),
    )
    related_fields = (
        OneToManyRelation('isRelevantVoor', 'is_relevant_voor', ZaakInformatieObjectEntiteit),
    )
    file_fields = ('inhoud',)
    fields = (
        'identificatie',
        'dct.omschrijving',
        'creatiedatum',
        'ontvangstdatum',
        'titel',
        'beschrijving',
        'formaat',
        'taal',
        'versie',
        'status',
        'verzenddatum',
        'vertrouwelijkAanduiding',
        'auteur',
        'link',
        'inhoud',
        # 'tijdvakGeldigheid',
        'isRelevantVoor',
    )
    matching_fields = (
        'identificatie',
        'dct.omschrijving',
        'titel',
    )


input_builder = Lk01Builder(EnkelvoudigDocumentEntiteit, 'VoegZaakdocumentToe')


class VoegZaakdocumentToe(ServiceBase):
    """
    De "voeg Zaakdocument toe"-service biedt DSC's de mogelijkheid om een nieuw
    document toe te voegen aan een lopende zaak. Hierbij moet altijd een
    documentidentificatie aangeleverd worden. De DSC kan zelf een
    documentidentificatie genereren of gebruik maken van de
    "genereer Document Identificatie"-service (zie paragraaf 4.3.7 service #13).

    Het ZS controleert altijd of de aangeleverde documentidentificatie uniek en
    geldig is. Het ZS maakt gebruik van de CMIS-documentservices om de
    wijzigingen met het DMS te synchroniseren.

    Zie: ZDS 1.2, paragraaf 4.3.4
    """
    input_model = input_builder.create_model()

    @rpc(input_model, _body_style="bare", _out_message_name="{http://www.egem.nl/StUF/StUF0301}Bv03Bericht", _returns=Bv03Bericht)
    def voegZaakdocumentToe_EdcLk01(ctx, data):
        """
        Er ontstaat een document wat direct aan een lopende zaak gekoppeld moet
        worden.
        """

        # Eisen aan ZS
        #
        # * Het ZS verwerkt berichten asynchroon en direct ("near realtime");
        # * De service provider controleert of de aangeleverde
        #   documentidentificatie uniek en geldig is (volgens RGBZ);

        # Interactie tussen ZS en DMS
        #
        # Het ZS zorgt ervoor dat het document dat is aangeboden door de DSC
        # wordt vastgelegd in het DMS. Hiervoor maakt het ZS gebruik van de
        # CMIS-services die aangeboden worden door het DMS. Hierbij gelden de
        # volgende eisen:
        #
        # * Het document wordt gerelateerd aan de juiste Zaakfolder (Zie 5.1)
        # * Het document wordt opgeslagen als objecttype EDC (Zie 5.2)
        # * Minimaal de vereiste metadata voor een EDC wordt vastgelegd in de
        #   daarvoor gedefinieerde objectproperties. In Tabel 3 is een mapping
        #   aangegeven tussen de StUF-ZKN-elementen en CMIS-objectproperties.
        with transaction.atomic():
            process_create(EnkelvoudigDocumentEntiteit, data)

            # determineer de afzender
            zender = data.stuurgegevens.zender
            created_by = zender.gebruiker or zender.administratie or zender.applicatie or zender.organisatie or None

            # vul de document met de inhoud
            document = EnkelvoudigDocumentProxy.objects.get(identificatie=data.object.identificatie)

            inhoud = data.object.inhoud
            content = inhoud.to_cmis()

            dms_client.maak_zaakdocument_met_inhoud(
                document._obj,
                filename=inhoud.bestandsnaam,
                sender=created_by,
                stream=content,
                content_type=inhoud.contentType if content is not None else None,
            )

            # relateer document aan juiste zaak folder
            zaak = ZaakProxy.objects.get(zaakidentificatie=data.object.isRelevantVoor[0].gerelateerde.identificatie)
            dms_client.relateer_aan_zaak(document._obj, zaak._obj)

        return {
            'stuurgegevens': get_bv03_stuurgegevens(data),
        }
