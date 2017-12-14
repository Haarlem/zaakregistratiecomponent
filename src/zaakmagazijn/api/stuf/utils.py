from copy import deepcopy
from decimal import Decimal

from django.conf import settings
from django.contrib.admin.utils import get_fields_from_path
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db.models.constants import LOOKUP_SEP

from lxml import etree
from spyne import Unicode
from spyne.model.complex import TypeInfo
from spyne.util.django import DEFAULT_FIELD_MAP as _DEFAULT_FIELD_MAP

from zaakmagazijn.utils import stuf_datetime
from zaakmagazijn.utils.fields import GMLField

from .models import DatumMetIndicator, TijdstipMetIndicator
from .simple_types import GeometrieIMGeo_e

DEFAULT_FIELD_MAP = dict(_DEFAULT_FIELD_MAP)
DEFAULT_FIELD_MAP['StUFDateField'] = DatumMetIndicator
DEFAULT_FIELD_MAP['StUFDateTimeField'] = TijdstipMetIndicator
DEFAULT_FIELD_MAP['GMLField'] = GeometrieIMGeo_e
DEFAULT_FIELD_MAP['ArrayField'] = Unicode.customize(max_occurs=Decimal('inf'))


def get_model_value(obj, field_name):
    """
    Returns the value belonging to `field_name` on `Model` instance.
    This works for related fields.

    Example::

        >>> get_model_value(Zaak, 'zaaktype__zaaktypeomschrijving')
        'Some description'

    """
    fields = field_name.split(LOOKUP_SEP)
    for field in fields:
        obj = getattr(obj, field)
    return obj


def set_model_value(obj, field_name, value):
    """
    Sets a value on the field name in a model intance. The model instance is
    returned to indicate if any related model was updated.
    This works for related fields.

    Example::

        >>> set_model_value(Zaak, 'zaaktype__zaaktypeomschrijving', 'New description')
        <ZaakType: ZaakType object>

    """
    attrs = field_name.split(LOOKUP_SEP)
    for attr in attrs[:-1]:
        obj = getattr(obj, attr)
    setattr(obj, attrs[-1], value)
    return obj


def get_model_field(model, field_name):
    """
    Returns the `Field` instance belonging to `field_name` on a `Model`
    instance or class. This works for related fields.

    Example::

        >>> get_model_field(Zaak, 'zaaktype__zaaktypeomschrijving')
        <django.db.models.fields.CharField: zaaktypeomschrijving>

    """
    from zaakmagazijn.rgbz_mapping.base import ModelProxy
    if issubclass(model, ModelProxy):
        return model.get_field(field_name)
    return get_fields_from_path(model, field_name)[-1]


def django_field_to_spyne_model(django_field, default=None, nullable=None, min_occurs=None):
    """
    Convert a django.db.models.Field to a spyne.model.primitive.* simple model.

    If the default, nullable or min_occurs parameter are None the value of these
    parameters is determined from the Django field.

    :param default Default value.
    :param nullable boolean The XML element can be nil.
    :param min_occurs int Amount of times The XML element can occur.
    """

    from zaakmagazijn.rgbz_mapping.base import ProxyField
    if isinstance(django_field, ProxyField):
        django_field = django_field.get_django_field()

    field_type = django_field.__class__.__name__
    spyne_model = DEFAULT_FIELD_MAP[field_type]

    kwargs = {}
    # NOTE: Taiga 397 reported issues with defaults. The default is
    # interpreted as "provided" by the request, which is not true.
    #
    # if default is None and django_field.has_default():
    #     kwargs['default'] = django_field.get_default()
    if default is not None:
        kwargs['default'] = default

    if nullable is None and django_field.null:
        kwargs['nullable'] = True
    elif nullable is not None:
        kwargs['nullable'] = nullable

    required = not (django_field.has_default() or django_field.blank or django_field.primary_key)
    if min_occurs is None:
        kwargs['min_occurs'] = 1 if required else 0
    else:
        kwargs['min_occurs'] = min_occurs

    for validator in django_field.validators:
        if type(validator) is MinLengthValidator:
            kwargs['min'] = validator.limit_value
        elif type(validator) is MaxLengthValidator:
            kwargs['min'] = validator.limit_value

    return spyne_model.customize(**kwargs)


def _create_filter(related_query_name1, related_query_name2):
    if related_query_name1:
        return related_query_name1 + '__' + related_query_name2
    return related_query_name2


