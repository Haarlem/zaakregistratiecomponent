from io import BytesIO

from auditlog.models import LogEntry
from lxml import etree

from zaakmagazijn.rgbz_mapping.utils import to_proxy_obj

from ...rgbz.choices import JaNee
from ...rgbz.tests.factory_models import (
    EnkelvoudigInformatieObjectFactory, ZaakFactory,
    ZaakInformatieObjectFactory
)
from ..stuf.choices import BerichtcodeChoices
from .base import BaseSoapTests, BaseTestPlatformTests


class DMSMockMixin:
    extra_client_mocks = [
        'zaakmagazijn.cmis.fields.dms_client',
        'zaakmagazijn.api.services.geef_zaakdocument_bewerken.dms_client',
    ]

    @property
    def _dms_client(self):
        return self._extra_mocked_dms_clients[0]

    @property
    def _service_dms_client(self):
        return self._extra_mocked_dms_clients[1]


class STPgeefZaakdocumentbewerken_Di02Tests(DMSMockMixin, BaseTestPlatformTests, BaseSoapTests):
    """
    Precondities:
    Scenario's voegZaakdocumentToe (P) en maakZaakdocument (P) zijn succesvol uitgevoerd.
    Dit scenario wil documenten bewerken die in scenario's voegZaakdocumentToe (P) en
    maakZaakdocument (P) zijn toegevoegd.
    """
    test_files_subfolder = 'stp_geefZaakdocumentbewerken'
    porttype = 'VerwerkSynchroonVrijBericht'
    antwoord_xpath = '/soap11env:Envelope/soap11env:Body/zds:geefZaakdocumentBewerken_EdcLa01'

    def setUp(self):
        super().setUp()
        self._dms_client.geef_inhoud.return_value = ('doc 1', BytesIO())
        self._service_dms_client.checkout.return_value = ('pwc-checkout-id', 'J. Unkrat')

        self.zaak = ZaakFactory.create(status_set__indicatie_laatst_gezette_status=JaNee.ja)

        self.edc1 = EnkelvoudigInformatieObjectFactory.create(
            titel='doc 1',
            informatieobjectidentificatie='123456789'
        )
        self.edc2 = EnkelvoudigInformatieObjectFactory.create(
            titel='doc 2',
            informatieobjectidentificatie='987654321'
        )

        self.zaakdocument = ZaakInformatieObjectFactory.create(zaak=self.zaak, informatieobject=self.edc1)
        self.zaakdocument2 = ZaakInformatieObjectFactory.create(zaak=self.zaak, informatieobject=self.edc2)

    def _test_response(self, response):
        self.assertEquals(response.status_code, 200, response.content)

        response_root = etree.fromstring(response.content)
        response_berichtcode = response_root.xpath(
            '//zds:stuurgegevens/stuf:berichtcode', namespaces=self.nsmap
        )[0].text
        self.assertEqual(response_berichtcode, BerichtcodeChoices.du02, response.content)

        response_object_element = response_root.xpath('//zds:edcLa01/zkn:antwoord/zkn:object', namespaces=self.nsmap)[0]
        response_edc_identificatie = response_object_element.xpath('zkn:identificatie', namespaces=self.nsmap)[0].text

        self.assertEqual(response_edc_identificatie, self.edc1.informatieobjectidentificatie)

        self._assert_xpath_results(
            response_root, '//zds:edcLa01/zkn:antwoord/zkn:object',
            1, namespaces=self.nsmap
        )
        self._assert_xpath_results(
            response_root, '//zds:parameters/zds:checkedOutId',
            1, namespaces=self.nsmap
        )

        checked_out_id = response_root.xpath('//zds:parameters/zds:checkedOutId', namespaces=self.nsmap)[0].text
        self.assertEqual(checked_out_id, 'pwc-checkout-id')

        checked_out_by = response_root.xpath('//zds:parameters/zds:checkedOutBy', namespaces=self.nsmap)[0].text
        self.assertEqual(checked_out_by, 'J. Unkrat')

    def test_geefZaakdocumentbewerken_Di02_01(self):
        vraag = 'geefZaakdocumentBewerken_Di02_01.xml'
        context = {
            'referentienummer': self.genereerID(10),
            'datumVandaag': self.genereerdatum(),
            'voegzaakdocumenttoe_identificatie_5': self.edc1.informatieobjectidentificatie,
            'zenderGebruiker': 'FIXME',
        }
        response = self._do_request(self.porttype, vraag, context)

        self._test_response(response)
        self._service_dms_client.checkout.assert_called_once_with(to_proxy_obj(self.edc1))

    def test_geefZaakdocumentbewerken_Di02_03(self):
        vraag = 'geefZaakdocumentBewerken_Di02_03.xml'
        context = {
            'referentienummer': self.genereerID(10),
            'datumVandaag': self.genereerdatum(),
            'voegzaakdocumenttoe_identificatie_7': self.edc1.informatieobjectidentificatie,
            'zenderGebruiker': 'FIXME',
        }
        response = self._do_request(self.porttype, vraag, context)

        self._test_response(response)
        self._service_dms_client.checkout.assert_called_once_with(to_proxy_obj(self.edc1))

    def test_geefZaakdocumentbewerken_Di02_05(self):
        vraag = 'geefZaakdocumentBewerken_Di02_05.xml'
        context = {
            'referentienummer': self.genereerID(10),
            'datumVandaag': self.genereerdatum(),
            'maakzaakdocument_identificatie_5': self.edc1.informatieobjectidentificatie,
        }
        response = self._do_request(self.porttype, vraag, context)

        self._test_response(response)
        self._service_dms_client.checkout.assert_called_once_with(to_proxy_obj(self.edc1))

    def test_geefZaakdocumentbewerken_Di02_07(self):
        vraag = 'geefZaakdocumentBewerken_Di02_07.xml'
        context = {
            'referentienummer': self.genereerID(10),
            'datumVandaag': self.genereerdatum(),
            'maakzaakdocument_identificatie_1': self.edc1.informatieobjectidentificatie,
        }
        response = self._do_request(self.porttype, vraag, context)

        self._test_response(response)
        self._service_dms_client.checkout.assert_called_once_with(to_proxy_obj(self.edc1))

