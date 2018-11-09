from io import BytesIO

from lxml import etree

from zaakmagazijn.api.stuf.choices import BerichtcodeChoices
from zaakmagazijn.api.tests.base import BaseTestPlatformTests
from zaakmagazijn.rgbz.choices import JaNee
from zaakmagazijn.rgbz.tests.factory_models import (
    EnkelvoudigInformatieObjectFactory, InformatieObjectTypeFactory,
    ZaakFactory, ZaakInformatieObjectFactory
)


class DMSMockMixin:
    extra_client_mocks = [
        'zaakmagazijn.cmis.fields.dms_client',
        'zaakmagazijn.api.services.update_zaakdocument.dms_client',
    ]

    @property
    def _dms_client(self):
        return self._extra_mocked_dms_clients[0]

    @property
    def _service_dms_client(self):
        return self._extra_mocked_dms_clients[1]


class STPupdateZaakdocument_DI02Tests(DMSMockMixin, BaseTestPlatformTests):
    """
    Precondities:
    Scenario's voegZaakdocumentToe (P) en  maakZaakdocument (P) zijn succesvol uitgevoerd.
    Dit scenario wijzigt documenten die in scenario's voegZaakdocumentToe (P) en maakZaakdocument (P) zijn toegevoegd.
    """
    test_files_subfolder = 'stp_updateZaakdocument'
    porttype = 'VerwerkSynchroonVrijBericht'

    def setUp(self):
        super().setUp()

        vandaag = self.genereerdatum()
        self.context = {
            'gemeentecode': '1234',
            'datumVandaag': vandaag,
            'datumGisteren': self.genereerdatum(-1),
            'datumEergisteren': self.genereerdatum(-2),
            'tijdstipRegistratie': self.genereerdatumtijd(),

            'zds_zaaktype_code': '12345678',
            'zds_zaaktype_omschrijving': 'Aanvraag burgerservicenummer behandelen',
            'referentienummer': self.genereerID(10),
            'creerzaak_identificatie_9': self.genereerID(10),
            'voegzaakdocumenttoe_identificatie_5': self.genereerID(10),
            'voegzaakdocumenttoe_identificatie_7': self.genereerID(10),
            'maakzaakdocument_identificatie_5': self.genereerID(10),
        }

        self._dms_client.geef_inhoud.return_value = 'dummy.txt', BytesIO()

        self.zaak = ZaakFactory.create(
            zaakidentificatie=self.context['gemeentecode'] + self.context['creerzaak_identificatie_9'],
            status_set__indicatie_laatst_gezette_status=JaNee.ja,
            omschrijving='omschrijving'
        )
        self.edc_type2 = InformatieObjectTypeFactory.create(informatieobjecttypeomschrijving='omschrijving1')
        self.zaakdocument = EnkelvoudigInformatieObjectFactory.create(
            informatieobjecttype__informatieobjecttypeomschrijving='omschrijving',
            informatieobjectidentificatie=self.context['voegzaakdocumenttoe_identificatie_5'],
            formaat='formaat',
            creatiedatum=vandaag,
            titel='titel',
            taal='taal',
            vertrouwelijkaanduiding='VERTROUWELIJK',
            auteur='auteur',
            link=None
        )
        ZaakInformatieObjectFactory.create(zaak=self.zaak, informatieobject=self.zaakdocument)

        self.zaakdocument2 = EnkelvoudigInformatieObjectFactory.create(
            informatieobjectidentificatie=self.context['voegzaakdocumenttoe_identificatie_7'],
            vertrouwelijkaanduiding='VERTROUWELIJK',
            auteur='auteur',
        )
        ZaakInformatieObjectFactory.create(zaak=self.zaak, informatieobject=self.zaakdocument2)

        self.zaakdocument3 = EnkelvoudigInformatieObjectFactory.create(
            informatieobjectidentificatie=self.context['maakzaakdocument_identificatie_5'],
            vertrouwelijkaanduiding='VERTROUWELIJK',
            auteur='auteur',
        )
        ZaakInformatieObjectFactory.create(zaak=self.zaak, informatieobject=self.zaakdocument3)

    def _test_response(self, response):
        self.assertEquals(response.status_code, 200, response.content)

        response_root = etree.fromstring(response.content)
        response_berichtcode = response_root.xpath(
            '//stuf:stuurgegevens/stuf:berichtcode', namespaces=self.nsmap
        )[0].text
        self.assertEqual(response_berichtcode, BerichtcodeChoices.bv02, response.content)

    def test_updateZaakdocument_Di02_01(self):
        vraag = 'updateZaakdocument_Di02_01.orig.xml'
        context = self.context.copy()
        response = self._do_request(self.porttype, vraag, context, stp_syntax=True)
        self._test_response(response)

        self.zaakdocument.refresh_from_db()
        self.assertEqual(self.zaakdocument.titel, 'titel1')
        self.assertEqual(self.zaakdocument.beschrijving, 'beschrijving1')
        self.assertEqual(self.zaakdocument.formaat, 'formaat1')
        self.assertEqual(self.zaakdocument.versie, 'vers1')
        self.assertEqual(self.zaakdocument.informatieobject_status, 'status1')
        self.assertEqual(self.zaakdocument.taal, 'taal1')
        # link is not part of the ZDS 1.2 spec.
        # self.assertEqual(document.link, 'link1')

        # inhoud is specified
        self.assertEqual(self._service_dms_client.update_zaakdocument.call_count, 1)
        call_args = self._service_dms_client.update_zaakdocument.call_args
        self.assertEqual(call_args[0][0], self.zaakdocument)
        self.assertEqual(call_args[0][1], self.context['voegzaakdocumenttoe_identificatie_5'])
        self.assertEqual(call_args[0][2].bestandsnaam, 'bestandsnaam')

    def test_updateZaakdocument_Di02_03(self):
        vraag = 'updateZaakdocument_Di02_03.orig.xml'
        context = self.context.copy()
        response = self._do_request(self.porttype, vraag, context, stp_syntax=True)
        self._test_response(response)

        # no inhoud present
        self._service_dms_client.update_zaakdocument.assert_called_once_with(self.zaakdocument2, self.context['voegzaakdocumenttoe_identificatie_7'], None)

    def test_updateZaakdocument_Di02_05(self):
        vraag = 'updateZaakdocument_Di02_05.orig.xml'
        context = self.context.copy()
        response = self._do_request(self.porttype, vraag, context, stp_syntax=True)
        self._test_response(response)

        # no inhoud present
        self._service_dms_client.update_zaakdocument.assert_called_once_with(self.zaakdocument3, self.context['maakzaakdocument_identificatie_5'], None)
