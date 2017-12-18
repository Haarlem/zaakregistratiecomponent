from lxml import etree
from zeep.xsd.const import Nil

from zaakmagazijn.api.stuf.choices import BerichtcodeChoices
from zaakmagazijn.api.tests.base import BaseSoapTests, BaseTestPlatformTests
from zaakmagazijn.rgbz.tests.factory_models import BesluitFactory

from ...rgbz.tests.factory_models import EnkelvoudigInformatieObjectFactory


class geefBesluitDetails_BslLv01Tests(BaseSoapTests):
    antwoord_xpath = '/soap11env:Envelope/soap11env:Body/zds:geefBesluitdetails_BslLa01/zkn:antwoord/zkn:object'

    def test_gelijk(self):
        besluit = BesluitFactory.create()
        # Should not show up, because the 'identificatie' field doesn't match.
        BesluitFactory.create()

        client = self._get_client('BeantwoordVraag')
        stuf_factory, zkn_factory, zds_factory = self._get_type_factories(client)

        response = client.service.geefBesluitdetails_BslLv01(
            stuurgegevens=stuf_factory['BSL-StuurgegevensLv01'](
                berichtcode='Lv01',
                entiteittype='BSL',
            ),
            parameters=stuf_factory['BSL-parametersVraagSynchroon'](
                sortering=1,
                indicatorVervolgvraag=False
            ),
            scope={
                'object': zkn_factory['geefBesluitDetails-BSL-vraagScope'](**{
                    'entiteittype': 'BSL',  # v
                    'identificatie': Nil,  # v
                    'datumBeslissing': Nil,  # v
                    'ingangsdatumWerking': Nil,  # v
                    'bst.omschrijving': Nil,
                }),
            },
            gelijk=zkn_factory['geefBesluitDetails-BSL-vraagSelectie'](
                entiteittype='BSL',  # v
                identificatie=besluit.identificatie,  # v
            )
        )
        self.assertEqual(len(response.antwoord), 1)
        self.assertEqual(
            response.antwoord.object.identificatie._value_1,
            besluit.besluitidentificatie
        )
        self.assertEquals(getattr(response.antwoord.object, 'bst.omschrijving')._value_1, besluit.besluittype.besluittypeomschrijving)

    def test_scope(self):
        informatieobject1 = EnkelvoudigInformatieObjectFactory.create()
        besluit = BesluitFactory.create(informatieobject=(informatieobject1,))

        client = self._get_client('BeantwoordVraag')
        stuf_factory, zkn_factory, zds_factory = self._get_type_factories(client)

        with client.options(raw_response=True):
            response = client.service.geefBesluitdetails_BslLv01(
                stuurgegevens=stuf_factory['BSL-StuurgegevensLv01'](
                    berichtcode='Lv01',
                    entiteittype='BSL',
                ),
                parameters=stuf_factory['BSL-parametersVraagSynchroon'](
                    sortering=1,
                    indicatorVervolgvraag='false'
                ),
                scope={
                    'object': zkn_factory['geefBesluitDetails-BSL-vraagScope'](**{
                        'entiteittype': 'BSL',  # v
                        'identificatie': Nil,  # v
                        'datumBeslissing': Nil,  # v
                        'ingangsdatumWerking': Nil,  # v
                        'bst.reactietermijn': Nil,
                        'isUitkomstVan': {
                            'entiteittype': 'BSLZAK',  # v
                            'gerelateerde': zkn_factory['geefBesluitDetails-ZAK-gerelateerdeVraagScope'](**{
                                'entiteittype': 'ZAK',  # v
                                'identificatie': Nil,
                            }),
                        },
                    })
                },
                gelijk=zkn_factory['geefBesluitDetails-BSL-vraagSelectie'](
                    entiteittype='BSL',  # v
                    identificatie=besluit.identificatie,  # v
                )
            )

        root = etree.fromstring(response.content)

        # The expectation is that only the selected fields are returned.
        antwoord_obj = self._get_body_root(root)
        self._assert_xpath_results(antwoord_obj, 'zkn:identificatie', 1, namespaces=self.nsmap)  # v
        self._assert_xpath_results(antwoord_obj, 'zkn:bst.omschrijving', 0, namespaces=self.nsmap)  # o
        self._assert_xpath_results(antwoord_obj, 'zkn:bst.omschrijvingGeneriek', 0, namespaces=self.nsmap)  # o
        self._assert_xpath_results(antwoord_obj, 'zkn:bst.categorie', 0, namespaces=self.nsmap)  # o
        self._assert_xpath_results(antwoord_obj, 'zkn:bst.reactietermijn', 1, namespaces=self.nsmap)  # o
        self._assert_xpath_results(antwoord_obj, 'zkn:bst.publicatieIndicatie', 0, namespaces=self.nsmap)  # o
        self._assert_xpath_results(antwoord_obj, 'zkn:bst.publicatieTekst', 0, namespaces=self.nsmap)  # o
        self._assert_xpath_results(antwoord_obj, 'zkn:bst.publicatieTermijn', 0, namespaces=self.nsmap)  # o
        self._assert_xpath_results(antwoord_obj, 'zkn:datumBeslissing', 1, namespaces=self.nsmap)  # v
        self._assert_xpath_results(antwoord_obj, 'zkn:toelichting', 0, namespaces=self.nsmap)  # o
        self._assert_xpath_results(antwoord_obj, 'zkn:ingangsdatumWerking', 1, namespaces=self.nsmap)  # v
        self._assert_xpath_results(antwoord_obj, 'zkn:einddatumWerking', 0, namespaces=self.nsmap)  # o
        self._assert_xpath_results(antwoord_obj, 'zkn:vervalreden', 0, namespaces=self.nsmap)  # o
        self._assert_xpath_results(antwoord_obj, 'zkn:datumPublicatie', 0, namespaces=self.nsmap)  # o
        self._assert_xpath_results(antwoord_obj, 'zkn:datumVerzending', 0, namespaces=self.nsmap)  # o
        self._assert_xpath_results(antwoord_obj, 'zkn:datumUiterlijkeReactie', 0, namespaces=self.nsmap)  # o
        self._assert_xpath_results(antwoord_obj, 'stuf:tijdvakGeldigheid', 1, namespaces=self.nsmap)  # o
        self._assert_xpath_results(
            antwoord_obj, 'stuf:tijdvakGeldigheid/stuf:beginGeldigheid', 1, namespaces=self.nsmap)  # v
        self._assert_xpath_results(
            antwoord_obj, 'stuf:tijdvakGeldigheid/stuf:eindGeldigheid', 1, namespaces=self.nsmap)  # v
        self._assert_xpath_results(antwoord_obj, 'zkn:tijdstipRegistratie', 0, namespaces=self.nsmap)  # o
        self._assert_xpath_results(antwoord_obj, 'zkn:isUitkomstVan', 1, namespaces=self.nsmap)  # v
        self._assert_xpath_results(antwoord_obj, 'zkn:isVastgelegdIn', 0, namespaces=self.nsmap)  # 0..N
        self._assert_xpath_results(antwoord_obj, 'zkn:isVastgelegdIn/zkn:gerelateerde', 0, namespaces=self.nsmap)
        self._assert_xpath_results(
            # v if parent present
            antwoord_obj, 'zkn:isVastgelegdIn/zkn:gerelateerde/zkn:identificatie', 0, namespaces=self.nsmap)
        self._assert_xpath_results(
            antwoord_obj, 'zkn:isVastgelegdIn/zkn:gerelateerde/zkn:titel', 0, namespaces=self.nsmap)


