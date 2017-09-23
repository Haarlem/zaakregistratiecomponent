from lxml import etree

from ...rgbz.choices import JaNee
from ...rgbz.tests.factory_models import (
    EnkelvoudigInformatieObjectFactory, StatusFactory, ZaakFactory,
    ZaakInformatieObjectFactory
)
from ..stuf.choices import BerichtcodeChoices
from .base import BaseTestPlatformTests


class DMSMockMixin:
    extra_client_mocks = [
        'zaakmagazijn.api.services.cancel_checkout.dms_client',
    ]

    @property
    def _service_dms_client(self):
        return self._extra_mocked_dms_clients[0]


class STPcancelCheckout_Di02Tests(DMSMockMixin, BaseTestPlatformTests):
    """
    Precondities:
    Scenario's maakZaakdocument (P) en  geefZaakdocumentbewerken (P) zijn succesvol uitgevoerd.
    Dit scenario betreft documenten die in scenario maakZaakdocument (P) zijn toegevoegd en in scenario
    geefZaakdocumentbewerken (P) zijn uitgecheckt.
    """
    test_files_subfolder = 'stp_cancelCheckout'
    porttype = 'VerwerkSynchroonVrijBericht'

    def setUp(self):
        super().setUp()
        self.status = StatusFactory.create(indicatie_laatst_gezette_status=JaNee.ja)
        self.zaak = ZaakFactory.create()
        self.zaak.status_set.add(self.status)
        self.edc1 = EnkelvoudigInformatieObjectFactory.create()
        self.zio = ZaakInformatieObjectFactory.create(zaak=self.zaak,
                                                      informatieobject=self.edc1)

        self.context = {
            'datumEergisteren': self.genereerdatumtijd(-2),
            'datumVandaag': self.genereerdatumtijd(),
            'datumMorgen': self.genereerdatumtijd(1),
            'referentienummer': self.genereerID(10),
            'maakzaakdocument_identificatie_1': self.edc1.informatieobjectidentificatie,
            'tijdstipRegistratie': self.genereerdatumtijd(),
            'zds_zaaktype_code': '12345678',
            'zds_zaaktype_omschrijving': 'Aanvraag burgerservicenummer behandelen',
            # TODO: [TECH] check this one!
            'checkoutid_doc1': 'doc1',
        }

    def _test_response(self, response):
        self.assertEquals(response.status_code, 200, response.content)

        response_root = etree.fromstring(response.content)
        response_berichtcode = response_root.xpath(
            '//stuf:stuurgegevens/stuf:berichtcode', namespaces=self.nsmap
        )[0].text
        self.assertEqual(response_berichtcode, BerichtcodeChoices.bv02, response.content)

    def test_cancelCheckout(self):
        vraag = 'cancelCheckout_Di02.xml'
        response = self._do_request(self.porttype, vraag, self.context)

        self._test_response(response)

        self._service_dms_client.cancel_checkout.assert_called_once_with(self.edc1, 'doc1')
