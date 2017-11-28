from zaakmagazijn.rgbz_mapping.models import (
    AnderZaakObjectProxy, ZaakKenmerkProxy, ZaakOpschortingProxy, ZaakProxy,
    ZaakVerlengingProxy
)

from ...stuf import StUFGegevensgroep


class KenmerkGegevensgroep(StUFGegevensgroep):
    model = ZaakKenmerkProxy
    field_mapping = (
        ('kenmerk', 'kenmerk'),
        ('bron', 'kenmerk_bron'),
    )


class OpschortingGegevensgroep(StUFGegevensgroep):
    model = ZaakOpschortingProxy
    field_mapping = (
        ('indicatie', 'indicatie_opschorting'),
        ('reden', 'reden_opschorting'),
    )


class VerlengingGegevensgroep(StUFGegevensgroep):
    model = ZaakVerlengingProxy
    field_mapping = (
        ('duur', 'duur_verlenging'),
        ('reden', 'reden_verlenging'),
    )


class AnderZaakObjectGegevensgroep(StUFGegevensgroep):
    model = AnderZaakObjectProxy
    field_mapping = (
        ('omschrijving', 'ander_zaakobject_omschrijving'),
        ('aanduiding', 'ander_zaakobject_aanduiding'),
        ('lokatie', 'ander_zaakobject_lokatie'),
        ('registratie', 'ander_zaakobject_registratie'),
    )
    required_fields = (
        'lokatie',
    )


class ResultaatGegevensgroep(StUFGegevensgroep):
    model = ZaakProxy
    field_mapping = (
        ('omschrijving', 'resultaatomschrijving'),
        ('toelichting', 'resultaattoelichting'),
    )
