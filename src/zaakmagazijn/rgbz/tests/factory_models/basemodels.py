import factory

from ....utils import stuf_datetime
from ...models import AdresBaseClass, NietNatuurlijkPersoonBaseClass


class NietNatuurlijkPersoonBaseClassFactory(factory.django.DjangoModelFactory):
    rsin = factory.Sequence(lambda n: n + 100000000)
    statutaire_naam = factory.Sequence(lambda n: 'Statutaire naam {0}'.format(n))
    datum_aanvang = stuf_datetime.today()

    class Meta:
        model = NietNatuurlijkPersoonBaseClass
        abstract = True


class AdresBaseClassFactory(factory.django.DjangoModelFactory):
    woonplaatsnaam = factory.Sequence(lambda n: 'woonplaats {}'.format(n))
    huisnummer = 1

    class Meta:
        model = AdresBaseClass
        abstract = True
