from zaakmagazijn.rgbz.models import Besluit, BesluitType

from ..base import ModelProxy, ProxyField, ProxyForeignKey
from ..manager import ProxyManager


class BesluitTypeProxy(ModelProxy):
    model = BesluitType
    objects = ProxyManager()
    fields = (
        ProxyField('besluittypeomschrijving', 'besluittypeomschrijving'),
        ProxyField(None, 'domein'),
        ProxyField(None, 'rsin'),
        ProxyField('besluittypeomschrijving_generiek', 'besluittypeomschrijving_generiek'),
        ProxyField('besluitcategorie', 'besluitcategorie'),
        ProxyField('reactietermijn', 'reactietermijn'),
        ProxyField('publicatie_indicatie', 'publicatie_indicatie'),
        ProxyField('publicatietekst', 'publicatietekst'),
        ProxyField('publicatietermijn', 'publicatietermijn'),
        ProxyField('datum_begin_geldigheid_besluittype', 'datum_begin_geldigheid_besluittype'),
        ProxyField('datum_einde_geldigheid_besluittype', 'datum_einde_geldigheid_besluittype'),
    )


class BesluitProxy(ModelProxy):
    model = Besluit
    objects = ProxyManager()
    fields = (
        ProxyField('besluitidentificatie', 'identificatie'),
        ProxyField('besluitdatum', 'besluitdatum'),
        ProxyField('besluittoelichting', 'besluittoelichting'),
        ProxyField(None, 'bestuursorgaan'),
        ProxyField('ingangsdatum', 'ingangsdatum'),
        ProxyField('vervaldatum', 'vervaldatum'),
        ProxyField('vervalreden', 'vervalreden'),
        ProxyField('publicatiedatum', 'publicatiedatum'),
        ProxyField('verzenddatum', 'verzenddatum'),
        ProxyField('uiterlijke_reactiedatum', 'uiterlijke_reactiedatum'),
        ProxyForeignKey('besluittype', 'besluittype', BesluitTypeProxy),
        ProxyForeignKey('zaak', 'zaak', 'zaakmagazijn.rgbz_mapping.models.Zaak'),
        ProxyForeignKey('informatieobject', 'informatieobject', 'zaakmagazijn.rgbz_mapping.models.Zaak'),
    )
