from lxml import etree

from zaakmagazijn.rgbz.choices import JaNee

from ...rgbz.tests.factory_models import (
    MedewerkerFactory, OrganisatorischeEenheidFactory, StatusTypeFactory,
    ZaakFactory
)
from ..stuf.choices import BerichtcodeChoices
from ..tests.base import BaseTestPlatformTests


class STPactualiseerZaakstatus_ZakLk01Tests(BaseTestPlatformTests):
    test_files_subfolder = 'stp_actualiseerZaakstatus'
    porttype = 'OntvangAsynchroon'

    def setUp(self):
        super().setUp()
        self.zaak = ZaakFactory.create()
        self.status_type = StatusTypeFactory.create(statustypeomschrijving='Intake afgerond')

        self.context = {
            'gemeentecode': '',
            'referentienummer': self.genereerID(10),

            'zds_zaaktype_code': '12345678',
            'zds_zaaktype_omschrijving': 'Aanvraag burgerservicenummer behandelen',

            'datumVandaag': self.genereerdatum(),
            'datumEergisteren': self.genereerdatum(),
            'tijdstipRegistratie': self.genereerdatumtijd(),
        }

    def _test_response(self, response):
        self.assertEquals(response.status_code, 200, response.content)

        response_root = etree.fromstring(response.content)
        response_berichtcode = response_root.xpath('//stuf:stuurgegevens/stuf:berichtcode', namespaces=self.nsmap)[0].text
        self.assertEqual(response_berichtcode, BerichtcodeChoices.bv03, response.content)

        status = self.zaak.status_set.filter(status_type__statustypeomschrijving=self.status_type.statustypeomschrijving).first()
        self.assertEqual(status.indicatie_laatst_gezette_status, JaNee.ja)

    def test_actualiseerZaakstatus_ZakLk01_01(self):
        vraag = 'actualiseerZaakstatus_ZakLk01_01.xml'

        oeh = OrganisatorischeEenheidFactory.create(
            organisatieidentificatie=11111,
            organisatieeenheididentificatie=33333,
        )
        self.context.update({
            'organisatorischeEenheidIdentificatie': oeh.identificatie,
            'genereerzaakident_identificatie_2': self.zaak.zaakidentificatie,
            'zds_zaakstatus_code': '87654321',
            'zds_zaakstatus_omschrijving': 'Intake afgerond',
        })
        response = self._do_request(self.porttype, vraag, self.context)

        self._test_response(response)

        status = self.zaak.status_set.filter(status_type__statustypeomschrijving=self.status_type.statustypeomschrijving).first()
        self.assertEqual(status.rol.betrokkene, oeh.betrokkene_ptr)

    def test_actualiseerZaakstatus_ZakLk01_03(self):
        vraag = 'actualiseerZaakstatus_ZakLk01_03.xml'

        medewerker = MedewerkerFactory.create(
            organisatorische_eenheid__organisatieeenheididentificatie=1111,
            medewerkeridentificatie=2222,
        )
        self.context.update({
            'medewerkerIdentificatie': medewerker.identificatie,
            'genereerzaakident_identificatie_4': self.zaak.zaakidentificatie,
            'zds_zaakstatus_code_2': '87654321',
            'zds_zaakstatus_omschrijving_2': 'Intake afgerond',
        })
        response = self._do_request(self.porttype, vraag, self.context)

        self._test_response(response)

        status = self.zaak.status_set.filter(status_type__statustypeomschrijving=self.status_type.statustypeomschrijving).first()
        self.assertEqual(status.rol.betrokkene, medewerker.betrokkene_ptr)

    def test_actualiseerZaakstatus_ZakLk01_05(self):
        vraag = 'actualiseerZaakstatus_ZakLk01_05.xml'

        oeh = OrganisatorischeEenheidFactory.create(
            organisatieidentificatie=11111,
            organisatieeenheididentificatie=33333,
        )

        self.context.update({
            'organisatorischeEenheidIdentificatie': oeh.identificatie,
            'genereerzaakident_identificatie_6': self.zaak.zaakidentificatie,
            'zds_zaakstatus_code_3': '87654321',
            'zds_zaakstatus_omschrijving_3': 'Intake afgerond',
        })
        response = self._do_request(self.porttype, vraag, self.context)

        self._test_response(response)

        status = self.zaak.status_set.filter(status_type__statustypeomschrijving=self.status_type.statustypeomschrijving).first()
        self.assertEqual(status.rol.betrokkene, oeh.betrokkene_ptr)

    def test_actualiseerZaakstatus_ZakLk01_07(self):
        vraag = 'actualiseerZaakstatus_ZakLk01_07.xml'

        medewerker = MedewerkerFactory.create(
            organisatorische_eenheid__organisatieeenheididentificatie=1111,
            medewerkeridentificatie=2222,
        )
        self.context.update({
            'medewerkerIdentificatie': medewerker.identificatie,
            'genereerzaakident_identificatie_6': self.zaak.zaakidentificatie,
            'zds_zaakstatus_code_4': '87654321',
            'zds_zaakstatus_omschrijving_4': 'Intake afgerond',
        })
        response = self._do_request(self.porttype, vraag, self.context)

        self._test_response(response)

        status = self.zaak.status_set.filter(status_type__statustypeomschrijving=self.status_type.statustypeomschrijving).first()
        self.assertEqual(status.rol.betrokkene, medewerker.betrokkene_ptr)
