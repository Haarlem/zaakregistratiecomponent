from django.core.exceptions import ValidationError
from django.test import TestCase

from zaakmagazijn.cmis.tests.mocks import MockDMSMixin

from ..models import Object
from ..validators import validate_nen360id
from .factory_models.objecten import (
    InrichtingsElementObjectFactory, KadastraalPerceelObjectFactory,
    ObjectFactory, ObjectMetZaakFactory, WijkObject, WijkObjectFactory
)


class ObjectTestCase(MockDMSMixin, TestCase):
    def test_helper_function_is_type_with_subclass(self):
        obj = WijkObjectFactory.create()
        obj = WijkObject.objects.get(pk=obj.pk)
        self.assertEqual(obj.object_ptr.is_type(), obj)

    def test_attr_objecttype_with_subclass(self):
        obj = WijkObjectFactory.create()
        obj = WijkObject.objects.get(pk=obj.pk)
        self.assertEqual(obj.object_ptr.objecttype, obj._meta.mnemonic)

    def test_helper_function_is_type(self):
        obj = ObjectFactory.create()
        obj = Object.objects.get(pk=obj.pk)
        self.assertEquals(obj.is_type(), obj)

    def test_attr_objecttype(self):
        obj = ObjectFactory.create()
        obj = Object.objects.get(pk=obj.pk)
        self.assertEqual(obj.objecttype, '???')

    def test_helper_function_relatie_betreft(self):
        obj = ObjectMetZaakFactory.create()
        self.assertEqual(obj.betreft(), obj.object_zaken.first())


class InrichtingsElementObjectTests(MockDMSMixin, TestCase):
    def test_nen360id_validator_too_short(self):
        inrichting = InrichtingsElementObjectFactory.create(identificatie='abc')
        with self.assertRaises(ValidationError) as e:
            inrichting.full_clean()
        self.assertIn(validate_nen360id.message, e.exception.message_dict['identificatie'])

    def test_nen360id_validator_valid(self):
        inrichting = InrichtingsElementObjectFactory.create(identificatie='BE.IMGEO.1234567890123456')
        self.assertIsNone(inrichting.full_clean())

    def test_nen360id_validator_too_long(self):
        inrichting = InrichtingsElementObjectFactory.create(identificatie='BE.IMGEO.1234567890123456x')
        with self.assertRaises(ValidationError) as e:
            inrichting.full_clean()
        self.assertIn(validate_nen360id.message, e.exception.message_dict['identificatie'])


class KadastraalPerceelObjectTests(MockDMSMixin, TestCase):
    def test_negative_number(self):
        perceel = KadastraalPerceelObjectFactory.create(identificatie='-1')
        with self.assertRaises(ValidationError) as e:
            perceel.full_clean()
        self.assertIn('De waarde moet een niet-negatief getal zijn.', e.exception.message_dict['identificatie'])

    def test_max_value_too_long(self):
        perceel = KadastraalPerceelObjectFactory.create(identificatie='1234567890123456')
        with self.assertRaises(ValidationError) as e:
            perceel.full_clean()

    def test_valid(self):
        perceel = KadastraalPerceelObjectFactory.create(identificatie='123456789012345')
        self.assertIsNone(perceel.full_clean())
