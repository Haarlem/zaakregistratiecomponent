from datetime import datetime, timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase

from zaakmagazijn.utils.stuf_datetime import stuf_date

from ..choices import JaNee
from ..models import ZaakInformatieObject
from .factory_models import (
    EigenschapFactory, StatusFactory, StatusTypeFactory, ZaakFactory,
    ZaakInformatieObjectFactory, ZaakMetInformatieObjectFactory,
    ZaakMetZakenRelatie, ZaakTypeFactory
)


class ZaakTestCase(TestCase):
    def test_zaakidentificatie_validatie_voor_diakrieten(self):
        with self.assertRaises(ValidationError):
            ZaakFactory.create(zaakidentificatie='identificatié')

    def test_hulpfunctie_relatie_kent(self):
        zaak = ZaakMetInformatieObjectFactory.create(
            status_set__indicatie_laatst_gezette_status=JaNee.ja
        )
        informatieobjecten = list(zaak.kent())
        self.assertEqual(len(informatieobjecten), 1)
        self.assertEqual(len(ZaakInformatieObject.objects.all()), 1)

        zaakinformatieobject = ZaakInformatieObject.objects.all().first()
        self.assertEqual(zaakinformatieobject.zaak, zaak)

    def test_hulpfunctie_relatie_heeft(self):
        yesterday = stuf_date(datetime.today() - timedelta(days=1))
        zaak = ZaakFactory.create()
        status1 = StatusFactory.create(zaak=zaak)
        status2 = StatusFactory.create(zaak=zaak, datum_status_gezet=yesterday)
        statussen = zaak.heeft()
        self.assertEqual(len(statussen), 2)
        self.assertTrue(status1 in statussen)
        self.assertTrue(status2 in statussen)

    def test_hulpfunctie_relatie_heeft_deelzaken(self):
        zaak1 = ZaakFactory.create()
        zaak2 = ZaakFactory.create(hoofdzaak=zaak1)
        zaak3 = ZaakFactory.create(hoofdzaak=zaak1)
        related_manager, filter_kwargs = zaak1.heeft_deelzaken()
        gerelateerde_zaken = list(related_manager.filter(**filter_kwargs))

        self.assertEqual(len(gerelateerde_zaken), 2)
        self.assertTrue(zaak2 in gerelateerde_zaken)
        self.assertTrue(zaak3 in gerelateerde_zaken)

    def test_hulpfunctie_relatie_heeft_gerelateerde(self):
        zaak = ZaakMetZakenRelatie.create()
        related_manager, filter_kwargs = zaak.heeft_gerelateerde()
        self.assertEqual(len(related_manager.filter(**filter_kwargs)), 1)

    def test_hulpfunctie_relatie_is_van(self):
        zaaktype = ZaakTypeFactory.create()
        zaak = ZaakFactory.create(zaaktype=zaaktype)
        self.assertEqual(zaak.is_van(), zaaktype)

    def test_hulpfunctie_relatie_is_deelzaak_van(self):
        hoofdzaak = ZaakFactory.create()
        zaak = ZaakFactory.create(hoofdzaak=hoofdzaak)
        self.assertEqual(zaak.is_deelzaak_van(), hoofdzaak)

    def test_hulpfunctie_eigenschappen(self):
        zaak = ZaakFactory.create()
        eigenschap1 = EigenschapFactory.create(zaak=zaak)
        eigenschap2 = EigenschapFactory.create(zaak=zaak)
        eigenschappen = zaak.eigenschappen()
        self.assertEqual(len(eigenschappen), 2)
        self.assertTrue(eigenschap1 in eigenschappen)
        self.assertTrue(eigenschap2 in eigenschappen)


class StatusTestCase(TestCase):
    def test_hulpfunctie_relatie_is_van(self):
        statustype1 = StatusTypeFactory.create()
        status = StatusFactory.create(status_type=statustype1)
        self.assertEqual(status.is_van(), statustype1)


class ZaakTypeTestCase(TestCase):
    def test_hulpfunctie_heeft(self):
        zaaktype = ZaakTypeFactory.create()
        statustype1 = StatusTypeFactory(zaaktype=zaaktype)
        statustype2 = StatusTypeFactory(zaaktype=zaaktype)
        statustypes = zaaktype.heeft()
        self.assertEqual(len(statustypes), 2)
        self.assertTrue(statustype1 in statustypes)
        self.assertTrue(statustype2 in statustypes)


class ZaakInformatieTestCase(TestCase):
    def test_hulpfunctie_relatie_is_relevant_voor(self):
        status = StatusFactory.create(indicatie_laatst_gezette_status=JaNee.ja)
        zaakinformatieobj = ZaakInformatieObjectFactory.create(zaak__status_set=[status])
        relevantie = zaakinformatieobj.is_relevant_voor()
        self.assertEqual(relevantie, status)