def create_query_args(filter_obj, related_query_name='', recurse=False):
    """
    Create django filter args from a hierarchy of StUF entities.

    :param filter_obj ComplexModel instantiated ComplexModel with result data containing filter arguments.
    :param related_query_name str Optional related query name which is prefixed before all query arguments.
    :param recursive bool If the function should recursively go through the entire hierarchy and create a filter
                          for all many to many and one to many relations as well.

    :return dict Keyword arguments which can be used in a Django ORM filter. i.e. model.filter(**kwargs)
    """
    if not filter_obj:
        return {}

    stuf_entiteit = filter_obj.stuf_entiteit
    django_model = stuf_entiteit.get_model()
    query_args = {}

    field_mapping = stuf_entiteit.get_django_field_mapping(filter_fields=True)
    for field_name, django_field_name, django_field in field_mapping:
        filter_value = getattr(filter_obj, field_name)
        # if hasattr(filter_value, 'data'):
        #     filter_value = filter_value.data
        query_args[_create_filter(related_query_name, django_field_name)] = filter_value

    if recurse:
        for field_name, related_name, related_cls in stuf_entiteit.get_related_fields(only_filter_fields=True):
            descriptor = getattr(django_model, related_name)
            related_obj = getattr(filter_obj, field_name)
            query_args.update(create_query_args(
                related_obj, _create_filter(related_query_name, descriptor.field.related_query_name()), recurse=True))
    return query_args


def to_django_value(spyne_obj, django_field):
    """
    Convert a spyne model to a django value
    """
    from zaakmagazijn.rgbz_mapping.base import ProxyField
    if isinstance(django_field, ProxyField):
        django_field = django_field.get_django_field()

    if hasattr(spyne_obj, 'to_django_value'):
        return spyne_obj.to_django_value(spyne_obj, django_field)

    # I haven't found a nice way to identify simples types yet, and to add a
    # 'to_django_value' method to the class to do the conversion.
    if type(django_field) is GMLField:
        return etree.tostring(deepcopy(spyne_obj))

    return spyne_obj


def to_spyne_value(django_obj, django_field, spyne_field):
    """
    Converts value from Django model to Spyne value.

    :param django_obj:
    :param django_field:
    :param spyne_field:
    :return:
    """
    # if 'data' in spyne_field._type_info and issubclass(spyne_field._type_info['data'], XmlData):
    #     return {'data': django_obj}

    if hasattr(spyne_field, 'to_spyne_value'):
        return spyne_field.to_spyne_value(django_obj, spyne_field)

    return django_obj


def reorder_type_info(fields, type_info, allow_partial=False):
    """
    re-order the given type_info into the order given with fields. Anything
    not mentioned in fields, will be appended last.
    """

    copy = TypeInfo(type_info.items())
    new = TypeInfo()
    for field in fields:
        if field not in copy:
            if allow_partial:
                # If we order the <gelijk> element, this element can contain far less elements than the <object>
                # element. This is a workaround by assuming the gelijk-order it the same as the object-order.
                continue
            else:
                raise KeyError('All fields must be present in the Spyne model: {} is missing.'.format(field))

        value = copy[field]
        del copy[field]
        new[field] = value

    # Add the fields not specified in fields last.
    for field, value in copy.items():
        new[field] = value
    return new


def get_spyne_field(spyne_model, *path):
    """
    Returns a `ComplexModel` or `SimpleType` depending on the given `path`.

    Example::

        >>> get_spyne_field(GeefZaakStatus_La01, 'antwoord/object/identificatie')
        <class 'spyne.model.primitive.xml.NormalizedString'>

        >>> get_spyne_field(GeefZaakStatus_La01, 'antwoord', 'object', 'identificatie')
        <class 'spyne.model.primitive.xml.NormalizedString'>

    :param spyne_model: The `ComplexModel` class.
    :param path: Like an xpath but simpler, or several path elements.
    :return: The resulting Spyne field.
    """
    if len(path) == 1:
        fields = path[0].split('/')
    else:
        fields = path

    for field in fields:
        spyne_model = spyne_model._type_info[field]
    return spyne_model


def get_systeem_zender():
    """
    Return the zender (sender) data, if we're the sender. sender data is based
    on what is stored in the settings.
    """
    from .protocols import IgnoreAttribute
    systeem = settings.ZAAKMAGAZIJN_SYSTEEM

    zender = {
        'organisatie': systeem['organisatie'] or IgnoreAttribute(),
        'applicatie': systeem['applicatie'] or IgnoreAttribute(),
        'administratie': systeem['administratie'] or IgnoreAttribute(),
        'gebruiker': systeem['gebruiker'] or IgnoreAttribute(),
    }
    return zender


def get_ontvanger(zender):
    """
    Based on the 'ontvanger' return the 'zender' data where we'll
    be returning the data to.
    """
    from .protocols import IgnoreAttribute

    if zender is None:
        return None

    ontvanger = {
        'organisatie': zender.organisatie or IgnoreAttribute(),
        'applicatie': zender.applicatie or IgnoreAttribute(),
        'administratie': zender.administratie or IgnoreAttribute(),
        'gebruiker': zender.gebruiker or IgnoreAttribute(),
    }
    return ontvanger


def get_bv03_stuurgegevens(data):
    from .choices import BerichtcodeChoices
    from ..utils import create_unique_id

    return {
        'berichtcode': BerichtcodeChoices.bv03,
        'zender': get_systeem_zender(),
        'ontvanger': get_ontvanger(data.stuurgegevens.zender),
        'referentienummer': create_unique_id(),
        'crossRefnummer': data.stuurgegevens.referentienummer,
        'tijdstipBericht': stuf_datetime.now()
    }
