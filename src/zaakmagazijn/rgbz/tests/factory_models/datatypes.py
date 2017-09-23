import factory

from ....rsgb.models import Voorvoegsel


class VoorvoegselFactory(factory.django.DjangoModelFactory):
    voorvoegselnummer = factory.sequence(lambda n: '0{0}'.format(n))
    lo3_voorvoegsel = factory.sequence(lambda n: 'LO3 voorvoegsel {0}'.format(n))
    voorvoegsel = factory.sequence(lambda n: 'Voorvoegsel {0}'.format(n))
    scheidingsteken = 'N'

    class Meta:
        model = Voorvoegsel
