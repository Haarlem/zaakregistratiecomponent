from io import BytesIO

from lxml import etree

from zaakmagazijn.api.stuf.choices import BerichtcodeChoices
from zaakmagazijn.api.tests.base import BaseTestPlatformTests
from zaakmagazijn.rgbz.choices import JaNee
from zaakmagazijn.rgbz.tests.factory_models import (
    EnkelvoudigInformatieObjectFactory, ZaakFactory,
    ZaakInformatieObjectFactory
)

from .test_geef_zaakdocument_lezen import DMSMockMixin


class STPgeefZaakdocumentlezen_EdcLv01Tests(DMSMockMixin, BaseTestPlatformTests):
    """
    Precondities:
    Scenario's voegZaakdocumentToe (P), maakZaakdocument (P) en updateZaakdocument (P) zijn succesvol uitgevoerd.

    Dit scenario bevraagt documenten die in scenario's voegZaakdocumentToe (P) en maakZaakdocument (P)
    zijn toegevoegd en (deels) in scenario updateZaakdocument (P) zijn gewijzigd.
    """
    porttype = 'Beantwoordvraag'
    maxDiff = None
    test_files_subfolder = 'stp_geefZaakdocumentlezen'

    def setUp(self):
        super().setUp()

        self._dms_client.geef_inhoud.return_value = ('doc 1', BytesIO())

        self.document = EnkelvoudigInformatieObjectFactory.create()
        self.zaak = ZaakFactory.create(status_set__indicatie_laatst_gezette_status=JaNee.ja)
        ZaakInformatieObjectFactory.create(zaak=self.zaak, informatieobject=self.document)

    def _test_response(self, response):
        self.assertEquals(response.status_code, 200, response.content)

        response_root = etree.fromstring(response.content)
        response_berichtcode = response_root.xpath(
            '//zkn:stuurgegevens/stuf:berichtcode',
            namespaces=self.nsmap
        )[0].text
        self.assertEqual(response_berichtcode, BerichtcodeChoices.la01, response.content)

        response_object_element = response_root.xpath('//zkn:antwoord/zkn:object', namespaces=self.nsmap)[0]
        response_edc_identificatie = response_object_element.xpath('zkn:identificatie', namespaces=self.nsmap)[0].text

        self.assertEqual(response_edc_identificatie, self.document.identificatie)

    def test_geefLijstZaakdocumentenlezen_EdcLv01_01(self):
        vraag = 'geefZaakdocumentLezen_EdcLv01_01.xml'
        context = {
            'voegzaakdocumenttoe_identificatie_1': self.document.identificatie,
        }
        response = self._do_request(self.porttype, vraag, context)

        self._test_response(response)

    def test_geefLijstZaakdocumentenlezen_EdcLv01_03(self):
        vraag = 'geefZaakdocumentLezen_EdcLv01_03.xml'
        context = {
            'voegzaakdocumenttoe_identificatie_1': self.document.identificatie,
        }
        response = self._do_request(self.porttype, vraag, context)

        self._test_response(response)

    def test_geefLijstZaakdocumentenlezen_EdcLv01_05(self):
        vraag = 'geefZaakdocumentLezen_EdcLv01_05.xml'
        context = {
            'voegzaakdocumenttoe_identificatie_1': self.document.identificatie,
        }
        response = self._do_request(self.porttype, vraag, context)

        self._test_response(response)

    def test_geefLijstZaakdocumentenlezen_EdcLv01_07(self):
        vraag = 'geefZaakdocumentLezen_EdcLv01_07.xml'
        context = {
            'voegzaakdocumenttoe_identificatie_1': self.document.identificatie,
        }
        response = self._do_request(self.porttype, vraag, context)

        self._test_response(response)

    def test_geefLijstZaakdocumentenlezen_EdcLv01_09(self):
        vraag = 'geefZaakdocumentLezen_EdcLv01_09.xml'
        context = {
            'voegzaakdocumenttoe_identificatie_3': self.document.identificatie,
        }
        response = self._do_request(self.porttype, vraag, context)

        self._test_response(response)

    def test_geefLijstZaakdocumentenlezen_EdcLv01_11(self):
        vraag = 'geefZaakdocumentLezen_EdcLv01_11.xml'
        context = {
            'maakzaakdocument_identificatie_1': self.document.identificatie,
        }
        response = self._do_request(self.porttype, vraag, context)

        self._test_response(response)

    def test_geefLijstZaakdocumentenlezen_EdcLv01_13(self):
        vraag = 'geefZaakdocumentLezen_EdcLv01_13.xml'
        context = {
            'voegzaakdocumenttoe_identificatie_5': self.document.identificatie,
        }

        response = self._do_request(self.porttype, vraag, context)

        self._test_response(response)
