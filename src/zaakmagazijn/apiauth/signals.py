# -*- coding: utf-8 -*-
import re

from django.utils.text import capfirst


def update_service_operations(sender, **kwargs):
    # TODO [TECH]: Retrieve all application service from Spyne instead of importing all applications.
    from ..api.applications import beantwoordvraag_app, verwerksynchroonvrijbericht_app, ontvangasynchroon_app
    from .models import ServiceOperation

    existing_service_operations = []
    new_service_operations = []

    # Create new service operations.
    for app in [beantwoordvraag_app, verwerksynchroonvrijbericht_app, ontvangasynchroon_app]:
        for service in app.services:
            for public_method_name in service.public_methods.keys():
                method, entity_level = public_method_name.split('_')
                pretty_name = '{} ({})'.format(capfirst(re.subn('([A-Z])', ' \\1', method)[0]), entity_level).strip()

                obj, is_created = ServiceOperation.objects.update_or_create(
                    operation_name=public_method_name,
                    defaults={
                        'name': pretty_name,
                        'namespace': app.tns
                    }
                )

                if is_created:
                    new_service_operations.append(obj)
                else:
                    existing_service_operations.append(obj)

    # Delete old service operations.
    pks_to_keep = [obj.pk for obj in new_service_operations] + [obj.pk for obj in existing_service_operations]
    nr_of_service_operations_deleted = ServiceOperation.objects.exclude(pk__in=pks_to_keep).delete()[0]

    # Report actions.
    nr_of_service_operations_created = len(new_service_operations)

    if nr_of_service_operations_created > 0 or nr_of_service_operations_deleted > 0:
        print('Service operations created: {}, removed: {}, total count: {}.'.format(
            nr_of_service_operations_created,
            nr_of_service_operations_deleted,
            nr_of_service_operations_created + len(existing_service_operations),
        ))
