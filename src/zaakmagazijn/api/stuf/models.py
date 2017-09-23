import base64
import decimal
import logging
from io import BytesIO

from spyne import Boolean, File, Integer, Unicode
from spyne.model.complex import ComplexModel, XmlAttribute, XmlData

from . import attributes, simple_types
from ...utils.fields import StUFDateField, StUFDateTimeField
from .attributes import element, exact, indOnvolledigeDatum, noValue
from .constants import STUF_XML_NS, XMIME_XML_NS, ZKN_XML_NS
from .ordering import BSLSortering, EDCSortering, ZAKSortering

logger = logging.getLogger(__name__)


class StufParameters(ComplexModel):
    __namespace__ = ZKN_XML_NS
    __type_name__ = 'Parameters'
    _type_info = (
        ('sortering', Integer),
        ('indicatorVervolgvraag', Boolean)
    )


class ParametersLk01(ComplexModel):
    __namespace__ = STUF_XML_NS
    __type_name__ = 'ParametersLk01'
    _type_info = (
        ('mutatiesoort', simple_types.Mutatiesoort),
        ('indicatorOvername', simple_types.IndicatorOvername.customize(default='V')),
    )


class ZAK_parametersVraagSynchroon(ComplexModel):
    __namespace__ = STUF_XML_NS
    __type_name__ = 'ZAK_parametersVraagSynchroon'
    _type_info = (
        # http://docplayer.nl/3947220-Cursus-stuf-maarten-van-den-broek-messagedesign.html
        # See ordering.ZAKSortering
        ('sortering', simple_types.ZAK_sortering),
        # "het gaat J/N om een vervolgvraag (default N)"
        ('indicatorVervolgvraag', Boolean.customize(default=False)),
        ('maximumAantal', simple_types.MaximumAantal.customize(min_occurs=0)),
        # TODO: [TECH] Taiga #151 Dit geeft aan dat we van updates op de hoogte gehouden willen worden. Niet geimplementeerd.
        # "plaats J/N afnemerindicatie voor geselecteerde objecten (default N)"
        ('indicatorAfnemerIndicatie', Boolean.customize(default=False, min_occurs=0)),
        # "geef aantal voorkomens terug dat voldoet aan selectie"
        ('indicatorAantal', Boolean.customize(default=False, min_occurs=0)),
    )
    ordering = ZAKSortering


class EDC_parametersVraagSynchroon(ComplexModel):
    __namespace__ = STUF_XML_NS
    __type_name__ = 'EDC_parametersVraagSynchroon'
    _type_info = (
        ('sortering', simple_types.EDC_sortering),
        ('indicatorVervolgvraag', Boolean.customize(default=False)),
        ('maximumAantal', simple_types.MaximumAantal.customize(default=15, min_occurs=0)),
        ('indicatorAfnemerIndicatie', Boolean.customize(default=False, min_occurs=0)),
        ('indicatorAantal', Boolean.customize(default=False, min_occurs=0)),
    )
    ordering = EDCSortering


class ParametersVraag_gzdb(ComplexModel):
    __namespace__ = STUF_XML_NS
    __type_name__ = 'ParametersVraag_gzdb'
    _type_info = (
        ('indicatorAfnemerIndicatie', Boolean.customize(default=False, min_occurs=0)),
    )


class ParametersAntwoordSynchroon(ComplexModel):
    """
    Type voor gebruik in La01, La07, La09, La11 en La13 berichten.
    """
    __namespace__ = ZKN_XML_NS
    __type_name__ = 'ParametersAntwoordSynchroon'
    # As with VraagParameters, indicatorVervolgvraag and indicatorAfnemerIndicatie are
    # XML booleans
    _type_info = (
        ('indicatorVervolgvraag', Boolean.customize(default=False)),
        # "er is J/N afnemerindicatie geplaatst (default N)"
        ('indicatorAfnemerIndicatie', Boolean.customize(default=False)),
        # "het aantal objecten dat aan de selectie voldoet" - non-negative integer
        ('aantalVoorkomens', simple_types.AantalVoorkomens.customize(min_occurs=0)),
    )


class BSL_parametersVraagSynchroon(ComplexModel):
    __namespace__ = STUF_XML_NS
    __type_name__ = 'BSL_parametersVraagSynchroon'
    _type_info = (
        ('sortering', simple_types.BSL_sortering),
        ('indicatorVervolgvraag', Boolean.customize(default=False)),
        ('maximumAantal', simple_types.MaximumAantal.customize(min_occurs=0)),
        ('indicatorAfnemerIndicatie', Boolean.customize(default=False, min_occurs=0)),
        ('indicatorAantal', Boolean.customize(default=False, min_occurs=0)),
    )
    ordering = BSLSortering


