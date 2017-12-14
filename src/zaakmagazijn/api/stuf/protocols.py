import copy
import logging
import os

from django.conf import settings

from lxml import etree, html
from lxml.builder import E
from spyne.const.xml import XSI
from spyne.protocol.soap import Soap11
from spyne.protocol.xml import SchemaValidationError
from spyne.util.six import text_type

from .choices import ClientFoutChoices
from .constants import GML_XML_NS

logger = logging.getLogger(__name__)


class IgnoreAttribute:
    """
    This is a hack to let Spyne not append elements, which weren't asked in the scope.
    """

    def __iter__(self):
        """
        This is a hack to go through the _get_members_etree loop when max_occurs
        is > 1. What happens is: to_parent gets called with IgnoreAttribute, once, and
        nothing is appended 'to_parent'.
        """
        return iter([self, ])


class Nil:
    def __init__(self, **attributes):
        self.attributes = attributes

    def __getattr__(self, name):
        if name in self.attributes:
            return self.attributes[name]
        raise AttributeError('{} not found'.format(name))

    def __str__(self):
        arguments = ','.join(['{}={}'.format(k, v) for k, v in self.attributes.items()])
        return 'Nil({})'.format(arguments)

    @staticmethod
    def to_django_value(spyne_obj, django_field):
        return None


class StUF(Soap11):
    """
    Specific requirements on top of Soap11 to serialize and deserialize for
    the StUF protocl (StUF 03.01)
    """

    def __init__(self, *args, **kwargs):
        if getattr(settings, 'DEBUG', False):
            kwargs['pretty_print'] = True
        # kwargs['validator'] = 'soft'

        super().__init__(*args, **kwargs)

    def to_parent(self, ctx, cls, inst, parent, ns, *args, **kwargs):
        """
        Allow serializing xsi:nil=True by setting the IgnoreAttribute class as a value of an attribute.
        Also, allow including optional fields which don't have IgnoreAttribute set. This is done to allow
        dealing with the scope parameters.
        """
        cls_attrs = self.get_cls_attrs(cls)
        if cls_attrs.min_occurs == 0 and isinstance(inst, IgnoreAttribute):
            return None

        if inst is None and cls.Attributes.min_occurs == 0:
            return self.null_to_parent(ctx, cls, inst, parent, ns, *args, **kwargs)
        return super().to_parent(ctx, cls, inst, parent, ns, *args, **kwargs)

    def from_element(self, ctx, cls, element):
        if bool(element.get(XSI('nil'))):
            attributes = dict([(key[key.find('}') + 1:], value) for key, value in element.attrib.items()])
            return Nil(**attributes)
        return super().from_element(ctx, cls, element)


class StUFSynchronous(StUF):
    """
    See StUF 03.01 4.4.3 Regels voor foutberichten.

        Op een synchroon bericht wordt gereageerd met een Fo02-foutbericht
        of de in StUF-standaard of het sectormodel gedefinieerde respons.
        Voor synchrone kennisgevingberichten, synchronisatieberichten en
        vraag/antwoord berichten beschrijft de StUF-standaard de respons
        en de foutafhandeling.

    Return required Faults as specified in the StUF 03.01 standard.
    """
    default_string_encoding = 'UTF-8'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serialization_handlers[SchemaValidationError] = self.schema_validation_error_to_parent

    def validate_document(self, payload):
        """
        Validate the document against the KING reference WSDL.
        """
        # TODO [TECH]: For some reason xmllint nor xmlstarlet validates
        # against the gml XSD properly. I can't find an xml validator which
        # does support this (my guess, they're all based on libxml2).

        if payload.xpath('//gml:*', namespaces={'gml': GML_XML_NS}):
            # Make a copy to prevent removing data.
            payload_copy = copy.deepcopy(payload)

            for el in payload_copy.xpath('//gml:*', namespaces={'gml': GML_XML_NS}):
                el.getparent().remove(el)
        else:
            # No need to make a copy. We're not removing anything.
            payload_copy = payload

        xsd_path = os.path.join(settings.ZAAKMAGAZIJN_ZDS_PATH, 'zds0120_msg_zs-dms_resolved2017.xsd')
        xmlschema = etree.XMLSchema(file=xsd_path)
        ret = xmlschema.validate(payload_copy)

        logger.debug("Validated ? %r" % ret)
        if not ret:
            error_text = text_type(xmlschema.error_log.last_error)
            raise SchemaValidationError(error_text.encode('ascii',
                                                           'xmlcharrefreplace'))

    def schema_validation_error_to_parent(self, ctx, cls, inst, parent, ns, **_):
        fault_cls = ctx.app.FAULT_CLASS

        # We've got no clue what the stuurgegevens are of the 'zender' at this point. We could improve
        # this and try to parse the request using lxml, and see if we can ressurect some data, that
        # seems to me like a bad idea.
        stuurgegevens_zender = None

        # NOTE: Raising a StUFFault here leads to a server error, since it's not handled by the
        # `Application.call_wrapper`.
        stuf_fault = fault_cls.from_details(
            ClientFoutChoices.stuf055, html.fromstring(inst.faultstring).text, ctx.service_class, stuurgegevens_zender
        )
        inst.detail = stuf_fault.detail

        subelts = [
            E("faultcode", '%s:%s' % (self.soap_env, stuf_fault.faultcode)),
            E("faultstring", stuf_fault.faultstring),
            E("faultactor", inst.faultactor),
        ]

        # add other nonstandard fault subelements with get_members_etree
        return self._fault_to_parent_impl(ctx, cls, inst, parent, ns, subelts)
