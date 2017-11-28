from itertools import groupby

from ...stuf.choices import ServerFoutChoices
from ...stuf.faults import StUFFault
from ...stuf.protocols import Nil
from ...stuf.utils import to_django_value


def _is_virtual_field(django_field):
    # skip virtual django model fields (=fields that don't have a db col)
    # in lookups/queries, since they don't exist in DB
    return not hasattr(django_field, 'get_col')


class KennisgevingObject:
    def __init__(self, stuf_entiteit, spyne_obj):
        assert spyne_obj is not None

        self.stuf_entiteit = stuf_entiteit
        self.spyne_obj = spyne_obj
        self.obj_relations = []
        self.obj_related = []
        if self.stuf_entiteit.is_entiteit():
            self.obj_verwerkingssoort = spyne_obj.verwerkingssoort if spyne_obj else None
        else:
            self.obj_verwerkingssoort = None

    def add_obj_relation(self, related_name, obj):
        self.obj_relations.append((related_name, obj), )

    def add_obj_related(self, fk_name, obj):
        assert len(self.obj_related) <= 1

        self.obj_related.append((fk_name, obj), )

    def get_obj_related(self):
        assert len(self.obj_related) <= 1
        if self.obj_related:
            return self.obj_related[0]
        return None

    def is_nil(self):
        return isinstance(self.spyne_obj, Nil)

    def __str__(self):
        if self.is_nil():
            return str(self.spyne_obj)

        return '{{{}}}'.format(', '.join(['{}={}'.format(k, v) for k, v in self.get_obj_kwargs().items()]))

    def _create(self, model, **kwargs):
        obj = model(**kwargs)

        # This bubbles up to the general exception handler.
        obj.full_clean()

        obj.save()

        return obj

    def get_or_create(self, related_manager=None, extra=None, extra_on_create=None):
        django_model = self.stuf_entiteit.get_model()
        assert related_manager is None or related_manager.model == django_model
        created = False
        try:
            obj = self.get(related_manager=related_manager, raise_fault=False, extra=extra)
        except django_model.DoesNotExist:
            obj = self.create(related_manager=related_manager, extra=extra, extra_on_create=extra_on_create)
            created = True
        return obj, created

    def create(self, related_manager=None, extra=None, extra_on_create=None):
        django_model = self.stuf_entiteit.get_model()
        assert related_manager is None or related_manager.model == django_model
        default_args = self.get_obj_kwargs()
        if extra:
            default_args.update(extra)
        if extra_on_create:
            default_args.update(extra_on_create)
        obj = self._create(django_model, **default_args)
        if related_manager:
            related_manager.add(obj)
        return obj

    def _get(self, related_manager=None, extra=None):
        """
        Retrieve the entiteit from the database and return as a Django ORM object.
        """

        django_model = self.stuf_entiteit.get_model()
        assert related_manager is None or related_manager.model == django_model

        query_args = self.get_obj_kwargs(matching_fields=True)

        if extra:
            query_args.update(extra)
        manager = related_manager or django_model.objects
        query_args = self.stuf_entiteit.add_extra_obj_kwargs(self.spyne_obj, query_args)
        return manager.get(**query_args)

    def get(self, related_manager=None, raise_fault=True, extra=None):
        if raise_fault:
            django_model = self.stuf_entiteit.get_model()
            assert related_manager is None or related_manager.model == django_model
            try:
                return self._get(related_manager=related_manager, extra=extra)
            except django_model.DoesNotExist as exception:
                raise StUFFault(ServerFoutChoices.stuf064, stuf_details=str(exception))
            except django_model.MultipleObjectsReturned as exception:
                raise StUFFault(ServerFoutChoices.stuf067, stuf_details=str(exception))
        return self._get(related_manager=related_manager, extra=extra)

    def create_django_obj_kwargs(self, matching_fields=False):
        """
        Create a dictionary with django type values, which can be used
        to filter using the Django ORM, or create/modify database fields.

        :return dictionary with django field names as keys, and values, converted to django values
                as values.
        """
        spyne_obj = self.spyne_obj
        obj = {}
        #
        # StUF 3.01 - 5.2.4 Het vullen van de <object> elementen
        #

        django_model = self.stuf_entiteit.get_model()
        first_level_mapping, second_level_mapping = self.stuf_entiteit._get_field_mapping_levels(matching_fields=matching_fields)

        # Process to 'first level' fields, which have no relation.
        for field_name, django_field_name, django_field in first_level_mapping:
            if django_field_name.startswith('_'):
                continue
            spyne_value = getattr(spyne_obj, field_name)

            if spyne_value is not None:
                value = to_django_value(spyne_value, django_field)
                obj[django_field_name] = value

        # Process the 'second level' fields, which have a foreign key relation
        for group, mapping in groupby(second_level_mapping, key=lambda o: o[0]):
            query = {}
            for _, field_name, django_field_name, django_field in mapping:
                if django_field_name.startswith('_'):
                    continue
                spyne_value = getattr(spyne_obj, field_name)
                if spyne_value:
                    value = to_django_value(spyne_value, django_field)
                    query[django_field_name] = value

            if query:
                from zaakmagazijn.rgbz_mapping.base import ModelProxy
                if issubclass(django_model, ModelProxy):
                    related_model = django_model.get_field(group)._relation_proxy_model
                else:
                    related_model = getattr(django_model, group).field.rel.to
                try:
                    # According to KING, this should be dealt with as a 'T', and not just as an 'I'
                    # As a side-effect, NPS.Naam (FK) is also nicely created.
                    related_obj, _ = related_model.objects.get_or_create(**query)
                except related_model.DoesNotExist as exception:
                    raise StUFFault(ServerFoutChoices.stuf064, stuf_details=str(exception))
                obj[group] = related_obj

        tijdvak_geldigheid = self.stuf_entiteit.get_tijdvak_geldigheid()
        if not matching_fields and tijdvak_geldigheid and self.spyne_obj.tijdvakGeldigheid:
            begin_geldigheid = to_django_value(self.spyne_obj.tijdvakGeldigheid.beginGeldigheid, None)
            eind_geldigheid = to_django_value(self.spyne_obj.tijdvakGeldigheid.eindGeldigheid, None)

            obj[tijdvak_geldigheid['begin_geldigheid']] = begin_geldigheid
            obj[tijdvak_geldigheid['eind_geldigheid']] = eind_geldigheid

        tijdvak_relatie = self.stuf_entiteit.get_tijdvak_relatie()
        if not matching_fields and tijdvak_relatie and self.spyne_obj.tijdvakRelatie:
            begin_relatie = to_django_value(self.spyne_obj.tijdvakRelatie.beginRelatie, None)
            eind_relatie = to_django_value(self.spyne_obj.tijdvakRelatie.eindRelatie, None)

            obj[tijdvak_relatie['begin_relatie']] = begin_relatie
            obj[tijdvak_relatie['eind_relatie']] = eind_relatie

        tijdstip_registratie = self.stuf_entiteit.get_tijdstip_registratie()
        if not matching_fields and tijdstip_registratie:
            obj[tijdstip_registratie] = to_django_value(self.spyne_obj.tijdstipRegistratie, None)

        return obj

    def get_obj_kwargs(self, matching_fields=False):
        assert self.spyne_obj is not None
        return self.create_django_obj_kwargs(matching_fields=matching_fields)

    def get_virtual_obj_kwargs(self):
        """
        Retrieves the fields on the Django model with the Spyne value.

        NOTE: this only goes one level deep.
        """
        assert self.spyne_obj is not None
        obj = {}
        first_level_mapping, _ = self.stuf_entiteit._get_field_mapping_levels()

        for field_name, django_field_name, django_field in first_level_mapping:
            if not django_field_name.startswith('_'):
                continue
            spyne_value = getattr(self.spyne_obj, field_name)
            if spyne_value:
                value = to_django_value(spyne_value, django_field)
                obj[django_field_name] = value
        return obj
