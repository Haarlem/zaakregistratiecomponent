import factory

from ..models import (
    Application, ApplicationGroup, Organisation, ServiceOperation
)


class ServiceOperationFactory(factory.django.DjangoModelFactory):
    name = factory.sequence(lambda n: 'service operation {0}'.format(n))
    operation_name = factory.sequence(lambda n: 'operation {0}'.format(n))

    class Meta:
        model = ServiceOperation


class OrganisationFactory(factory.django.DjangoModelFactory):
    name = factory.sequence(lambda n: 'organisation {0}'.format(n))

    class Meta:
        model = Organisation


class ApplicationFactory(factory.django.DjangoModelFactory):
    name = factory.sequence(lambda n: 'application {0}'.format(n))
    organisation = factory.SubFactory(OrganisationFactory)

    class Meta:
        model = Application


class ApplicationGroupFactory(factory.django.DjangoModelFactory):
    name = factory.sequence(lambda n: 'group {0}'.format(n))

    class Meta:
        model = ApplicationGroup
