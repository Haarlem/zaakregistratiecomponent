import difflib
import logging
import os.path
import random
import re
import string
import subprocess
from collections import OrderedDict
from datetime import datetime, timedelta
from tempfile import NamedTemporaryFile

from django.conf import settings
from django.template import Context, Template
from django.test import LiveServerTestCase as _LiveServerTestCase
from django.test.utils import override_settings

import requests
from lxml import etree
from lxml.etree import _Element
from requests import Session
from zeep import Client, Transport
from zeep.xsd import CompoundValue

from ...cmis.tests.mocks import MockDMSMixin
from ...utils import stuf_datetime
from ..stuf.constants import STUF_XML_NS, ZDS_XML_NS, ZKN_XML_NS
from .utils import sort_xml_attributes

logger = logging.getLogger(__name__)


class StUFMixin:
    maxDiff = None

    nsmap = OrderedDict((
        ('zkn', 'http://www.egem.nl/StUF/sector/zkn/0310'),
        ('bg', 'http://www.egem.nl/StUF/sector/bg/0310'),
        ('stuf', 'http://www.egem.nl/StUF/StUF0301'),
        ('zds', 'http://www.stufstandaarden.nl/koppelvlak/zds0120'),
        ('soap11env', 'http://schemas.xmlsoap.org/soap/envelope/'),
        ('gml', 'http://www.opengis.net/gml'),
        ('xsi', 'http://www.w3.org/2001/XMLSchema-instance'),
    ))


class XmlHelperMixin:
    def _from_string(self, val):
        return str(etree.tostring(etree.fromstring(val), pretty_print=True).decode('utf-8'))

    def _from_element(self, val):
        return str(etree.tostring(val, pretty_print=True).decode('utf-8'))

    def _from_zeep_object(self, val):
        return str(val)

    def pretty_print(self, val):
        """
        This function should only be used for debugging and should not be part
        of a test.

        :param val: A `zeep`, `lxml` or `str` value.
        """
        print(self.pretty_str(val))

    def pretty_str(self, val):
        """
        Helper function to return an XML response in a readable format.

        :param val: A `zeep`, `lxml` or `str` value.
        :return: pretty formatted XML string.
        """
        if val is None:
            return ''

        if isinstance(val, list) and len(val) > 0:
            val = val[0]

        if isinstance(val, CompoundValue):
            ret = self._from_zeep_object(val)
        elif isinstance(val, _Element):
            ret = self._from_element(val)
        else:
            ret = self._from_string(val)

        return ret

    def _assert_xpath_results(self, root, xpath, results, namespaces=None):
        namespaces = namespaces or root.nsmap
        elements = root.xpath(xpath, namespaces=namespaces)

        msg = ''
        if len(elements) != results:
            # Only pretty print if there will be an error
            msg = ': {}'.format(self.pretty_str(root))

        self.assertEqual(
            len(elements),
            results,
            msg="{} was found {} times {} times was expected{}".format(xpath, len(elements), results, msg)
        )

    # This was another attempt at implementing this, using lxml to iterate trough both trees.
    # It didn't work very well. That's why I used difflib instead.

    # def compare(file, example, response):
    #     errors = []
    #     for example_node, response_node in zip(example, response):
    #         if example_node.tag == '{http://www.egem.nl/StUF/sector/zkn/0310}identificatie' and response_node.tag == '{http://www.egem.nl/StUF/sector/zkn/0310}identificatie':
    #             continue

    #         root_tree = example_node.getroottree()

    #         example_children = example_node.getchildren()
    #         response_children = response_node.getchildren()
    #         if example_node.tag != response_node.tag:
    #             errors.append('{}\n{} != {}\n{}\n'.format(
    #                 file,
    #                 example_node.tag, response_node.tag,
    #                 root_tree.getpath(example_node),
    #             ))

    #         if example_children:
    #             errors += compare(file, response_children, example_children)
    #         else:
    #             if example_node.text != response_node.text:
    #                 errors.append('{}\n{} != {}\n{}\n'.format(
    #                     file,
    #                     example_node.text, response_node.text,
    #                     root_tree.getpath(example_node)
    #                 ))
    #     return errors

    def xml_get_element(self, element, path):
        elements = element.xpath(path, namespaces=self.nsmap)
        self.assertEquals(len(elements), 1, "Expected to find one element {}".format(path))
        return elements[0]

    def xml_remove_element(self, element, path):
        """
        Remove the matched elements from a xpath query.

        :param element Element that should be searched for, for elements to be removed.
        :param path xpath query, each matched element will be removed.
        """
        results = element.xpath(path, namespaces=self.nsmap)
        for result in results:
            result.getparent().remove(result)

    def assert_xml_equal(self, element1, element2, message=None, show_diff=True):
        """
        Assert that the string output of two lxml elements are equal. If not, print
        the diff of the mismatching lines. A couple of cleanups steps are performed before
        doing the comparison:

        1. Element attributes are sorted.
        2. Namespace definitions (xmlns:* attributes) are removed.
        3. Whitepace is removed.

        :param element1 lxml Element to be compared
        :param element2 lxml Element to be compared
        """
        sort_xml_attributes(element1)
        sort_xml_attributes(element2)

        etree.cleanup_namespaces(element1, top_nsmap=self.nsmap)
        etree.cleanup_namespaces(element2, top_nsmap=self.nsmap)

        element1_str = etree.tostring(element1, encoding=str)
        element2_str = etree.tostring(element2, encoding=str)

        # Remove namespaces
        element1_str = re.sub('xmlns\:\w+=\"[^\"]+\" ', '', element1_str)
        element2_str = re.sub('xmlns\:\w+=\"[^\"]+\" ', '', element2_str)

        # Strip out whitespace
        element1_list = [l.strip() for l in element1_str.split('\n')]
        element2_list = [l.strip() for l in element2_str.split('\n')]

        errors = list(difflib.unified_diff(element1_list, element2_list))

        if show_diff:
            message = '{}{}'.format(
                '{}\n'.format(message) if message else '',
                '\n'.join(errors)
            )

        self.assertEqual(len(errors), 0, message)