class ScopeAttribute(Unicode):
    """
    This model is used to determine if 'xsi:nil=True' is set. When this
    attribute is set The SOAP11 input class's method from_element is called
    and returns the default value of the Models Attribute, in this case being True.
    """
    pass


class BaseStuurgegevens(ComplexModel):
    __namespace__ = STUF_XML_NS
    _type_info = [
        ('berichtcode', simple_types.Berichtcode)
    ]


class Systeem(ComplexModel):
    __namespace__ = STUF_XML_NS
    __type_name__ = 'Systeem'
    _type_info = [
        ('organisatie', simple_types.Organisatie.customize(min_occurs=0)),
        ('applicatie', simple_types.Applicatie),
        ('administratie', simple_types.Administratie.customize(min_occurs=0)),
        ('gebruiker', simple_types.Gebruiker.customize(min_occurs=0)),
    ]


class ZAK_StuurgegevensLk01(ComplexModel):
    __namespace__ = STUF_XML_NS
    __type_info__ = [
        ('berichtcode', simple_types.Berichtcode.customize(default='Lk01', pattern='Lk01')),  # BerichtcodeLk01 fixed=Lk01
        ('zender', Systeem),
        ('ontvanger', Systeem),
        ('referentienummer', simple_types.Refnummer),
        ('tijdstipBericht', simple_types.Tijdstip),
        ('entiteittype', simple_types.EntiteittypeZAK),
    ]


class DatumMetIndicator(ComplexModel):
    __namespace__ = STUF_XML_NS
    __type_name__ = 'DatumMetIndicator'
    _type_info = element + [
        ('indOnvolledigeDatum', indOnvolledigeDatum),
        ('data', XmlData(Unicode)),
    ]

    @classmethod
    def to_django_value(cls, spyne_obj, django_field):
        if spyne_obj.data is None:
            return ''
        return '{}'.format(spyne_obj.data)

    @classmethod
    def to_spyne_value(cls, django_obj, spyne_field):
        # TODO: [TECH] implement indOnvolledigeDatum support
        return {
            'data': django_obj
        }

    @classmethod
    def django_field_type(cls):
        return StUFDateField


class Tijdstip_e(ComplexModel):
    __namespace__ = STUF_XML_NS
    __type_name__ = 'Tijdstip_e'
    _type_info = element + [
        ('data', XmlData(simple_types.Tijdstip))
    ]


class TijdstipMetIndicator(ComplexModel):
    """
    In the XSD TijdstipMetIndicator extends from Tijdstip_e
    """
    __namespace__ = STUF_XML_NS
    __type_name__ = 'TijdstipMetIndicator'
    # __extends__ = Tijdstip_e
    _type_info = element + [
        ('indOnvolledigeDatum', indOnvolledigeDatum),
        ('data', XmlData(simple_types.Tijdstip))
    ]

    @classmethod
    def to_django_value(cls, spyne_obj, django_field):
        if spyne_obj.data is None:
            return ''
        return '{}'.format(spyne_obj.data)

    @classmethod
    def to_spyne_value(cls, django_obj, spyne_field):
        # TODO: [TECH] implement indOnvolledigeDatum support
        return {
            'data': django_obj
        }

    @classmethod
    def django_field_type(cls):
        return StUFDateTimeField


class TijdvakGeldigheid(ComplexModel):
    __namespace__ = STUF_XML_NS
    __type_name__ = 'tijdvakGeldigheid'
    _type_info = [
        ('beginGeldigheid', DatumMetIndicator.customize(nillable=True)),
        ('eindGeldigheid', DatumMetIndicator.customize(nillable=True)),
    ]

    class Attributes(ComplexModel.Attributes):
        sub_ns = STUF_XML_NS


class TijdvakObject(ComplexModel):
    __namespace__ = STUF_XML_NS
    __type_name__ = 'TijdvakObject'
    _type_info = [
        ('beginGeldigheid', DatumMetIndicator.customize(nillable=True)),
        ('eindGeldigheid', DatumMetIndicator.customize(nillable=True, min_occurs=0)),
    ]


