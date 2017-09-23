import factory

from ....rgbz.choices import JaNee
from ....utils import stuf_datetime
from ...models import AcademischeTitel, LandGebied


class AcademischeTitelFactory(factory.django.DjangoModelFactory):
    academische_titelcode = 'Aa'
    omschrijving_academische_titel = factory.Sequence(lambda n: 'omschrijving academische titel {0}'.format(n))
    positie_academische_titel_tov_naam = JaNee.ja
    datum_begin_geldigheid_titel = stuf_datetime.today()

    class Meta:
        model = AcademischeTitel


class LandGebiedFactory(factory.django.DjangoModelFactory):
    landcode = 'NL'
    landnaam = 'Nederland'
    ingangsdatum_land = stuf_datetime.today()

    class Meta:
        model = LandGebied
