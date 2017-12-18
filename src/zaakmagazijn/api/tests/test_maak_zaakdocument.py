from datetime import date
from io import BytesIO

from django.conf import settings

from lxml import etree

from zaakmagazijn.api.stuf.choices import BerichtcodeChoices
from zaakmagazijn.api.tests.base import BaseSoapTests, BaseTestPlatformTests
from zaakmagazijn.rgbz.choices import JaNee
from zaakmagazijn.rgbz.models import (
    EnkelvoudigInformatieObject, ZaakInformatieObject
)
from zaakmagazijn.rgbz.tests.factory_models import (
    InformatieObjectTypeFactory, ZaakFactory
)
from zaakmagazijn.utils import stuf_datetime


class DMSMockMixin:
    extra_client_mocks = [
        'zaakmagazijn.cmis.fields.dms_client',
        'zaakmagazijn.api.services.maak_zaakdocument.dms_client',
    ]

    @property
    def _dms_client(self):
        return self._extra_mocked_dms_clients[0]

    @property
    def _service_dms_client(self):
        return self._extra_mocked_dms_clients[1]


class maakZaakdocument_EdcLk01Tests(DMSMockMixin, BaseSoapTests):

    def setUp(self):
        super().setUp()
        self.iot = InformatieObjectTypeFactory.create()

        self.zender = {
            'organisatie': 'Maykin Media',
            'applicatie': 'Test',
            'administratie': 'Support',
            'gebruiker': 'john.doe@example.com',
        }
        self.ontvanger = settings.ZAAKMAGAZIJN_SYSTEEM

    def test_create(self):
        self._dms_client.geef_inhoud.return_value = ('doc 1', BytesIO())

        zaak = ZaakFactory.create(status_set__indicatie_laatst_gezette_status=JaNee.ja)
        client = self._get_client('OntvangAsynchroon')
        stuf_factory, zkn_factory, zds_factory = self._get_type_factories(client)
        today = date.today().strftime('%Y%m%d')

        response = client.service.maakZaakdocument_EdcLk01(
            parameters=stuf_factory['ParametersLk01'](
                indicatorOvername='V',
                mutatiesoort='T',
            ),
            stuurgegevens=stuf_factory['EDC-StuurgegevensLk01'](
                berichtcode='Lk01',
                entiteittype='EDC',
                zender=self.zender,
                ontvanger=self.ontvanger,
                referentienummer='1234',
                tijdstipBericht=stuf_datetime.now(),
            ),
            object=zkn_factory['MaakZaakdocument-EDC-kennisgeving'](**{
                'entiteittype': 'EDC',
                'verwerkingssoort': 'T',
                'identificatie': '12345ABC',
                'dct.omschrijving': self.iot.informatieobjecttypeomschrijving,
                'creatiedatum': today,
                'ontvangstdatum': today,
                'titel': 'To be Everywhere is to be Nowhere',
                'beschrijving': '2016 album',
                'formaat': 'CD',
                'taal': 'Engels',
                'versie': '1',
                'status': 'Gepubliceerd',
                'verzenddatum': today,
                'vertrouwelijkAanduiding': 'OPENBAAR',
                'auteur': 'Thrice',
                # 'link': ''
                'inhoud': stuf_factory.BinaireInhoud(
                    b'',
                    bestandsnaam='to_be_everywhere.flac',
                    contentType='audio/flac',
                ),
                # 'tijdvakGeldigheid': stuf_factory.tijdvakGeldigheid(
                #     beginGeldigheid=today,
                # ),
                # 'tijdstipRegistratie': '',
                # 'extraElementend': None,
                'isRelevantVoor': zkn_factory['EDCZAK-kennisgeving'](
                    entiteittype='EDCZAK',
                    verwerkingssoort='T',
                    gerelateerde=zkn_factory['ZAK-kerngegevensKennisgeving'](
                        entiteittype='ZAK',
                        verwerkingssoort='I',
                        identificatie=zaak.zaakidentificatie,
                        omschrijving=zaak.omschrijving,
                        # isVan=None
                    ),
                    # titel
                    # beschrijving
                    # registratiedatum
                    # stt.volgnummer
                    # stt.omschrijving
                    # sta.datumStatusGezet
                    # tijdvakRelatie
                    # tijdvakGeldigheid
                    # tijdstipRegistratie
                    # extraElementen
                )
            })
        )

        self.assertIsNotNone(response)
        self.assertEquals(EnkelvoudigInformatieObject.objects.count(), 1)
        zaakdocument = ZaakInformatieObject.objects.get()
        self.assertEquals(zaakdocument.zaak, zaak)
        self.assertIsNotNone(zaakdocument.informatieobject)

    def test_zs_dms_interaction(self):
        """
        Het ZS maakt gebruik van de CMIS-documentservices om de wijzigingen met
        het DMS te synchroniseren.

        Het ZS zorgt ervoor dat het document dat is aangeboden door de DSC
        wordt vastgelegd in het DMS. Hiervoor maakt het ZS gebruik van de
        CMIS-services die aangeboden worden door het DMS. Hierbij gelden de
        volgende eisen:

        * Het document wordt gerelateerd aan de juiste Zaakfolder (Zie 5.1)
        * Het document wordt opgeslagen als objecttype EDC (Zie 5.2)
        * Minimaal de vereiste metadata voor een EDC wordt vastgelegd in de
          daarvoor gedefinieerde objectproperties. In Tabel 3 is een mapping
          aangegeven tussen de StUF-ZKN-elementen en CMIS-objectproperties.
        """
        self._dms_client.geef_inhoud.return_value = ('doc 1', BytesIO())

        zaak = ZaakFactory.create(status_set__indicatie_laatst_gezette_status=JaNee.ja)
        client = self._get_client('OntvangAsynchroon')
        stuf_factory, zkn_factory, zds_factory = self._get_type_factories(client)
        today = date.today().strftime('%Y%m%d')

        response = client.service.maakZaakdocument_EdcLk01(
            parameters=stuf_factory['ParametersLk01'](
                indicatorOvername='V',
                mutatiesoort='T',
            ),
            stuurgegevens=stuf_factory['EDC-StuurgegevensLk01'](
                berichtcode='Lk01',
                entiteittype='EDC',
                zender=self.zender,
                ontvanger=self.ontvanger,
                referentienummer='1234',
                tijdstipBericht=stuf_datetime.now(),
            ),
            object=zkn_factory['MaakZaakdocument-EDC-kennisgeving'](**{
                'entiteittype': 'EDC',
                'verwerkingssoort': 'T',
                'identificatie': '12345ABC',
                'dct.omschrijving': self.iot.informatieobjecttypeomschrijving,
                'creatiedatum': today,
                'ontvangstdatum': today,
                'titel': 'To be Everywhere is to be Nowhere',
                'beschrijving': '2016 album',
                'formaat': 'CD',
                'taal': 'Engels',
                'versie': '1',
                'status': 'Gepubliceerd',
                'verzenddatum': today,
                'vertrouwelijkAanduiding': 'OPENBAAR',
                'auteur': 'Thrice',
                # 'link': ''
                'inhoud': stuf_factory.BinaireInhoud(
                    b'',
                    bestandsnaam='to_be_everywhere.flac',
                    contentType='audio/flac',
                ),
                # 'tijdvakGeldigheid': stuf_factory.tijdvakGeldigheid(
                #     beginGeldigheid=today,
                # ),
                # 'tijdstipRegistratie': '',
                # 'extraElementend': None,
                'isRelevantVoor': zkn_factory['EDCZAK-kennisgeving'](
                    entiteittype='EDCZAK',
                    verwerkingssoort='T',
                    gerelateerde=zkn_factory['ZAK-kerngegevensKennisgeving'](
                        entiteittype='ZAK',
                        verwerkingssoort='I',
                        identificatie=zaak.zaakidentificatie,
                        omschrijving=zaak.omschrijving,
                        # isVan=None
                    ),
                    # titel
                    # beschrijving
                    # registratiedatum
                    # stt.volgnummer
                    # stt.omschrijving
                    # sta.datumStatusGezet
                    # tijdvakRelatie
                    # tijdvakGeldigheid
                    # tijdstipRegistratie
                    # extraElementen
                )
            })
        )

        self.assertIsNotNone(response)
        # assert that the correct DMS client calls were made
        document = EnkelvoudigInformatieObject.objects.get()

        # the document should have been registered in the DMS
        self._service_dms_client.maak_zaakdocument.assert_called_once_with(
            document, filename='to_be_everywhere.flac', sender='john.doe@example.com')

        # the document should have been moved to the correct folder
        self._service_dms_client.relateer_aan_zaak.assert_called_once_with(document, zaak)

    def test_zs_dms_interaction2_no_inhoud(self):
        """
        Het ZS maakt gebruik van de CMIS-documentservices om de wijzigingen met
        het DMS te synchroniseren.

        Het ZS zorgt ervoor dat het document dat is aangeboden door de DSC
        wordt vastgelegd in het DMS. Hiervoor maakt het ZS gebruik van de
        CMIS-services die aangeboden worden door het DMS. Hierbij gelden de
        volgende eisen:

        * Het document wordt gerelateerd aan de juiste Zaakfolder (Zie 5.1)
        * Het document wordt opgeslagen als objecttype EDC (Zie 5.2)
        * Minimaal de vereiste metadata voor een EDC wordt vastgelegd in de
          daarvoor gedefinieerde objectproperties. In Tabel 3 is een mapping
          aangegeven tussen de StUF-ZKN-elementen en CMIS-objectproperties.
        """
        self._dms_client.geef_inhoud.return_value = ('doc 1', BytesIO())

        zaak = ZaakFactory.create(status_set__indicatie_laatst_gezette_status=JaNee.ja)
        client = self._get_client('OntvangAsynchroon')
        stuf_factory, zkn_factory, zds_factory = self._get_type_factories(client)
        today = date.today().strftime('%Y%m%d')

        response = client.service.maakZaakdocument_EdcLk01(
            parameters=stuf_factory['ParametersLk01'](
                indicatorOvername='V',
                mutatiesoort='T',
            ),
            stuurgegevens=stuf_factory['EDC-StuurgegevensLk01'](
                berichtcode='Lk01',
                entiteittype='EDC',
                zender=self.zender,
                ontvanger=self.ontvanger,
                referentienummer='1234',
                tijdstipBericht=stuf_datetime.now(),
            ),
            object=zkn_factory['MaakZaakdocument-EDC-kennisgeving'](**{
                'entiteittype': 'EDC',
                'verwerkingssoort': 'T',
                'identificatie': '12345ABC',
                'dct.omschrijving': self.iot.informatieobjecttypeomschrijving,
                'creatiedatum': today,
                'ontvangstdatum': today,
                'titel': 'To be Everywhere is to be Nowhere',
                'beschrijving': '2016 album',
                'formaat': 'CD',
                'taal': 'Engels',
                'versie': '1',
                'status': 'Gepubliceerd',
                'verzenddatum': today,
                'vertrouwelijkAanduiding': 'OPENBAAR',
                'auteur': 'Thrice',
                # 'link': ''
                # 'tijdvakGeldigheid': stuf_factory.tijdvakGeldigheid(
                #     beginGeldigheid=today,
                # ),
                # 'tijdstipRegistratie': '',
                # 'extraElementend': None,
                'isRelevantVoor': zkn_factory['EDCZAK-kennisgeving'](
                    entiteittype='EDCZAK',
                    verwerkingssoort='T',
                    gerelateerde=zkn_factory['ZAK-kerngegevensKennisgeving'](
                        entiteittype='ZAK',
                        verwerkingssoort='I',
                        identificatie=zaak.zaakidentificatie,
                        omschrijving=zaak.omschrijving,
                        # isVan=None
                    ),
                    # titel
                    # beschrijving
                    # registratiedatum
                    # stt.volgnummer
                    # stt.omschrijving
                    # sta.datumStatusGezet
                    # tijdvakRelatie
                    # tijdvakGeldigheid
                    # tijdstipRegistratie
                    # extraElementen
                )
            })
        )

        self.assertIsNotNone(response)
        # assert that the correct DMS client calls were made
        document = EnkelvoudigInformatieObject.objects.get()

        # the document should have been registered in the DMS
        self._service_dms_client.maak_zaakdocument.assert_called_once_with(
            document, filename=None, sender='john.doe@example.com')

        # the document should have been moved to the correct folder
        self._service_dms_client.relateer_aan_zaak.assert_called_once_with(document, zaak)


