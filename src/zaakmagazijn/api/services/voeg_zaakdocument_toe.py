from django.conf import settings
from django.db import transaction

from spyne import ServiceBase, rpc

from ...cmis.client import default_client as dms_client
from ...rgbz.models import (
    EnkelvoudigInformatieObject, Zaak, ZaakInformatieObject
)
from ...utils import stuf_datetime
from ..stuf import OneToManyRelation, StUFEntiteit
from ..stuf.choices import BerichtcodeChoices
from ..stuf.models import Bv03Bericht  # , TijdvakGeldigheid
from ..utils import create_unique_id
from ..zds import Lk01Builder
from ..zds.kennisgevingsberichten import process_create


class ZaakEntiteit(StUFEntiteit):
    mnemonic = 'ZAK'
    model = Zaak
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
    model = ZaakInformatieObject
    gerelateerde = ('zaak', ZaakEntiteit)
    field_mapping = ()  # Intentionally left blank


class InformatieObjectEntiteit(StUFEntiteit):
    mnemonic = 'EDC'  # Correct?
    model = EnkelvoudigInformatieObject
    field_mapping = (
        ('identificatie', 'informatieobjectidentificatie'),
        ('dct.omschrijving', 'informatieobjecttype__informatieobjecttypeomschrijving'),
        ('creatiedatum', 'creatiedatum'),
        ('ontvangstdatum', 'ontvangstdatum'),
        ('titel', 'titel'),
        ('beschrijving', 'beschrijving'),
        ('formaat', 'formaat'),
        ('taal', 'taal'),
        ('versie', 'versie'),
        ('status', 'informatieobject_status'),
        ('verzenddatum', 'verzenddatum'),
        ('vertrouwelijkAanduiding', 'vertrouwlijkaanduiding'),
        ('auteur', 'auteur'),
        # ('link', 'link'),
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
        # 'link',
        'inhoud',
        # 'tijdvakGeldigheid',
        'isRelevantVoor',
    )
    matching_fields = (
        'identificatie',
        'dct.omschrijving',
        'titel',
    )

    # TODO: [TECH] Taiga #188 entititeittype attribute should be "fixed"


input_builder = Lk01Builder(InformatieObjectEntiteit, 'VoegZaakdocumentToe')


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

    @rpc(input_model, _body_style="bare", _out_message_name="Bv03Bericht", _returns=Bv03Bericht)
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
            process_create(InformatieObjectEntiteit, data)

            # relateer document aan juiste zaak folder
            document = EnkelvoudigInformatieObject.objects.get(informatieobjectidentificatie=data.object.identificatie)
            zaak = Zaak.objects.get(zaakidentificatie=data.object.isRelevantVoor[0].gerelateerde.identificatie)
            dms_client.relateer_aan_zaak(document, zaak)

        return {
            'stuurgegevens': {
                'berichtcode': BerichtcodeChoices.bv03,
                'zender': settings.ZAAKMAGAZIJN_SYSTEEM,
                'ontvanger': data.stuurgegevens.zender,
                'referentienummer': create_unique_id(),
                'tijdstipBericht': stuf_datetime.now()
            },
        }
