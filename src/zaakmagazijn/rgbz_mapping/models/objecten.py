from zaakmagazijn.rgbz.models import (
    BuurtObject, GemeentelijkeOpenbareRuimteObject, GemeenteObject,
    HuishoudenObject, InrichtingsElementObject, KadastraalPerceelObject,
    KunstwerkDeelObject, MaatschappelijkeActiviteitObject, Object,
    OpenbareRuimteObject, OverigeAdresseerbaarObjectAanduidingObject,
    OverigGebouwdObject, PandObject, SpoorbaanDeelObject, TerreinDeelObject,
    WaterdeelObject, WegdeelObject, WijkObject, WoonplaatsObject,
    WozdeelObject, WozObject, WozWaardeObject, ZaakObject, ZakelijkRechtObject
)
from zaakmagazijn.rsgb.models import (
    AardZakelijkRecht, AdresMetPostcode, Deelobjectcode, KadastraleAanduiding,
    SoortWOZObject
)

from ..base import AutoMapper, ModelProxy, ProxyField, ProxyForeignKey
from ..manager import ProxyManager
from ..registry import proxy_registry


class ObjectProxy(ModelProxy):
    model = Object
    fields = ()

    def is_type(self):
        django_obj = self.to_django_obj()
        child_obj = django_obj.is_type()
        child_proxy_model = proxy_registry.get_proxy_model(child_obj.__class__)

        return child_proxy_model.from_django_obj(child_obj)


class OverigeAdresseerbaarObjectAanduidingObjectProxy(ModelProxy):
    model = OverigeAdresseerbaarObjectAanduidingObject

    fields = (
        ProxyField('identificatie', 'identificatie'),
        ProxyField('woonplaatsnaam', 'woonplaatsnaam'),
        ProxyField('naam_openbare_ruimte', 'naam_openbare_ruimte'),
        ProxyField('huisnummer', 'huisnummer'),
        ProxyField('huisletter', 'huisletter'),
        ProxyField('huisnummertoevoeging', 'huisnummertoevoeging'),
        ProxyField('postcode', 'postcode'),
        ProxyField('datum_begin_geldigheid_adresseerbaar_object_aanduiding', 'datum_begin_geldigheid_adresseerbaar_object_aanduiding'),
        ProxyField('datum_einde_geldigheid_adresseerbaar_object_aanduiding', 'datum_einde_geldigheid_adresseerbaar_object_aanduiding'),
    )
    objects = ProxyManager()


class BuurtObjectProxy(ModelProxy):
    model = BuurtObject
    fields = AutoMapper()
    objects = ProxyManager()


class GemeenteObjectProxy(ModelProxy):
    model = GemeenteObject
    fields = AutoMapper()
    objects = ProxyManager()


class GemeentelijkeOpenbareRuimteObjectProxy(ModelProxy):
    model = GemeentelijkeOpenbareRuimteObject
    fields = AutoMapper()
    objects = ProxyManager()


class InrichtingsElementObjectProxy(ModelProxy):
    model = InrichtingsElementObject
    fields = AutoMapper()
    objects = ProxyManager()


class KadastraleAanduidingProxy(ModelProxy):
    model = KadastraleAanduiding
    fields = AutoMapper()
    objects = ProxyManager()


class KadastraalPerceelObjectProxy(ModelProxy):
    model = KadastraalPerceelObject

    fields = (
        ProxyField('identificatie', 'identificatie'),
        ProxyField('begrenzing_perceel', 'begrenzing_perceel'),
        ProxyField('datum_begin_geldigheid_kadastrale_onroerende_zaak', 'datum_begin_geldigheid_kadastrale_onroerende_zaak'),
        ProxyField('datum_einde_geldigheid_kadastrale_onroerende_zaak', 'datum_einde_geldigheid_kadastrale_onroerende_zaak'),
        ProxyForeignKey('kadastrale_aanduiding', 'kadastrale_aanduiding', KadastraleAanduidingProxy)
    )
    objects = ProxyManager()


class HuishoudenObjectProxy(ModelProxy):
    model = HuishoudenObject
    fields = AutoMapper()
    objects = ProxyManager()


class KunstwerkDeelObjectProxy(ModelProxy):
    model = KunstwerkDeelObject
    fields = AutoMapper()
    objects = ProxyManager()


class MaatschappelijkeActiviteitObjectProxy(ModelProxy):
    model = MaatschappelijkeActiviteitObject
    fields = AutoMapper()
    objects = ProxyManager()


