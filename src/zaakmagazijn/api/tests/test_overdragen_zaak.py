from unittest import skip

from lxml import etree

from ...apiauth.choices import EndpointTypeChoices
from ...apiauth.tests.factory_models import ApplicationFactory
from ...async.consumer import Consumer
from ...rgbz.tests.factory_models import ZaakFactory
from ..stuf.choices import BerichtcodeChoices
from .base import BaseTestPlatformTests


class STPoverdragenZaak_Du01Tests(BaseTestPlatformTests):
    maxDiff = None
    test_files_subfolder = 'stp_overdragenZaak'

    def setUp(self):
        super().setUp()

        # Reset the cached WSDL since it might contain the URL of
        # the other LiveServerTestCase (which uses a different port)
        from zaakmagazijn.api import views
        from spyne.interface import AllYourInterfaceDocuments

        # TODO [TECH]: Find a proper way to get all the WSDLs
        for view in [views.ontvangasynchroon_view]:
            view.__wrapped__._wsdl = None
            view.__wrapped__.doc = AllYourInterfaceDocuments(view.__wrapped__.app.interface)

        self.ontvanger = ApplicationFactory(name='TTA', organisation__name='ORG')

        # Basically, we communicate with ourselves... (we implemented DI01 just for testing).
        self.ontvanger.endpoint_set.create(
            type=EndpointTypeChoices.ontvang_asynchroon,
            url='{}/{}/?WSDL'.format(self.live_server_url, 'OntvangAsynchroon')
        )

        self.consumer = Consumer(self.ontvanger)
        self.zaak = ZaakFactory.create(zaaktype__archiefclassificatiecode='123')

    def test_overdragenZaak_Du01_geaccepteerd(self):
        """
        1. Verzoek overdragenZaak_Di01: STP -> ZS
        2. Antwoord Bv03: ZS -> STP

        3. Asynchroon antwoord: overdragenZaakDu01: ZS -> STP
        4. Antwoord Bv03: STP -> ZS
        """
        # Step 1 & 2
        context = {
            'referentienummer': self.genereerID(10),
            'zaakidentificatie': self.zaak.zaakidentificatie,
        }
        response = self._do_request('OntvangAsynchroon', 'overdragenZaak_Di01.xml', context)

        response_root = etree.fromstring(response.content)
        response_berichtcode = response_root.xpath('//stuf:stuurgegevens/stuf:berichtcode', namespaces=self.nsmap)[0].text

        self.assertEqual(response_berichtcode, BerichtcodeChoices.bv03, response.content)

        # Step 3 & 4
        response = self.consumer.overdragenZaak(self.zaak, True, context['referentienummer'], melding='melding')

        response_root = etree.fromstring(response.content)
        response_berichtcode = response_root.xpath('//stuf:stuurgegevens/stuf:berichtcode', namespaces=self.nsmap)[0].text

        self.assertEqual(response_berichtcode, BerichtcodeChoices.bv03)

    def test_overdragenZaak_Du01_geweigerd(self):
        """
        1. Verzoek overdragenZaak_Di01: STP -> ZS
        2. Antwoord Bv03: ZS -> STP

        3. Asynchroon antwoord: overdragenZaakDu01: ZS -> STP
        4. Antwoord Bv03: STP -> ZS
        """

        # Step 1 & 2
        context = {
            'referentienummer': self.genereerID(10),
            'zaakidentificatie': self.zaak.zaakidentificatie,
        }
        response = self._do_request('OntvangAsynchroon', 'overdragenZaak_Di01.xml', context)

        response_root = etree.fromstring(response.content)
        response_berichtcode = response_root.xpath('//stuf:stuurgegevens/stuf:berichtcode', namespaces=self.nsmap)[0].text

        self.assertEqual(response_berichtcode, BerichtcodeChoices.bv03, response.content)

        # Step 3 & 4
        response = self.consumer.overdragenZaak(self.zaak, False, context['referentienummer'], melding='melding')

        response_root = etree.fromstring(response.content)
        response_berichtcode = response_root.xpath('//stuf:stuurgegevens/stuf:berichtcode', namespaces=self.nsmap)[0].text

        self.assertEqual(response_berichtcode, BerichtcodeChoices.bv03)
