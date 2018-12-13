import logging

from django.db.models.constants import LOOKUP_SEP

logger = logging.getLogger(__name__)


class ProxyQuerySet:
    def __init__(self, proxy_model, queryset=None):
        self.proxy_model = proxy_model
        self.queryset = queryset

        if self.queryset is None:
            self.queryset = self.get_django_model().objects.all()

    def get_django_model(self):
        return self.proxy_model.model

    def __iter__(self):
        for obj in self.queryset:
            yield self.proxy_model.from_django_obj(obj)

    def all(self):
        return self

    def count(self):
        return self.queryset.count()

    def exists(self):
        return self.queryset.exists()

    def delete(self):
        return self.queryset.delete()

    def distinct(self):
        return self.__class__(proxy_model=self.proxy_model, queryset=self.queryset.distinct())

    def __getitem__(self, k):
        queryset = self.queryset.__getitem__(k)
        return self.__class__(proxy_model=self.proxy_model, queryset=queryset)

    def order_by(self, *field_names):
        new_order_by = []
        for field_name in field_names:
            new_order_by.append(self.translate_nested_order_by(field_name))

        new_queryset = self.queryset.order_by(*new_order_by)
        return self.__class__(proxy_model=self.proxy_model, queryset=new_queryset)

    def translate_nested_order_by(self, field):
        reverse = field.startswith('-')
        if reverse:
            field = field[1:]

        new_lookup = ''
        prev_model = self.proxy_model
        for part in field.split(LOOKUP_SEP):
            if new_lookup:
                new_lookup += LOOKUP_SEP
            field = prev_model.get_field(part)
            rgbz2_field_name = field.rgbz2_name
            if not hasattr(field, 'relation_proxy_model'):
                new_lookup += rgbz2_field_name
                break
            else:
                # Hack to remove "_set" postfix.
                if rgbz2_field_name.endswith('_set'):
                    rgbz2_field_name = rgbz2_field_name[:-4]
                new_lookup += rgbz2_field_name

            prev_model = field.relation_proxy_model

        if reverse:
            new_lookup = '-{}'.format(new_lookup)

        return new_lookup

    def translate_nested_filter(self, field):
        new_lookup = ''
        prev_model = self.proxy_model
        for part in field.split(LOOKUP_SEP):
            if new_lookup:
                new_lookup += LOOKUP_SEP
            field = prev_model.get_field(part)
            new_lookup += field.rgbz2_name
            if not hasattr(field, 'relation_proxy_model'):
                break
            prev_model = field.relation_proxy_model

        return new_lookup

    def filter(self, **kwargs):
        """
        *args is not supported.

        Filtering is a bit trippy, since we want to filter on RGBZ1 values, and not
        on RGBZ2 values.
        """
        direct_translatable_fields = list(self.proxy_model.get_fields(
            in_rgbz1=True, in_rgbz2=True, is_foreign_key=True,
            is_field=True, only_non_computed=True
        ))
        applicable_fields = {field for field in self.proxy_model.get_fields(in_rgbz1=True, is_foreign_key=True, is_field=True) if field.rgbz1_name in kwargs}

        extra_fields = kwargs.keys() - {field.rgbz1_name for field in applicable_fields}

        extra_filter_kwargs = {
            self.translate_nested_filter(field_name): kwargs[field_name] for field_name in extra_fields}

        # Get the fields that are part of both RGBZ1, and RGBZ2 and are not computed. Basically
        # all fields that are directly translated. This is done so we don't get the entire database back.
        filterable_fields = [field for field in direct_translatable_fields if field.rgbz1_name in kwargs]
        filter_kwargs = {field.rgbz2_name: self.proxy_model._to_rgbz2_field(field, kwargs) for field in filterable_fields}

        full_filter_kwargs = {}
        full_filter_kwargs.update(filter_kwargs)
        full_filter_kwargs.update(extra_filter_kwargs)
        filtered_queryset = self.queryset.filter(**full_filter_kwargs)

        # Line below only for logging purposes
        _mapped_kwargs = {}

        if applicable_fields:
            filter_pks = []
            for obj in filtered_queryset:
                # Iterate over all fields and if they all match, add the PK to the
                # filter.
                match = False
                for field in applicable_fields:
                    filter_value = field.get_django_field().to_python(kwargs[field.rgbz1_name])
                    db_value = self.proxy_model._to_rgbz1_field(field, obj)

                    # Line below only for logging purposes
                    _mapped_kwargs[field.rgbz2_name] = filter_value

                    match = filter_value == db_value
                    if not match:
                        break

                if match:
                    filter_pks.append(obj.pk)

            filtered_queryset = filtered_queryset.filter(pk__in=filter_pks)

        return self.__class__(proxy_model=self.proxy_model, queryset=filtered_queryset)

    def get(self, **kwargs):
        proxy_queryset = self.filter(**kwargs)
        queryset = proxy_queryset.queryset
        django_obj = queryset.get()
        return self.proxy_model.from_django_obj(django_obj)

    def first(self):
        django_obj = self.queryset.first()
        return self.proxy_model.from_django_obj(django_obj)


class BaseManager:
    def get_proxy_queryset(self):
        raise NotImplementedError

    def get(self, **kwargs):
        return self.get_proxy_queryset().get(**kwargs)

    def filter(self, **kwargs):
        return self.get_proxy_queryset().filter(**kwargs)

    def all(self):
        return self.get_proxy_queryset().all()

    def exists(self):
        return self.get_proxy_queryset().exists()

    def get_or_create(self, defaults=None, **kwargs):
        try:
            return self.get(**kwargs), False
        except self.model.DoesNotExist:
            create_kwargs = {}
            create_kwargs.update(kwargs)
            if defaults:
                create_kwargs.update(defaults)
            return self.create(**create_kwargs), True


class ProxyManager(BaseManager):
    def create(self, **kwargs):
        """
        *args is not supported.
        """

        rgbz2_kwargs = self.proxy_model.to_rgbz2_kwargs(kwargs)
        django_model = self.proxy_model.get_model()
        django_obj = django_model.objects.create(**rgbz2_kwargs)

        return self.proxy_model.from_django_obj(django_obj)

    @property
    def model(self):
        return self.proxy_model

    def get_proxy_queryset(self):
        return ProxyQuerySet(proxy_model=self.proxy_model)

    def contribute_to_class(self, proxy_model, name):
        self.proxy_model = proxy_model


class ProxyRelatedManager(BaseManager):
    def __init__(self, proxy_model, related_manager):
        self.proxy_model = proxy_model
        self.related_manager = related_manager

    @property
    def model(self):
        return self.proxy_model

    def get_proxy_queryset(self):
        return ProxyQuerySet(proxy_model=self.proxy_model, queryset=self.related_manager.all())

    def create(self, **kwargs):
        rgbz2_kwargs = self.proxy_model.to_rgbz2_kwargs(kwargs)
        django_obj = self.related_manager.create(**rgbz2_kwargs)

        return self.proxy_model.from_django_obj(django_obj)

    def add(self, *proxy_objs, **kwargs):
        return self.related_manager.add(*[obj.to_django_obj() for obj in proxy_objs], **kwargs)