class OpenbareRuimteObjectProxy(ModelProxy):
    model = OpenbareRuimteObject
    fields = AutoMapper()
    objects = ProxyManager()


class PandObjectProxy(ModelProxy):
    model = PandObject
    fields = AutoMapper()
    objects = ProxyManager()


class SpoorbaanDeelObjectProxy(ModelProxy):
    model = SpoorbaanDeelObject
    fields = AutoMapper()
    objects = ProxyManager()


class TerreinDeelObjectProxy(ModelProxy):
    model = TerreinDeelObject
    fields = AutoMapper()
    objects = ProxyManager()


class AdresMetPostcodeProxy(ModelProxy):
    model = AdresMetPostcode
    fields = AutoMapper()
    objects = ProxyManager()


class OverigGebouwdObjectProxy(ModelProxy):
    model = OverigGebouwdObject
    objects = ProxyManager()
    fields = (
        ProxyField('geometrie', 'geometrie'),
        ProxyField('datum_begin_geldigheid', 'datum_begin_geldigheid'),
        ProxyField('datum_einde_geldigheid', 'datum_einde_geldigheid'),
        ProxyForeignKey('locatieadres', 'locatieadres', AdresMetPostcodeProxy),
    )


class WaterdeelObjectProxy(ModelProxy):
    model = WaterdeelObject
    fields = AutoMapper()
    objects = ProxyManager()


class WegdeelObjectProxy(ModelProxy):
    model = WegdeelObject
    fields = AutoMapper()
    objects = ProxyManager()


class WijkObjectProxy(ModelProxy):
    model = WijkObject
    fields = AutoMapper()
    objects = ProxyManager()


class WoonplaatsObjectProxy(ModelProxy):
    model = WoonplaatsObject
    fields = AutoMapper()
    objects = ProxyManager()


class DeelobjectcodeProxy(ModelProxy):
    model = Deelobjectcode
    fields = AutoMapper()
    objects = ProxyManager()


class WozdeelObjectProxy(ModelProxy):
    model = WozdeelObject
    fields = (
        ProxyField('nummer_wozdeelobject', 'nummer_wozdeelobject'),
        ProxyForeignKey('code_wozdeelobject', 'code_wozdeelobject', DeelobjectcodeProxy),
        ProxyField('datum_begin_geldigheid_deelobject', 'datum_begin_geldigheid_deelobject'),
        ProxyField('datum_einde_geldigheid_deelobject', 'datum_einde_geldigheid_deelobject'),
    )
    objects = ProxyManager()


class SoortWozObjectProxy(ModelProxy):
    model = SoortWOZObject
    fields = AutoMapper()
    objects = ProxyManager()


class WozObjectProxy(ModelProxy):
    model = WozObject
    fields = (
        ProxyField('identificatie', 'identificatie'),
        ProxyField('geometrie', 'geometrie'),
        ProxyForeignKey('soortobjectcode', 'soortobjectcode', SoortWozObjectProxy),
        ProxyField('datum_begin_geldigheid_wozobject', 'datum_begin_geldigheid_wozobject'),
        ProxyField('datum_einde_geldigheid_wozobject', 'datum_einde_geldigheid_wozobject'),
        ProxyForeignKey('adresaanduiding', 'adresaanduiding', AdresMetPostcodeProxy),
    )
    objects = ProxyManager()


class WozWaardeObjectProxy(ModelProxy):
    model = WozWaardeObject
    fields = AutoMapper()
    objects = ProxyManager()


class AardZakelijkRechtProxy(ModelProxy):
    model = AardZakelijkRecht
    fields = AutoMapper()
    objects = ProxyManager()


class ZakelijkRechtObjectProxy(ModelProxy):
    model = ZakelijkRechtObject
    fields = (
        ProxyField('identificatie', 'identificatie'),
        ProxyForeignKey('aanduiding_aard_verkregen_recht', 'aanduiding_aard_verkregen_recht', AardZakelijkRechtProxy),
        ProxyField('ingangsdatum_recht', 'ingangsdatum_recht'),
        ProxyField('einddatum_recht', 'einddatum_recht'),
    )
    objects = ProxyManager()


class ZaakObjectProxy(ModelProxy):
    model = ZaakObject
    fields = (
        ProxyForeignKey('object', 'object', ObjectProxy),
        ProxyField('relatieomschrijving', 'relatieomschrijving'),
    )
    objects = ProxyManager()
