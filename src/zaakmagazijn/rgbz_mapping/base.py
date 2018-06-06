import inspect

from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.db.models.constants import LOOKUP_SEP
from django.utils.module_loading import import_string

from ..api.stuf.utils import get_model_field
from .exceptions import NoValueError
from .manager import ProxyRelatedManager
from .registry import proxy_registry


class ProxyOneToManyDescriptor:
    def __init__(self, relation):
        self.relation = relation

    def __get__(self, instance, cls=None):
        if instance is None:
            return self

        django_obj = instance._obj
        related_manager = getattr(django_obj, self.relation.rgbz2_name)
        proxy_model = self.relation.relation_proxy_model

        return ProxyRelatedManager(proxy_model, related_manager)


class ModelProxyBase(type):
    def __new__(cls, name, bases, attrs):
        new_class = super().__new__(cls, name, bases, attrs)

        fields = getattr(new_class, 'fields', [])

        if isinstance(fields, list) or isinstance(fields, tuple):
            for field in fields:
                field.set_proxy_model(new_class)
        else:
            fields.set_proxy_model(new_class)

        for obj_name, obj in attrs.items():
            if not inspect.isclass(obj) and hasattr(obj, 'contribute_to_class'):
                obj.contribute_to_class(new_class, obj_name)

        django_model = new_class.get_model()
        if django_model:
            new_class.DoesNotExist = django_model.DoesNotExist
            new_class.MultipleObjectsReturned = django_model.MultipleObjectsReturned

            for relation in new_class.get_fields(in_rgbz1=True, is_relation=True):
                setattr(new_class, relation.rgbz1_name, ProxyOneToManyDescriptor(relation))

            proxy_registry.register_proxy_model(new_class)

        return new_class