class geefBesluitDetails_BslLa01Tests(BaseSoapTests):
    antwoord_xpath = '/soap11env:Envelope/soap11env:Body/zds:geefBesluitdetails_BslLa01'

    def setUp(self):
        super().setUp()
        self.besluit = BesluitFactory()

    def _do_simple_request(self, raw_response=False):
        """
        Do a simple SOAP request.
        """
        client = self._get_client('BeantwoordVraag')
        stuf_factory, zkn_factory, zds_factory = self._get_type_factories(client)

        with client.options(raw_response=raw_response):
            return client.service.geefBesluitdetails_BslLv01(
                stuurgegevens=stuf_factory['BSL-StuurgegevensLv01'](
                    berichtcode='Lv01',
                    entiteittype='BSL',
                ),
                parameters=stuf_factory['BSL-parametersVraagSynchroon'](
                    sortering=1,
                    indicatorVervolgvraag=False
                ),
                scope={
                    'object': zkn_factory['geefBesluitDetails-BSL-vraagScope'](**{
                        'entiteittype': 'BSL',  # v
                        'identificatie': Nil,  # v
                        'datumBeslissing': Nil,  # v
                        'ingangsdatumWerking': Nil,  # v
                        'bst.omschrijving': Nil,
                    })
                },
                gelijk=zkn_factory['geefBesluitDetails-BSL-vraagSelectie'](
                    entiteittype='BSL',  # v
                    identificatie=self.besluit.identificatie,  # v
                )
            )

    def test_namespace_response(self):
        """
        Verify that the namespace of the response is as expected.
        """
        result = self._do_simple_request(raw_response=True)
        root = etree.fromstring(result.content)
        namespaces = {ns for el in root.iterdescendants() for ns in el.nsmap.values()}

        self.assertIn('http://www.egem.nl/StUF/sector/zkn/0310', namespaces)
        self.assertIn('http://www.egem.nl/StUF/StUF0301', namespaces)
        self.assertIn('http://www.stufstandaarden.nl/koppelvlak/zds0120', namespaces)

    def test_root_element(self):
        """
        Test that the root element in soapenv:Body is called geefBesluitDetails_BslLv01
        and has the namespace 'http://www.stufstandaarden.nl/koppelvlak/zds0120'
        """
        result = self._do_simple_request(raw_response=True)
        root = etree.fromstring(result.content)
        self._assert_xpath_results(root, self.antwoord_xpath, 1, namespaces=self.nsmap)

    def test_stuurgegevens_element(self):
        """
        Test that in the geefBesluitDetails_BslLv01 element there is an element
        called stuurgegevens which has the namespace 'http://www.egem.nl/StUF/sector/zkn/0310'
        """
        result = self._do_simple_request(raw_response=True)
        root = etree.fromstring(result.content)
        self._assert_xpath_results(self._get_body_root(root), 'zkn:stuurgegevens', 1, namespaces=self.nsmap)

    def test_antwoord_element(self):
        """
        Test that in the geefBesluitDetails_BslLv01 element there is an element
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
        Test that the object element has an attribute entiteittype and has the namespace 'http://www.egem.nl/StUF/StUF0301'
        """
        result = self._do_simple_request(raw_response=True)
        root = etree.fromstring(result.content)
        self._assert_xpath_results(self._get_body_root(root), 'zkn:antwoord/zkn:object[@stuf:entiteittype]', 1, namespaces=self.nsmap)


