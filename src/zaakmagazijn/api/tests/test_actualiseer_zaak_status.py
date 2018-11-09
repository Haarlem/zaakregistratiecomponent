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

        self.status_type_1 = StatusTypeFactory.create(
            statustypeomschrijving='Intake afgerond', statustypevolgnummer=1, zaaktype=self.zaak.zaaktype)
        self.status_type_3 = StatusTypeFactory.create(
            statustypeomschrijving='Toegekend', statustypevolgnummer=3, zaaktype=self.zaak.zaaktype)
        self.status_type_5 = StatusTypeFactory.create(
            statustypeomschrijving='Opgepakt', statustypevolgnummer=5, zaaktype=self.zaak.zaaktype)
        self.status_type_7 = StatusTypeFactory.create(
            statustypeomschrijving='Voltooid', statustypevolgnummer=7, zaaktype=self.zaak.zaaktype)

        self.context = {
            'gemeentecode': '',
            'referentienummer': self.genereerID(10),

            'zds_zaaktype_code': '12345678',
            'zds_zaaktype_omschrijving': 'Aanvraag burgerservicenummer behandelen',

            'datumVandaag': self.genereerdatum(),
            'datumEergisteren': self.genereerdatum(),
            'tijdstipRegistratie': self.genereerdatumtijd(),
        }

    def _test_response(self, response, status_type):
        self.assertEquals(response.status_code, 200, response.content)

        response_root = etree.fromstring(response.content)
        response_berichtcode = response_root.xpath('//stuf:stuurgegevens/stuf:berichtcode', namespaces=self.nsmap)[0].text
        self.assertEqual(response_berichtcode, BerichtcodeChoices.bv03, response.content)

        status = self.zaak.status_set.filter(status_type__statustypeomschrijving=status_type.statustypeomschrijving).first()
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
            'zds_zaakstatus_omschrijving': self.status_type_1.statustypeomschrijving,
        })
        response = self._do_request(self.porttype, vraag, self.context)

        self._test_response(response, self.status_type_1)

        status = self.zaak.status_set.filter(status_type__statustypeomschrijving=self.status_type_1.statustypeomschrijving).first()
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
            'zds_zaakstatus_omschrijving_2': self.status_type_3.statustypeomschrijving,
        })
        response = self._do_request(self.porttype, vraag, self.context)

        self._test_response(response, self.status_type_3)

        status = self.zaak.status_set.filter(status_type__statustypeomschrijving=self.status_type_3.statustypeomschrijving).first()
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
            'zds_zaakstatus_omschrijving_3':  self.status_type_5.statustypeomschrijving,
        })
        response = self._do_request(self.porttype, vraag, self.context)

        self._test_response(response, self.status_type_5)

        status = self.zaak.status_set.filter(status_type__statustypeomschrijving=self.status_type_5.statustypeomschrijving).first()
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
            'zds_zaakstatus_omschrijving_4':  self.status_type_7.statustypeomschrijving,
        })
        response = self._do_request(self.porttype, vraag, self.context)

        self._test_response(response, self.status_type_7)

        status = self.zaak.status_set.filter(status_type__statustypeomschrijving=self.status_type_7.statustypeomschrijving).first()
        self.assertEqual(status.rol.betrokkene, medewerker.betrokkene_ptr)



