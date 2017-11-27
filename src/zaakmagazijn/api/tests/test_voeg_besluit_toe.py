import time

from lxml import etree

from zaakmagazijn.utils import stuf_datetime

from ...rgbz.choices import JaNee
from ...rgbz.tests.factory_models import (
    Besluit, BesluitTypeFactory, StatusFactory, ZaakInformatieObjectFactory
)
from ..stuf.choices import BerichtcodeChoices
from .base import BaseSoapTests, BaseTestPlatformTests


class voegBesluitToe_Di01Tests(BaseSoapTests):
    def test_create(self):
        client = self._get_client('OntvangAsynchroon')
        stuf_factory, zkn_factory, zds_factory = self._get_type_factories(client)

        status = StatusFactory.create(indicatie_laatst_gezette_status=JaNee.ja)
        zaak = status.zaak
        zio = ZaakInformatieObjectFactory.create(zaak=zaak, status=status)
        edc = zio.informatieobject
        bst = BesluitTypeFactory.create(besluittypeomschrijving='omschrijving')

        today = time.strftime('%Y%m%d')

        self.assertEquals(Besluit.objects.all().count(), 0)

        zender = {
            'organisatie': 'Maykin Media',
            'applicatie': 'Test',
            'administratie': 'Support',
            'gebruiker': 'john.doe@example.com',
        }
        ontvanger = {
            'organisatie': 'Maykin Media',
            'applicatie': 'TTA',
            'administratie': 'Support',
            'gebruiker': 'john.doe@example.com',
        }

        response = client.service.voegBesluitToe_Di01(
            stuurgegevens=stuf_factory['Di01-Stuurgegevens-vbt'](
                berichtcode='Di01',
                zender=zender,
                ontvanger=ontvanger,
                referentienummer='1234',
                tijdstipBericht=stuf_datetime.now(),
                functie='voegBesluitToe',
            ),
            object=zkn_factory['VoegBesluitToe_object'](
                besluit=zkn_factory['VoegBesluitToe-BSL-kennisgeving'](**{
                    'identificatie': '12345ABC',
                    'bst.omschrijving': bst.besluittypeomschrijving,
                    'datumBeslissing': today,
                    'ingangsdatumWerking': today,
                    'tijdvakGeldigheid': stuf_factory.TijdvakGeldigheid(
                        beginGeldigheid=today,
                    ),
                    'isVastgelegdIn': zkn_factory['VoegBesluitToe-BSLEDC-kennisgeving'](
                        gerelateerde=zkn_factory['VoegBesluitToe-EDC-kerngegevensKennisgeving'](
                            identificatie=edc.informatieobjectidentificatie
                        )
                    )
                }),
                zaak=zkn_factory['VoegBesluitToe_ZAK-kerngegevensKennisgeving'](
                    identificatie=zaak.zaakidentificatie,
                )
            )
        )
        self.assertEquals(zaak.besluit_set.count(), 1)

        besluit = zaak.besluit_set.get()
        self.assertEquals(besluit.besluitidentificatie, '12345ABC')
        self.assertEquals(besluit.ingangsdatum, today)
        self.assertEquals(besluit.besluittype, bst)
        self.assertEquals(besluit.informatieobject.get(), edc.informatieobject_ptr)


