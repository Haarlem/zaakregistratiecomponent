from django.db import models

from ...rgbz.models import (
    EnkelvoudigInformatieObject, InformatieObject, InformatieObjectType,
    SamengesteldInformatieObject
)
from ...rgbz.validators import validate_starts_with_gemeentecode
from ..base import ModelProxy, ProxyField, ProxyForeignKey, ProxyOneToMany
from ..manager import ProxyManager


class DocumentTypeProxy(ModelProxy):
    model = InformatieObjectType
    mnemonic = 'DCT'

    fields = (
        ProxyField('documenttypeomschrijving', 'informatieobjecttypeomschrijving'),
        ProxyField('documentcategorie', 'informatieobjectcategorie'),
        ProxyField('documenttypeomschrijving_generiek', None, rgbz1_field=models.CharField(
            verbose_name='documenttypeomschrijving_generiek', max_length=80, blank=True)),
    )
    objects = ProxyManager()

    @classmethod
    def to_rgbz1_documenttypeomschrijving_generiek(cls, obj):
        generiek = obj.informatieobjecttypeomschrijving_generiek
        if generiek:
            return generiek.informatieobjecttypeomschrijving_generiek

        return None


class DocumentProxy(ModelProxy):
    model = InformatieObject
    mnemonic = '??'
    fields = (
        ProxyField('identificatie', 'informatieobjectidentificatie'),
        ProxyField(None, 'bronorganisatie'),
        ProxyField('documentcreatiedatum', 'creatiedatum'),
        ProxyField('documentontvangstdatum', 'ontvangstdatum'),
        ProxyField('documenttitel', 'titel'),
        ProxyField('documentbeschrijving', 'beschrijving'),
        ProxyField('documentverzenddatum', 'verzenddatum'),
        ProxyField('vertrouwelijkaanduiding', 'vertrouwelijkaanduiding'),
        ProxyField('documentauteur', 'auteur'),
        ProxyField('_inhoud', '_inhoud', is_virtual=True),
        ProxyForeignKey('documenttype', 'informatieobjecttype', DocumentTypeProxy),
        ProxyOneToMany('zaakinformatieobject_set', 'zaakinformatieobject_set', 'zaakmagazijn.rgbz_mapping.models.ZaakDocumentProxy'),
    )
    objects = ProxyManager()


class EnkelvoudigDocumentProxy(ModelProxy):
    model = EnkelvoudigInformatieObject
    mnemonic = 'EDC'
    fields = list(DocumentProxy.fields) + [
        ProxyField('documentformaat', 'formaat'),
        ProxyField('documenttaal', 'taal'),
        ProxyField('documentversie', 'versie'),
        ProxyField('documentstatus', 'informatieobject_status'),
        ProxyField('documentlink', 'link'),
    ]
    objects = ProxyManager()

    def __init__(self, _obj=None, **kwargs):
        _inhoud = kwargs.pop('_inhoud', None)

        super().__init__(_obj, **kwargs)

    @classmethod
    def from_django_obj(cls, obj):
        _obj = obj.is_type()
        return super().from_django_obj(_obj)

    @classmethod
    def to_rgbz2_informatieobjectidentificatie(cls, rgbz1_kwargs):
        val = str(rgbz1_kwargs['identificatie'])
        validate_starts_with_gemeentecode(val)
        return val

    @classmethod
    def to_rgbz2_bronorganisatie(cls, rgbz1_kwargs):
        return str(rgbz1_kwargs['identificatie'])[:4]

    @classmethod
    def to_rgbz1_documentformaat(cls, obj):
        # The specification in RGBZ 1.0 for "documentformaat" indicates type
        # AN10. This effectively means that only 10 characters can be
        # returned. However, the XSD of ZDS 1.2 indicates a max of 85
        # characters. In agreement with Haarlem, this value is not cut off.
        return obj.formaat

    @classmethod
    def to_rgbz1_documentlink(cls, obj):
        return obj.link[:200] if obj.link else None

    @classmethod
    def to_rgbz1__inhoud(cls, obj):
        from django.utils.functional import lazystr
        return lazystr(lambda obj: obj._inhoud)

    def is_relevant_voor(self):
        return self.zaakinformatieobject_set, {}

    # """
    # Proxy this the the virtual _inhoud CMIS field directly.
    # """

    def _get_inhoud(self):
        return self._obj._inhoud

    def _set_inhoud(self, value):
        self._obj._inhoud = value

    _inhoud = property(_get_inhoud, _set_inhoud)


class SamengesteldInformatieObjectProxy(ModelProxy):
    model = SamengesteldInformatieObject
    mnemonic = 'SDC'
    fields = list(DocumentProxy.fields)
