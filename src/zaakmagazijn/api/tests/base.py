import logging
import os.path
import random
import string
from datetime import datetime, timedelta

from django.template import Context, Template
from django.test import LiveServerTestCase

import requests
from lxml import etree
from lxml.etree import _Element
from zeep import Client
from zeep.xsd import CompoundValue

from ...cmis.tests.mocks import MockDMSMixin
from ...utils import stuf_datetime
from ..stuf.constants import STUF_XML_NS, ZDS_XML_NS, ZKN_XML_NS

logger = logging.getLogger(__name__)


class StUFMixin:
    maxDiff = None

    nsmap = {
        'zkn': 'http://www.egem.nl/StUF/sector/zkn/0310',
        'bg': 'http://www.egem.nl/StUF/sector/bg/0310',
        'stuf': 'http://www.egem.nl/StUF/StUF0301',
        'zds': 'http://www.stufstandaarden.nl/koppelvlak/zds0120',
        'soap11env': 'http://schemas.xmlsoap.org/soap/envelope/',
        'gml': 'http://www.opengis.net/gml',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }


class XmlHelperMixin:
    def _print_from_string(self, str):
        print(etree.tostring(etree.fromstring(str), pretty_print=True).decode('utf-8'))

    def _print_from_element(self, el):
        print(etree.tostring(el, pretty_print=True).decode('utf-8'))

    def _print_from_zeep_object(self, obj):
        print(obj)

    def pretty_print(self, val):
        """
        Helper function to print an XML response in a readable format. This
        function should only be used for debugging and should not be part of a
        test.

        :param val: A `zeep`, `lxml` or `str` value.
        """
        if isinstance(val, CompoundValue):
            self._print_from_zeep_object(val)
        elif isinstance(val, _Element):
            self._print_from_element(val)
        else:
            self._print_from_string(val)

    def _assert_xpath_results(self, root, xpath, results, namespaces=None):
        namespaces = namespaces or root.nsmap
        elements = root.xpath(xpath, namespaces=namespaces)
        self.assertEqual(
            len(elements),
            results,
            msg="{} was found {} times {} times was expected".format(xpath, len(elements), results)
        )


class BaseSoapTests(StUFMixin, XmlHelperMixin, MockDMSMixin, LiveServerTestCase):
    def _get_client(self, soap_port, **kwargs):
        # Reset the cached WSDL since it might contain the URL of
        # the other LiveServerTestCase (which uses a different port)
        from zaakmagazijn.api import views
        from spyne.interface import AllYourInterfaceDocuments

        # TODO: [TECH] Find a proper way to get all the WSDLs
        for view in [views.verwerksynchroonvrijbericht_view, views.beantwoordvraag_view, views.ontvangasynchroon_view]:
            view.__wrapped__._wsdl = None
            view.__wrapped__.doc = AllYourInterfaceDocuments(view.__wrapped__.app.interface)

        return Client('{}/{}/?WSDL'.format(self.live_server_url, soap_port), **kwargs)

    def _get_type_factories(self, client):
        zkn_factory = client.type_factory(ZKN_XML_NS)
        stuf_factory = client.type_factory(STUF_XML_NS)
        zds_factory = client.type_factory(ZDS_XML_NS)
        return stuf_factory, zkn_factory, zds_factory

    def _get_body_root(self, root):
        return root.xpath(self.antwoord_xpath, namespaces=self.nsmap)[0]


