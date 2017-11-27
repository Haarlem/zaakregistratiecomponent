import urllib.parse
import uuid

from django.conf import settings

from lxml import etree

from zaakmagazijn.rgbz_mapping.models import EnkelvoudigDocumentProxy

from .stuf.choices import ServerFoutChoices


def create_unique_id():
    gemeente_code = settings.ZAAKMAGAZIJN_GEMEENTE_CODE
    assert len(gemeente_code) == 4, 'Gemeentecode should always be 4 characters long'

    return '{}{}'.format(gemeente_code, str(uuid.uuid4()))


def get_enkelvoudig_informatie_object_or_fault(identificatie: str) -> EnkelvoudigDocumentProxy:
    """
    Retrieve the EnkelvoudigDocumentProxy belonging to :param:`identificatie`, or
    raise the appropriate StUFFault.
    """
    from .stuf.faults import StUFFault

    eio = EnkelvoudigDocumentProxy.objects.filter(identificatie=identificatie).first()
    if eio is None:
        raise StUFFault(
            ServerFoutChoices.stuf064,
            stuf_details='Gerefereerde zaakdocument is niet aanwezig'
        )

    if not eio.zaakinformatieobject_set.exists():
        raise StUFFault(
            ServerFoutChoices.stuf064,
            stuf_details='Gerefereerde document is wel aanwezig maar geen zaakdocument'
        )

    return eio


def rewrite_wsdl(content, schema_url, soap_address):
    """
    Rewrite the URLs and paths within a WSDL file to the requested paths.

    :param content Contents of the WSDL file.
    :param schema_url The new URL where the WSDL/XSD schema's can be found.
    :param soap_address The URL that'll be used as a SOAP endpoint.
    """
    root = etree.fromstring(content)
    namespaces = {
        'wsdl': 'http://schemas.xmlsoap.org/wsdl/',
        'soap': 'http://schemas.xmlsoap.org/wsdl/soap/',
        'xs': 'http://www.w3.org/2001/XMLSchema'
    }
    for element in root.xpath('/wsdl:definitions/wsdl:import', namespaces=namespaces):
        element.attrib['location'] = urllib.parse.urljoin(schema_url, element.attrib['location'])

    for element in root.xpath('/wsdl:definitions/wsdl:service/wsdl:port/soap:address', namespaces=namespaces):
        _, _, path, query, fragment = urllib.parse.urlsplit(element.attrib['location'])
        schema, netloc, _, _, _ = urllib.parse.urlsplit(soap_address)
        element.attrib['location'] = urllib.parse.urlunsplit((schema, netloc, path, query, fragment))

    for element in root.xpath('/wsdl:definitions/wsdl:types/xs:schema/xs:import', namespaces=namespaces):
        element.attrib['schemaLocation'] = urllib.parse.urljoin(schema_url, element.attrib['schemaLocation'])

    return etree.tostring(root, pretty_print=True)
