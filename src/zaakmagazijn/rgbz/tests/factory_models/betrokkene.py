import factory

from ....rsgb.tests.factory_models.mixins import (
    BereikenMixinFactory, RekeningnummerMixinFactory
)
from ....utils import stuf_datetime
from ...choices import (
    AardRelatieVerzending, GeslachtsAanduiding, Rolomschrijving,
    RolomschrijvingGeneriek
)
from ...models import (
    Betrokkene, GemeenteObject, Klantcontact, KlantContactpersoon, Medewerker,
    NaamGebruik, NatuurlijkPersoon, NietNatuurlijkPersoon,
    OrganisatorischeEenheid, Rol, Verzending, Vestiging,
    VestigingVanZaakBehandelendeOrganisatie
)
from .basemodels import NietNatuurlijkPersoonBaseClassFactory
from .mixins import BSNMixinFactory, GeslachtsAanduidingMixinFactory


class BetrokkeneFactory(factory.django.DjangoModelFactory):
    identificatie = factory.Sequence(lambda n: 'identificatié {0}'.format(n))

    class Meta:
        model = Betrokkene


class NatuurlijkPersoonFactory(BSNMixinFactory, BereikenMixinFactory, GeslachtsAanduidingMixinFactory,
                               RekeningnummerMixinFactory, BetrokkeneFactory):
    identificatie = factory.Sequence(lambda n: 'natuurlijk persoon identificatié {0}'.format(n))
    nummer_ander_natuurlijk_persoon = factory.Sequence(lambda n: 'unieknummer {0}'.format(n))
    verblijfadres = factory.SubFactory('zaakmagazijn.rsgb.tests.factory_models.VerblijfAdresFactory')
    naam = factory.SubFactory('zaakmagazijn.rgbz.tests.factory_models.NaamFactory')
    academische_titel = factory.SubFactory('zaakmagazijn.rsgb.tests.factory_models.AcademischeTitelFactory')
    aanduiding_naamgebruik = NaamGebruik.eigen
    geboortedatum_ingeschreven_persoon = stuf_datetime.today()
    naam_aanschrijving = factory.SubFactory('zaakmagazijn.rsgb.tests.factory_models.NaamAanschrijvingFactory')
    correspondentieadres = factory.SubFactory('zaakmagazijn.rsgb.tests.factory_models.CorrespondentieadresFactory')
    verblijf_buitenland = factory.SubFactory('zaakmagazijn.rsgb.tests.factory_models.VerblijfBuitenlandFactory')
    postadres = factory.SubFactory('zaakmagazijn.rsgb.tests.factory_models.PostAdresFactory')

    class Meta:
        model = NatuurlijkPersoon
        abstract = False


class NietNatuurlijkPersoonFactory(BereikenMixinFactory, NietNatuurlijkPersoonBaseClassFactory, RekeningnummerMixinFactory, BetrokkeneFactory):
    identificatie = factory.Sequence(lambda n: 'niet natuurlijk persoon identificatié {0}'.format(n))
    naam = factory.Sequence(lambda n: 'naam {0}'.format(n))
    nummer_ander_buitenlands_nietnatuurlijk_persoon = factory.Sequence(lambda n: 'nummer {0}'.format(n))
    correspondentieadres = factory.SubFactory('zaakmagazijn.rsgb.tests.factory_models.CorrespondentieadresFactory')
    postadres = factory.SubFactory('zaakmagazijn.rsgb.tests.factory_models.PostAdresFactory')

    class Meta:
        model = NietNatuurlijkPersoon


class VestigingFactory(BereikenMixinFactory, RekeningnummerMixinFactory, BetrokkeneFactory):
    identificatie = factory.Sequence(lambda n: 'vestiging identificatié {0}'.format(n))
    naam = factory.Sequence(lambda n: 'naam {0}'.format(n))
    handelsnaam = factory.Sequence(lambda n: ['handelsnaam {0}'.format(n), ])
    locatieadres = factory.SubFactory('zaakmagazijn.rsgb.tests.factory_models.LocatieadresFactory')
    datum_aanvang = stuf_datetime.today()

    class Meta:
        model = Vestiging


class VestigingVanZaakBehandelendeOrganisatieFactory(VestigingFactory):
    identificatie = factory.Sequence(lambda n: 'VZO identificatié {0}'.format(n))

    class Meta:
        model = VestigingVanZaakBehandelendeOrganisatie


