import factory

from ....rgbz.models import (
    BuurtObject, GemeenteObject, InrichtingsElementObject,
    KadastraalPerceelObject, Object,
    OverigeAdresseerbaarObjectAanduidingObject, WijkObject, ZaakObject
)
from ....utils import stuf_datetime
from ...choices import TyperingInrichtingselement
from .basemodels import AdresBaseClassFactory


class ObjectFactory(factory.django.DjangoModelFactory):
    identificatie = factory.Sequence(lambda n: '0000{0}'.format(n))

    class Meta:
        model = Object


class OverigeAdresseerbaarObjectAanduidingObjectFactory(ObjectFactory, AdresBaseClassFactory):
    datum_begin_geldigheid_adresseerbaar_object_aanduiding = stuf_datetime.today()
    datum_einde_geldigheid_adresseerbaar_object_aanduiding = stuf_datetime.today()

    class Meta:
        model = OverigeAdresseerbaarObjectAanduidingObject


class BuurtObjectFactory(ObjectFactory):
    buurtcode = factory.Sequence(lambda n: '{0}'.format(n))
    buurtnaam = factory.Sequence(lambda n: 'buurt {0}'.format(n))

    datum_begin_geldigheid_buurt = stuf_datetime.today()
    datum_einde_geldigheid_buurt = stuf_datetime.today()

    wijkcode = factory.Sequence(lambda n: '{0}'.format(n))
    gemeentecode = factory.Sequence(lambda n: '{0}'.format(n))

    class Meta:
        model = BuurtObject


class GemeenteObjectFactory(ObjectFactory):
    gemeentenaam = factory.Sequence(lambda n: 'gemeente {0}'.format(n))

    datum_begin_geldigheid_gemeente = stuf_datetime.today()
    datum_einde_geldigheid_gemeente = stuf_datetime.today()

    class Meta:
        model = GemeenteObject


class ZaakObjectFactory(factory.django.DjangoModelFactory):
    zaak = factory.SubFactory('zaakmagazijn.rgbz.tests.factory_models.ZaakFactory')
    object = factory.SubFactory('zaakmagazijn.rgbz.tests.factory_models.ObjectFactory')

    class Meta:
        model = ZaakObject


class ObjectMetZaakFactory(ObjectFactory):
    relation = factory.RelatedFactory('zaakmagazijn.rgbz.tests.factory_models.ZaakObjectFactory', 'object')


class WijkObjectFactory(ObjectFactory):
    wijkcode = factory.Sequence(lambda n: '{0}'.format(n))
    wijknaam = factory.Sequence(lambda n: 'wijknaam {0}'.format(n))
    datum_begin_geldigheid_wijk = stuf_datetime.today()
    gemeentecode = factory.Sequence(lambda n: '{0}'.format(n))

    class Meta:
        model = WijkObject


class InrichtingsElementObjectFactory(ObjectFactory):
    inrichtingselementtype = TyperingInrichtingselement.bak
    datum_begin_geldigheid_inrichtingselement = stuf_datetime.today()

    class Meta:
        model = InrichtingsElementObject


class KadastraalPerceelObjectFactory(ObjectFactory):
    begrenzing_perceel = 'abc'
    datum_begin_geldigheid_kadastrale_onroerende_zaak = stuf_datetime.today()

    class Meta:
        model = KadastraalPerceelObject
