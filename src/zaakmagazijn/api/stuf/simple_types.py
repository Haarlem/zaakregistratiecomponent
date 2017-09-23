from django.conf import settings

from spyne import (
    AnyXml, Boolean, Decimal, Integer, NonNegativeInteger, SimpleModel,
    Unicode
)

from .constants import BG_XML_NS, STUF_XML_NS, XMIME_XML_NS


def Mandatory(cls, **_kwargs):
    kwargs = dict(min_occurs=1, nillable=False)

    return cls.customize(**kwargs)


# StUF simple types

# Wordt zowel als attribute als Type gebruikt.
AantalVoorkomens = NonNegativeInteger.customize(__namespace__=STUF_XML_NS, type_name='AantalVoorkomens')

Administratie = Mandatory(Unicode.customize(__namespace__=STUF_XML_NS, type_name='Administratie', max_len=50))

Applicatie = Mandatory(Unicode.customize(__namespace__=STUF_XML_NS, type_name='Applicatie', min_len=3, max_len=50))

Berichtcode = Mandatory(Unicode.customize(__namespace__=STUF_XML_NS, type_name='Berichtcode'))

Code = Mandatory(Unicode.customize(__namespace__=STUF_XML_NS, type_name='Code', max_len=10))

Datum = Decimal.customize(__namespace__=STUF_XML_NS, type_name='Datum', total_digits=8, fraction_digits=0)

Entiteittype = Unicode.customize(__namespace__=STUF_XML_NS, type_name='Entiteittype', max_len=30)

EntiteittypeBSL = Entiteittype.customize(__namespace__=STUF_XML_NS, type_name='EntiteittypeBSL', pattern='BSL')

EntiteittypeEDC = Entiteittype.customize(__namespace__=STUF_XML_NS, type_name='EntiteittypeEDC', pattern='EDC')

EntiteittypeZAK = Entiteittype.customize(__namespace__=STUF_XML_NS, type_name='EntiteittypeZAK', pattern='ZAK')


# NOTE: Exact Should not even be defined. It should be just a Boolean but Spyne bugs out in tht case.
class Exact(SimpleModel):
    __extends__ = Boolean
    __type_name__ = 'Exact'
    __namespace__ = STUF_XML_NS

    class Attributes(SimpleModel.Attributes):
        default = 'true'

    @classmethod
    def from_string(cls, value):
        if value == 'true':
            return True
        return False

    @classmethod
    def to_unicode(cls, value):
        return str(value).lower()


Foutcode = Mandatory(Unicode.customize(__namespace__=STUF_XML_NS, type_name='Foutcode', max_len=7))

Foutplek = Mandatory(Unicode.customize(__namespace__=STUF_XML_NS, type_name='Foutplek', values={'client', 'server'}))

Foutomschrijving = Mandatory(Unicode.customize(__namespace__=STUF_XML_NS, type_name='Foutomschrijving', max_len=200))

Foutdetails = Mandatory(Unicode.customize(__namespace__=STUF_XML_NS, type_name='Foutdetails', max_len=1000))

FoutdetailsXML = AnyXml.customize(__namespace__=STUF_XML_NS, type_name='FoutdetailsXML')

Functie = Unicode.customize(__namespace__=STUF_XML_NS, type_name='Functie', max_len=30)

FunctieoverdragenZaak = Functie.customize(__namespace__=STUF_XML_NS, type_name='FunctieoverdragenZaak', values={'overdragenZaak', })

FunctieVrijBerichtElement = Unicode.customize(__namespace__=STUF_XML_NS, type_name='FunctieVrijBerichtElement', values={'antwoord', 'entiteit', 'selectie', 'update', 'zaakinfo'})

FunctievoegBesluitToe = Functie.customize(__namespace__=STUF_XML_NS, type_name='FunctievoegBesluitToe', values={'voegBesluitToe', })

Gebruiker = Mandatory(Unicode.customize(__namespace__=STUF_XML_NS, type_name='Gebruiker', max_len=100))

IndicatorOvername = Mandatory(Unicode.customize(__namespace__=STUF_XML_NS, type_name='IndicatorOvername', values={'I', 'V'}))

MaximumAantal = Integer.customize(__namespace__=STUF_XML_NS, type_name='MaximumAantal', default=settings.ZAAKMAGAZIJN_DEFAULT_MAX_NR_RESULTS, total_digits=8)

Melding = Mandatory(Unicode.customize(__namespace__=STUF_XML_NS, type_name='Melding', max_len=250))

Mutatiesoort = Functie.customize(__namespace__=STUF_XML_NS, type_name='Mutatiesoort', values={'T', 'W', 'V', 'E', 'I', 'R', 'S', 'O'})

Omschrijving = Mandatory(Unicode.customize(__namespace__=STUF_XML_NS, type_name='Omschrijving', max_len=80))

Organisatie = Mandatory(Unicode.customize(__namespace__=STUF_XML_NS, typespe_name='Organisatie', max_len=200))

OverdragenZaak_antwoord = Mandatory(Unicode(__namespace__=STUF_XML_NS, type_name='OverdragenZaak-antwoord', values={'Overdracht geaccepteerd', 'Overdracht geweigerd'}))

Refnummer = Mandatory(Unicode.customize(__namespace__=STUF_XML_NS, type_name='Refnummer', max_len=40))


Sortering = NonNegativeInteger.customize(__namespace__=STUF_XML_NS, type_name='Sortering', total_digits=2)

Tijdstip = Mandatory(Unicode.customize(__namespace__=STUF_XML_NS, type_name='Tijdstip', pattern='[0-9]{8,17}'))

ZaakIdentificatie_r = Unicode.customize(__namespace__=STUF_XML_NS, type_name='ZaakIdentificatie-r', min_len=5, max_len=40)

BSL_sortering = Sortering.customize(__namespace__=STUF_XML_NS, type_name='BSL-sortering', ge=0, le=9)

# Defined as Unicodes instead of Booleans, as Spyne doesn't seem to like 'em.
StufBoolean = Unicode.customize(default="false", pattern="(true|false)")

ZAK_sortering = Sortering.customize(__namespace__=STUF_XML_NS, type_name='ZAK-sortering', ge=0, le=13)

EDC_sortering = Sortering.customize(__namespace__=STUF_XML_NS, type_name='EDC-sortering', ge=0, le=9)

GeometrieIMGeo_e = AnyXml.customize(__namespace__=BG_XML_NS, type_name='GeometrieIMGeo-e')
