from lxml import etree
from zeep.xsd.const import Nil

from zaakmagazijn.api.stuf.choices import BerichtcodeChoices
from zaakmagazijn.rgbz.choices import JaNee

from ...rgbz.tests.factory_models import (
    ZaakFactory, ZaakInformatieObjectFactory
)
from .base import BaseSoapTests, BaseTestPlatformTests


class geefLijstZaakdocumenten_ZakLv01Tests(BaseSoapTests):
    def test_gelijk(self):
        zio = ZaakInformatieObjectFactory.create(zaak__status_set__indicatie_laatst_gezette_status=JaNee.ja)
        ZaakInformatieObjectFactory.create(zaak__status_set__indicatie_laatst_gezette_status=JaNee.ja)

        client = self._get_client('Beantwoordvraag')
        stuf_factory, zkn_factory, zds_factory = self._get_type_factories(client)

        response = client.service.geefLijstZaakdocumenten_ZakLv01(
            stuurgegevens=stuf_factory.ZAK_StuurgegevensGeefLijstZaakdocumentenLv01(
                berichtcode='Lv01',
                entiteittype='ZAK',
            ),
            parameters=stuf_factory.ZAK_parametersVraagSynchroon(
                sortering=1,
                indicatorVervolgvraag=False
            ),
            scope=zkn_factory.GeefLijstZaakdocumenten_vraagScope(
                object=zkn_factory.GeefLijstZaakdocumenten_ZAK_vraagScope(
                    entiteittype='ZAK',
                    identificatie=Nil,
                    heeftRelevant=zkn_factory.GeefLijstZaakdocumenten_ZAKEDC_vraagScope(**{
                        'entiteittype': 'EDC',
                        'titel': Nil,
                        'beschrijving': Nil,
                        'gerelateerde': zkn_factory.GeefLijstZaakdocumenten_EDC_vraagScope(**{
                            'identificatie': Nil,
                            'creatiedatum': Nil,
                            'titel': Nil,
                            'link': Nil,
                        }),
                    })
                )
            ),
            gelijk=zkn_factory.GeefLijstZaakdocumenten_ZAK_vraagSelectie(
                identificatie=zio.zaak.zaakidentificatie,
            )
        )
        self.assertEquals(len(response.antwoord.object), 1)
        self.assertEquals(len(response.antwoord.object[0].heeftRelevant), 1)

    # TODO: test_scope