class STPmaakZaakDocument_EdcLk01Tests(DMSMockMixin, BaseTestPlatformTests):
    """
    Precondities:
    Scenario's creeerZaak (P) is succesvol uitgevoerd. Dit scenario maakt documenten
    bij zaken die gemaakt zijn in creeerZaak (P).
    """
    test_files_subfolder = 'stp_maakZaakdocument'
    porttype = 'OntvangAsynchroon'

    def setUp(self):
        super().setUp()
        self.zaak_1 = ZaakFactory.create(status_set__indicatie_laatst_gezette_status=JaNee.ja)
        self.zaak_3 = ZaakFactory.create(status_set__indicatie_laatst_gezette_status=JaNee.ja)
        self.zaak_5 = ZaakFactory.create(status_set__indicatie_laatst_gezette_status=JaNee.ja)

        self.edc_type = InformatieObjectTypeFactory.create(
            informatieobjecttypeomschrijving='omschrijving')
        self.edc_type2 = InformatieObjectTypeFactory.create(
            informatieobjecttypeomschrijving='Aanvraag burgerservicenummer behandelen'
        )

        self.context = {
            'gemeentecode': '',
            'referentienummer': self.genereerID(10),
            'datumVandaag': self.genereerdatum(),
            'datumEergisteren': self.genereerdatum(-2),

            'tijdstipRegistratie': self.genereerdatumtijd(),
            'zds_zaaktype_code': '12345678',
            'zds_zaaktype_omschrijving': 'Aanvraag burgerservicenummer behandelen',

            'maakzaakdocument_identificatie': '123456789ABC'
        }

    def _test_response(self, response, bestandsnaam=None):
        self.assertEquals(response.status_code, 200, response.content)

        response_root = etree.fromstring(response.content)
        response_berichtcode = response_root.xpath(
            '//stuf:stuurgegevens/stuf:berichtcode', namespaces=self.nsmap
        )[0].text
        self.assertEqual(response_berichtcode, BerichtcodeChoices.bv03, response.content)

        zio = ZaakInformatieObject.objects.get()
        self.assertEqual(zio.zaak, self.zaak_1)
        self.assertEqual(
            zio.informatieobject.informatieobjectidentificatie,
            '123456789ABC'
        )

        # the content should not have been set
        self._service_dms_client.zet_inhoud.assert_not_called()
        self._service_dms_client.maak_zaakdocument_met_inhoud.assert_not_called()

    def test_maakZaakDocument_EdcLk01_01(self):
        self._dms_client.geef_inhoud.return_value = ('doc 1', BytesIO())

        vraag = 'maakZaakdocument_EdcLk01_01.xml'
        self.context.update(
            creerzaak_identificatie=self.zaak_1.zaakidentificatie,
            creerzaak_omschrijving=self.zaak_1.omschrijving,
        )
        response = self._do_request(self.porttype, vraag, self.context)

        self._test_response(response)
        self._validate_response(response)

        # assert that a document was created
        zio = ZaakInformatieObject.objects.get()
        self._service_dms_client.maak_zaakdocument.assert_called_once_with(
            zio.informatieobject.enkelvoudiginformatieobject, filename='bestandsnaam', sender='STP')

    def test_maakZaakDocument_EdcLk01_03(self):
        self._dms_client.geef_inhoud.return_value = ('doc 1', BytesIO())
        vraag = 'maakZaakdocument_EdcLk01_03.xml'
        self.context.update(
            creerzaak_identificatie=self.zaak_1.zaakidentificatie,
            creerzaak_omschrijving=self.zaak_1.omschrijving,
        )
        response = self._do_request(self.porttype, vraag, self.context)

        self._test_response(response)
        self._validate_response(response)

        # assert that a document was created, even though <inhoud> is not present
        zio = ZaakInformatieObject.objects.get()
        self._service_dms_client.maak_zaakdocument.assert_called_once_with(
            zio.informatieobject.enkelvoudiginformatieobject, filename=None, sender='STP')

    def test_maakZaakDocument_EdcLk01_05(self):
        self._dms_client.geef_inhoud.return_value = ('doc 1', BytesIO())
        vraag = 'maakZaakdocument_EdcLk01_05.xml'
        self.context.update(
            creerzaak_identificatie=self.zaak_1.zaakidentificatie,
            creerzaak_omschrijving=self.zaak_1.omschrijving,
        )

        response = self._do_request(self.porttype, vraag, self.context)

        self._test_response(response)
        self._validate_response(response)

        # assert that a document was created, even though <inhoud> is not present
        zio = ZaakInformatieObject.objects.get()
        self._service_dms_client.maak_zaakdocument.assert_called_once_with(
            zio.informatieobject.enkelvoudiginformatieobject, filename=None, sender='STP')
