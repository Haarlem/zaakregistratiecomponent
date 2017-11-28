import decimal

from spyne import ComplexModel, XmlAttribute

from zaakmagazijn.api.stuf.constants import STUF_XML_NS, ZKN_XML_NS

from ...stuf import simple_types
from ...stuf.models import Systeem

# Du01


class Du01_Stuurgegevens_oz(ComplexModel):
    __namespace__ = STUF_XML_NS
    __type_name__ = 'Du01-Stuurgegevens-oz'
    _type_info = [
        ('berichtcode', simple_types.Berichtcode.customize(fixed='Du01')),
        ('zender', Systeem),
        ('ontvanger', Systeem),
        ('referentienummer', simple_types.Refnummer),
        ('tijdstipBericht', simple_types.Tijdstip),
        ('crossRefnummer', simple_types.Refnummer),
        ('functie', simple_types.FunctieoverdragenZaak),
    ]


class OverdragenZaak_ZAK_opdrachtbevestiging_r(ComplexModel):
    __namespace__ = ZKN_XML_NS
    __type_name__ = 'OverdragenZaak-ZAK-opdrachtbevestiging-r'
    _type_info = [
        # Attributes
        ('entiteittype', XmlAttribute(simple_types.Entiteittype.customize(fixed='ZAK'), ref='entiteittype')),
        # <attribute ref="StUF:sleutelVerzendend"/>
        # <attribute ref="StUF:sleutelOntvangend"/>
        # <attribute ref="StUF:sleutelGegevensbeheer"/>
        # <attribute ref="StUF:sleutelSynchronisatie"/>
        # <attribute ref="StUF:noValue"/>
        # <attribute ref="StUF:scope"/>
        # <attribute ref="StUF:verwerkingssoort"/>
        # Elements
        ('identificatie', simple_types.ZaakIdentificatie_r),
    ]


class OverdragenZaak_ZAK_opdrachtbevestiging_e(ComplexModel):
    __namespace__ = ZKN_XML_NS
    __type_name__ = 'OverdragenZaak-ZAK-opdrachtbevestiging-e'
    __extends__ = OverdragenZaak_ZAK_opdrachtbevestiging_r
    _type_info = [
        # Attributes
        ('functie', XmlAttribute(simple_types.FunctieVrijBerichtElement.customize(fixed='entiteit'), ref='functie')),  # use=required, default should be fixed
        # Elements
        ('antwoord', simple_types.OverdragenZaak_antwoord),
    ]


class Du01_overdragenZaak(ComplexModel):
    __namespace__ = ZKN_XML_NS
    __type_name__ = 'Du01_overdragenZaak'
    _type_info = [
        ('stuurgegevens', Du01_Stuurgegevens_oz),
        ('melding', simple_types.Melding.customize(min_occurs=0, max_occurs=decimal.Decimal('inf'))),
        ('object', OverdragenZaak_ZAK_opdrachtbevestiging_e),
    ]

# Di01


class Di01_Stuurgegevens_oz(ComplexModel):
    __namespace__ = STUF_XML_NS
    __type_name__ = 'Di01-Stuurgegevens-oz'
    _type_info = [
        ('berichtcode', simple_types.Berichtcode.customize(fixed='Di01')),
        ('zender', Systeem),
        ('ontvanger', Systeem),
        ('referentienummer', simple_types.Refnummer),
        ('tijdstipBericht', simple_types.Tijdstip),
        ('functie', simple_types.FunctieoverdragenZaak),
    ]


class OverdragenZaak_ZKT_kerngegevens(ComplexModel):
    __namespace__ = ZKN_XML_NS
    __type_name__ = 'OverdragenZaak-ZKT-kerngegevens'
    _type_info = [
        # Attributes
        ('entiteittype', XmlAttribute(simple_types.Entiteittype.customize(fixed='ZKT'), ref='entiteittype')),
        # <attribute ref="StUF:sleutelVerzendend"/>
        # <attribute ref="StUF:sleutelOntvangend"/>
        # <attribute ref="StUF:sleutelGegevensbeheer"/>
        # <attribute ref="StUF:sleutelSynchronisatie"/>
        # <attribute ref="StUF:verwerkingssoort"/>
        # Elements
        ('omschrijving', simple_types.Omschrijving),  # Omschrijving-e
        ('code', simple_types.Code),  # Code-e
        # ('ingangsdatumObject', DatumMetIndicator.customize(nillable=True, min_occurs=0))
    ]


class OverdragenZaak_ZAKZKT_kerngegevens(ComplexModel):
    __namespace__ = ZKN_XML_NS
    __type_name__ = 'OverdragenZaak-ZAKZKT-kerngegevens'
    _type_info = [
        # Attributes
        ('entiteittype', XmlAttribute(simple_types.Entiteittype.customize(fixed='ZAKZKT'), ref='entiteittype')),
        # <attribute ref="StUF:aantalVoorkomens"/>
        # <attribute ref="StUF:aardAantal"/>
        # <attribute ref="StUF:sleutelVerzendend"/>
        # <attribute ref="StUF:sleutelOntvangend"/>
        # <attribute ref="StUF:sleutelGegevensbeheer"/>
        # <attribute ref="StUF:sleutelSynchronisatie"/>
        # <attribute ref="StUF:noValue"/>
        # <attribute ref="StUF:verwerkingssoort"/>
        # Elements
        ('gerelateerde', OverdragenZaak_ZKT_kerngegevens)
    ]


class OverdragenZaak_ZAK_opdracht_r(ComplexModel):
    __namespace__ = ZKN_XML_NS
    __type_name__ = 'OverdragenZaak-ZAK-opdracht-r'
    _type_info = [
        # Attributes
        ('entiteittype', XmlAttribute(simple_types.Entiteittype.customize(fixed='ZAK'), ref='entiteittype')),
        # <attribute ref="StUF:sleutelVerzendend"/>
        # <attribute ref="StUF:sleutelOntvangend"/>
        # <attribute ref="StUF:sleutelGegevensbeheer"/>
        # <attribute ref="StUF:sleutelSynchronisatie"/>
        # <attribute ref="StUF:noValue"/>
        # <attribute ref="StUF:scope"/>
        # <attribute ref="StUF:verwerkingssoort"/>
        ('identificatie', simple_types.ZaakIdentificatie_r),
        ('isVan', OverdragenZaak_ZAKZKT_kerngegevens.customize(nillable=True)),
    ]


class OverdragenZaak_ZAK_opdracht_e(ComplexModel):
    __namespace__ = ZKN_XML_NS
    __type_name__ = 'OverdragenZaak-ZAK-opdracht-e'
    __extends__ = OverdragenZaak_ZAK_opdracht_r
    _type_info = [
        # Attributes
        ('functie', XmlAttribute(simple_types.FunctieVrijBerichtElement.customize(fixed='entiteit'), ref='functie')),  # use=required
    ]


class DI01_overdragenZaak(ComplexModel):
    __namespace__ = STUF_XML_NS
    __type_name__ = 'DI01_overdragenZaak'
    _type_info = [
        ('stuurgegevens', Di01_Stuurgegevens_oz),
        ('melding', simple_types.Melding.customize(min_occurs=0, max_occurs=decimal.Decimal('inf'))),
        ('object', OverdragenZaak_ZAK_opdracht_e),
    ]
