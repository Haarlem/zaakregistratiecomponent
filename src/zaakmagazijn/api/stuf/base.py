import logging
from itertools import groupby

from django.core.exceptions import FieldDoesNotExist, ImproperlyConfigured
from django.db.models.constants import LOOKUP_SEP

from spyne.model.complex import ComplexModel

from .utils import get_model_field

logger = logging.getLogger(__name__)


def complex_model_factory(type_name, namespace, mapping):
    """
    Create a ComplexModel class

    :param type_name Desired type name
    :param namespace XML namespace that will be set.
    :param mapping spyne-style _type_info mapping.
    """
    complex_model = ComplexModel

    # Class attributes for the new form class.
    class_attrs = {
        '__namespace__': namespace,
        '__type_name__': type_name,
        '_type_info': mapping,
        'declare_order': 'declared'  # See _get_ordered_attributes if you're wondering.
    }
    class_name = type_name.replace('-', '')

    # Instantiate type(complex_model) in order to use the same metaclass as form.
    return type(complex_model)(class_name, (complex_model,), class_attrs)


class BaseRelation:
    pass


class OneToManyRelation(BaseRelation):
    def __init__(self, field_name, related_name, stuf_entiteit, min_occurs=0, max_occurs=None):
        """
        :param field_name str: name of the element, that should be used for this relation.
        :param related_name str: Can be
            * 'self', then it refers to itself, and no related manager is followed.
            * refer to a attribute on a django object which is a related manager.
            * refer to a method on a django object which returns a a related_manager and default_kwargs*
        :param stuf_entiteit StUFEntiteit: The stuf entiteit that should be used for interpreting this relation.
        :param min_occurs int: Minimum amount of times this relation should occur.
        :param max_occurs int: Maximum amount of times this relation should occur. If None, it's infinite.

        *Note: default_kwargs is a dictionary of field names with their values, which should be used for filtering of relations
          when used in Beantwoordvraag services, and always be set in Kennisgevingsberichten (and also used for filtering there, ofcourse)
        """
        self.field_name = field_name
        self.related_name = related_name
        self.stuf_entiteit = stuf_entiteit
        self.min_occurs = min_occurs
        self.max_occurs = max_occurs

        if self.max_occurs and self.min_occurs > self.max_occurs:
            raise ImproperlyConfigured('min_occurs should always be less than or equal to max_occurs')

        if related_name == 'self' and (self.max_occurs is None or self.max_occurs > 1):
            raise ImproperlyConfigured('A relation to \'self\' can occur only once.')

        assert self.min_occurs >= 0
        assert self.max_occurs is None or self.max_occurs >= 0


class ForeignKeyRelation(BaseRelation):
    def __init__(self, field_name, fk_name, stuf_entiteit):
        self.field_name = field_name
        self.fk_name = fk_name
        self.stuf_entiteit = stuf_entiteit
        self.min_occurs = 0  # TODO
        self.max_occurs = 1


