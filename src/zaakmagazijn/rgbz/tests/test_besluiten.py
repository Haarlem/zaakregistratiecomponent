from unittest import skip

from django.core.exceptions import ValidationError
from django.test import TestCase

from .factory_models import (
    BesluitFactory, BesluitTypeFactory, InformatieObjectFactory, ZaakFactory
)


class BesluitTestCase(TestCase):

    @skip('TODO [TECH]: identificatie field on besluit is deleted, it used to have AlphanumericExcludingDiacritic(start=5)')
    def test_besluit_validatie(self):
        with self.assertRaises(ValidationError):
            BesluitFactory.create(identificatie='identificatiéééé')

    def test_besluit_validatie_uitzondering_voor_gemeente_code(self):
        correcte_besluitidentificatie = 'éééIDENTIFCaTie'
        besluit = BesluitFactory.create(identificatie=correcte_besluitidentificatie)
        self.assertEqual(besluit.besluitidentificatie, correcte_besluitidentificatie)

    def test_hulpfunctie_relatie_is_uitkomst_van(self):
        zaak = ZaakFactory.create()
        besluit = BesluitFactory.create(zaak=zaak)
        self.assertEqual(besluit.is_uitkomst_van(), zaak)

    def test_hulpfunctie_relatie_is_van(self):
        besluittype = BesluitTypeFactory.create()
        besluit = BesluitFactory.create(besluittype=besluittype)
        self.assertEqual(besluit.is_van(), besluittype)

    def test_hulpfunctie_kan_vast_gelegd_zijn_als(self):
        informatieobject1 = InformatieObjectFactory.create()
        informatieobject2 = InformatieObjectFactory.create()
        besluit = BesluitFactory.create(informatieobject=(informatieobject1, informatieobject2))
        informatieobjecten = list(besluit.kan_vastgelegd_zijn_als())
        self.assertEqual(len(informatieobjecten), 2)
        self.assertEqual(informatieobjecten, [informatieobject1, informatieobject2])
