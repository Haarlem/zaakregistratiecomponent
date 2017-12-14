
from lxml import etree
from zeep.xsd.const import Nil

from ...rgbz.tests.factory_models import BesluitFactory
from .base import BaseSoapTests


class geefLijstBesluiten_ZakLv01Tests(BaseSoapTests):
    antwoord_xpath = '/soap11env:Envelope/soap11env:Body/zds:geefLijstBesluiten_ZakLa01'

    def test_gelijk(self):
        besluit = BesluitFactory.create()
        zaak = besluit.zaak
        BesluitFactory.create(zaak=zaak)
        BesluitFactory.create()

        client = self._get_client('BeantwoordVraag')
        stuf_factory, zkn_factory, zds_factory = self._get_type_factories(client)

        response = client.service.geefLijstBesluiten_ZakLv01(
            # http://www.egem.nl/StUF/StUF0301:ZAK-StuurgegevensLv01
            stuurgegevens=stuf_factory['ZAK-StuurgegevensLv01'](
                berichtcode='Lv01',
                entiteittype='ZAK',
            ),
            # http://www.egem.nl/StUF/StUF0301:ZAK-parametersVraagSynchroon
            parameters=stuf_factory['ZAK-parametersVraagSynchroon'](
                sortering=1,
                indicatorVervolgvraag=False
            ),
            scope={
                # http://www.egem.nl/StUF/sector/zkn/0310:GeefLijstBesluiten-ZAK-vraagScope
                'object': zkn_factory['GeefLijstBesluiten-ZAK-vraagScope'](
                    entiteittype='ZAK',
                    identificatie=Nil,
                    # http://www.egem.nl/StUF/sector/zkn/0310:GeefLijstBesluiten-ZAKBSL-vraag
                    leidtTot=zkn_factory['GeefLijstBesluiten-ZAKBSL-vraag'](
                        entiteittype='ZAKBSL',
                        # http://www.egem.nl/StUF/sector/zkn/0310:GeefLijstBesluiten-BSL-gerelateerdeVraag
                        gerelateerde=zkn_factory['GeefLijstBesluiten-BSL-gerelateerdeVraag'](
                            entiteittype='BSL',
                            # Mandatory elements:
                            identificatie=Nil,
                            datumBeslissing=Nil,
                            ingangsdatumWerking=Nil,
                        )
                    )
                )
            },
            # http://www.egem.nl/StUF/sector/zkn/0310:GeefLijstBesluiten-ZAK-vraagSelectie
            gelijk=zkn_factory['GeefLijstBesluiten-ZAK-vraagSelectie'](
                entiteittype='ZAK',  # v
                identificatie=zaak.zaakidentificatie,
            )
        )
        self.assertEquals(len(response.antwoord.object), 1)
        self.assertEquals(len(response.antwoord.object[0].leidtTot), 2)

    def test_namespace_response(self):
        besluit = BesluitFactory.create()
        zaak = besluit.zaak

        client = self._get_client('BeantwoordVraag')
        stuf_factory, zkn_factory, zds_factory = self._get_type_factories(client)

        with client.options(raw_response=True):
            response = client.service.geefLijstBesluiten_ZakLv01(
                stuurgegevens=stuf_factory['ZAK-StuurgegevensLv01'](
                    berichtcode='Lv01',
                    entiteittype='ZAK',
                ),
                parameters=stuf_factory['ZAK-parametersVraagSynchroon'](
                    sortering=1,
                    indicatorVervolgvraag=False
                ),
                scope={
                    'object': zkn_factory['GeefLijstBesluiten-ZAK-vraagScope'](
                        entiteittype='ZAK',
                        identificatie=Nil,
                        leidtTot=zkn_factory['GeefLijstBesluiten-ZAKBSL-vraag'](
                            entiteittype='ZAKBSL',
                            gerelateerde=zkn_factory['GeefLijstBesluiten-BSL-gerelateerdeVraag'](**{
                                'entiteittype': 'BSL',
                                # Mandatory elements:
                                'identificatie': Nil,
                                'datumBeslissing': Nil,
                                'ingangsdatumWerking': Nil,
                                # Optional elements:
                                'datumPublicatie': Nil,
                                'bst.omschrijving': Nil,
                            })
                        )
                    )
                },
                gelijk=zkn_factory['GeefLijstBesluiten-ZAK-vraagSelectie'](
                    entiteittype='ZAK',  # v
                    identificatie=zaak.zaakidentificatie,
                )
            )

        root = etree.fromstring(response.content)

        # The expectation is that only the selected fields are returned.
        antwoord_obj = root.xpath(
            '/soap11env:Envelope/soap11env:Body/zds:geefLijstBesluiten_ZakLa01/zkn:antwoord/zkn:object', namespaces=self.nsmap)[0]
        self._assert_xpath_results(antwoord_obj, 'zkn:identificatie', 1, namespaces=self.nsmap)

        self._assert_xpath_results(antwoord_obj, 'zkn:leidtTot', 1, namespaces=self.nsmap)
        self._assert_xpath_results(antwoord_obj, 'zkn:leidtTot/zkn:gerelateerde', 1, namespaces=self.nsmap)

        gerelateerde_element = antwoord_obj.xpath('zkn:leidtTot/zkn:gerelateerde', namespaces=self.nsmap)[0]
        self._assert_xpath_results(gerelateerde_element, 'zkn:identificatie', 1, namespaces=self.nsmap)
        self._assert_xpath_results(gerelateerde_element, 'zkn:datumBeslissing', 1, namespaces=self.nsmap)
        self._assert_xpath_results(gerelateerde_element, 'zkn:bst.omschrijving', 1, namespaces=self.nsmap)
        self._assert_xpath_results(gerelateerde_element, 'zkn:toelichting', 0, namespaces=self.nsmap)
        self._assert_xpath_results(gerelateerde_element, 'zkn:ingangsdatumWerking', 1, namespaces=self.nsmap)
        self._assert_xpath_results(gerelateerde_element, 'zkn:einddatumWerking', 0, namespaces=self.nsmap)
        self._assert_xpath_results(gerelateerde_element, 'zkn:vervalreden', 0, namespaces=self.nsmap)
        self._assert_xpath_results(gerelateerde_element, 'zkn:datumPublicatie', 1, namespaces=self.nsmap)
        self._assert_xpath_results(gerelateerde_element, 'zkn:datumVerzending', 0, namespaces=self.nsmap)
        self._assert_xpath_results(gerelateerde_element, 'zkn:datumUiterlijkeReactie', 0, namespaces=self.nsmap)
        self._assert_xpath_results(gerelateerde_element, 'zkn:tijdvakGeldigheid', 0, namespaces=self.nsmap)
        self._assert_xpath_results(gerelateerde_element, 'zkn:tijdvakGeldigheid/zkn:beginGeldigheid', 0, namespaces=self.nsmap)
        self._assert_xpath_results(gerelateerde_element, 'zkn:tijdvakGeldigheid/zkn:eindGeldigheid', 0, namespaces=self.nsmap)
        # TODO [TECH]: Taiga #210
        # self._assert_xpath_results(antwoord_obj, 'zkn:leidtTot/zkn:tijdstipRegistratie', 0, namespaces=self.nsmap)

    def test_tijdvak_geldigheid(self):
        besluit = BesluitFactory.create(
            besluittype__datum_begin_geldigheid_besluittype="20170830",
            besluittype__datum_einde_geldigheid_besluittype=None
        )
        zaak = besluit.zaak

        client = self._get_client('BeantwoordVraag')
        stuf_factory, zkn_factory, zds_factory = self._get_type_factories(client)

        with client.options(raw_response=True):
            response = client.service.geefLijstBesluiten_ZakLv01(
                stuurgegevens=stuf_factory['ZAK-StuurgegevensLv01'](
                    berichtcode='Lv01',
                    entiteittype='ZAK',
                ),
                parameters=stuf_factory['ZAK-parametersVraagSynchroon'](
                    sortering=1,
                    indicatorVervolgvraag=False
                ),
                scope={
                    'object': zkn_factory['GeefLijstBesluiten-ZAK-vraagScope'](
                        entiteittype='ZAK',  # v
                        scope='alles',
                        leidtTot=zkn_factory['GeefLijstBesluiten-ZAKBSL-vraag'](
                            entiteittype='ZAKBSL',
                            gerelateerde=zkn_factory['GeefLijstBesluiten-BSL-gerelateerdeVraag'](
                                entiteittype='BSL',
                                # Mandatory elements:
                                identificatie=Nil,
                                datumBeslissing=Nil,
                                ingangsdatumWerking=Nil,
                            )
                        )
                    )
                },
                gelijk=zkn_factory['GeefLijstBesluiten-ZAK-vraagSelectie'](
                    entiteittype='ZAK',  # v
                    identificatie=zaak.zaakidentificatie,
                )
            )

        root = etree.fromstring(response.content)
        expected = [
            'zkn:antwoord/zkn:object/zkn:leidtTot/zkn:gerelateerde/stuf:tijdvakGeldigheid/stuf:beginGeldigheid[text()="20170830"]',
            'zkn:antwoord/zkn:object/zkn:leidtTot/zkn:gerelateerde/stuf:tijdvakGeldigheid/stuf:eindGeldigheid[@xsi:nil="true"]',
        ]
        for expectation in expected:
            self._assert_xpath_results(self._get_body_root(root), expectation, 1, namespaces=self.nsmap)


