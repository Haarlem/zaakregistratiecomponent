import factory
import factory.fuzzy

from ....rgbz.choices import AardRelatieZakenRelatie, ArchiefStatus, JaNee
from ....utils import stuf_datetime
from ...models import (
    Eigenschap, Status, StatusType, Zaak, ZaakInformatieObject, ZaakType,
    ZakenRelatie
)
from ..factory_models import RolFactory


class ZaakTypeFactory(factory.django.DjangoModelFactory):
    zaaktypeidentificatie = factory.fuzzy.FuzzyInteger(0, 99999)
    zaaktypeomschrijving = factory.Sequence(lambda n: 'omschrijving {0}'.format(n))
    zaaktypeomschrijving_generiek = factory.Sequence(lambda n: 'omschrijving generiek {0}'.format(n))

    datum_begin_geldigheid_zaaktype = stuf_datetime.today()
    datum_einde_geldigheid_zaaktype = stuf_datetime.today()

    rsin = 123

    doorlooptijd_behandeling = factory.fuzzy.FuzzyInteger(0, 999)

    publicatie_indicatie = JaNee.ja

    class Meta:
        model = ZaakType
        django_get_or_create = ('zaaktypeidentificatie',)


class ZaakFactory(factory.django.DjangoModelFactory):
    zaakidentificatie = factory.Sequence(lambda n: 'identificatie {0}'.format(n))
    bronorganisatie = factory.Sequence(lambda n: n)
    omschrijving = factory.Sequence(lambda n: 'omschrijving {0}'.format(n))

    registratiedatum = stuf_datetime.today()

    einddatum = stuf_datetime.today()
    startdatum = stuf_datetime.today()
    einddatum_gepland = stuf_datetime.today()
    uiterlijke_einddatum_afdoening = stuf_datetime.today()

    verantwoordelijke_organisatie = factory.Sequence(lambda n: n)
    publicatiedatum = stuf_datetime.today()

    archiefstatus = ArchiefStatus.nog_te_archiveren

    ander_zaakobject = factory.RelatedFactory('zaakmagazijn.rgbz.tests.factory_models.AnderZaakObjectFactory', 'zaak')
    kenmerken = factory.RelatedFactory('zaakmagazijn.rgbz.tests.factory_models.ZaakKenmerkFactory', 'zaak')

    zaaktype = factory.SubFactory(ZaakTypeFactory)

    class Meta:
        model = Zaak

    @factory.post_generation
    def status_set(obj, create, extracted, **kwargs):
        if not create:
            return

        if not extracted and not kwargs:
            return

        if extracted:
            obj.status_set.set(extracted)
        else:
            StatusFactory.create(zaak=obj, **kwargs)


class EigenschapFactory(factory.django.DjangoModelFactory):
    zaak = factory.SubFactory(ZaakFactory)
    data = factory.Sequence(lambda n: 'JSONData{0}'.format(n))

    class Meta:
        model = Eigenschap


class StatusTypeFactory(factory.django.DjangoModelFactory):
    statustypeomschrijving = factory.Sequence(lambda n: 'omschrijving {0}'.format(n))
    statustypevolgnummer = factory.Sequence(lambda n: '0{0}5'.format(n))

    datum_begin_geldigheid_statustype = stuf_datetime.today()
    datum_einde_geldigheid_statustype = stuf_datetime.today()
    zaaktype = factory.SubFactory(ZaakTypeFactory)

    class Meta:
        model = StatusType


class StatusFactory(factory.django.DjangoModelFactory):
    datum_status_gezet = stuf_datetime.today()
    zaak = factory.SubFactory(ZaakFactory)
    rol = factory.SubFactory(RolFactory, zaak=factory.SelfAttribute('..zaak'))
    status_type = factory.SubFactory(StatusTypeFactory)

    class Meta:
        model = Status


class ZaakInformatieObjectFactory(factory.django.DjangoModelFactory):
    zaak = factory.SubFactory(ZaakFactory)
    informatieobject = factory.SubFactory('zaakmagazijn.rgbz.tests.factory_models.EnkelvoudigInformatieObjectFactory')
    titel = factory.Sequence(lambda n: 'Dit is een titel {0}'.format(n))
    registratiedatum = stuf_datetime.today()
    status = factory.SubFactory(StatusFactory)

    class Meta:
        model = ZaakInformatieObject


class ZaakMetInformatieObjectFactory(ZaakFactory):
    membership = factory.RelatedFactory(ZaakInformatieObjectFactory, 'zaak')


class ZakenRelatieFactory(factory.django.DjangoModelFactory):
    aard_relatie = AardRelatieZakenRelatie.bijdrage
    onderhanden_zaak = factory.SubFactory(ZaakFactory)
    andere_zaak = factory.SubFactory(ZaakFactory)

    class Meta:
        model = ZakenRelatie


class ZaakMetZakenRelatie(ZaakFactory):
    deelname = factory.RelatedFactory(ZakenRelatieFactory, 'onderhanden_zaak')
