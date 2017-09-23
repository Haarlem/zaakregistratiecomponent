import factory

from ...choices import GeslachtsAanduiding
from ...models import BSNMixin, GeslachtsAanduidingMixin, Rekeningnummer


class RekeningnummerFactory(factory.django.DjangoModelFactory):
    iban = factory.Sequence(lambda n: 'iban{0}'.format(n))
    bic = factory.Sequence(lambda n: 'ABNA{0}03'.format(n))

    class Meta:
        model = Rekeningnummer


class BSNMixinFactory(factory.django.DjangoModelFactory):
    burgerservicenummer = factory.Sequence(lambda n: int('3928{0}'.format(n)))

    class Meta:
        model = BSNMixin
        abstract = True


class GeslachtsAanduidingMixinFactory(factory.django.DjangoModelFactory):
    geslachtsaanduiding = GeslachtsAanduiding.man

    class Meta:
        model = GeslachtsAanduidingMixin
        abstract = True