class BaseTestPlatformTests(StUFMixin, XmlHelperMixin, MockDMSMixin, LiveServerTestCase):
    """
    Base class for performing tests copied from the StUF test platform.
    """

    # if not specified, template_name is expected in /files, otherwise in /files/test_files_subfolder
    test_files_subfolder = None

    def _create_soap_envelope(self):

        envelope = etree.Element('{http://schemas.xmlsoap.org/soap/envelope/}Envelope', nsmap=self.nsmap)
        header = etree.SubElement(envelope, '{http://schemas.xmlsoap.org/soap/envelope/}Header', nsmap=self.nsmap)
        body = etree.SubElement(envelope, '{http://schemas.xmlsoap.org/soap/envelope/}Body', nsmap=self.nsmap)
        return envelope, header, body

    def _build_template(self, template_name, context):
        files_path = os.path.join(os.path.dirname(__file__), 'files')

        if self.test_files_subfolder:
            template_name = os.path.join(self.test_files_subfolder, template_name)

        template_file = open(os.path.join(files_path, template_name), 'rb')
        template = Template(template_file.read())
        context = context if isinstance(context, Context) else Context(context)
        rendered_template = template.render(context)
        content = etree.fromstring(rendered_template.encode('utf-8'))
        envelope, header, body = self._create_soap_envelope()
        body.append(content)

        rendered_envelope = etree.tostring(envelope, xml_declaration=True, encoding="UTF-8", pretty_print=True)
        return rendered_envelope

    def _normalize_envelope(self, root_element):
        envelope, header, body = self._create_soap_envelope()

        for element in list(root_element.xpath('/soap11env:Envelope/soap11env:Body', namespaces=self.nsmap)[0]):
            body.append(element)

        return envelope

    def genereerID(self, amount, type=None):
        """
        In most cases 'genereerId(10)' is called which should return a string of length 10 existing of
        numbers.
        However, 'genereerId(10, "Alfanumeriek")' should return a string of length 10 existing of letters
        """
        if type == 'Alfanumeriek':
            return ''.join([random.choice(string.ascii_letters) for _ in range(amount)])

        return ''.join([random.choice([str(i) for i in range(1, 9 + 1)]) for x in range(1, amount + 1)])

    def genereerdatumtijd(self, days_offset=0):
        """
        equivalent in STP:
        genereerdatumtijd(0, "yyyyMMddHHmmss")  for today
        """
        the_time = datetime.now()

        if days_offset != 0:
            the_time += timedelta(days=days_offset)

        return the_time.strftime(stuf_datetime.DATETIME_FORMAT)

    def genereerdatum(self, days_offset=0):
        """
        Return the datetime like genereerdatumtijd,
        but in the short format "yyyyMMdd"

        genereerdatum(2) is equal to STP genereerdatumtijd(2, "yyyyMMdd") for day after tomorrow
        genereerdatum(-1) is equal to STP genereerdatumtijd(-1, "yyyyMMdd") for yesterday
        """
        the_time = datetime.now()

        if days_offset != 0:
            the_time += timedelta(days=days_offset)

        return the_time.strftime(stuf_datetime.DATE_FORMAT)

    def get_context_data(self, **kwargs):
        default_context = {
            'zenderOrganisatie': 'KING',
            'zenderApplicatie': 'STP',
            'ontvangerOrganisatie': 'ORG',
            'ontvangerApplicatie': 'TTA',
            'tijdstipBericht': self.genereerdatumtijd(),
        }
        default_context.update(kwargs)
        return default_context

    def _do_request(self, soap_port, template_name, extra_context=None):
        """
        Calls the Zaakmagazijn SOAP endpoint with the given request.

        soap_port: 'OntvangAsynchroon', 'BeantwoordVraag' etc
        template_name: the template's filename in the tests/files/ directory, used to build the request
        extra_context: any additional context for processing the template
        """
        
        if extra_context is None:
            extra_context = {}

        # Full request I intercepted was:
        #
        # POST /VerwerkSynchroonVrijBericht HTTP/1.0
        # X-Real-IP: 87.250.154.26
        # X-Forwarded-For: 87.250.154.26
        # X-Forwarded-Proto: https
        # X-Scheme: https
        # Host: haarlem-zaakmagazijn.maykin.nl
        # Connection: close
        # Content-Length: 1011
        # content-type: text/xml; charset=utf-8
        # appId: 50583302
        # partyId: 00000000000000000000041
        # SOAPAction:
        # Cache-Control: no-cache
        # Pragma: no-cache
        # User-Agent: Java/1.7.0_75
        # Accept: text/html, image/gif, image/jpeg, *; q=.2, */*; q=.2

        # <?xml version="1.0" encoding="UTF-8"?><soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
        #     <soapenv:Header/>
        #     <soapenv:Body><ZDS:genereerZaakIdentificatie_Di02 xmlns:StUF="http://www.egem.nl/StUF/StUF0301" xmlns:ZDS="http://www.stufstandaarden.nl/koppelvlak/zds0120" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.stufstandaarden.nl/koppelvlak/zds0120 zds0120_msg_zs-dms.xsd">
        #     <ZDS:stuurgegevens>
        #         <StUF:berichtcode>Di02</StUF:berichtcode>
        #         <StUF:zender>
        #             <StUF:organisatie>KING</StUF:organisatie>
        #             <StUF:applicatie>STP</StUF:applicatie>
        #             <StUF:gebruiker/>
        #         </StUF:zender>
        #         <StUF:ontvanger>
        #             <StUF:organisatie>ORG</StUF:organisatie>
        #             <StUF:applicatie>TTA</StUF:applicatie>
        #             <StUF:gebruiker/>
        #         </StUF:ontvanger>
        #         <StUF:tijdstipBericht>20170627161630</StUF:tijdstipBericht>
        #         <StUF:functie>genereerZaakidentificatie</StUF:functie>
        #     </ZDS:stuurgegevens>
        # </ZDS:genereerZaakIdentificatie_Di02></soapenv:Body>
        # </soapenv:Envelope>

        # Reset the cached WSDL since it might contain the URL of
        # the other LiveServerTestCase (which uses a different port)
        from zaakmagazijn.api import views
        from spyne.interface import AllYourInterfaceDocuments

        # TODO: [TECH] Find a proper way to get all the WSDLs
        for view in [views.verwerksynchroonvrijbericht_view, views.beantwoordvraag_view]:
            view.__wrapped__._wsdl = None
            view.__wrapped__.doc = AllYourInterfaceDocuments(view.__wrapped__.app.interface)

        # Maybe a bit too overkill.
        headers = {
            'SOAPAction': '',
            'User-Agent': 'Java/1.7.0_75',
            'partyId': '00000000000000000000041',
            'appId': '50583302'
        }

        context = self.get_context_data(**extra_context)
        rendered_envelope = self._build_template(template_name, context)
        logger.debug(rendered_envelope.decode(encoding='utf-8'))
        response = requests.post('{}/{}'.format(self.live_server_url, soap_port), rendered_envelope, headers=headers)
        logger.debug(etree.tostring(etree.fromstring(response.content), xml_declaration=True, encoding="UTF-8", pretty_print=True).decode(encoding='utf-8'))
        return response