class TijdvakRelatie(ComplexModel):
    __namespace__ = STUF_XML_NS
    __type_name__ = 'TijdvakRelatie'
    _type_info = [
        ('beginRelatie', TijdstipMetIndicator.customize(nillable=True)),
        ('eindRelatie', TijdstipMetIndicator.customize(nillable=True, min_occurs=0)),
    ]


class Bv01BerichtStuurgegevens(ComplexModel):
    __namespace__ = STUF_XML_NS
    _type_info = [
        ('berichtcode', simple_types.Berichtcode.customize(pattern='Bv01')),  # fixed=Bv01
        ('zender', Systeem),
        ('ontvanger', Systeem),
        ('referentienummer', simple_types.Refnummer),
        ('tijdstipBericht', simple_types.Tijdstip),
        ('crossRefnummer', simple_types.Refnummer),
    ]


class Bv01Bericht(ComplexModel):
    __namespace__ = STUF_XML_NS
    __type_name__ = 'Bv01Bericht'
    _type_info = [
        ('stuurgegevens', Bv01BerichtStuurgegevens),
        ('melding', simple_types.Melding.customize(min_occurs=0, max_occurs=decimal.Decimal('inf'))),
    ]


class Bv02BerichtStuurgegevens(ComplexModel):
    __namespace__ = STUF_XML_NS
    _type_info = [
        ('berichtcode', simple_types.Berichtcode.customize(pattern='Bv02')),  # fixed=Bv02
    ]


class Bv02Bericht(ComplexModel):
    __namespace__ = STUF_XML_NS
    __type_name__ = 'Bv02Bericht'
    _type_info = [
        ('stuurgegevens', Bv02BerichtStuurgegevens),
        ('melding', simple_types.Melding.customize(min_occurs=0, max_occurs=decimal.Decimal('inf'))),
    ]


class Bv03BerichtStuurgegevens(ComplexModel):
    __namespace__ = STUF_XML_NS
    _type_info = [
        ('berichtcode', simple_types.Berichtcode.customize(pattern='Bv03')),  # fixed=Bv03
        ('zender', Systeem),
        ('ontvanger', Systeem),
        ('referentienummer', simple_types.Refnummer),
        ('tijdstipBericht', simple_types.Tijdstip),
        ('crossRefnummer', simple_types.Refnummer),
    ]


class Bv03Bericht(ComplexModel):
    __namespace__ = STUF_XML_NS
    __type_name__ = 'Bv03Bericht'
    _type_info = [
        ('stuurgegevens', Bv03BerichtStuurgegevens),
    ]


class Bv04BerichtStuurgegevens(ComplexModel):
    __namespace__ = STUF_XML_NS
    _type_info = [
        ('berichtcode', simple_types.Berichtcode.customize(pattern='Bv04')),
        ('zender', Systeem),
        ('ontvanger', Systeem),
        ('referentienummer', simple_types.Refnummer),
        ('tijdstipBericht', simple_types.Tijdstip),
        ('crossRefnummer', simple_types.Refnummer),
    ]


class Bv04Bericht(ComplexModel):
    __namespace__ = STUF_XML_NS
    __type_name__ = 'Bv04Bericht'
    _type_info = [
        ('stuurgegevens', Bv04BerichtStuurgegevens),
    ]


class BinaireInhoud(ComplexModel):
    __namespace__ = STUF_XML_NS
    __type_name__ = 'BinaireInhoud'
    _type_info = [
        ('data', XmlData(File)),
        ('bestandsnaam', XmlAttribute(attributes.Bestandsnaam, ref='bestandsnaam')),
        ('contentType', XmlAttribute(attributes.ContentType, ref='contentType')),
    ]

    def to_cmis(self) -> BytesIO:
        if self.data is None:
            return None

        self.data.rollover()
        self.data.handle.seek(0)
        encoded = self.data.handle.read()
        return BytesIO(base64.b64decode(encoded))


class ExtraElement(ComplexModel):
    __namespace__ = STUF_XML_NS
    __type_name__ = 'extraElement'
    _type_info = [
        ('data', XmlData(Unicode)),
        ('noValue', noValue),
        ('exact', exact),
        ('naam', XmlAttribute(Unicode.customize(min_occurs=1))),
        ('indOnvolledigeDatum', indOnvolledigeDatum),
    ]


class ExtraElementen(ComplexModel):
    __namespace__ = STUF_XML_NS
    __type_name__ = 'extraElementen'
    _type_info = [
        ('extraElement', ExtraElement.customize(min_occurs=1, max_occurs=decimal.Decimal('inf'))),
    ]