class STPvoegBesluitToe_Di01Tests(BaseTestPlatformTests):
    """
    Precondities:
    Scenario's creeerZaak (P) en voegZaakdocumentToe (P) zijn succesvol uitgevoerd.
    Dit scenario voegt besluiten toe aan zaken die gemaakt zijn in creeerZaak (P) met documenten die zijn toegevoegd in voegZaakdocumentToe (P).
    """
    maxDiff = None
    test_files_subfolder = 'stp_voegBesluitToe'
    porttype = 'OntvangAsynchroon'

    def setUp(self):
        super().setUp()

        self.status = StatusFactory.create(indicatie_laatst_gezette_status=JaNee.ja)
        self.zaak = self.status.zaak

        self.context = {
            'gemeentecode': '',
            'referentienummer': self.genereerID(10),
            'datumVandaag': self.genereerdatum(),
            'datumEergisteren': self.genereerdatum(-2),
            'tijdstipRegistratie': self.genereerdatumtijd(),
        }

    def _test_response(self, response):
        self.assertEquals(response.status_code, 200, response.content)

        response_root = etree.fromstring(response.content)
        response_berichtcode = response_root.xpath('//stuf:stuurgegevens/stuf:berichtcode', namespaces=self.nsmap)[0].text
        self.assertEqual(response_berichtcode, BerichtcodeChoices.bv03, response.content)

        self.assertEqual(self.zaak.besluit_set.count(), 1)

    def test_voegBesluitToe_Di01_01(self):
        """
        1. Verzoek voegBesluitToe_Di01: STP -> ZS
        2. Antwoord Bv03Bericht: ZS -> STP
        """
        bst = BesluitTypeFactory.create(besluittypeomschrijving=None)
        besluit_identificatie = self.genereerID(10)

        vraag = 'voegBesluitToe_Di01_01.xml'
        self.context.update(
            genereerbesluitident_identificatie_2=besluit_identificatie,
            creerzaak_identificatie_7=self.zaak.zaakidentificatie,
        )
        response = self._do_request(self.porttype, vraag, self.context)

        self._test_response(response)

        besluit = self.zaak.besluit_set.get()
        self.assertEquals(besluit.besluitidentificatie, besluit_identificatie)
        self.assertEquals(besluit.besluittype, bst)
        self.assertEquals(besluit.informatieobject.count(), 0)

    def test_voegBesluitToe_Di01_03(self):
        """
        3. Verzoek voegBesluitToe_Di01: STP -> ZS
        4. Antwoord Bv03Bericht: ZS -> STP
        """
        bst = BesluitTypeFactory.create(besluittypeomschrijving='omschrijving')
        besluit_identificatie = self.genereerID(10)

        zio_1 = ZaakInformatieObjectFactory.create(zaak=self.zaak, status=self.status)
        edc_1 = zio_1.informatieobject

        zio_2 = ZaakInformatieObjectFactory.create(zaak=self.zaak, status=self.status)
        edc_2 = zio_2.informatieobject

        vraag = 'voegBesluitToe_Di01_03.xml'
        self.context.update(
            voegbesluittoe_identificatie_3=besluit_identificatie,
            voegzaakdocumenttoe_identificatie_1=edc_1.informatieobjectidentificatie,
            voegzaakdocumenttoe_identificatie_3=edc_2.informatieobjectidentificatie,
            creerzaak_identificatie_7=self.zaak.zaakidentificatie,
        )
        response = self._do_request(self.porttype, vraag, self.context)

        self._test_response(response)

        besluit = self.zaak.besluit_set.get()
        self.assertEquals(besluit.besluitidentificatie, besluit_identificatie)
        self.assertEquals(besluit.besluittype, bst)
        self.assertEquals(besluit.informatieobject.count(), 2)

    def test_voegBesluitToe_Di01_05(self):
        """
        5. Verzoek voegBesluitToe_Di01: STP -> ZS
        6. Antwoord Bv03Bericht: ZS -> STP
        """
        bst = BesluitTypeFactory.create(besluittypeomschrijving=None)
        besluit_identificatie = self.genereerID(10)

        zio = ZaakInformatieObjectFactory.create(zaak=self.zaak, status=self.status)
        edc = zio.informatieobject

        vraag = 'voegBesluitToe_Di01_05.xml'
        self.context.update(
            voegzaakdocumenttoe_identificatie_1=edc.informatieobjectidentificatie,
            creerzaak_identificatie_7=self.zaak.zaakidentificatie,
            voegbesluittoe_identificatie_5=besluit_identificatie,
        )
        response = self._do_request(self.porttype, vraag, self.context)

        self._test_response(response)

        besluit = self.zaak.besluit_set.get()
        self.assertEquals(besluit.besluitidentificatie, besluit_identificatie)
        self.assertEquals(besluit.besluittype, bst)
        self.assertEquals(besluit.informatieobject.count(), 1)

    def test_voegBesluitToe_Di01_07(self):
        """
        7. Verzoek voegBesluitToe_Di01: STP -> ZS
        8. Antwoord Bv03Bericht: ZS -> STP
        """
        bst = BesluitTypeFactory.create(besluittypeomschrijving=None)
        besluit_identificatie = self.genereerID(10)

        zio_1 = ZaakInformatieObjectFactory.create(zaak=self.zaak, status=self.status)
        edc_1 = zio_1.informatieobject

        zio_2 = ZaakInformatieObjectFactory.create(zaak=self.zaak, status=self.status)
        edc_2 = zio_2.informatieobject

        vraag = 'voegBesluitToe_Di01_07.xml'
        self.context.update(
            voegzaakdocumenttoe_identificatie_1=edc_1.informatieobjectidentificatie,
            voegbesluittoe_identificatie_7=besluit_identificatie,
            voegzaakdocumenttoe_identificatie_3=edc_2.informatieobjectidentificatie,
            creerzaak_identificatie_7=self.zaak.zaakidentificatie,
        )
        response = self._do_request(self.porttype, vraag, self.context)

        self._test_response(response)

        besluit = self.zaak.besluit_set.get()
        self.assertEquals(besluit.besluitidentificatie, besluit_identificatie)
        self.assertEquals(besluit.besluittype, bst)
        self.assertEquals(besluit.informatieobject.count(), 2)

    def test_voegBesluitToe_Di01_09(self):
        """
        9. Verzoek voegBesluitToe_Di01: STP -> ZS
        10. Antwoord Bv03Bericht: ZS -> STP
        """
        bst = BesluitTypeFactory.create(besluittypeomschrijving=None)
        besluit_identificatie = self.genereerID(10)

        vraag = 'voegBesluitToe_Di01_09.xml'
        self.context.update(
            voegbesluittoe_identificatie_9=besluit_identificatie,
            creerzaak_identificatie_7=self.zaak.zaakidentificatie,
        )
        response = self._do_request(self.porttype, vraag, self.context)

        self._test_response(response)

        besluit = self.zaak.besluit_set.get()
        self.assertEquals(besluit.besluitidentificatie, besluit_identificatie)
        self.assertEquals(besluit.besluittype, bst)
        self.assertEquals(besluit.informatieobject.count(), 0)