class ModelProxy(metaclass=ModelProxyBase):
    model = None

    def __init__(self, _obj=None, **rgbz1_kwargs):
        """
        *args is not supported.
        """

        default_field_names = {'pk', }

        rgbz1_field_names = {field.rgbz1_name for field in self.get_fields(in_rgbz1=True, is_field=True, is_foreign_key=True)}
        kwargs_fields_names = set(rgbz1_kwargs.keys())
        undefined_field_names = kwargs_fields_names.difference(rgbz1_field_names.union(default_field_names))
        if undefined_field_names:
            raise ValueError('The following fields aren\'t valid rgbz1 fields: {}'.format(undefined_field_names))

        # There are two ways which a ModelProxy can be initiated, either
        # it's based on an existing Django ORM object, or a new Django ORM is created
        # on given kwargs.
        if _obj:
            self._obj = _obj
            for field_name, value in rgbz1_kwargs.items():
                setattr(self, field_name, value)
        else:
            django_model = self.get_model()
            self._obj = django_model(**self.to_rgbz2_kwargs(rgbz1_kwargs))

            for field_name in rgbz1_field_names:
                field = self.get_field(field_name)
                if field.has_default():
                    default = field.get_default()
                else:
                    default = None
                setattr(self, field_name, rgbz1_kwargs.get(field_name, default))

    def __eq__(self, other):
        if not isinstance(other, ModelProxy):
            return False
        return self.pk == other.pk

    def full_clean(self):
        self.to_django_obj()
        try:
            return self._obj.full_clean()
        except ValidationError as e:
            raise ValidationError('{}: {}'.format(self._obj, e))

    def delete(self):
        return self._obj.delete()

    @classmethod
    def get_model(cls):
        return cls.model

    @classmethod
    def _get_field(cls, rgbz1_name):
        mapping = {field.rgbz1_name: field for field in cls.fields}

        try:
            return mapping[rgbz1_name]
        except KeyError:
            raise ValueError(
                'Can\'t find a field name \'{rgbz1_name}\' on the proxy model {proxy_model}'.format(
                    rgbz1_name=rgbz1_name, proxy_model=cls.__name__))

    @classmethod
    def get_field(cls, rgbz1_name):
        """
        """

        pieces = rgbz1_name.split(LOOKUP_SEP)
        model = cls
        for piece in pieces:
            field = model._get_field(piece)
            if not hasattr(field, 'relation_proxy_model'):
                break
            model = field.relation_proxy_model

        return field

    @classmethod
    def _to_rgbzx_method(cls, field, rgbz_version):
        field_name = getattr(field, 'rgbz{rgbz_version}_name'.format(rgbz_version=rgbz_version))
        return getattr(cls, 'to_rgbz{rgbz_version}_{field_name}'.format(rgbz_version=rgbz_version, field_name=field_name), None)

    @classmethod
    def _to_rgbz1_field(cls, field, obj):
        to_rgbz1_method = cls._to_rgbzx_method(field, 1)
        if to_rgbz1_method:
            return to_rgbz1_method(obj)

        assert field.rgbz1_name, '{field_name}: Either define a to_rgbz1_{field_name} ' \
                                 'method or set a rgbz1 field name'.format(field_name=field.rgbz1_name)
        if isinstance(field, ProxyForeignKey):
            fk_obj = getattr(obj, field.rgbz2_name)
            # TODO [TECH]: It's probably a good idea to lazy-load ForeignKeys.
            return field.relation_proxy_model.from_django_obj(fk_obj) if fk_obj else None
        else:
            return getattr(obj, field.rgbz2_name)

    @classmethod
    def to_rgbz1_kwargs(cls, obj):
        rgbz1_kwargs = {}
        for field in cls.get_fields(in_rgbz1=True, is_field=True, is_foreign_key=True):
            try:
                rgbz1_kwargs[field.rgbz1_name] = cls._to_rgbz1_field(field, obj)
            except NoValueError:
                pass
        return rgbz1_kwargs

    @classmethod
    def _to_rgbz2_field(cls, field, kwargs):
        to_rgbz2_method = cls._to_rgbzx_method(field, 2)
        if to_rgbz2_method:
            return to_rgbz2_method(kwargs)

        assert field.rgbz1_name, '{field_name}: Either define a to_rgbz2_{field_name} ' \
                                 'method or set a rgbz1 field name'.format(field_name=field.rgbz2_name)
        if isinstance(field, ProxyForeignKey):
            value = kwargs.get(field.rgbz1_name)
            if value:
                return value.to_django_obj()
            return None
        else:
            return kwargs.get(field.rgbz1_name, field.get_default() if field.has_default() else None)

    @classmethod
    def to_rgbz2_kwargs(cls, kwargs):
        """
        Convert a dictionary of rgbz1 field values to rgbz2 field values.
        """
        rgbz2_kwargs = {}
        for field in cls.get_fields(in_rgbz2=True, is_field=True, is_foreign_key=True):
            if field.is_virtual:
                continue
            try:
                rgbz2_kwargs[field.rgbz2_name] = cls._to_rgbz2_field(field, kwargs)
            except NoValueError:
                pass
        return rgbz2_kwargs

    @classmethod
    def get_fields(cls, in_rgbz1=False, in_rgbz2=False, is_field=False,
                   is_foreign_key=False, is_relation=False, only_non_computed=False):
        """
        Return fields that are defined on the model.

        :param in_rgbz1 If True, fields that are not part of RGBZ 1.0 are filtered out.
        :param in_rgbz2 If True, fields that are not part of RGBZ 2.0 are filtered out.

        if both in_rgbz1 and in_rgbz2 are False, _all_ fields are returned.

        :param is_field If True, fields that are a ProxyField are returned.
        :param is_foreign_key if True, fields that are a ProxyForeignKey are returned
        :param is_relation If True, fields that are a ProxyOneToMany are returned.rgbz1_name

        If, for example 'is_field' is set, and 'is_foreign_key' as well, both ProxyFields and ProxyForeignKeys are
        returned.

        :param only_non_computed If True, return only non-computed fields.
        """
        fields_to_return = []
        for field in cls.fields:
            if (in_rgbz1 and field.rgbz1_name is None) or (in_rgbz2 and field.rgbz2_name is None):
                continue

            if only_non_computed and (cls._to_rgbzx_method(field, 1) or cls._to_rgbzx_method(field, 2)):
                continue

            if (is_field and isinstance(field, ProxyField)) or \
               (is_foreign_key and isinstance(field, ProxyForeignKey)) or \
               (is_relation and isinstance(field, ProxyOneToMany)):
                fields_to_return.append(field)
        return fields_to_return

    def to_django_obj(self):
        rgbz1_kwargs = {field.rgbz1_name: getattr(self, field.rgbz1_name)
                        for field in self.get_fields(in_rgbz1=True, is_field=True, is_foreign_key=True)}
        rgbz2_kwargs = self.to_rgbz2_kwargs(rgbz1_kwargs)

        for field_name, value in rgbz2_kwargs.items():
            setattr(self._obj, field_name, value)
        return self._obj

    @classmethod
    def from_django_obj(cls, obj):
        """
        Convert a Django obj, which is RGBZ2.0 to a ProxyModel obj, which is
        RGBZ 1.0.

        :param obj Django model instance.
        """

        kwargs = cls.to_rgbz1_kwargs(obj)
        kwargs.update({
            'pk': obj.pk
        })
        return cls(_obj=obj, **kwargs)

    def save(self):
        django_obj = self.to_django_obj()
        django_obj.save()