class geefLijstBesluiten_ZakLa01Tests(BaseSoapTests):
    antwoord_xpath = '/soap11env:Envelope/soap11env:Body/zds:geefLijstBesluiten_ZakLa01'

    def setUp(self):
        super().setUp()

        besluit = BesluitFactory.create()
        self.zaak = besluit.zaak

    def _do_simple_request(self, raw_response=False):
        """
        Do a simple SOAP request.
        """
        client = self._get_client('BeantwoordVraag')
        stuf_factory, zkn_factory, zds_factory = self._get_type_factories(client)

        with client.options(raw_response=raw_response):
            return client.service.geefLijstBesluiten_ZakLv01(
                stuurgegevens=stuf_factory['ZAK-StuurgegevensLv01'](
                    berichtcode='Lv01',
                    entiteittype='ZAK',
                ),
                parameters=stuf_factory['ZAK-parametersVraagSynchroon'](
                    sortering=1,
                    indicatorVervolgvraag=False
                ),
                scope={
                    'object': zkn_factory['GeefLijstBesluiten-ZAK-vraagScope'](
                        entiteittype='ZAK',
                        identificatie=Nil,
                        leidtTot=zkn_factory['GeefLijstBesluiten-ZAKBSL-vraag'](
                            entiteittype='ZAKBSL',
                            gerelateerde=zkn_factory['GeefLijstBesluiten-BSL-gerelateerdeVraag'](
                                entiteittype='BSL',
                                # Mandatory elements:
                                identificatie=Nil,
                                datumBeslissing=Nil,
                                ingangsdatumWerking=Nil,
                            )
                        )
                    )
                },
                gelijk=zkn_factory['GeefLijstBesluiten-ZAK-vraagSelectie'](
                    entiteittype='ZAK',  # v
                    identificatie=self.zaak.zaakidentificatie,
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
        Test that the root element in soapenv:Body is called geefLijstBesluiten_ZakLa01
        and has the namespace 'http://www.stufstandaarden.nl/koppelvlak/zds0120'
        """
        result = self._do_simple_request(raw_response=True)
        root = etree.fromstring(result.content)
        self._assert_xpath_results(root, self.antwoord_xpath, 1, namespaces=self.nsmap)

    def test_stuurgegevens_element(self):
        """
        Test that in the geefLijstBesluiten_ZakLa01 element there is an element
        called stuurgegevens which has the namespace 'http://www.egem.nl/StUF/sector/zkn/0310'
        """
        result = self._do_simple_request(raw_response=True)
        root = etree.fromstring(result.content)
        self._assert_xpath_results(self._get_body_root(root), 'zkn:stuurgegevens', 1, namespaces=self.nsmap)
        self._assert_xpath_results(self._get_body_root(root), 'zkn:stuurgegevens/stuf:berichtcode[text()="La01"]', 1, namespaces=self.nsmap)
        self._assert_xpath_results(self._get_body_root(root), 'zkn:stuurgegevens/stuf:entiteittype[text()="ZAK"]', 1, namespaces=self.nsmap)

    def test_antwoord_element(self):
        """
        Test that in the geefLijstBesluiten_ZakLa01 element there is an element
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


class geefLijstBesluiten_Fo02BerichtTests(BaseSoapTests):
    antwoord_xpath = '/soap11env:Envelope/soap11env:Body/soap11env:Fault/detail/stuf:Fo02Bericht'

    def setUp(self):
        super().setUp()

        besluit = BesluitFactory.create()
        self.zaak = besluit.zaak

    def test_validation_error_message(self):
        client = self._get_client('BeantwoordVraag', strict=False)

        #
        # This is what we hope to receive.
        #
        # <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:stuf="http://www.egem.nl/StUF/StUF0301">
        #   <soapenv:Body>
        #     <soapenv:Fault>
        #       <faultcode>?</faultcode>
        #       <faultstring xml:lang="?">?</faultstring>
        #       <!--Optional:-->
        #       <faultactor>?</faultactor>
        #       <!--Optional:-->
        #       <detail>
        #         <stuf:Fo02Bericht>
        #           <stuf:stuurgegevens>
        #             <stuf:berichtcode>Fo02</stuf:berichtcode>
        #           </stuf:stuurgegevens>
        #           <stuf:body>
        #             <stuf:code>?</stuf:code>
        #             <stuf:plek>?</stuf:plek>
        #             <stuf:omschrijving>?</stuf:omschrijving>
        #           </stuf:body>
        #         </stuf:Fo02Bericht>
        #         <!--You may enter ANY elements at this point-->
        #       </detail>
        #     </soapenv:Fault>
        #   </soapenv:Body>
        # </soapenv:Envelope>

        with client.options(raw_response=True):
            stuf_factory, zkn_factory, zds_factory = self._get_type_factories(client)

            response = client.service.geefLijstBesluiten_ZakLv01(
                stuurgegevens=stuf_factory['ZAK-StuurgegevensLv01'](
                    berichtcode='Lv01',
                    entiteittype='AAA',
                ),
                parameters=stuf_factory['ZAK-parametersVraagSynchroon'](
                    sortering=99,  # Is too high.
                    indicatorVervolgvraag=False
                ),
                scope={
                    'object': zkn_factory['GeefLijstBesluiten-ZAK-vraagScope'](
                        entiteittype='ZAK',
                        identificatie=Nil,
                        leidtTot=zkn_factory['GeefLijstBesluiten-ZAKBSL-vraag'](
                            entiteittype='ZAKBSL',
                            gerelateerde=zkn_factory['GeefLijstBesluiten-BSL-gerelateerdeVraag'](
                                entiteittype='BSL',
                                # Mandatory elements:
                                identificatie=Nil,
                                datumBeslissing=Nil,
                                ingangsdatumWerking=Nil,
                            )
                        )
                    )
                },
                gelijk=zkn_factory['GeefLijstBesluiten-ZAK-vraagSelectie'](
                    entiteittype='ZAK',  # v
                    identificatie=self.zaak.zaakidentificatie,
                )
            )

        root = etree.fromstring(response.content)
        #
        # These should be part of spyne's testsuite.
        #
        self._assert_xpath_results(root, '/soap11env:Envelope/soap11env:Body/soap11env:Fault/detail', 1, namespaces=self.nsmap)

        expected_once = [
            'stuf:stuurgegevens',
            'stuf:stuurgegevens/stuf:berichtcode[text()="Fo02"]',
            'stuf:body',
            'stuf:body/stuf:code[text()="StUF055"]',
            'stuf:body/stuf:plek[text()="client"]',
        ]
        for expectation in expected_once:
            self._assert_xpath_results(self._get_body_root(root), expectation, 1, namespaces=self.nsmap)
