from zaakmagazijn.rgbz.models import (
    AnderZaakObject, Contactpersoon, ZaakKenmerk, ZaakOpschorting,
    ZaakVerlenging
)
from zaakmagazijn.rsgb.models import (
    AdresMetPostcode, Correspondentieadres, LandGebied, Locatieadres,
    PostAdres, VerblijfBuitenland
)

from ..base import ModelProxy, ProxyField, ProxyForeignKey
from ..manager import ProxyManager


class AdresMetPostcodeProxy(ModelProxy):
    model = AdresMetPostcode
    fields = (
        ProxyField('woonplaatsnaam', 'woonplaatsnaam'),
        ProxyField('naam_openbare_ruimte', 'naam_openbare_ruimte'),
        ProxyField('huisletter', 'huisletter'),
        ProxyField('huisnummer', 'huisnummer'),
        ProxyField('huisnummertoevoeging', 'huisnummertoevoeging'),
        ProxyField('postcode', 'postcode')
    )
    objects = ProxyManager()


class LandGebiedProxy(ModelProxy):
    model = LandGebied
    fields = (
        ProxyField('landnaam', 'landnaam'),
    )
    objects = ProxyManager()


class VerblijfBuitenlandProxy(ModelProxy):
    model = VerblijfBuitenland
    fields = (
        ProxyField('adres_buitenland_1', 'adres_buitenland_1'),
        ProxyField('adres_buitenland_2', 'adres_buitenland_2'),
        ProxyField('adres_buitenland_3', 'adres_buitenland_3'),
        ProxyForeignKey('land', 'land', LandGebiedProxy)
        # ProxyField('land__landnaam', 'land__landnaam')
    )
    objects = ProxyManager()


class LocatieadresProxy(ModelProxy):
    model = Locatieadres
    fields = (
        ProxyField('huisnummer', 'huisnummer'),
        ProxyField('huisletter', 'huisletter'),
        ProxyField('huisnummertoevoeging', 'huisnummertoevoeging'),
        ProxyField('naam_openbare_ruimte', 'naam_openbare_ruimte'),
        ProxyField('straatnaam', 'straatnaam'),
        ProxyField('postcode', 'postcode'),
        ProxyField('woonplaatsnaam', 'woonplaatsnaam'),
    )
    objects = ProxyManager()


class CorrespondentieadresProxy(ModelProxy):
    model = Correspondentieadres
    fields = (
        #    ADRESSEERBAAR OBJECT AANDUIDING .  Huisnummer    RSGB.ADRESSEERBAAR OBJECT AANDUIDING.Huisnummer
        ProxyField('huisnummer', 'huisnummer'),
        #    ADRESSEERBAAR OBJECT AANDUIDING . Huisletter     RSGB.ADRESSEERBAAR OBJECT AANDUIDING.Huisletter
        ProxyField('huisletter', 'huisletter'),
        #    ADRESSEERBAAR OBJECT AANDUIDING .  Huisnummertoevoeging  RSGB.ADRESSEERBAAR OBJECT AANDUIDING.Huisnummertoevoeging
        ProxyField('huisnummertoevoeging', 'huisnummertoevoeging'),
        #    GEMEENTELIJKE OPENBARE RUIMTE .  Naam openbare ruimte    RSGB.OPENBARE RUIMTE.Naam openbare ruimte
        ProxyField('naam_openbare_ruimte', 'naam_openbare_ruimte'),
        #    GEMEENTELIJKE OPENBARE RUIMTE .  Straatnaam  RSGB.OPENBARE RUIMTE.Straatnaam
        ProxyField('straatnaam', 'straatnaam'),
        #    ADRESSEERBAAR OBJECT AANDUIDING . Postcode   RSGB.ADRESSEERBAAR OBJECT AANDUIDING.Postcode
        ProxyField('postcode', 'postcode'),
        #    WOONPLAATS . Woonplaatsnaam  RSGB.WOONPLAATS.Woonplaatsnaam
        ProxyField('woonplaatsnaam', 'woonplaatsnaam'),
    )
    objects = ProxyManager()


class PostAdresProxy(ModelProxy):
    model = PostAdres
    fields = (
        ProxyField('postadrestype', 'postadrestype'),
        ProxyField('postbus_of_antwoordnummer', 'postbus_of_antwoordnummer'),
        ProxyField('postadres_postcode', 'postadres_postcode'),
        ProxyField(None, 'woonplaatsnaam'),
    )


class ZaakKenmerkProxy(ModelProxy):
    model = ZaakKenmerk
    fields = (
        ProxyField('kenmerk', 'kenmerk'),
        ProxyField('kenmerk_bron', 'kenmerk_bron'),
    )
    objects = ProxyManager()


class ZaakOpschortingProxy(ModelProxy):
    model = ZaakOpschorting
    fields = (
        ProxyField('indicatie_opschorting', 'indicatie_opschorting'),
        ProxyField('reden_opschorting', 'reden_opschorting'),
    )
    objects = ProxyManager()


class ZaakVerlengingProxy(ModelProxy):
    model = ZaakVerlenging
    fields = (
        ProxyField('duur_verlenging', 'duur_verlenging'),
        ProxyField('reden_verlenging', 'reden_verlenging'),
    )
    objects = ProxyManager()


class AnderZaakObjectProxy(ModelProxy):
    model = AnderZaakObject
    fields = (
        ProxyField('ander_zaakobject_omschrijving', 'ander_zaakobject_omschrijving'),
        ProxyField('ander_zaakobject_aanduiding', 'ander_zaakobject_aanduiding'),
        ProxyField('ander_zaakobject_lokatie', 'ander_zaakobject_lokatie'),
        ProxyField('ander_zaakobject_registratie', 'ander_zaakobject_registratie'),

        ProxyForeignKey('zaak', 'zaak', 'zaakmagazijn.rgbz_mapping.models.ZaakProxy'),

    )
    objects = ProxyManager()


class ContactpersoonProxy(ModelProxy):
    model = Contactpersoon
    fields = (
        ProxyField('contactpersoonnaam', 'contactpersoonnaam'),
        ProxyField('contactpersoon_functie', 'contactpersoon_functie'),
        ProxyField('contactpersoon_telefoonnummer', 'contactpersoon_telefoonnummer'),
        ProxyField('contactpersoon_emailadres', 'contactpersoon_emailadres'),
    )
    objects = ProxyManager()
