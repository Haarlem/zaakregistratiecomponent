from lxml import etree

from ...apiauth.choices import EndpointTypeChoices
from ...apiauth.tests.factory_models import ApplicationFactory
from ...async.consumer import Consumer
from ...rgbz.tests.factory_models import ZaakFactory
from ..stuf.choices import BerichtcodeChoices
from .base import BaseSoapTests, BaseTestPlatformTests


class overdragenZaak_Du01Tests(BaseSoapTests):
    pass


class STPoverdragenZaak_Du01Tests(BaseTestPlatformTests):
    maxDiff = None
    test_files_subfolder = 'stp_overdragenZaak'

    def setUp(self):
        super().setUp()

        # Reset the cached WSDL since it might contain the URL of
        # the other LiveServerTestCase (which uses a different port)
        from zaakmagazijn.api import views
        from spyne.interface import AllYourInterfaceDocuments

        # TODO: [TECH] Find a proper way to get all the WSDLs
        for view in [views.ontvangasynchroon_view]:
            view.__wrapped__._wsdl = None
            view.__wrapped__.doc = AllYourInterfaceDocuments(view.__wrapped__.app.interface)

        self.ontvanger = ApplicationFactory(name='STP', organisation__name='KING')

        # Basically, we communicate with ourselves... (we implemented DI01 just for testing).
        self.ontvanger.endpoint_set.create(
            type=EndpointTypeChoices.ontvang_asynchroon,
            url='{}/{}/?WSDL'.format(self.live_server_url, 'OntvangAsynchroon')
        )

        self.consumer = Consumer(self.ontvanger)
        self.zaak = ZaakFactory.create(zaaktype__archiefclassificatiecode='123')

    def test_overdragenZaak_Di01_geaccepteerd(self):
        """
        1. Verzoek overdragenZaak_Di01: ZS -> STP
        2. Antwoord Bv03: STP -> ZS

        3. Asynchroon antwoord: overdragenZaakDu01: STP -> ZS
        4. Antwoord Bv03: ZS -> STP
        """

        # Step 1 & 2
        response = self.consumer.overdragenZaak(self.zaak, melding='melding')

        response_root = etree.fromstring(response.content)
        response_berichtcode = response_root.xpath('//stuf:stuurgegevens/stuf:berichtcode', namespaces=self.nsmap)[0].text

        self.assertEqual(response_berichtcode, BerichtcodeChoices.bv03)

        # Step 3 & 4
        context = {
            'referentienummer': self.genereerID(10),
            'zaakidentificatie': self.zaak.zaakidentificatie,
            'antwoord': 'Overdracht geaccepteerd',
        }
        response = self._do_request('OntvangAsynchroon', 'overdragenZaak_Du01.xml', context)

        response_root = etree.fromstring(response.content)
        response_berichtcode = response_root.xpath('//stuf:stuurgegevens/stuf:berichtcode', namespaces=self.nsmap)[0].text

        self.assertEqual(response_berichtcode, BerichtcodeChoices.bv03, response.content)

    def test_overdragenZaak_Du01_geweigerd(self):
        """
        5. Verzoek overdragenZaak_Di01: ZS -> STP
        6. Antwoord Bv03: STP -> ZS

        7. Asynchroon antwoord: overdragenZaakDu01: STP -> ZS
        8. Antwoord Bv03: ZS -> STP
        """

        # Step 1 & 2
        response = self.consumer.overdragenZaak(self.zaak, melding='melding')

        response_root = etree.fromstring(response.content)
        response_berichtcode = response_root.xpath('//stuf:stuurgegevens/stuf:berichtcode', namespaces=self.nsmap)[0].text

        self.assertEqual(response_berichtcode, BerichtcodeChoices.bv03)

        # Step 3 & 4
        context = {
            'referentienummer': self.genereerID(10),
            'zaakidentificatie': self.zaak.zaakidentificatie,
            'antwoord': 'Overdracht geweigerd',
        }
        response = self._do_request('OntvangAsynchroon', 'overdragenZaak_Du01.xml', context)

        response_root = etree.fromstring(response.content)
        response_berichtcode = response_root.xpath('//stuf:stuurgegevens/stuf:berichtcode', namespaces=self.nsmap)[0].text

        self.assertEqual(response_berichtcode, BerichtcodeChoices.bv03, response.content)
