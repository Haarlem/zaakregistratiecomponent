import factory

from ...models import (
    AdresMetPostcode, Bezoekadres, Correspondentieadres, KadastraleAanduiding,
    KadastraleAanduidingBaseClass, Locatieadres, PostAdres, PostadresType,
    VerblijfAdres, VerblijfBuitenland
)


class AdresMetPostcodeFactory(factory.django.DjangoModelFactory):
    woonplaatsnaam = factory.Sequence(lambda n: 'woonplaatsnaam {0}'.format(n))
    naam_openbare_ruimte = factory.Sequence(lambda n: 'naam_openbare_ruimte {0}'.format(n))
    huisnummer = factory.Sequence(lambda n: n + 1)

    class Meta:
        model = AdresMetPostcode


class CorrespondentieadresFactory(AdresMetPostcodeFactory):
    straatnaam = factory.sequence(lambda n: 'straatnaam {0}'.format(n))

    class Meta:
        model = Correspondentieadres


class BezoekadresFactory(CorrespondentieadresFactory):
    class Meta:
        model = Bezoekadres


class LocatieadresFactory(CorrespondentieadresFactory):
    class Meta:
        model = Locatieadres


class VerblijfAdresFactory(AdresMetPostcodeFactory):
    straatnaam = factory.sequence(lambda n: 'straatnaam {0}'.format(n))
    locatie_beschrijving = factory.Sequence(lambda n: 'Dit is een locatiebeschrijving{0}'.format(n))

    class Meta:
        model = VerblijfAdres


class PostAdresFactory(factory.django.DjangoModelFactory):
    postadres_postcode = factory.Sequence(lambda n: '300{0}'.format(n))
    postadrestype = PostadresType.postbusnummer
    postbus_of_antwoordnummer = factory.Sequence(lambda n: 'num'.format(n))
    woonplaatsnaam = factory.sequence(lambda n: 'Woonplaats naam {0}'.format(n))

    class Meta:
        model = PostAdres


class VerblijfBuitenlandFactory(factory.django.DjangoModelFactory):
    adres_buitenland_1 = factory.Sequence(lambda n: 'Adres buiteland 1 {0}'.format(n))
    land = factory.SubFactory('zaakmagazijn.rsgb.tests.factory_models.LandGebiedFactory')

    class Meta:
        model = VerblijfBuitenland


class KadastraleAanduidingBaseClassFactory(factory.django.DjangoModelFactory):
    kadastralegemeentecode = factory.Sequence(lambda n: 'GE{0}'.format(n))
    perceelnummer = factory.sequence(lambda n: n)
    sectie = 'AN'

    class Meta:
        model = KadastraleAanduidingBaseClass
        abstract = True


class KadastraleAanduidingFactory(KadastraleAanduidingBaseClassFactory):
    appartementsrechtvolgnummer = factory.sequence(lambda n: n)

    class Meta:
        model = KadastraleAanduiding
