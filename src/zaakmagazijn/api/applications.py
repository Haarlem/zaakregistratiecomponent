import logging

from lxml import etree
from spyne import Application as _Application, error
from spyne.const.xml import XSD

from ..apiauth.utils import handle_authorization
from .services import (
    ActualiseerZaakstatus, CancelCheckout, CreeerZaak, GeefBesluitDetails,
    GeefLijstBesluiten, GeefLijstZaakdocumenten, GeefZaakdetails,
    GeefZaakdocumentBewerken, GeefZaakdocumentLezen, GeefZaakstatus,
    GenereerBesluitIdentificatie, GenereerDocumentIdentificatie,
    GenereerZaakIdentificatie, MaakZaakdocument, OntkoppelZaakdocument,
    OverdragenZaak, UpdateBesluit, UpdateZaak, UpdateZaakdocument,
    VoegBesluitToe, VoegZaakdocumentToe
)
from .stuf.attributes import (
    Bestandsnaam, ContentType, IndOnvolledigeDatum, NoValue, Scope__Anonymous,
    Verwerkingssoort
)
from .stuf.constants import XMIME_XML_NS
from .stuf.faults import SpyneAsyncStUFFault, SpyneStUFFault
from .stuf.models import ExtraElementen, Tijdstip_e, TijdvakGeldigheid
from .stuf.protocols import StUFSynchronous
from .stuf.simple_types import Entiteittype, Exact, FunctieVrijBerichtElement

logger = logging.getLogger(__name__)


class Application(_Application):

    FAULT_CLASS = SpyneStUFFault

    def add_custom_elements(self, document):
        """
        Add attributes and elements to the WSDL which will be re-used in other
        namespaces, and can be referenced to with <attribute ref="xxx" />
        """
        from spyne.interface.xml_schema.model import simple_get_restriction_tag

        # These are global elements.
        #    <element name="StUF-berichtenSet">
        #       <annotation>
        #          <documentation xml:lang="nl">In het schema van de StUF-standaard kan dit element slechts gedefinieerd worden met als types anyType voor de  # noqa
        # 				elementen die voor kunnen komen in een berichtenbestand. De verschillende sectormodellen definieren deze  # noqa
        # 				elementen in meer detail. Een correcte validatie is mogelijk door in het bericht expliciet het sectormodel te specificeren  # noqa
        # 				waartegen het bericht gevalideerd dient te worden.</documentation>
        #       </annotation>
        #       <complexType>
        #          <choice minOccurs="0" maxOccurs="unbounded">
        #             <element name="bericht"/>
        #          </choice>
        #       </complexType>
        #    </element>
        #    <element name="extraElementen" type="StUF:ExtraElementen"/>
        #    <element name="tijdvakObject" type="StUF:TijdvakObject"/>
        #    <element name="tijdvakRelatie" type="StUF:TijdvakRelatie"/>
        #    <complexType name="ParametersAntwoordSynchroon">
        #       <annotation>
        #          <documentation>Type voor gebruik in La01, La07, La09, La11 en La13 berichten.</documentation>
        #       </annotation>
        #       <sequence>
        #          <element name="indicatorVervolgvraag" type="boolean"/>
        #          <element name="indicatorAfnemerIndicatie" type="boolean" default="false" minOccurs="0"/>
        #          <element name="aantalVoorkomens" type="StUF:AantalVoorkomens" minOccurs="0"/>
        #       </sequence>
        #    </complexType>
        #    <complexType name="ParametersLk01">
        #       <sequence>
        #          <element name="mutatiesoort" type="StUF:Mutatiesoort"/>
        #          <element name="indicatorOvername" type="StUF:IndicatorOvername" default="V"/>
        #       </sequence>
        #    </complexType>
        #    <complexType name="ParametersLk02">
        #       <sequence>
        #          <element name="mutatiesoort" type="StUF:Mutatiesoort"/>
        #       </sequence>
        #    </complexType>

        global_elements = {
            'extraElementen': ExtraElementen,
            'tijdstipRegistratie': Tijdstip_e.customize(nillable=True),
            'tijdvakGeldigheid': TijdvakGeldigheid,
        }

        # Global attribute groups
        #    <attributeGroup name="entiteit">
        #       <attribute ref="StUF:sleutelVerzendend"/>
        #       <attribute ref="StUF:sleutelOntvangend"/>
        #       <attribute ref="StUF:sleutelGegevensbeheer"/>
        #       <attribute ref="StUF:sleutelSynchronisatie"/>
        #       <attribute ref="StUF:noValue"/>
        #       <attribute ref="StUF:scope"/>
        #       <attribute ref="StUF:verwerkingssoort"/>
        #    </attributeGroup>
        #    <attributeGroup name="entiteitZonderSleutels">
        #       <attribute ref="StUF:noValue"/>
        #       <attribute ref="StUF:scope"/>
        #       <attribute ref="StUF:verwerkingssoort"/>
        #    </attributeGroup>
        #    <attributeGroup name="element">
        #       <attribute ref="StUF:noValue"/>
        #       <attribute ref="StUF:exact"/>
        #    </attributeGroup>
        #    <attributeGroup name="relatie">
        #       <annotation>
        #          <documentation>'aantalVoorkomens' en 'aardAantal' zijn deprecated.</documentation>
        #       </annotation>
        #       <attributeGroup ref="StUF:entiteit"/>
        #       <attribute ref="StUF:aantalVoorkomens"/>
        #       <attribute ref="StUF:aardAantal"/>
        #    </attributeGroup>

        # Global attributes
        # <attribute name="aantalVoorkomens" type="StUF:AantalVoorkomens"/>
        # <attribute name="aardAantal" type="StUF:AardAantal"/>
        # <attribute name="metagegeven" type="boolean" fixed=True/>
        # <attribute name="schemaLocation" type="string"/>
        # <attribute name="sleutelVerzendend" type="StUF:Sleutel"/>
        # <attribute name="sleutelOntvangend" type="StUF:Sleutel"/>
        # <attribute name="sleutelGegevensbeheer" type="StUF:Sleutel"/>
        # <attribute name="sleutelSynchronisatie" type="StUF:Sleutel"/>

        global_attributes = {
            'entiteittype': Entiteittype,
            'bestandsnaam': Bestandsnaam,
            'contentType': ContentType,
            'exact': Exact,  # .customize(default=True),
            'functie': FunctieVrijBerichtElement,
            'indOnvolledigeDatum': IndOnvolledigeDatum,  # .customize(default='V'),
            'noValue': NoValue,
            'scope': Scope__Anonymous,
            'verwerkingssoort': Verwerkingssoort,
        }
        for name, simple_type in global_attributes.items():
            simple_get_restriction_tag(document, simple_type)

            attribute = etree.Element(XSD('attribute'))
            attribute.set('name', name)
            attribute.set('type', simple_type.get_type_name_ns(document.interface))

            document.add_element(simple_type, attribute)

        for name, cls in global_elements.items():
            document.add(cls, set())

        # the contentType namespace doesn't get imported properly, so this HACKKKK solves it
        # nasty, but if it works...
        document.interface.imports[XMIME_XML_NS] = set()

    def call_wrapper(self, ctx):
        """
        The call wrapper is the first to be handling exceptions.

        NOTE: `SchemaValidationError` does not pass through here.
        """

        try:
            stuurgegevens_zender = ctx.in_object[0].stuurgegevens
        except IndexError:
            stuurgegevens_zender = None

        try:
            # Check if "zender" is authorized
            handle_authorization(ctx)
            return ctx.service_class.call_wrapper(ctx)
        # Log `Fault`s and if not already an instance of `self.FAULT_CLASS`, re-raise
        # as such.
        except error.Fault as e:
            sc = ctx.service_class
            logger.error(e)
            raise self.FAULT_CLASS.from_fault(e, sc, stuurgegevens_zender)
        # Log `Exception`s and re-raise as `self.FAULT_CLASS`s.
        except Exception as e:
            sc = ctx.service_class
            logger.exception(e)
            raise self.FAULT_CLASS.from_exception(e, sc, stuurgegevens_zender)