class STPgeefBesluitDetailsTests(BaseTestPlatformTests):
    maxDiff = None
    test_files_subfolder = 'stp_geefBesluitDetails'
    porttype = 'BeantwoordVraag'

    def setUp(self):
        super().setUp()
        self.informatieobject1 = EnkelvoudigInformatieObjectFactory.create()
        self.besluit = BesluitFactory.create(
            informatieobject=[self.informatieobject1, ],
            besluittype__datum_begin_geldigheid_besluittype='20170830',
            besluittype__datum_einde_geldigheid_besluittype=None,
        )

    def _test_response(self, response):
        self.assertEquals(response.status_code, 200, response.content)

        response_root = etree.fromstring(response.content)
        response_berichtcode = response_root.xpath('//zkn:stuurgegevens/stuf:berichtcode', namespaces=self.nsmap)[0].text
        self.assertEqual(response_berichtcode, BerichtcodeChoices.la01, response.content)

        response_object_element = response_root.xpath('//zkn:antwoord/zkn:object', namespaces=self.nsmap)[0]

        response_besluit_id = response_object_element.xpath('zkn:identificatie', namespaces=self.nsmap)[0].text
        self.assertEqual(response_besluit_id, self.besluit.besluitidentificatie, response.content)

        response_zaak_id = response_object_element.xpath('zkn:isUitkomstVan/zkn:gerelateerde/zkn:identificatie', namespaces=self.nsmap)[0].text
        self.assertEqual(response_zaak_id, self.besluit.zaak.zaakidentificatie, response.content)

    def test_geefBesluitDetails_BslLv01_01(self):
        vraag = 'geefBesluitDetails_BslLv01_01.xml'
        context = {
            'genereerbesluitident_identificatie_2': self.besluit.besluitidentificatie,
            'referentienummer': self.genereerID(10),
        }
        response = self._do_request(self.porttype, vraag, context)

        self._test_response(response)

        response_root = etree.fromstring(response.content)
        response_object_element = response_root.xpath('//zkn:antwoord/zkn:object', namespaces=self.nsmap)[0]

        dct_omschrijving = response_object_element.xpath('zkn:isVastgelegdIn/zkn:gerelateerde/zkn:dct.omschrijving', namespaces=self.nsmap)[0].text
        self.assertEqual(dct_omschrijving, self.informatieobject1.informatieobjecttype.informatieobjecttypeomschrijving, response.content)

    def test_geefBesluitDetails_BslLv01_03(self):
        vraag = 'geefBesluitDetails_BslLv01_03.xml'
        context = {
            'voegbesluittoe_identificatie_3': self.besluit.besluitidentificatie,
            'referentienummer': self.genereerID(10),
        }
        response = self._do_request(self.porttype, vraag, context)

        self._test_response(response)

    def test_geefBesluitDetails_BslLv01_05(self):
        vraag = 'geefBesluitDetails_BslLv01_05.xml'
        context = {
            'voegbesluittoe_identificatie_5': self.besluit.besluitidentificatie,
            'referentienummer': self.genereerID(10),
        }
        response = self._do_request(self.porttype, vraag, context)

        self._test_response(response)

    def test_geefBesluitDetails_BslLv01_07(self):
        vraag = 'geefBesluitDetails_BslLv01_07.xml'
        context = {
            'voegbesluittoe_identificatie_7': self.besluit.besluitidentificatie,
            'referentienummer': self.genereerID(10),
        }
        response = self._do_request(self.porttype, vraag, context)

        self._test_response(response)

    def test_geefBesluitDetails_BslLv01_09(self):
        vraag = 'geefBesluitDetails_BslLv01_09.xml'
        context = {
            'voegbesluittoe_identificatie_9': self.besluit.besluitidentificatie,
            'referentienummer': self.genereerID(10),
        }
        response = self._do_request(self.porttype, vraag, context)

        self._test_response(response)

    def test_geefBesluitDetails_BslLv01_11(self):
        vraag = 'geefBesluitDetails_BslLv01_11.xml'
        context = {
            'voegbesluittoe_identificatie_3': self.besluit.besluitidentificatie,
            'referentienummer': self.genereerID(10),
        }
        response = self._do_request(self.porttype, vraag, context)

        self._test_response(response)

        root = etree.fromstring(response.content)
        expected = [
            '//zkn:antwoord/zkn:object/stuf:tijdvakGeldigheid/stuf:beginGeldigheid[text()="20170830"]',
            '//zkn:antwoord/zkn:object/stuf:tijdvakGeldigheid/stuf:eindGeldigheid[@xsi:nil="true"]',
        ]
        for expectation in expected:
            self._assert_xpath_results(root, expectation, 1, namespaces=self.nsmap)

    def test_geefBesluitDetails_BslLv01_13(self):
        vraag = 'geefBesluitDetails_BslLv01_13.xml'
        context = {
            'voegbesluittoe_identificatie_3': self.besluit.besluitidentificatie,
            'referentienummer': self.genereerID(10),
        }
        response = self._do_request(self.porttype, vraag, context)

        self._test_response(response)
