from unittest import skip

import requests
from lxml import etree
from mock import patch
from spyne import Fault, InternalError
from zeep.xsd.const import Nil

from ...rgbz.choices import JaNee
from ...rgbz.tests.factory_models import StatusFactory
from ..stuf.choices import (
    BerichtcodeChoices, ClientFoutChoices, ServerFoutChoices
)
from ..stuf.faults import StUFFault
from .base import BaseSoapTests


class StUFFaultTests(BaseSoapTests):
    """
    Exception handling is coupled in various ways and on various levels. We use `geefZaakstatus_ZakLv01` as an example
    request.

    Example response according to the XSD::

        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:stuf="http://www.egem.nl/StUF/StUF0301">
          <soapenv:Body>
            <soapenv:Fault>
              <faultcode>?</faultcode>
              <faultstring xml:lang="?">?</faultstring>
              <!--Optional:-->
              <faultactor>?</faultactor>
              <!--Optional:-->
              <detail>
                <stuf:Fo02Bericht>
                  <stuf:stuurgegevens>
                    <stuf:berichtcode>Fo02</stuf:berichtcode>
                  </stuf:stuurgegevens>
                  <stuf:body>
                    <stuf:code>?</stuf:code>
                    <stuf:plek>?</stuf:plek>
                    <stuf:omschrijving>?</stuf:omschrijving>
                  </stuf:body>
                </stuf:Fo02Bericht>
                <!--You may enter ANY elements at this point-->
              </detail>
            </soapenv:Fault>
          </soapenv:Body>
        </soapenv:Envelope>

    """

    def setUp(self):
        super().setUp()

        self.client = self._get_client('BeantwoordVraag', strict=False)

        self.status = StatusFactory.create()
        self.zaak = self.status.zaak

    def _simple_request(self, zaak_id=None, entiteittype=None):
        if zaak_id is None:
            zaak_id = self.zaak.zaakidentificatie
        if entiteittype is None:
            entiteittype = 'ZAK'

        with self.client.options(raw_response=True):
            stuf_factory, zkn_factory, zds_factory = self._get_type_factories(self.client)

            response = self.client.service.geefZaakstatus_ZakLv01(
                stuurgegevens=stuf_factory['ZAK-StuurgegevensLv01'](
                    berichtcode='Lv01',
                    entiteittype=entiteittype),
                parameters=stuf_factory['ZAK-parametersVraagSynchroon'](
                    sortering=1,
                    indicatorVervolgvraag=False),
                scope={
                    'object': zkn_factory['GeefZaakStatus-ZAK-vraagScope'](
                        entiteittype='ZAK',
                        identificatie=Nil,
                        heeft=zkn_factory['GeefZaakStatus-ZAKSTT-vraagScope'](
                            entiteittype='ZAKSTT',
                            indicatieLaatsteStatus=Nil,
                            datumStatusGezet=Nil,
                            gerelateerde=zkn_factory['GeefZaakStatus-STT-vraag'](
                                entiteittype='STT',
                                volgnummer=Nil,
                            )
                        )
                    ),
                },
                gelijk=zkn_factory['GeefZaakStatus-ZAK-vraagSelectie'](
                    entiteittype='ZAK',
                    identificatie=zaak_id,
                    heeft=zkn_factory['GeefZaakStatus-ZAKSTT-vraagSelectie'](
                        entiteittype='ZAKSTT',
                        indicatieLaatsteStatus=JaNee.ja,
                    )
                )
            )
        return etree.fromstring(response.content)

    def _validate_stuf_fault_xml(self, xml, stuf_berichtcode, stuf_code, stuf_plek, stuf_omschrijving, stuf_details=None):
        fault_xpath = '/soap11env:Envelope/soap11env:Body/soap11env:Fault'
        self._assert_xpath_results(xml, fault_xpath, 1, namespaces=self.nsmap)

        fault_root = xml.xpath(fault_xpath, namespaces=self.nsmap)[0]
        expected_once = [
            # See: Protocolbindingen voor StUF, chapter 4
            'faultcode[starts-with(.,"{}:{}")]'.format('soap11env', stuf_plek),
            'faultstring[text()="{}"]'.format(stuf_omschrijving),
            # 'faultactor[text()=""]',
        ]
        for expectation in expected_once:
            self._assert_xpath_results(fault_root, expectation, 1, namespaces=self.nsmap)

        detail_xpath = '{}/detail'.format(fault_xpath)
        self._assert_xpath_results(xml, detail_xpath, 1, namespaces=self.nsmap)

        body_root_xpath = '{}/stuf:{}Bericht'.format(detail_xpath, stuf_berichtcode)
        self._assert_xpath_results(xml, body_root_xpath, 1, namespaces=self.nsmap)

        body_root = xml.xpath(body_root_xpath, namespaces=self.nsmap)[0]
        expected_once = [
            'stuf:stuurgegevens',
            'stuf:stuurgegevens/stuf:berichtcode[text()="{}"]'.format(stuf_berichtcode),
            'stuf:body',
            'stuf:body/stuf:code[text()="{}"]'.format(stuf_code),
            'stuf:body/stuf:plek[text()="{}"]'.format(stuf_plek),
            'stuf:body/stuf:omschrijving[text()="{}"]'.format(stuf_omschrijving),
        ]
        if stuf_details is not None:
            expected_once.append('stuf:body/stuf:details[text()="{}"]'.format(stuf_details))

        for expectation in expected_once:
            self._assert_xpath_results(body_root, expectation, 1, namespaces=self.nsmap)

    @patch('zaakmagazijn.api.services.geef_zaak_status.output_builder.create_data')
    def test_raise_fault(self, mock_create_data):
        """
        Test raised `Fault` to be communicated as a StUF fault message.
        """
        mock_create_data.side_effect = Fault(faultstring='The error message', detail='Some details about the error.')

        xml = self._simple_request()
        self._validate_stuf_fault_xml(
            xml,
            BerichtcodeChoices.fo02,
            ServerFoutChoices.stuf058,
            'server',
            ServerFoutChoices.values.get(ServerFoutChoices.stuf058),
            stuf_details='Some details about the error.'
        )

    @patch('zaakmagazijn.api.services.geef_zaak_status.output_builder.create_data')
    def test_raise_fault_subclass(self, mock_create_data):
        """
        Test raised `Fault` to be communicated as a StUF fault message.
        """
        mock_create_data.side_effect = InternalError(Exception())

        xml = self._simple_request()
        self._validate_stuf_fault_xml(
            xml,
            BerichtcodeChoices.fo02,
            ServerFoutChoices.stuf058,
            'server',
            ServerFoutChoices.values.get(ServerFoutChoices.stuf058)
        )

    @patch('zaakmagazijn.api.services.geef_zaak_status.output_builder.create_data')
    def test_raise_exception(self, mock_create_data):
        """
        Test raised `Exception` to be communicated as a StUF fault message.
        """
        mock_create_data.side_effect = Exception('Something terrible happened.')

        xml = self._simple_request()
        self._validate_stuf_fault_xml(
            xml,
            BerichtcodeChoices.fo02,
            ServerFoutChoices.stuf058,
            'server',
            ServerFoutChoices.values.get(ServerFoutChoices.stuf058),
            stuf_details='Something terrible happened.'
        )

    @patch('zaakmagazijn.api.services.geef_zaak_status.output_builder.create_data')
    def test_raise_stuf_fault(self, mock_create_data):
        """
        Test raised `StUFFault`.
        """
        mock_create_data.side_effect = StUFFault(
            ClientFoutChoices.stuf010
        )

        xml = self._simple_request()
        self._validate_stuf_fault_xml(
            xml,
            BerichtcodeChoices.fo02,
            ClientFoutChoices.stuf010,
            'client',
            ClientFoutChoices.values.get(ClientFoutChoices.stuf010)
        )

    @skip("Since schema validation for the input is disabled, this error case can't happen anymore and this test fails.")
    def test_schema_validation_error(self):
        """
        Test `SchemaValidationError` because it is handled differently then other `Fault`s.
        """
        xml = self._simple_request(entiteittype='AAA')
        self._validate_stuf_fault_xml(
            xml,
            BerichtcodeChoices.fo02,
            ClientFoutChoices.stuf055,
            'client',
            ClientFoutChoices.values.get(ClientFoutChoices.stuf055)
        )

    @skip('Unsure if this error should be wrapped in a StUF Fault.')
    def test_xml_syntax_error(self):
        xml_request_str = """
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
                <soapenv:Header/>
                <soapenv:Body>
                    <oops:foo/>
                </soapenv:Body>
            </soapenv:Envelope>

        """
        response = requests.post('{}/{}/'.format(self.live_server_url, 'BeantwoordVraag'), data=xml_request_str)
        xml_response = etree.fromstring(response.content)

        self._validate_stuf_fault_xml(
            xml_response,
            BerichtcodeChoices.fo02,
            ClientFoutChoices.stuf055,
            'client',
            ClientFoutChoices.values.get(ClientFoutChoices.stuf055)
        )
