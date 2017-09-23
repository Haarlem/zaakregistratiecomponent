import datetime

from lxml import etree

from ...rgbz.tests.factory_models import (
    Besluit, BesluitFactory, BesluitTypeFactory,
    EnkelvoudigInformatieObjectFactory
)
from ...utils import stuf_datetime
from ..stuf.choices import BerichtcodeChoices
from .base import BaseTestPlatformTests


class STPupdateBesluit_BslLk01Tests(BaseTestPlatformTests):
    maxDiff = None
    test_files_subfolder = 'stp_updateBesluit'
    porttype = 'OntvangAsynchroon'

    def setUp(self):
        super().setUp()

        self.besluit = BesluitFactory.create()
        self.today_date = datetime.date.today()

        self.today = self.today_date.strftime(stuf_datetime.DATE_FORMAT)
        self.two_days_ago = (self.today_date - datetime.timedelta(days=2)).strftime(stuf_datetime.DATE_FORMAT)

    def _test_response(self, response):
        self.assertEquals(response.status_code, 200, response.content)

        response_root = etree.fromstring(response.content)
        response_berichtcode = response_root.xpath('//stuf:stuurgegevens/stuf:berichtcode', namespaces=self.nsmap)[0].text
        self.assertEqual(response_berichtcode, BerichtcodeChoices.bv03, response.content)

    def test_updateBesluit_BslLk01_01(self):
        """
        STP test: update an existing Besluit by setting its besluittype and toelichting
        """

        self.besluit.besluittype = BesluitTypeFactory.create(
            besluittypeomschrijving=None)
        self.besluit.save()

        besluittype = BesluitTypeFactory.create(besluittypeomschrijving='bst.omschrijving')

        vraag = 'updateBesluit_BslLk01_1.xml'
        context = {
            'voegbesluittoe_identificatie_5': self.besluit.besluitidentificatie,
            'datumVandaag': self.today,
            'datumEergisteren': self.two_days_ago,
        }
        response = self._do_request(self.porttype, vraag, context)

        self._test_response(response)

        # Check if update worked
        besluit = Besluit.objects.get(identificatie=self.besluit.besluitidentificatie)
        self.assertEqual(besluit.besluittype, besluittype)
        self.assertEqual(besluit.besluittoelichting, 'toelichting_update')

    def test_updateBesluit_BslLk01_03(self):
        """
        STP test:
        Update an existing Besluit with 2 documents iob1+iob3.
        Replace iob3 document with iob5, keeping iob1 intact
        """
        besluittype = BesluitTypeFactory.create(besluittypeomschrijving='bst.omschrijving3')
        informatieobject1 = EnkelvoudigInformatieObjectFactory.create(informatieobjectidentificatie='iob1')
        informatieobject3 = EnkelvoudigInformatieObjectFactory.create(informatieobjectidentificatie='iob3')
        self.besluit = BesluitFactory.create(informatieobject=(informatieobject1, informatieobject3))
        informatieobject5 = EnkelvoudigInformatieObjectFactory.create(informatieobjectidentificatie='iob5')

        vraag = 'updateBesluit_BslLk01_3.xml'
        context = {
            'voegbesluittoe_identificatie_7': self.besluit.besluitidentificatie,
            'voegzaakdocumenttoe_identificatie_1': informatieobject1.informatieobjectidentificatie,
            'voegzaakdocumenttoe_identificatie_3': informatieobject3.informatieobjectidentificatie,
            'voegzaakdocumenttoe_identificatie_5': informatieobject5.informatieobjectidentificatie,
            'datumVandaag': self.today,
            'datumEergisteren': self.two_days_ago,
        }
        response = self._do_request(self.porttype, vraag, context)

        self._test_response(response)

        # Check if update worked
        besluit = Besluit.objects.get(identificatie=self.besluit.besluitidentificatie)
        self.assertEqual(besluit.besluittype, besluittype)
        self.assertEqual(besluit.besluittoelichting, 'toelichting3')
        self.assertEqual(besluit.besluitdatum, self.today)
        self.assertEqual(besluit.ingangsdatum, self.today)
        self.assertEqual(besluit.vervaldatum, self.today)
        self.assertEqual(besluit.publicatiedatum, self.today)
        self.assertEqual(besluit.verzenddatum, self.today)
        self.assertEqual(besluit.uiterlijke_reactiedatum, self.today)
        self.assertEqual(besluit.vervalreden, 'Besluit met tijdelijke werking')

        # Check InformatieObjecten
        iobs = besluit.kan_vastgelegd_zijn_als().values_list('informatieobjectidentificatie', flat=True)
        self.assertEqual(len(iobs), 2)
        self.assertTrue('iob1' in iobs)
        self.assertTrue('iob5' in iobs)

    def test_updateBesluit_BslLk01_05(self):
        besluittype = BesluitTypeFactory.create(besluittypeomschrijving='bst.omschrijving')
        informatieobject5 = EnkelvoudigInformatieObjectFactory.create()
        self.assertEqual(len(self.besluit.kan_vastgelegd_zijn_als()), 0)

        vraag = 'updateBesluit_BslLk01_5.xml'
        context = {
            'voegbesluittoe_identificatie_9': self.besluit.besluitidentificatie,
            'voegzaakdocumenttoe_identificatie_5': informatieobject5.informatieobjectidentificatie,
            'datumVandaag': self.today,
            'datumEergisteren': self.two_days_ago,
        }
        response = self._do_request(self.porttype, vraag, context)

        self._test_response(response)

        # Check if update worked and we've linked an IO
        besluit = Besluit.objects.get(identificatie=self.besluit.besluitidentificatie)
        self.assertEqual(besluit.besluittype, besluittype)
        self.assertEqual(besluit.kan_vastgelegd_zijn_als()[0].informatieobjectidentificatie, informatieobject5.informatieobjectidentificatie)