class geefLijstZaakdocumenten_ZakLa01Tests(BaseSoapTests):
    antwoord_xpath = '/soap11env:Envelope/soap11env:Body/zds:geefLijstZaakdocumenten_ZakLa01'

    def setUp(self):
        super().setUp()

        self.zio = ZaakInformatieObjectFactory.create(zaak__status_set__indicatie_laatst_gezette_status=JaNee.ja)
        self.zaak = self.zio.zaak

    def _do_simple_request(self, raw_response=False):
        """
        Do a simple SOAP request.
        """
        client = self._get_client('Beantwoordvraag')
        stuf_factory, zkn_factory, zds_factory = self._get_type_factories(client)

        with client.options(raw_response=raw_response):
            return client.service.geefLijstZaakdocumenten_ZakLv01(
                stuurgegevens=stuf_factory.ZAK_StuurgegevensGeefLijstZaakdocumentenLv01(
                    berichtcode='Lv01',
                    entiteittype='ZAK',
                ),
                parameters=stuf_factory.ZAK_parametersVraagSynchroon(
                    sortering=1,
                    indicatorVervolgvraag=False
                ),
                scope=zkn_factory.GeefLijstZaakdocumenten_vraagScope(
                    object=zkn_factory.GeefLijstZaakdocumenten_ZAK_vraagScope(
                        entiteittype='ZAK',
                        identificatie=Nil,
                        heeftRelevant=zkn_factory.GeefLijstZaakdocumenten_ZAKEDC_vraagScope(**{
                            'entiteittype': 'ZAKEDC',
                            'titel': Nil,
                            'beschrijving': Nil,
                            'gerelateerde': zkn_factory.GeefLijstZaakdocumenten_EDC_vraagScope(**{
                                'identificatie': Nil,
                                'creatiedatum': Nil,
                                'titel': Nil,
                                'link': Nil,
                            }),
                        }
                        )
                    )
                ),
                gelijk=zkn_factory.GeefLijstZaakdocumenten_ZAK_vraagSelectie(
                    identificatie=self.zio.zaak.zaakidentificatie,
                )
            )

    def test_namespace_response(self):
        """
        Verify that the namespace of the response is as expected.
        """
        result = self._do_simple_request(raw_response=True)
        root = etree.fromstring(result.content)
        self.assertEquals(
            set(root.nsmap.values()),
            {
                'http://www.egem.nl/StUF/sector/zkn/0310',
                'http://www.egem.nl/StUF/StUF0301',
                'http://www.stufstandaarden.nl/koppelvlak/zds0120',
                'http://schemas.xmlsoap.org/soap/envelope/',
                'http://www.w3.org/2001/XMLSchema-instance'
            }
        )

    def test_root_element(self):
        """
        Test that the root element in soapenv:Body is called geefLijstZaakdocumenten_ZakLa01
        and has the namespace 'http://www.stufstandaarden.nl/koppelvlak/zds0120'
        """
        result = self._do_simple_request(raw_response=True)
        root = etree.fromstring(result.content)
        self._assert_xpath_results(root, self.antwoord_xpath, 1, namespaces=self.nsmap)

    def test_stuurgegevens_element(self):
        """
        Test that in the geefLijstZaakdocumenten_ZakLa01 element there is an element
        called stuurgegevens which has the namespace 'http://www.egem.nl/StUF/sector/zkn/0310'
        """
        result = self._do_simple_request(raw_response=True)
        root = etree.fromstring(result.content)
        self._assert_xpath_results(self._get_body_root(root), 'zkn:stuurgegevens', 1, namespaces=self.nsmap)
        self._assert_xpath_results(
            self._get_body_root(root), 'zkn:stuurgegevens/stuf:berichtcode[text()="La01"]',
            1, namespaces=self.nsmap
        )
        self._assert_xpath_results(
            self._get_body_root(root), 'zkn:stuurgegevens/stuf:entiteittype[text()="ZAK"]',
            1, namespaces=self.nsmap
        )

    def test_antwoord_element(self):
        """
        Test that in the geefLijstZaakdocumenten_ZakLa01 element there is an element
        called antwoord which has the namespace 'http://www.egem.nl/StUF/sector/zkn/0310'
        """
        result = self._do_simple_request(raw_response=True)
        root = etree.fromstring(result.content)
        self._assert_xpath_results(self._get_body_root(root), 'zkn:antwoord', 1, namespaces=self.nsmap)

    def test_object_element(self):
        """
        Test that in the antwoord element there is an element
        called object which has the namespace 'http://www.egem.nl/StUF/sector/zkn/0310'
        """
        result = self._do_simple_request(raw_response=True)
        root = etree.fromstring(result.content)
        self._assert_xpath_results(self._get_body_root(root), 'zkn:antwoord/zkn:object', 1, namespaces=self.nsmap)

    def test_entiteittype_attribute(self):
        """
        Test that the object element has an attribute entiteittype and has the
        namespace 'http://www.egem.nl/StUF/StUF0301'
        """
        result = self._do_simple_request(raw_response=True)
        root = etree.fromstring(result.content)
        self._assert_xpath_results(
            self._get_body_root(root), 'zkn:antwoord/zkn:object[@stuf:entiteittype]',
            1, namespaces=self.nsmap
        )


class MaykingeefLijstZaakdocumenten_ZakLv01Tests(BaseTestPlatformTests):
    porttype = 'Beantwoordvraag'
    maxDiff = None
    test_files_subfolder = 'maykin_geefLijstZaakdocumenten'

    def test_taiga_issue_282(self):
        """
        Regression test from Taiga issue #282

        When no results  are returned because the scope does not match, return an empty list,
        instead of return 'EmptyResultError', which isn't very friendly.
        """
        zaak = ZaakFactory.create(zaakidentificatie='WLO-9192')
        vraag = 'geefLijstZaakdocumenten_ZakLv01_taiga282.xml'
        response = self._do_request(self.porttype, vraag, {})
        response_root = etree.fromstring(response.content)

        response_berichtcode = response_root.xpath(
            '//zkn:stuurgegevens/stuf:berichtcode',
            namespaces=self.nsmap
        )[0].text
        self.assertEqual(response_berichtcode, BerichtcodeChoices.la01, response.content)

        objects = response_root.xpath('//zkn:antwoord/child::*', namespaces=self.nsmap)
        self.assertEquals(len(objects), 0)