class AsyncApplication(Application):
    FAULT_CLASS = SpyneAsyncStUFFault


beantwoordvraag_app = Application(
    [GeefBesluitDetails, GeefZaakstatus, GeefLijstBesluiten, GeefZaakdetails,
     GeefLijstZaakdocumenten, GeefZaakdocumentLezen],
    tns='http://www.stufstandaarden.nl/koppelvlak/zds0120',
    name='Beantwoordvraag',
    in_protocol=StUFSynchronous(validator='lxml'),
    out_protocol=StUFSynchronous()
)

verwerksynchroonvrijbericht_app = Application(
    [CancelCheckout, GeefZaakdocumentBewerken, GenereerZaakIdentificatie,
     GenereerBesluitIdentificatie, GenereerDocumentIdentificatie,
     OntkoppelZaakdocument, UpdateZaakdocument],
    tns='http://www.stufstandaarden.nl/koppelvlak/zds0120',
    name='VerwerkSynchroonVrijBericht',
    in_protocol=StUFSynchronous(validator='lxml'),
    out_protocol=StUFSynchronous()
)

ontvangasynchroon_app = AsyncApplication(
    [ActualiseerZaakstatus, CreeerZaak, MaakZaakdocument, OverdragenZaak,
     UpdateZaak, UpdateBesluit, VoegBesluitToe, VoegZaakdocumentToe],
    tns='http://www.stufstandaarden.nl/koppelvlak/zds0120',
    name='OntvangAsynchroon',
    in_protocol=StUFSynchronous(validator='lxml'),
    out_protocol=StUFSynchronous()
)


def _on_method_exception_object(ctx):
    """
    After the context wrapper, the `method_exception_object` event is handled.
    The only reason to implement this, is to couple certain "FoutBerichten" to
    applications.

    NOTE: `SchemaValidationError` does not pass through here.
    """
    pass

# beantwoordvraag_app.event_manager.add_listener('method_exception_object', _on_method_exception_object)
# verwerksynchroonvrijbericht_app.event_manager.add_listener('method_exception_object', _on_method_exception_object)
