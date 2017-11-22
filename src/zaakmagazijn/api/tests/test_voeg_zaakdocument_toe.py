import base64
import time
from datetime import date, datetime
from unittest import skipIf

from django.test import override_settings

from lxml import etree

from zaakmagazijn.cmis.client import CMISDMSClient
from zaakmagazijn.cmis.tests.test_cmis_client import DMSMixin
from zaakmagazijn.utils import stuf_datetime
from zaakmagazijn.utils.tests import on_jenkins, should_skip_cmis_tests

from ...rgbz.choices import JaNee
from ...rgbz.models import EnkelvoudigInformatieObject, ZaakInformatieObject
from ...rgbz.tests.factory_models import (
    InformatieObjectTypeFactory, StatusFactory, ZaakFactory
)
from ..stuf.choices import BerichtcodeChoices
from .base import BaseSoapTests, BaseTestPlatformTests


class DMSMockMixin:
    extra_client_mocks = [
        'zaakmagazijn.cmis.fields.dms_client',
        'zaakmagazijn.api.services.voeg_zaakdocument_toe.dms_client',
    ]

    @property
    def _dms_client(self):
        return self._extra_mocked_dms_clients[0]

    @property
    def _service_dms_client(self):
        return self._extra_mocked_dms_clients[1]


class voegZaakdocumentToe_EdcLk01Tests(DMSMockMixin, BaseSoapTests):

    def setUp(self):
        super().setUp()
        self.iot = InformatieObjectTypeFactory.create()
        self.zender = {
            'organisatie': 'Maykin Media',
            'applicatie': 'Test',
            'administratie': 'Support',
            'gebruiker': 'john.doe@example.com',
        }
        self.ontvanger = {
            'organisatie': 'Maykin Media',
            'applicatie': 'TTA',
            'administratie': 'Support',
            'gebruiker': 'john.doe@example.com',
        }

    def test_create(self):
        zaak = ZaakFactory.create(status_set__indicatie_laatst_gezette_status=JaNee.ja)
        client = self._get_client('OntvangAsynchroon')
        stuf_factory, zkn_factory, zds_factory = self._get_type_factories(client)
        today = date.today().strftime('%Y%m%d')

        stuurgegevens = stuf_factory.EDC_StuurgegevensVoegZaakdocumentToeLk01(
            berichtcode='Lk01',
            entiteittype='EDC',
            zender=self.zender,
            ontvanger=self.ontvanger,
            referentienummer='1234',
            tijdstipBericht=stuf_datetime.now(),
        )

        # Note that the content is base64 encoded twice, and thus increases in size
        # when encoded. suppose we want to send 100 bytes, this will be encoded
        # as 100 * (8/6) * (8/6) = ~178 bytes.
        big_ass_file = b'a' * 22 * 1024**2 # 22MB
        inhoud = stuf_factory.BinaireInhoud(
            base64.b64encode(big_ass_file),
            bestandsnaam='to_be_everywhere.flac',
            contentType='audio/flac',
        )

        response = client.service.voegZaakdocumentToe_EdcLk01(
            parameters=stuf_factory.EDC_ParametersVoegZaakdocumentToeLk01(
                indicatorOvername='V',
                mutatiesoort='T',
            ),
            stuurgegevens=stuurgegevens,
            object=zkn_factory.EDC_VoegZaakdocumentToe(**{
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
                'inhoud': inhoud,
                # 'tijdvakGeldigheid': stuf_factory.tijdvakGeldigheid(
                #     beginGeldigheid=today,
                # ),
                # 'tijdstipRegistratie': '',
                # 'extraElementend': None,
                'isRelevantVoor': [zkn_factory.EDCZAK_VoegZaakdocumentToe(
                    entiteittype='EDCZAK',
                    verwerkingssoort='T',
                    gerelateerde=zkn_factory.ZAK_VoegZaakdocumentToe(
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
                )]
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
        zaak = ZaakFactory.create(status_set__indicatie_laatst_gezette_status=JaNee.ja)
        client = self._get_client('OntvangAsynchroon')
        stuf_factory, zkn_factory, zds_factory = self._get_type_factories(client)
        today = date.today().strftime('%Y%m%d')

        stuurgegevens = stuf_factory.EDC_StuurgegevensVoegZaakdocumentToeLk01(
            berichtcode='Lk01',
            entiteittype='EDC',
            zender=self.zender,
            ontvanger=self.ontvanger,
            referentienummer='1234',
            tijdstipBericht=stuf_datetime.now(),
        )
        inhoud = stuf_factory.BinaireInhoud(
            base64.b64encode(b'helloworld'),
            bestandsnaam='to_be_everywhere.flac',
            contentType='audio/flac',
        )

        response = client.service.voegZaakdocumentToe_EdcLk01(
            parameters=stuf_factory.EDC_ParametersVoegZaakdocumentToeLk01(
                indicatorOvername='V',
                mutatiesoort='T',
            ),
            stuurgegevens=stuurgegevens,
            object=zkn_factory.EDC_VoegZaakdocumentToe(**{
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
                'inhoud': inhoud,
                # 'tijdvakGeldigheid': stuf_factory.tijdvakGeldigheid(
                #     beginGeldigheid=today,
                # ),
                # 'tijdstipRegistratie': '',
                # 'extraElementend': None,
                'isRelevantVoor': zkn_factory.EDCZAK_VoegZaakdocumentToe(
                    entiteittype='EDCZAK',
                    verwerkingssoort='T',
                    gerelateerde=zkn_factory.ZAK_VoegZaakdocumentToe(
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
        self._dms_client.maak_zaakdocument.assert_called_once_with(document, filename='to_be_everywhere.flac')

        # the content should have been set
        self.assertEqual(self._dms_client.zet_inhoud.call_count, 1)
        self.assertEqual(
            self._dms_client.zet_inhoud.call_args[0][0],
            document
        )

        stream = self._dms_client.zet_inhoud.call_args[0][1]
        stream.seek(0)
        self.assertEqual(stream.read(), b'helloworld')
        self.assertEqual(
            self._dms_client.zet_inhoud.call_args[0][2],
            'audio/flac'
        )

        # the document should have been moved to the correct folder
        self._service_dms_client.relateer_aan_zaak.assert_called_once_with(document, zaak)


class STPvoegZaakdocumentToe_EdcLk01Tests(DMSMockMixin, BaseTestPlatformTests):
    """
    Precondities:

    Scenario's creeerZaak (P) is succesvol uitgevoerd. Dit scenario voegt
    documenten toe aan zaken die gemaakt zijn in creeerZaak (P).
    """
    maxDiff = None
    test_files_subfolder = 'stp_voegZaakdocumentToe'
    porttype = 'OntvangAsynchroon'

    def setUp(self):
        super().setUp()

        self.zaak = ZaakFactory.create(status_set__indicatie_laatst_gezette_status=JaNee.ja)
        self.edc_type = InformatieObjectTypeFactory.create(informatieobjecttypeomschrijving='omschrijving')

        self.context = {
            'zaak': self.zaak,
            'gemeentecode': '',
            'referentienummer': self.genereerID(10),
            'datumVandaag': self.genereerdatum(),
            'datumEergisteren': self.genereerdatum(-2),
            'tijdstipRegistratie': self.genereerdatumtijd(),

            'zds_zaaktype_code': '12345678',
            'zds_zaaktype_omschrijving': 'Aanvraag burgerservicenummer behandelen',
        }

    def _test_response(self, response):
        self.assertEquals(response.status_code, 200, response.content)

        response_root = etree.fromstring(response.content)
        response_berichtcode = response_root.xpath(
            '//stuf:stuurgegevens/stuf:berichtcode', namespaces=self.nsmap
        )[0].text
        self.assertEqual(response_berichtcode, BerichtcodeChoices.bv03, response.content)

        # assert that a document was created
        zio = ZaakInformatieObject.objects.get()
        self._dms_client.maak_zaakdocument.assert_called_once_with(
            zio.informatieobject.enkelvoudiginformatieobject, filename='bestandsnaam'
        )

        # assert that inhoud was set
        self.assertEqual(self._dms_client.zet_inhoud.call_count, 1)
        bytes = self._dms_client.zet_inhoud.call_args[0][1].getvalue()

        # it's double encoded
        expected_string = 'UjBsR09EbGhjZ0dTQUxNQUFBUUNBRU1tQ1p0dU1GUXhEUzhi'
        expected_bytes = base64.b64decode(base64.b64decode(expected_string))

        self.assertEqual(bytes, expected_bytes)

    def test_voegZaakdocumentToe_EdcLk01_01(self):
        """
        1. Verzoek voegZaakdocumentToe_EdcLk01: STP -> ZS
        2. Antwoord Bv03Bericht: ZS -> STP
        """
        vraag = 'voegZaakdocumentToe_EdcLk01_01.xml'
        self.context.update(
            voegzaakdocumenttoe_identificatie_1=self.genereerID(10),
            creerzaak_identificatie_7=self.zaak.zaakidentificatie,
        )
        response = self._do_request(self.porttype, vraag, self.context)

        self._test_response(response)

    def test_voegZaakdocumentToe_EdcLk01_03(self):
        """
        3. Verzoek voegZaakdocumentToe_EdcLk01: STP -> ZS
        4. Antwoord Bv03Bericht: ZS -> STP
        """
        vraag = 'voegZaakdocumentToe_EdcLk01_03.xml'
        self.context.update(
            voegzaakdocumenttoe_identificatie_3=self.genereerID(10),
            creerzaak_identificatie_7=self.zaak.zaakidentificatie,
        )
        response = self._do_request(self.porttype, vraag, self.context)

        self._test_response(response)

    def test_voegZaakdocumentToe_EdcLk01_05(self):
        """
        5. Verzoek voegZaakdocumentToe_EdcLk01: STP -> ZS
        6. Antwoord Bv03Bericht: ZS -> STP
        """
        vraag = 'voegZaakdocumentToe_EdcLk01_05.xml'
        self.context.update(
            voegzaakdocumenttoe_identificatie_5=self.genereerID(10),
            creerzaak_identificatie_9=self.zaak.zaakidentificatie,
        )
        response = self._do_request(self.porttype, vraag, self.context)

        self._test_response(response)

    def test_voegZaakdocumentToe_EdcLk01_07(self):
        """
        7. Verzoek voegZaakdocumentToe_EdcLk01: STP -> ZS
        8. Antwoord Bv03Bericht: ZS -> STP
        """
        vraag = 'voegZaakdocumentToe_EdcLk01_07.xml'
        self.context.update(
            voegzaakdocumenttoe_identificatie_7=self.genereerID(10),
            creerzaak_identificatie_9=self.zaak.zaakidentificatie,
        )
        response = self._do_request(self.porttype, vraag, self.context)

        self._test_response(response)

    def test_voegZaakdocumentToe_EdcLk01_09(self):
        """
        9. Verzoek voegZaakdocumentToe_EdcLk01: STP -> ZS
        10. Antwoord Bv03Bericht: ZS -> STP
        """
        vraag = 'voegZaakdocumentToe_EdcLk01_09.xml'
        self.context.update(
            voegzaakdocumenttoe_identificatie_9=self.genereerID(10),
            creerzaak_identificatie_9=self.zaak.zaakidentificatie,
        )
        response = self._do_request(self.porttype, vraag, self.context)

        self._test_response(response)


class voegZaakdocumentToe_EdcLk01RegressionTests(DMSMixin, BaseTestPlatformTests):
    maxDiff = None
    test_files_subfolder = 'maykin_voegZaakdocumentToe'
    porttype = 'OntvangAsynchroon'
    disable_mocks = True

    @skipIf(on_jenkins() or should_skip_cmis_tests(), "Skipped while there's not Alfresco running on Jenkins")
    @override_settings(CMIS_UPLOAD_TO='zaakmagazijn.cmis.utils.upload_to_date_based')
    def test_index_error_list_index_out_of_range(self):
        """
        See: https://taiga.maykinmedia.nl/project/haarlem-zaakmagazijn/issue/278
        """
        zaak = ZaakFactory.create(
            zaakidentificatie='0392f576ff4a-af98-4669-8fc6-625c7190aa9d',
            status_set__indicatie_laatst_gezette_status=JaNee.ja
        )
        zaak.zaakkenmerk_set.all().delete()
        edc_type = InformatieObjectTypeFactory.create(informatieobjecttypeomschrijving='test')

        vraag = 'voegZaakdocumentToe_EdcLk01_taiga278.xml'
        response = self._do_request(self.porttype, vraag)

        self.assertEquals(response.status_code, 200, response.content)


class voegZaakdocumentToe_EdcLk01EndToEndTests(BaseSoapTests):
    maxDiff = None
    test_files_subfolder = 'maykin_voegZaakdocumentToe'
    porttype = 'OntvangAsynchroon'
    disable_mocks = True

    def setUp(self):
        time.sleep(2)
        self.client = CMISDMSClient()
        self.addCleanup(self._removeTree)
        # Create zaak
        self.zaak = ZaakFactory.create(
            zaakidentificatie='123456789',
            einddatum=None,
        )
        StatusFactory.create(zaak=self.zaak, indicatie_laatst_gezette_status=JaNee.ja)

        # Create zaak folder
        self.client.creeer_zaakfolder(self.zaak)

    def _removeTree(self):
        """
        Remove the created Zaak root folder and all children from the DMS.
        """
        try:
            root_folder = self.client._repo.getObjectByPath('/Zaken')
        except ObjectNotFoundException:
            return
        root_folder.deleteTree()

    @skipIf(on_jenkins() or should_skip_cmis_tests(), "Skipped while there's not Alfresco running on Jenkins")
    def test_upload_small_file(self):
        """
        See: https://taiga.maykinmedia.nl/project/haarlem-zaakmagazijn/issue/387
        """

        self.iot = InformatieObjectTypeFactory.create()
        self.zender = {
            'organisatie': 'Maykin Media',
            'applicatie': 'Test',
            'administratie': 'Support',
            'gebruiker': 'john.doe@example.com',
        }
        self.ontvanger = {
            'organisatie': 'Maykin Media',
            'applicatie': 'TTA',
            'administratie': 'Support',
            'gebruiker': 'john.doe@example.com',
        }
        client = self._get_client('OntvangAsynchroon')

        stuf_factory, zkn_factory, zds_factory = self._get_type_factories(client)
        today = date.today().strftime('%Y%m%d')

        stuurgegevens = stuf_factory.EDC_StuurgegevensVoegZaakdocumentToeLk01(
            berichtcode='Lk01',
            entiteittype='EDC',
            zender=self.zender,
            ontvanger=self.ontvanger,
            referentienummer='1234',
            tijdstipBericht=stuf_datetime.now(),
        )

        big_ass_file = b'a' * 1 * 1024**2 # 1MB
        name = '{}.flac'.format(int(time.time()))

        inhoud = stuf_factory.BinaireInhoud(
            base64.b64encode(big_ass_file),
            bestandsnaam=name,
            contentType='audio/flac',
        )
        response = client.service.voegZaakdocumentToe_EdcLk01(
            parameters=stuf_factory.EDC_ParametersVoegZaakdocumentToeLk01(
                indicatorOvername='V',
                mutatiesoort='T',
            ),
            stuurgegevens=stuurgegevens,
            object=zkn_factory.EDC_VoegZaakdocumentToe(**{
                'entiteittype': 'EDC',
                'verwerkingssoort': 'T',
                'identificatie': '12345ABC{}'.format(int(time.time())),
                'dct.omschrijving': self.iot.informatieobjecttypeomschrijving,
                'creatiedatum': today,
                'ontvangstdatum': today,
                'titel': 'To be Everywhere {}'.format(int(time.time())),
                'beschrijving': '2016 album',
                'formaat': 'CD',
                'taal': 'Engels',
                'versie': '1',
                'status': 'Gepubliceerd',
                'verzenddatum': today,
                'vertrouwelijkAanduiding': 'OPENBAAR',
                'auteur': 'Thrice',
                # 'link': ''
                'inhoud': inhoud,
                # 'tijdvakGeldigheid': stuf_factory.tijdvakGeldigheid(
                #     beginGeldigheid=today,
                # ),
                # 'tijdstipRegistratie': '',
                # 'extraElementend': None,
                'isRelevantVoor': [zkn_factory.EDCZAK_VoegZaakdocumentToe(
                    entiteittype='EDCZAK',
                    verwerkingssoort='T',
                    gerelateerde=zkn_factory.ZAK_VoegZaakdocumentToe(
                        entiteittype='ZAK',
                        verwerkingssoort='I',
                        identificatie=self.zaak.zaakidentificatie,
                        omschrijving=self.zaak.omschrijving,
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
                )]
            })
        )

    @skipIf(on_jenkins() or should_skip_cmis_tests(), "Skipped while there's not Alfresco running on Jenkins")
    def test_upload_large_file(self):
        """
        See: https://taiga.maykinmedia.nl/project/haarlem-zaakmagazijn/issue/387
        """

        self.iot = InformatieObjectTypeFactory.create()
        self.zender = {
            'organisatie': 'Maykin Media',
            'applicatie': 'Test',
            'administratie': 'Support',
            'gebruiker': 'john.doe@example.com',
        }
        self.ontvanger = {
            'organisatie': 'Maykin Media',
            'applicatie': 'TTA',
            'administratie': 'Support',
            'gebruiker': 'john.doe@example.com',
        }
        client = self._get_client('OntvangAsynchroon')

        stuf_factory, zkn_factory, zds_factory = self._get_type_factories(client)
        today = date.today().strftime('%Y%m%d')

        stuurgegevens = stuf_factory.EDC_StuurgegevensVoegZaakdocumentToeLk01(
            berichtcode='Lk01',
            entiteittype='EDC',
            zender=self.zender,
            ontvanger=self.ontvanger,
            referentienummer='1234',
            tijdstipBericht=stuf_datetime.now(),
        )

        # Note that the content is base64 encoded twice, and thus increases in size
        # when encoded.
        big_ass_file = b'a' * 3 * 1024**2 # 22MB
        name = '{}.flac'.format(int(time.time()))

        inhoud = stuf_factory.BinaireInhoud(
            base64.b64encode(big_ass_file),
            bestandsnaam=name,
            contentType='audio/flac',
        )
        response = client.service.voegZaakdocumentToe_EdcLk01(
            parameters=stuf_factory.EDC_ParametersVoegZaakdocumentToeLk01(
                indicatorOvername='V',
                mutatiesoort='T',
            ),
            stuurgegevens=stuurgegevens,
            object=zkn_factory.EDC_VoegZaakdocumentToe(**{
                'entiteittype': 'EDC',
                'verwerkingssoort': 'T',
                'identificatie': '12345ABC{}'.format(int(time.time())),
                'dct.omschrijving': self.iot.informatieobjecttypeomschrijving,
                'creatiedatum': today,
                'ontvangstdatum': today,
                'titel': 'To be Everywhere {}'.format(int(time.time())),
                'beschrijving': '2016 album',
                'formaat': 'CD',
                'taal': 'Engels',
                'versie': '1',
                'status': 'Gepubliceerd',
                'verzenddatum': today,
                'vertrouwelijkAanduiding': 'OPENBAAR',
                'auteur': 'Thrice',
                # 'link': ''
                'inhoud': inhoud,
                # 'tijdvakGeldigheid': stuf_factory.tijdvakGeldigheid(
                #     beginGeldigheid=today,
                # ),
                # 'tijdstipRegistratie': '',
                # 'extraElementend': None,
                'isRelevantVoor': [zkn_factory.EDCZAK_VoegZaakdocumentToe(
                    entiteittype='EDCZAK',
                    verwerkingssoort='T',
                    gerelateerde=zkn_factory.ZAK_VoegZaakdocumentToe(
                        entiteittype='ZAK',
                        verwerkingssoort='I',
                        identificatie=self.zaak.zaakidentificatie,
                        omschrijving=self.zaak.omschrijving,
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
                )]
            })
        )