class FieldBase:
    def __str__(self):
        translation = '{} to {}'.format(self.rgbz1_name, self.rgbz2_name)
        path = '{}.{}'.format(self.__class__.__module__, self.__class__.__name__)
        return '<{}: {}>'.format(path, translation)

    def get_django_field(self):
        # Try to determine what kind of field we're emulating.

        if self.rgbz2_name is None:
            raise ImproperlyConfigured(
                'For field {field_name} either a rgbz2 field name, or a rgbz1 field type needs to be '
                'defined in order to determine the django field that is being emulated.'.format(field_name=self.rgbz1_name))

        if self.proxy_model is None:
            raise AttributeError
        django_model = self.proxy_model.get_model()
        return get_model_field(django_model, self.rgbz2_name)

    def has_default(self):
        return False

    def get_default(self):
        raise NotImplementedError


class ProxyField(FieldBase):
    def __init__(self, rgbz1_name, rgbz2_name, rgbz1_field=None, is_virtual=False):
        self.rgbz1_name = rgbz1_name
        self.rgbz2_name = rgbz2_name
        self.proxy_model = None
        self.rgbz1_field = rgbz1_field
        self.is_virtual = is_virtual

    def set_proxy_model(self, proxy_model):
        self.proxy_model = proxy_model

    def get_django_field(self):
        # Try to determine what kind of field we're emulating.

        if self.rgbz1_field:
            return self.rgbz1_field

        return super().get_django_field()

    def __getattr__(self, name):
        django_field = self.get_django_field()
        if name == 'name':
            return self.rgbz1_name
        return getattr(django_field, name)

    def has_default(self):
        django_field = self.get_django_field()
        return django_field.has_default()

    def get_default(self):
        django_field = self.get_django_field()
        return django_field.get_default()


class ProxyOneToMany:
    def __init__(self, rgbz1_name, rgbz2_name, model, is_virtual=False):
        self.rgbz1_name = rgbz1_name
        self.rgbz2_name = rgbz2_name
        self.proxy_model = None
        self.is_virtual = is_virtual

        self._relation_proxy_model = model

    @property
    def relation_proxy_model(self):
        model = self._relation_proxy_model
        return import_string(model) if isinstance(model, str) else model

    def set_proxy_model(self, proxy_model):
        self.proxy_model = proxy_model


class ProxyForeignKey(FieldBase):
    def __init__(self, rgbz1_name, rgbz2_name, model, is_virtual=False):
        self.rgbz1_name = rgbz1_name
        self.rgbz2_name = rgbz2_name
        self.proxy_model = None
        self.is_virtual = is_virtual
        self._relation_proxy_model = model

    @property
    def relation_proxy_model(self):
        model = self._relation_proxy_model
        return import_string(model) if isinstance(model, str) else model

    def set_proxy_model(self, proxy_model):
        self.proxy_model = proxy_model


class AutoMapper:
    """
    Automatically convert Django's non-relation ORM fields to a ProxyField. This
    is useful if the Django fields are a 1-to-1 mapping to the RGBZ 1.0 fields.

    usage:

    > class ExampleProxy(ModelProxy):
    >    model = Example
    >    fields = AutoMapper()
    >    objects = ProxyManager()

    """
    def __init__(self):
        self.proxy_model = None

    def set_proxy_model(self, proxy_model):
        self.proxy_model = proxy_model

    def __iter__(self):
        django_model = self.proxy_model.get_model()
        for field in django_model._meta.get_fields(include_hidden=True):
            if not field.is_relation:
                proxy_field = ProxyField(field.name, field.name)
                proxy_field.set_proxy_model(self.proxy_model)
                yield proxy_field
        raise StopIteration