class BaseEntiteit:
    name = None
    model = None
    field_mapping = None
    related_fields = None
    filter_fields = None
    fields = None
    gerelateerde = None
    gegevensgroepen = None
    file_fields = None
    matching_fields = None
    custom_fields = None
    namespace = 'http://www.egem.nl/StUF/sector/zkn/0310'

    @classmethod
    def _get_field_mapping_levels(cls, matching_fields=False):
        field_mapping = cls.get_django_field_mapping(matching_fields=matching_fields)
        # NOTE: This is far too complicated for what it does.
        split_field_mapping = [
            (field_name, django_field_name.split(LOOKUP_SEP), django_field)
            for field_name, django_field_name, django_field in field_mapping
        ]
        first_level_mapping = [
            (field_name, LOOKUP_SEP.join(django_field_name), django_field)
            for field_name, django_field_name, django_field in split_field_mapping if len(django_field_name) == 1]
        second_level_mapping = [
            (django_field_name[0], field_name, django_field_name[1], django_field)
            for field_name, django_field_name, django_field in split_field_mapping if len(django_field_name) == 2]
        return first_level_mapping, second_level_mapping

    @classmethod
    def get_namespace(cls):
        return cls.namespace

    @classmethod
    def is_entiteit(cls):
        """
        If this is an actual 'Entiteit' and should include the 'entiteittype'
        attribute when serialized.
        """
        raise NotImplementedError

    @classmethod
    def get_fields(cls):
        return cls.fields or ()

    @classmethod
    def get_custom_fields(cls):
        """
        Custom fields are basically raw Spyne TypeInfo data. There is no link
        with any Django field. Any processing of these fields should be done
        manually.
        """
        return cls.custom_fields or ()

    @classmethod
    def get_related_fields(cls, only_filter_fields=False, gegevensgroepen=True):
        related_fields = cls.related_fields or ()
        if gegevensgroepen:
            related_fields = related_fields + cls.get_gegevensgroepen()
        if only_filter_fields:
            return [related_field for related_field in related_fields
                    if related_field.field_name in cls.get_filter_fields()]

        deprecated_fields = [related_field for related_field in related_fields if not isinstance(related_field, BaseRelation)]
        if deprecated_fields:
            raise ImproperlyConfigured('related_fields in {} should be changed to use OneToManyRelation or ForeignKeyRelation'.format(cls.__name__))

        return related_fields or ()

    @classmethod
    def get_gerelateerde(cls):
        return cls.gerelateerde

    @classmethod
    def get_gegevensgroepen(cls):
        return cls.gegevensgroepen or ()

    @classmethod
    def get_field_mapping(cls):
        if cls.field_mapping is None:
            raise ImproperlyConfigured('A field_mapping is required for a StUFEntiteit {}'.format(str(cls)))
        return cls.field_mapping

    @classmethod
    def get_file_fields(cls):
        return cls.file_fields or ()

    @classmethod
    def get_django_field_mapping(cls, filter_fields=False, matching_fields=False):
        """
        Return a list of tuples with the StUF/SOAP field name as the first
        item of the tuple, the django field name as the second, django field itself
        as the last.

        :param filter_fields Boolean Only return the fields that are specified
                                     as 'filter_fields'.

        :return list of tuples with (field_name, django_field_name, django_field)
        """
        result = []
        unknown_fields_names = []

        for field_name, django_field_name in cls.get_field_mapping():
            if filter_fields and field_name not in cls.get_filter_fields():
                continue
            if matching_fields and field_name not in cls.get_matching_fields():
                continue

            try:
                result.append(
                    (field_name, django_field_name, get_model_field(cls.get_model(), django_field_name))
                )
            except FieldDoesNotExist as e:
                unknown_fields_names.append(django_field_name)
        if unknown_fields_names:
            raise ImproperlyConfigured(
                'Unknown field names: {0} on entiteit {1}'
                .format(', '.join(unknown_fields_names), cls.__name__))
        return result

    @classmethod
    def get_filter_fields(cls):
        # TODO: [TECH] check if all filter_fields actually exist.
        return cls.filter_fields or ()

    @classmethod
    def get_matching_fields(cls):
        if cls.matching_fields is None:
            raise ImproperlyConfigured('matching_fields are required for a StUFEntiteit')
        return cls.matching_fields or ()

    @classmethod
    def get_model(cls):
        if cls.model is None:
            raise ImproperlyConfigured('A model is required for a StUFEntiteit')
        return cls.model

    @classmethod
    def get_mnemonic(cls):
        if cls.mnemonic is None:
            raise ImproperlyConfigured('A mnemonic is required for a StUFEntiteit')
        return cls.mnemonic

    @classmethod
    def get_tijdvak_geldigheid(cls):
        if getattr(cls, 'begin_geldigheid', None) or getattr(cls, 'eind_geldigheid', None):
            return {
                'begin_geldigheid': getattr(cls, 'begin_geldigheid', None),
                'eind_geldigheid': getattr(cls, 'eind_geldigheid', None),
            }
        return None


class StUFEntiteit(BaseEntiteit):
    @classmethod
    def is_entiteit(cls):
        return True

    @classmethod
    def heeft_kerngegevens(cls):
        return False


class StUFKerngegevens(StUFEntiteit):
    @classmethod
    def is_entiteit(cls):
        return True

    @classmethod
    def heeft_kerngegevens(cls):
        return True


class StUFGegevensgroep(BaseEntiteit):
    @classmethod
    def is_entiteit(cls):
        return False

    @classmethod
    def get_mnemonic(cls):
        """
        In reality a 'Gegevensgroep' does not have a mnemonic defined, but
        pretend there is done, needed to create the appropriate spyne models.
        """
        return cls.get_model().__name__

    @classmethod
    def heeft_kerngegevens(cls):
        return False


class ComplexModelBuilder():
    # global cache for spyne models
    model_cache = {}

    @classmethod
    def create(cls, *args, **kwargs):
        instance = cls(*args, **kwargs)
        model = instance.create_model()
        return model(**instance.create_data())

    def create_model(self):
        """
        Method which calls the factor to build the ComplexModel class.
        """
        raise NotImplementedError()

    def create_data(self):
        """
        Method which creates the data needed to initiate the class created
        with 'create_model'.

        Does not have to be implemented if the class is only use to process
        input data.
        """
        raise NotImplementedError()

    def create_reusable_model(self, name, namespace, type_info):
        """
        Create a spyne model, uniquely identified by 'name' and 'namespace' that
        if it has been created before, won't be created again.
        """
        key = '{}{}'.format(namespace, name)

        if key not in self.model_cache:
            self.model_cache[key] = complex_model_factory(name, namespace, type_info)

        return self.model_cache[key]
