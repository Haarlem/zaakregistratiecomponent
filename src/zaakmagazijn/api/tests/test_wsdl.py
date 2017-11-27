from django.test.utils import override_settings

import requests
from lxml import etree

from .base import BaseSoapTests


class WSDLTests(BaseSoapTests):
    def test_appinfo(self):
        """
        Make sure we're being fed the KING wsdl for beantwoordvraag.
        """
        appinfo = [
            b'<StUF:onderdeel>http://www.stufstandaarden.nl/koppelvlak/zds0120</StUF:onderdeel>',
            b'<StUF:patch>zds120_20170401</StUF:patch>',
            b'<StUF:patchdatum>20170401</StUF:patchdatum>',
            b'<StUF:schemaversie>1</StUF:schemaversie>',
        ]
        response = requests.get('{}/BeantwoordVraag/?WSDL'.format(self.live_server_url, ))
        for expectation in appinfo:
            self.assertIn(expectation, response.content)
        response = requests.get('{}/VerwerkSynchroonVrijBericht/?WSDL'.format(self.live_server_url, ))
        for expectation in appinfo:
            self.assertIn(expectation, response.content)
        response = requests.get('{}/OntvangAsynchroon/?WSDL'.format(self.live_server_url, ))
        for expectation in appinfo:
            self.assertIn(expectation, response.content)

    @override_settings(ZAAKMAGAZIJN_REFERENCE_WSDL=False)
    def test_spyne_wsdl(self):
        response = requests.get('{}/BeantwoordVraag/?WSDL'.format(self.live_server_url, ), allow_redirects=False)

        namespaces = {
            'wsdl': 'http://schemas.xmlsoap.org/wsdl/',
            'soap': 'http://schemas.xmlsoap.org/wsdl/soap/',
            'xs': 'http://www.w3.org/2001/XMLSchema'
        }
        root = etree.fromstring(response.content)
        wsdl_imports = root.xpath('/wsdl:definitions/wsdl:import', namespaces=namespaces)
        self.assertEqual(len(wsdl_imports), 0)

        soap_addresses = root.xpath('/wsdl:definitions/wsdl:service/wsdl:port/soap:address', namespaces=namespaces)
        self.assertGreaterEqual(len(soap_addresses), 1)
        for element in soap_addresses:
            self.assertTrue(element.attrib['location'].startswith(self.live_server_url))

        schema_imports = root.xpath('/wsdl:definitions/wsdl:types/xs:schema/xs:import', namespaces=namespaces)
        self.assertGreaterEqual(len(schema_imports), 1)
        for element in schema_imports:
            self.assertTrue('schemaLocation' not in element.attrib)

    @override_settings(
        ZAAKMAGAZIJN_REFERENCE_WSDL=True,
        ZAAKMAGAZIJN_ZDS_URL='http://zds-url',
        ZAAKMAGAZIJN_URL='http://zaakmagazijn-url')
    def test_rewrite(self):
        response = requests.get('{}/BeantwoordVraag/?WSDL'.format(self.live_server_url, ), allow_redirects=False)

        namespaces = {
            'wsdl': 'http://schemas.xmlsoap.org/wsdl/',
            'soap': 'http://schemas.xmlsoap.org/wsdl/soap/',
            'xs': 'http://www.w3.org/2001/XMLSchema'
        }
        root = etree.fromstring(response.content)
        wsdl_imports = root.xpath('/wsdl:definitions/wsdl:import', namespaces=namespaces)
        self.assertGreaterEqual(len(wsdl_imports), 1)
        for element in wsdl_imports:
            self.assertTrue(element.attrib['location'].startswith('http://zds-url'))

        soap_addresses = root.xpath('/wsdl:definitions/wsdl:service/wsdl:port/soap:address', namespaces=namespaces)
        self.assertGreaterEqual(len(soap_addresses), 1)
        for element in soap_addresses:
            self.assertTrue(element.attrib['location'].startswith('http://zaakmagazijn-url'))

        schema_imports = root.xpath('/wsdl:definitions/wsdl:types/xs:schema/xs:import', namespaces=namespaces)
        self.assertGreaterEqual(len(schema_imports), 1)
        for element in schema_imports:
            self.assertTrue(element.attrib['schemaLocation'].startswith('http://zds-url'))