class OrganisatorischeEenheidFactory(BereikenMixinFactory, BetrokkeneFactory):
    organisatieidentificatie = factory.Sequence(lambda n: n)
    datum_ontstaan = stuf_datetime.today()
    organisatieeenheididentificatie = factory.Sequence(lambda n: 'identificatié {0}'.format(n))
    gevestigd_in = factory.SubFactory('zaakmagazijn.rgbz.tests.factory_models.VestigingVanZaakBehandelendeOrganisatieFactory')
    naam = factory.Sequence(lambda n: 'naam {0}'.format(n))

    class Meta:

        model = OrganisatorischeEenheid


class MedewerkerFactory(BetrokkeneFactory):
    medewerkeridentificatie = factory.Sequence(lambda n: 'identificatié {0}'.format(n))
    achternaam = factory.Sequence(lambda n: 'Achtérnaam {0}'.format(n))
    functie = factory.Sequence(lambda n: 'Functié {0}'.format(n))
    voorletters = factory.Sequence(lambda n: 'Voorletters {0}'.format(n))
    organisatorische_eenheid = factory.SubFactory(
        'zaakmagazijn.rgbz.tests.factory_models.OrganisatorischeEenheidFactory')
    identificatie = factory.Sequence(lambda n: 'medewerkeridentificatié {0}'.format(n))
    geslachtsaanduiding = GeslachtsAanduiding.man
    roepnaam = factory.Sequence(lambda n: 'Roépnaam {0}'.format(n))

    class Meta:
        model = Medewerker


class KlantcontactFactory(factory.django.DjangoModelFactory):
    identificatie = factory.Sequence(lambda n: 'id {0}'.format(n))
    datumtijd = stuf_datetime.today()
    onderwerp = factory.Sequence(lambda n: 'onderwerp {0}'.format(n))
    zaak = factory.SubFactory('zaakmagazijn.rgbz.tests.factory_models.ZaakFactory')
    medewerker = factory.SubFactory('zaakmagazijn.rgbz.tests.factory_models.MedewerkerFactory')

    class Meta:
        model = Klantcontact


class KlantContactpersoonFactory(factory.django.DjangoModelFactory):
    klantcontact = factory.SubFactory('zaakmagazijn.rsgb.tests.factory_models.KlantcontactFactory')
    vestiging = factory.SubFactory('zaakmagazijn.rgbz.tests.factory_models.VestigingFactory')
    contactpersoon = factory.SubFactory('zaakmagazijn.rgbz.tests.factory_models.ContactpersoonFactory')

    class Meta:
        model = KlantContactpersoon


class KlantcontactMetVestigingFactory(KlantcontactFactory):
    membership = factory.RelatedFactory(KlantContactpersoonFactory, 'klantcontact')


class RolFactory(factory.django.DjangoModelFactory):
    betrokkene = factory.SubFactory('zaakmagazijn.rgbz.tests.factory_models.MedewerkerFactory')
    zaak = factory.SubFactory('zaakmagazijn.rgbz.tests.factory_models.ZaakFactory')
    rolomschrijving = Rolomschrijving.adviseur

    @factory.lazy_attribute
    def rolomschrijving_generiek(self):
        return Rol.get_rol_defaults(self.rolomschrijving)['rolomschrijving_generiek']

    @factory.lazy_attribute
    def roltoelichting(self):
        return Rol.get_rol_defaults(self.rolomschrijving)['roltoelichting']

    class Meta:
        model = Rol


class VerzendingFactory(factory.django.DjangoModelFactory):
    betrokkene = factory.SubFactory('zaakmagazijn.rsgb.tests.factory_models.BetrokkeneFactory')
    informatieobject = factory.SubFactory('zaakmagazijn.rgbz.tests.factory_models.InformatieObjectFactory')
    aard_relatie = AardRelatieVerzending.afzender

    class Meta:
        model = Verzending


class BetrokkeneMetRolFactory(BetrokkeneFactory):
    membership = factory.RelatedFactory(RolFactory, 'betrokkene')


class BetrokkeneMetVerzendingFactory(BetrokkeneFactory):
    membership = factory.RelatedFactory(VerzendingFactory, 'betrokkene')


class GemeenteObjectFactory(factory.django.DjangoModelFactory):
    identificatie = factory.Sequence(lambda n: 'natuurlijk persoon identificatié {0}'.format(n))
    datum_begin_geldigheid_gemeente = stuf_datetime.today()

    class Meta:
        model = GemeenteObject