class GeefZaakdocumentbewerken_AuditlogTests(DMSMockMixin, BaseTestPlatformTests, BaseSoapTests):
    """
    Precondities:
    Scenario's voegZaakdocumentToe (P) en maakZaakdocument (P) zijn succesvol uitgevoerd.
    Dit scenario wil documenten bewerken die in scenario's voegZaakdocumentToe (P) en
    maakZaakdocument (P) zijn toegevoegd.
    """
    test_files_subfolder = 'stp_geefZaakdocumentbewerken'
    porttype = 'VerwerkSynchroonVrijBericht'
    antwoord_xpath = '/soap11env:Envelope/soap11env:Body/zds:geefZaakdocumentBewerken_EdcLa01'

    def setUp(self):
        super().setUp()
        self._dms_client.geef_inhoud.return_value = ('doc 1', BytesIO())
        self._service_dms_client.checkout.return_value = ('pwc-checkout-id', 'J. Unkrat')

        self.zaak = ZaakFactory.create(status_set__indicatie_laatst_gezette_status=JaNee.ja)

        self.edc1 = EnkelvoudigInformatieObjectFactory.create(
            titel='doc 1',
            informatieobjectidentificatie='123456789'
        )
        self.edc2 = EnkelvoudigInformatieObjectFactory.create(
            titel='doc 2',
            informatieobjectidentificatie='987654321'
        )

        self.zaakdocument = ZaakInformatieObjectFactory.create(zaak=self.zaak, informatieobject=self.edc1)
        self.zaakdocument2 = ZaakInformatieObjectFactory.create(zaak=self.zaak, informatieobject=self.edc2)

    def _test_response(self, response):
        self.assertEquals(response.status_code, 200, response.content)

        response_root = etree.fromstring(response.content)
        response_berichtcode = response_root.xpath(
            '//zds:stuurgegevens/stuf:berichtcode', namespaces=self.nsmap
        )[0].text
        self.assertEqual(response_berichtcode, BerichtcodeChoices.du02, response.content)

        response_object_element = response_root.xpath('//zds:edcLa01/zkn:antwoord/zkn:object', namespaces=self.nsmap)[0]
        response_edc_identificatie = response_object_element.xpath('zkn:identificatie', namespaces=self.nsmap)[0].text

        self.assertEqual(response_edc_identificatie, self.edc1.informatieobjectidentificatie)

        self._assert_xpath_results(
            response_root, '//zds:edcLa01/zkn:antwoord/zkn:object',
            1, namespaces=self.nsmap
        )
        self._assert_xpath_results(
            response_root, '//zds:parameters/zds:checkedOutId',
            1, namespaces=self.nsmap
        )

        checked_out_id = response_root.xpath('//zds:parameters/zds:checkedOutId', namespaces=self.nsmap)[0].text
        self.assertEqual(checked_out_id, 'pwc-checkout-id')

        checked_out_by = response_root.xpath('//zds:parameters/zds:checkedOutBy', namespaces=self.nsmap)[0].text
        self.assertEqual(checked_out_by, 'J. Unkrat')

    def test_geefZaakdocumentbewerken_Di02_01(self):
        vraag = 'geefZaakdocumentBewerken_Di02_01.xml'
        context = {
            'referentienummer': self.genereerID(10),
            'datumVandaag': self.genereerdatum(),
            'voegzaakdocumenttoe_identificatie_5': self.edc1.informatieobjectidentificatie,
            'zenderGebruiker': 'FIXME',
        }
        count = LogEntry.objects.count()

        response = self._do_request(self.porttype, vraag, context)

        self._test_response(response)
        self.assertEqual(LogEntry.objects.count(), count + 1)

        log_entry = LogEntry.objects.latest()
        self.assertEqual(log_entry.action, LogEntry.Action.READ)
        self.assertEqual(log_entry.content_type.model, 'enkelvoudiginformatieobject')
        self.assertEqual(log_entry.additional_data['functie'], 'geefZaakdocumentBewerken_Di02')