class LiveServerTestCase(_LiveServerTestCase):
    def setUp(self):
        super().setUp()

        # Override the setting ZAAKMAGAZIJN_URL with the live server URL.
        self.override = override_settings(
            ZAAKMAGAZIJN_URL=self.live_server_url)
        self.override.enable()

    def tearDown(self):
        self.override.disable()


class BaseSoapTests(StUFMixin, XmlHelperMixin, MockDMSMixin, LiveServerTestCase):
    def _get_client(self, soap_port, **kwargs):
        # Reset the cached WSDL since it might contain the URL of
        # the other LiveServerTestCase (which uses a different port)
        from zaakmagazijn.api import views
        from spyne.interface import AllYourInterfaceDocuments

        # TODO [TECH]: Find a proper way to get all the WSDLs
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
        ret = root.xpath(self.antwoord_xpath, namespaces=self.nsmap)
        # Only parse ret if the response failed.
        if len(ret) == 0:
            self.assertTrue(False, self.pretty_str(root))
        return ret[0]


class BaseTestPlatformTests(StUFMixin, XmlHelperMixin, MockDMSMixin, LiveServerTestCase):
    """
    Base class for performing tests copied from the StUF test platform.
    """

    # if not specified, template_name is expected in /files, otherwise in /files/test_files_subfolder
    test_files_subfolder = None

    def _validate_response(self, response, msg=None):
        """
        Validate what is stored in the SOAP11 body element against the ZDS xsd.
        """
        return self._validate_xml(response.content, msg)

    def _validate_xml(self, xml, msg=None):
        soap_body = etree.fromstring(xml).xpath('/soap11env:Envelope/soap11env:Body', namespaces=self.nsmap)[0]
        assert len(soap_body) == 1, 'Expected one element in the SOAP body.'

        # TODO [TECH]: For some reason xmllint nor xmlstarlet validates
        # against the gml XSD properly. I can't find an xml validator which
        # does support this (my guess, they're all based on libxml2).
        for el in soap_body.xpath('//gml:*', namespaces=self.nsmap):
            el.getparent().remove(el)

        xsd_path = os.path.join(settings.ZAAKMAGAZIJN_ZDS_PATH, 'zds0120_msg_zs-dms_resolved2017.xsd')
        xmlschema = etree.XMLSchema(file=xsd_path)
        returncode = 0 if xmlschema.validate(soap_body[0]) else 1

        if returncode != 0 and not msg:
            msg = '; '.join(map(str, xmlschema.error_log.filter_from_errors()))

        self.assertEqual(returncode, 0, msg=msg)

    def _create_soap_envelope(self):

        envelope = etree.Element('{http://schemas.xmlsoap.org/soap/envelope/}Envelope', nsmap=self.nsmap)
        header = etree.SubElement(envelope, '{http://schemas.xmlsoap.org/soap/envelope/}Header', nsmap=self.nsmap)
        body = etree.SubElement(envelope, '{http://schemas.xmlsoap.org/soap/envelope/}Body', nsmap=self.nsmap)
        return envelope, header, body

    def _build_template(self, template_name, context, stp_syntax=False):
        files_path = os.path.join(os.path.dirname(__file__), 'files')

        if self.test_files_subfolder:
            template_name = os.path.join(self.test_files_subfolder, template_name)

        template_file = open(os.path.join(files_path, template_name), 'rb')
        template_contents = template_file.read()

        if stp_syntax:
            template_contents = template_contents.replace(b'${', b'{{ ').replace(b'#{', b'{{ ').replace(b'}', b' }}')

        template = Template(template_contents)
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

    def _do_request(self, soap_port, template_name, extra_context=None, stp_syntax=False):
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

        # TODO [TECH]: Find a proper way to get all the WSDLs
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
        rendered_envelope = self._build_template(template_name, context, stp_syntax=stp_syntax)
        logger.debug(rendered_envelope.decode(encoding='utf-8'))
        self._validate_xml(rendered_envelope)
        response = requests.post('{}/{}'.format(self.live_server_url, soap_port), rendered_envelope, headers=headers)
        logger.debug(etree.tostring(etree.fromstring(response.content), xml_declaration=True, encoding="UTF-8", pretty_print=True).decode(encoding='utf-8'))
        return response

