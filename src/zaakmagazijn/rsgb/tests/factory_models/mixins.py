import factory

from ....rgbz.models import BereikenMixin, RekeningnummerMixin
from ....rgbz.tests.factory_models.mixins import RekeningnummerFactory


class BereikenMixinFactory(factory.django.DjangoModelFactory):
    telefoonnummer = factory.Sequence(lambda n: '0600{0}'.format(n))
    emailadres = factory.Sequence(lambda n: 'test{0}@email.country'.format(n))
    faxnummer = factory.Sequence(lambda n: '15555{0}'.format(n))

    class Meta:
        model = BereikenMixin
        abstract = True


class RekeningnummerMixinFactory(factory.django.DjangoModelFactory):
    rekeningnummer = factory.SubFactory(RekeningnummerFactory)

    class Meta:
        model = RekeningnummerMixin
        abstract = True
