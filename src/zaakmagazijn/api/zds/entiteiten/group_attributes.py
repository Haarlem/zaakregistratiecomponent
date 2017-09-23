from zaakmagazijn.rgbz.models import (
    AnderZaakObject, Contactpersoon, ZaakKenmerk, ZaakOpschorting,
    ZaakVerlenging
)

from ...stuf import StUFEntiteit, StUFGegevensgroep


class KenmerkGegevensgroep(StUFGegevensgroep):
    model = ZaakKenmerk
    field_mapping = (
        ('kenmerk', 'kenmerk'),
        ('bron', 'kenmerk_bron'),
    )


class OpschortingGegevensgroep(StUFGegevensgroep):
    model = ZaakOpschorting
    field_mapping = (
        ('indicatie', 'indicatie_opschorting'),
        ('reden', 'reden_opschorting'),
    )


class VerlengingGegevensgroep(StUFGegevensgroep):
    model = ZaakVerlenging
    field_mapping = (
        ('duur', 'duur_verlenging'),
        ('reden', 'reden_verlenging'),
    )


class AnderZaakObjectGegevensgroep(StUFGegevensgroep):
    model = AnderZaakObject
    field_mapping = (
        ('omschrijving', 'ander_zaakobject_omschrijving'),
        ('aanduiding', 'ander_zaakobject_aanduiding'),
        ('lokatie', 'ander_zaakobject_lokatie'),
        ('registratie', 'ander_zaakobject_registratie'),
    )


class CTPEntiteit(StUFEntiteit):
    model = Contactpersoon
    mnemonic = 'CTP'
