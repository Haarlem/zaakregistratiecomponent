from django.core.exceptions import ValidationError
from django.test import TestCase

from .factory_models import (
    EnkelvoudigInformatieObjectFactory, SamengesteldInformatieObjectFactory
)


class SamenGesteldInformatieObjectTestCase(TestCase):

    def test_hulpfunctie_relatie_omvat_met_twee_enkelvoudige_objecten(self):
        samengesteldinfobj = SamengesteldInformatieObjectFactory.create()
        deelnemer1 = EnkelvoudigInformatieObjectFactory.create(samengesteld_informatieobject=samengesteldinfobj)
        deelnemer2 = EnkelvoudigInformatieObjectFactory.create(samengesteld_informatieobject=samengesteldinfobj)
        self.assertEqual(len(samengesteldinfobj.omvat()), 2)
        self.assertTrue(deelnemer1 in samengesteldinfobj.omvat())
        self.assertTrue(deelnemer2 in samengesteldinfobj.omvat())

    def test_hulpfunctie_relatie_omvat_met_1_enkelvoudig_object(self):
        samengesteldinfobj = SamengesteldInformatieObjectFactory.create()
        EnkelvoudigInformatieObjectFactory.create(samengesteld_informatieobject=samengesteldinfobj)
        with self.assertRaises(ValidationError):
            samengesteldinfobj.omvat()
