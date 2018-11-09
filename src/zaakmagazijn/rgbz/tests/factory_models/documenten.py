import factory

from ....utils import stuf_datetime
from ...models import (
    EnkelvoudigInformatieObject, InformatieObject, InformatieObjectType,
    SamengesteldInformatieObject,
    InformatieObjectTypeOmschrijvingGeneriek)
from .zaken import ZaakInformatieObjectFactory


class InformatieObjectTypeOmschrijvingGeneriekFactory(factory.django.DjangoModelFactory):
    informatieobjecttypeomschrijving_generiek = factory.Sequence(lambda n: 'omschrijving {0}'.format(n))
    definitie_informatieobjecttypeomschrijving_generiek = 'definitie'
    herkomst_informatieobjecttypeomschrijving_generiek = 'herkomst'
    hierarchie_informatieobjecttypeomschrijving_generiek = 'hierarchie'

    class Meta:
        model = InformatieObjectTypeOmschrijvingGeneriek


class InformatieObjectTypeFactory(factory.django.DjangoModelFactory):
    informatieobjecttypeomschrijving = factory.Sequence(lambda n: 'informatieobjecttype omschrijving {0}'.format(n))
    domein = factory.Sequence(lambda n: 'Dm{0}'.format(n))
    rsin = factory.Sequence(lambda n: n + 100000000)
    informatieobjectcategorie = factory.Sequence(lambda n: 'Informatieobject categorie {0}'.format(n))
    datum_begin_geldigheid_informatieobjecttype = stuf_datetime.today()

    class Meta:
        model = InformatieObjectType


class InformatieObjectFactory(factory.django.DjangoModelFactory):
    informatieobjectidentificatie = factory.Sequence(lambda n: 'identificatie {0}'.format(n))
    bronorganisatie = factory.Sequence(lambda n: n)
    creatiedatum = stuf_datetime.today()
    informatieobjecttype = factory.SubFactory(InformatieObjectTypeFactory)

    class Meta:
        model = InformatieObject


class EnkelvoudigInformatieObjectFactory(InformatieObjectFactory):
    taal = 'Nederlands'
    formaat = 'application/excel'
    link = 'http://example.com/test.xlsx'
    titel = factory.Faker('bs')

    class Meta:
        model = EnkelvoudigInformatieObject

    @factory.post_generation
    def zaak(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            ZaakInformatieObjectFactory.create(zaak=extracted, informatieobject=self)


class SamengesteldInformatieObjectFactory(InformatieObjectFactory):
    class Meta:
        model = SamengesteldInformatieObject
