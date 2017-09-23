from lxml import etree

from zaakmagazijn.api.stuf.choices import BerichtcodeChoices
from zaakmagazijn.api.tests.base import BaseTestPlatformTests
from zaakmagazijn.rgbz.choices import JaNee
from zaakmagazijn.rgbz.tests.factory_models import (
    EnkelvoudigInformatieObject, EnkelvoudigInformatieObjectFactory, Status,
    StatusFactory, Zaak, ZaakFactory, ZaakInformatieObject,
    ZaakInformatieObjectFactory
)


class DMSMockMixin:
    extra_client_mocks = [
        'zaakmagazijn.api.services.ontkoppel_zaakdocument.dms_client',
    ]

    @property
    def _service_dms_client(self):
        return self._extra_mocked_dms_clients[0]


class STPontkoppelZaakdocument_Di02Tests(DMSMockMixin, BaseTestPlatformTests):
    """
    Precondities:
    Scenario creeerZaak (P) is succesvol uitgevoerd.
    Dit scenario betreft documenten bij zaken die in scenario creeerZaak (P) zijn toegevoegd.
    Scenario voegZaakdocumentToe (P) is succesvol uitgevoerd.
    Dit scenario betreft documenten die in scenario voegZaakdocumentToe (P) is toegevoegd
    """
    test_files_subfolder = 'stp_ontkoppelZaakdocument'
    porttype = 'VerwerkSynchroonVrijBericht'

    def setUp(self):
        super().setUp()
        self.status = StatusFactory.create(indicatie_laatst_gezette_status=JaNee.ja)
        self.zaak = ZaakFactory.create()
        self.zaak.status_set.add(self.status)
        self.edc1 = EnkelvoudigInformatieObjectFactory.create()
        self.zio = ZaakInformatieObjectFactory.create(zaak=self.zaak,
                                                      informatieobject=self.edc1)

    def _test_response(self, response):
        self.assertEquals(response.status_code, 200, response.content)

        response_root = etree.fromstring(response.content)
        response_berichtcode = response_root.xpath(
            '//stuf:stuurgegevens/stuf:berichtcode', namespaces=self.nsmap
        )[0].text
        self.assertEqual(response_berichtcode, BerichtcodeChoices.bv02, response.content)

    def test_ontkoppelZaakdocument_Di02(self):
        # set up mocks
        self._service_dms_client.is_locked.return_value = False

        vraag = 'ontkoppelZaakdocument_Di02.xml'
        context = {
            'datumVandaag': self.genereerdatum(),
            'creerzaak_identificatie_7': self.zaak.zaakidentificatie,
            'voegzaakdocumenttoe_identificatie_9': self.edc1.informatieobjectidentificatie,
            'referentienummer': self.genereerID(10),
            'gemeentecode': '',
            'zds_zaaktype_code': '12345678',
            'zds_zaaktype_omschrijving': 'Aanvraag burgerservicenummer behandelen',
        }
        response = self._do_request(self.porttype, vraag, context)

        self._test_response(response)

        self.assertFalse(ZaakInformatieObject.objects.filter(zaak=self.zaak, informatieobject=self.edc1).exists())
        self.assertEqual(Zaak.objects.filter(id=self.zaak.id).count(), 1)
        self.assertEqual(EnkelvoudigInformatieObject.objects.filter(id=self.edc1.id).count(), 1)
        self.assertEqual(Status.objects.filter(id=self.status.id).count(), 1)

        self._service_dms_client.is_locked.assert_called_once_with(self.edc1)
        self._service_dms_client.ontkoppel_zaakdocument.assert_called_once_with(self.edc1, self.zaak)
        # self._service_dms_client.verwijder_document.assert_called_once_with(self.edc1)
        self._service_dms_client.verwijder_document.assert_not_called()
