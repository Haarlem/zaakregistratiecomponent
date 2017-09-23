import factory
import factory.fuzzy

from ....utils import stuf_datetime
from ...choices import JaNee
from ...models import Besluit, BesluitInformatieObject, BesluitType


class BesluitTypeFactory(factory.django.DjangoModelFactory):
    domein = factory.sequence(lambda n: 'do{0}'.format(n))
    rsin = factory.Sequence(lambda n: n + 100000000)
    reactietermijn = factory.sequence(lambda n: n)
    publicatietekst = factory.sequence(lambda n: 'Publicatie tekst {0} !!!!!!'.format(n))
    publicatietermijn = 365
    besluitcategorie = 'ABCDEF'
    publicatie_indicatie = JaNee.ja
    besluittypeomschrijving = factory.fuzzy.FuzzyText(length=20)
    datum_begin_geldigheid_besluittype = stuf_datetime.today()
    datum_einde_geldigheid_besluittype = stuf_datetime.today()

    class Meta:
        model = BesluitType


class BesluitFactory(factory.django.DjangoModelFactory):
    identificatie = factory.sequence(lambda n: 'identificatie {0}'.format(n))
    besluittoelichting = factory.Sequence(lambda n: 'Toelichting op besluit {0}'.format(n))
    besluitdatum = stuf_datetime.today()
    ingangsdatum = stuf_datetime.today()
    besluittype = factory.SubFactory(BesluitTypeFactory)
    zaak = factory.SubFactory('zaakmagazijn.rgbz.tests.factory_models.ZaakFactory')

    @factory.post_generation
    def informatieobject(self, create, extracted, **kwargs):
        if not create:
            from ..factory_models import InformatieObjectFactory
            self.informatieobject.add(InformatieObjectFactory.create())
            return
        if extracted:
            for infobj in extracted:
                BesluitInformatieObject.objects.create(besluit=self, informatieobject=infobj)

    class Meta:
        model = Besluit