class actualiseerZaakstatus_ZakLk01RegressionTests(BaseTestPlatformTests):
    test_files_subfolder = 'maykin_actualiseerZaakstatus'
    porttype = 'OntvangAsynchroon'

    def setUp(self):
        super().setUp()

        self.context = {
            'gemeentecode': '',
            'referentienummer': self.genereerID(10),

            'zds_zaaktype_code': '12345678',
            'zds_zaaktype_omschrijving': 'Aanvraag burgerservicenummer behandelen',

            'datumVandaag': self.genereerdatum(),
            'datumEergisteren': self.genereerdatum(),
            'tijdstipRegistratie': self.genereerdatumtijd(),
        }

    def test_incorrect_empty_statustoelichting_value_stored(self):
        """
        See: https://taiga.maykinmedia.nl/project/haarlem-zaakmagazijn/issue/404
        """
        zaak = ZaakFactory.create()
        status_type = StatusTypeFactory.create(statustypeomschrijving='Intake afgerond', statustypevolgnummer=3)
        medewerker = MedewerkerFactory.create(
            organisatorische_eenheid__organisatieeenheididentificatie=1111,
            medewerkeridentificatie=2222,
        )

        vraag = 'actualiseerZaakstatus_ZakLk01_taiga404.xml'

        self.context.update({
            'medewerkerIdentificatie': medewerker.identificatie,
            'genereerzaakident_identificatie_4': zaak.zaakidentificatie,
            'zds_zaakstatus_code_2': '87654321',
            'zds_zaakstatus_omschrijving_2': 'Intake afgerond',
        })

        response = self._do_request(self.porttype, vraag, self.context)
        self.assertEquals(response.status_code, 200, response.content)

        status = zaak.status_set.filter(status_type__statustypeomschrijving=status_type.statustypeomschrijving).first()
        self.assertIsNone(status.statustoelichting)

    def test_multiple_statustypes_without_zaaktype(self):
        """
        See: https://taiga.maykinmedia.nl/project/haarlem-zaakmagazijn/issue/414
        """
        zaak = ZaakFactory.create()
        status_type = StatusTypeFactory.create(
            statustypeomschrijving='Intake afgerond', statustypevolgnummer=1, zaaktype=zaak.zaaktype)
        StatusTypeFactory.create(statustypeomschrijving='Intake afgerond', statustypevolgnummer=1)
        medewerker = MedewerkerFactory.create(
            organisatorische_eenheid__organisatieeenheididentificatie=1111,
            medewerkeridentificatie=2222,
        )

        vraag = 'actualiseerZaakstatus_ZakLk01_taiga414-1.xml'

        self.context.update({
            'medewerkerIdentificatie': medewerker.identificatie,
            'genereerzaakident_identificatie_4': zaak.zaakidentificatie,
            'zds_zaakstatus_code_2': '87654321',
            'zds_zaakstatus_omschrijving_2': 'Intake afgerond',
        })

        response = self._do_request(self.porttype, vraag, self.context)
        self.assertEquals(response.status_code, 500, response.content)

        response_root = etree.fromstring(response.content)

        response_berichtcode = response_root.xpath('//stuf:stuurgegevens/stuf:berichtcode', namespaces=self.nsmap)[0].text
        self.assertEqual(response_berichtcode, BerichtcodeChoices.fo03, response.content)

        details = response_root.xpath('//stuf:body/stuf:details', namespaces=self.nsmap)[0].text
        self.assertEqual(details, "Statustype is niet uniek identificeerbaar", response.content)

    def test_multiple_statustypes_with_zaaktype(self):
        """
        See: https://taiga.maykinmedia.nl/project/haarlem-zaakmagazijn/issue/414
        """
        zaak = ZaakFactory.create(zaaktype__zaaktypeidentificatie=12345)
        status_type = StatusTypeFactory.create(
            statustypeomschrijving='Intake afgerond', statustypevolgnummer=1, zaaktype=zaak.zaaktype)
        StatusTypeFactory.create(statustypeomschrijving='Intake afgerond', statustypevolgnummer=1)
        medewerker = MedewerkerFactory.create(
            organisatorische_eenheid__organisatieeenheididentificatie=1111,
            medewerkeridentificatie=2222,
        )

        vraag = 'actualiseerZaakstatus_ZakLk01_taiga414-2.xml'

        self.context.update({
            'medewerkerIdentificatie': medewerker.identificatie,
            'genereerzaakident_identificatie_4': zaak.zaakidentificatie,
            'zds_zaakstatus_code_2': '87654321',
            'zds_zaakstatus_omschrijving_2': 'Intake afgerond',
        })

        response = self._do_request(self.porttype, vraag, self.context)
        self.assertEquals(response.status_code, 200, response.content)

        status = zaak.status_set.filter(status_type__statustypeomschrijving=status_type.statustypeomschrijving).first()
        self.assertIsNone(status.statustoelichting)