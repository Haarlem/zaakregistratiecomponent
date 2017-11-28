from lxml import etree
from mock import patch

from ...utils import stuf_datetime
from ..stuf.choices import BerichtcodeChoices
from .base import BaseSoapTests, BaseTestPlatformTests


class GenereerDocumentIdentificatie_Du02(BaseSoapTests):
    maxDiff = None
    antwoord_xpath = '/soap11env:Envelope/soap11env:Body/zds:genereerDocumentIdentificatie_Du02'

    def _do_simple_request(self, raw_response=False):
        client = self._get_client('VerwerkSynchroonVrijBericht')
        stuf_factory = client.type_factory('http://www.egem.nl/StUF/StUF0301')

        with client.options(raw_response=raw_response):
            return client.service.genereerDocumentIdentificatie_Di02(
                stuurgegevens=stuf_factory['Di02-Stuurgegevens-gdi'](
                    berichtcode='Di02',
                    referentienummer='123',
                    tijdstipBericht=stuf_datetime.now(),
                    functie='genereerDocumentIdentificatie'
                )
            )

    @patch('zaakmagazijn.api.services.genereer_document_identificatie.create_unique_id')
    def test_create(self, create_unique_id_mock):
        create_unique_id_mock.return_value = '0000aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'

        result = self._do_simple_request(raw_response=True)
        root = etree.fromstring(result.content)
        self._assert_xpath_results(root, self.antwoord_xpath, 1, namespaces=self.nsmap)

        expected = [
            'zds:stuurgegevens',
            'zds:stuurgegevens/stuf:berichtcode[text()="Du02"]',
            'zds:stuurgegevens/stuf:functie[text()="genereerDocumentidentificatie"]',
            'zds:document',
            'zds:document[@stuf:entiteittype="EDC"]',
            'zds:document[@stuf:functie="entiteit"]',
            'zds:document/zkn:identificatie[text()="0000aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"]',
        ]
        for expectation in expected:
            self._assert_xpath_results(self._get_body_root(root), expectation, 1, namespaces=self.nsmap)


class STPGenereerDocumentIdentificatie_Du02Tests(BaseTestPlatformTests):
    maxDiff = None
    test_files_subfolder = 'stp_genereerDocumentIdentificatie'
    porttype = 'VerwerkSynchroonVrijBericht'

    def _test_response(self, response):
        self.assertEquals(response.status_code, 200, response.content)

        response_root = etree.fromstring(response.content)
        response_berichtcode = response_root.xpath('//zds:stuurgegevens/stuf:berichtcode', namespaces=self.nsmap)[0].text
        self.assertEqual(response_berichtcode, BerichtcodeChoices.du02, response.content)

        response_functie = response_root.xpath('//zds:stuurgegevens/stuf:functie', namespaces=self.nsmap)[0].text
        self.assertEqual(response_functie, 'genereerDocumentidentificatie', response.content)

        response_identificatie = response_root.xpath('//zds:document/zkn:identificatie', namespaces=self.nsmap)[0].text
        self.assertTrue(len(response_identificatie) == 40)

    def test_create(self):
        vraag = 'genereerDocumentIdentificatie_Di02.xml'
        context = {}
        response = self._do_request(self.porttype, vraag, context)

        self._test_response(response)
        self._validate_response(response)