class STPgeefLijstZaakdocumenten_ZakLv01Tests(BaseTestPlatformTests):
    porttype = 'Beantwoordvraag'
    maxDiff = None
    test_files_subfolder = 'stp_geefLijstZaakdocumenten'

    def setUp(self):
        super().setUp()

        self.zio_1 = ZaakInformatieObjectFactory.create(zaak__status_set__indicatie_laatst_gezette_status=JaNee.ja)
        self.zaak = self.zio_1.zaak
        self.zio_2 = ZaakInformatieObjectFactory.create(zaak=self.zaak)

        zio_3 = ZaakInformatieObjectFactory.create(zaak__status_set__indicatie_laatst_gezette_status=JaNee.ja)

    def _test_response(self, response):
        self.assertEquals(response.status_code, 200, response.content)

        response_root = etree.fromstring(response.content)
        response_berichtcode = response_root.xpath(
            '//zkn:stuurgegevens/stuf:berichtcode',
            namespaces=self.nsmap
        )[0].text

        self.assertEqual(response_berichtcode, BerichtcodeChoices.la01, response.content)

        response_object_element = response_root.xpath('//zkn:antwoord/zkn:object', namespaces=self.nsmap)[0]
        response_zaak_identificatie = response_object_element.xpath('zkn:identificatie', namespaces=self.nsmap)[0].text

        self.assertEqual(response_zaak_identificatie, self.zaak.zaakidentificatie)

        response_relevant_elementen = response_object_element.xpath('zkn:heeftRelevant', namespaces=self.nsmap)
        self.assertEqual(len(response_relevant_elementen), 2)

        response_edc_identificaties = [
            el.xpath('zkn:gerelateerde/zkn:identificatie', namespaces=self.nsmap)[0].text
            for el in response_relevant_elementen
        ]
        self.assertSetEqual(
            set(response_edc_identificaties),
            {
                self.zio_1.informatieobject.informatieobjectidentificatie,
                self.zio_2.informatieobject.informatieobjectidentificatie
            }
        )

    def test_geefLijstZaakdocumenten_ZakLv01_01(self):
        """
        1. Verzoek geefLijstZaakdocumenten_ZakLv01_01: STP -> ZS
        2. Antwoord geefLijstZaakdocumenten_ZakLa01_02: ZS -> STP

        note: scope="alles"
        """
        vraag = 'geefLijstZaakdocumenten_ZakLv01_01.xml'
        context = {
            'zaakidentificatie': self.zaak.zaakidentificatie,
        }
        response = self._do_request(self.porttype, vraag, context)

        self._test_response(response)

        response_root = etree.fromstring(response.content)
        response_object_element = response_root.xpath('//zkn:antwoord/zkn:object', namespaces=self.nsmap)[0]
        response_relevant_elementen = response_object_element.xpath('zkn:heeftRelevant', namespaces=self.nsmap)
        response_edc_omschrijving = [
            el.xpath('zkn:gerelateerde/zkn:dct.omschrijving', namespaces=self.nsmap)[0].text
            for el in response_relevant_elementen
        ]
        self.assertSetEqual(
            set(response_edc_omschrijving),
            {
                self.zio_1.informatieobject.informatieobjecttype.informatieobjecttypeomschrijving,
                self.zio_2.informatieobject.informatieobjecttype.informatieobjecttypeomschrijving
            }
        )

    def test_geefLijstZaakdocumenten_ZakLv01_03(self):
        """
        3. Verzoek geefLijstZaakdocumenten_ZakLv01_03: STP -> ZS
        4. Antwoord geefLijstZaakdocumenten_ZakLa01_04: ZS -> STP

        note: scope="allesZonderMetagegevensMaarKerngegevensGerelateerden"
        """
        vraag = 'geefLijstZaakdocumenten_ZakLv01_03.xml'
        context = {
            'zaakidentificatie': self.zaak.zaakidentificatie,
        }
        response = self._do_request(self.porttype, vraag, context)

        self._test_response(response)

    def test_geefLijstZaakdocumenten_ZakLv01_05(self):
        """
        5. Verzoek geefLijstZaakdocumenten_ZakLv01_05: STP -> ZS
        6. Antwoord geefLijstZaakdocumenten_ZakLa01_06: ZS -> STP
        """
        vraag = 'geefLijstZaakdocumenten_ZakLv01_05.xml'
        context = {
            'zaakidentificatie': self.zaak.zaakidentificatie,
        }
        response = self._do_request(self.porttype, vraag, context)

        self._test_response(response)

    def test_geefLijstZaakdocumenten_ZakLv01_07(self):
        """
        7. Verzoek geefLijstZaakdocumenten_ZakLv01_07: STP -> ZS
        8. Antwoord geefLijstZaakdocumenten_ZakLa01_08: ZS -> STP
        """
        vraag = 'geefLijstZaakdocumenten_ZakLv01_07.xml'
        context = {
            'zaakidentificatie': self.zaak.zaakidentificatie,
        }
        response = self._do_request(self.porttype, vraag, context)

        self._test_response(response)

    def test_geefLijstZaakdocumenten_ZakLv01_09(self):
        """
        9. Verzoek geefLijstZaakdocumenten_ZakLv01_09: STP -> ZS
        10. Antwoord geefLijstZaakdocumenten_ZakLa01_10: ZS -> STP
        """
        vraag = 'geefLijstZaakdocumenten_ZakLv01_09.xml'
        context = {
            'zaakidentificatie': self.zaak.zaakidentificatie,
        }
        response = self._do_request(self.porttype, vraag, context)

        self._test_response(response)
