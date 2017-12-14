from datetime import datetime, timedelta
from unittest import skip

from lxml import etree
from zeep.xsd.const import Nil

from zaakmagazijn.utils.stuf_datetime import stuf_date

from ...rgbz.choices import JaNee
from ...rgbz.tests.factory_models import (
    StatusFactory, Zaak, ZaakFactory, ZaakTypeFactory
)
from ..stuf.choices import BerichtcodeChoices
from ..stuf.ordering import ZAKSortering
from .base import BaseSoapTests, BaseTestPlatformTests


class geefZaakstatus_ZakLv01Tests(BaseSoapTests):

    def setUp(self):
        super().setUp()
        self.yesterday = stuf_date(datetime.today() - timedelta(days=1))
        self.two_days_ago = stuf_date(datetime.today() - timedelta(days=2))

    def test_gelijk(self):
        zaak = ZaakFactory.create()
        status1 = StatusFactory.create(zaak=zaak, datum_status_gezet=self.two_days_ago)
        status2 = StatusFactory.create(zaak=zaak, datum_status_gezet=self.yesterday)
        # This status should be filtered out, because it doesn't match the filter (indicatieLaatsteStatus does not match).
        status3 = StatusFactory.create(zaak=zaak, indicatie_laatst_gezette_status=JaNee.ja)

        # Should not show up, because the 'identificatie' field doesn't match.
        other_zaak = ZaakFactory.create()
        other_status = StatusFactory.create(zaak=other_zaak)

        client = self._get_client('BeantwoordVraag')
        stuf_factory, zkn_factory, zds_factory = self._get_type_factories(client)

        response = client.service.geefZaakstatus_ZakLv01(
            stuurgegevens=stuf_factory['ZAK-StuurgegevensLv01'](
                berichtcode='Lv01',
                entiteittype='ZAK',),
            parameters=stuf_factory['ZAK-parametersVraagSynchroon'](
                sortering=1,
                indicatorVervolgvraag=False),
            scope={
                'object': zkn_factory['GeefZaakStatus-ZAK-vraagScope'](
                    entiteittype='ZAK',
                    identificatie=Nil,
                    heeft=zkn_factory['GeefZaakStatus-ZAKSTT-vraagScope'](
                        entiteittype='ZAKSTT',
                        indicatieLaatsteStatus=Nil,
                        datumStatusGezet=Nil,
                        gerelateerde=zkn_factory['GeefZaakStatus-STT-vraag'](
                            entiteittype='STT',
                            volgnummer=Nil,
                        )
                    )
                ),
            },
            gelijk=zkn_factory['GeefZaakStatus-ZAK-vraagSelectie'](
                entiteittype='ZAK',
                identificatie=zaak.zaakidentificatie,
                heeft=zkn_factory['GeefZaakStatus-ZAKSTT-vraagSelectie'](
                    entiteittype='ZAKSTT',
                    indicatieLaatsteStatus=JaNee.ja,
                )
            )
        )
        self.assertEquals(len(response.antwoord.object), 1)
        self.assertEquals(len(response.antwoord.object[0].heeft), 1)

    @skip('TODO [KING]: \'toelichting\' is optional in the scope, but required in '
          'the response. To me, this seems like a bug in the XSD.')
    def test_scope(self):
        zaak = ZaakFactory.create()
        status1 = StatusFactory.create(zaak=zaak)

        client = self._get_client('BeantwoordVraag')
        stuf_factory, zkn_factory, zds_factory = self._get_type_factories(client)

        with client.options(raw_response=True):
            response = client.service.geefZaakstatus_ZakLv01(
                stuurgegevens=stuf_factory['ZAK-StuurgegevensLv01'](
                    berichtcode='Lv01',
                    entiteittype='ZAK',),
                parameters=stuf_factory['ZAK-parametersVraagSynchroon'](
                    sortering=1,
                    indicatorVervolgvraag=False),
                scope={
                    'object': zkn_factory['GeefZaakStatus-ZAK-vraagScope'](
                        entiteittype='ZAK',
                        identificatie=Nil,
                        heeft=zkn_factory['GeefZaakStatus-ZAKSTT-vraagScope'](
                            entiteittype='ZAKSTT',
                            indicatieLaatsteStatus=Nil,
                            datumStatusGezet=Nil,
                            gerelateerde=zkn_factory['GeefZaakStatus-STT-vraag'](
                                entiteittype='STT',
                                volgnummer=Nil,
                            )
                        )
                    )
                },
                gelijk=zkn_factory['GeefZaakStatus-ZAK-vraagSelectie'](
                    entiteittype='ZAK',
                    identificatie=zaak.zaakidentificatie,
                    heeft=zkn_factory['GeefZaakStatus-ZAKSTT-vraagSelectie'](
                        entiteittype='ZAKSTT',
                        indicatieLaatsteStatus=JaNee.ja,
                    )
                )
            )

        root = etree.fromstring(response.content)

        # The expectation is that only the selected fields are returned.
        antwoord_obj = root.xpath(
            '/soap11env:Envelope/soap11env:Body/zds:geefZaakstatus_ZakLa01/zkn:antwoord/zkn:object', namespaces=self.nsmap)[0]
        self._assert_xpath_results(antwoord_obj, 'zkn:identificatie', 1, namespaces=self.nsmap)
        self._assert_xpath_results(antwoord_obj, 'zkn:heeft', 1, namespaces=self.nsmap)
        # optional and not asked for.
        self._assert_xpath_results(antwoord_obj, 'zkn:heeft/zkn:toelichting', 0, namespaces=self.nsmap)
        # required and not asked for.
        self._assert_xpath_results(antwoord_obj, 'zkn:heeft/zkn:indicatieLaatsteStatus', 1, namespaces=self.nsmap)

    @skip('TODO There is only one way to sort a list of 1 zaak. This test should be '
          'moved to geefZaakdetail or another service which returns multiple objects.')
    def test_sortering_parameters(self):
        """
        Test to verify that the sorting is done according to the Stuf XSD constants.
        """
        zaak1 = ZaakFactory.create()
        zaak2 = ZaakFactory.create()
        zaak3 = ZaakFactory.create()
        zaak4 = ZaakFactory.create()
        zaak5 = ZaakFactory.create()

        client = self._get_client('BeantwoordVraag')
        stuf_factory, zkn_factory, zds_factory = self._get_type_factories(client)

        # TODO [TECH]: Taiga #208 Expand ZaakFactory to auto-create various rol/betrokkenen? (can't sort on non-existing data,
        # this would allow testing of sorting variables 6 through 13
        for i in range(1, 6):
            response = client.service.geefZaakstatus_ZakLv01(
                stuurgegevens=stuf_factory['ZAK-StuurgegevensLv01'](
                    berichtcode='Lv01',
                    entiteittype='ZAK',),
                parameters=stuf_factory['ZAK-parametersVraagSynchroon'](
                    sortering=i,
                    indicatorVervolgvraag=False, ),
                scope={
                    'object': zkn_factory['GeefZaakStatus-ZAK-vraagScope'](
                        entiteittype='ZAK',
                        identificatie=Nil),
                },
                gelijk=zkn_factory['GeefZaakStatus-ZAK-vraagSelectie'](
                    entiteittype='ZAK',
                    identificatie=zaak1.zaakidentificatie,
                    heeft=zkn_factory['GeefZaakStatus-ZAKSTT-vraagSelectie'](
                        entiteittype='ZAKSTT',
                        indicatieLaatsteStatus=JaNee.ja,
                    )
                )
            )
            self.assertEquals(len(response.antwoord.object), 5)
            objs = response.antwoord.object
            order_by = ZAKSortering[i]
            zaken = Zaak.objects.all().order_by(*order_by)
            for j in range(0, 5):
                self.assertEquals(objs[j].identificatie, zaken[j].zaakidentificatie,
                                  msg='Sortering {} with ordering {} failed'.format(i, order_by))

    @skip('TODO This test should be moved to geefZaakdetail or another service which returns multiple objects.')
    def test_maximum_aantal_parameter(self):
        """
        Test to see if we can properly limit the maximum number of results.
        """
        zaak1 = ZaakFactory.create()
        zaak2 = ZaakFactory.create()
        zaak3 = ZaakFactory.create()
        zaak4 = ZaakFactory.create()

        client = self._get_client('BeantwoordVraag')
        stuf_factory, zkn_factory, zds_factory = self._get_type_factories(client)

        response = client.service.geefZaakstatus_ZakLv01(
            stuurgegevens=stuf_factory['ZAK-StuurgegevensLv01'](
                berichtcode='Lv01',
                entiteittype='ZAK',),
            parameters=stuf_factory['ZAK-parametersVraagSynchroon'](
                sortering=1,
                indicatorVervolgvraag=False,
                maximumAantal=3
            ),
            scope=zkn_factory.GeefZaakStatus_vraagScope(
                object=zkn_factory.GeefZaakStatus_ZAK_vraagScope(
                    entiteittype='ZAK',
                    identificatie=Nil)),
        )
        self.assertEquals(len(response.antwoord.object), 3)

    @skip('TODO This test should be moved to geefZaakdetail or another service which returns multiple objects.')
    def test_vervolg_aantal_parameters(self):
        """
        Test to see if we can request the total number of objects found,
        and if the other parameters are passed through as expected.
        """
        zaaktype = ZaakTypeFactory.create()
        ZaakFactory.create_batch(20, zaaktype=zaaktype)

        client = self._get_client('BeantwoordVraag')
        stuf_factory, zkn_factory, zds_factory = self._get_type_factories(client)

        response = client.service.geefZaakstatus_ZakLv01(
            stuurgegevens=stuf_factory['ZAK-StuurgegevensLv01'](
                berichtcode='Lv01',
                entiteittype='ZAK',),
            parameters=stuf_factory['ZAK-parametersVraagSynchroon'](
                sortering=1,
                indicatorVervolgvraag=True,
                indicatorAfnemerIndicatie=True,
                maximumAantal=3,
                indicatorAantal=True
            ),
            scope=zkn_factory.GeefZaakStatus_vraagScope(
                object=zkn_factory.GeefZaakStatus_ZAK_vraagScope(
                    entiteittype='ZAK',
                    identificatie=Nil)),
        )
        self.assertEquals(len(response.antwoord.object), 3)
        self.assertEquals(response.parameters.aantalVoorkomens, 20)
        self.assertEquals(response.parameters.indicatorVervolgvraag, True)
        self.assertEquals(response.parameters.indicatorAfnemerIndicatie, True)


class geefZaakstatus_ZakLa01Tests(BaseSoapTests):
    antwoord_xpath = '/soap11env:Envelope/soap11env:Body/zds:geefZaakstatus_ZakLa01'

    def setUp(self):
        super().setUp()
        self.status = StatusFactory.create(indicatie_laatst_gezette_status=JaNee.ja)
        self.zaak = self.status.zaak

    def _do_simple_request(self, raw_response=False):
        """
        Do a simple SOAP request.
        """
        client = self._get_client('BeantwoordVraag')
        stuf_factory, zkn_factory, zds_factory = self._get_type_factories(client)

        with client.options(raw_response=raw_response):
            return client.service.geefZaakstatus_ZakLv01(
                stuurgegevens=stuf_factory['ZAK-StuurgegevensLv01'](
                    berichtcode='Lv01',
                    entiteittype='ZAK'),
                parameters=stuf_factory['ZAK-parametersVraagSynchroon'](
                    sortering=1,
                    indicatorVervolgvraag=False),
                scope={
                    'object': zkn_factory['GeefZaakStatus-ZAK-vraagScope'](
                        entiteittype='ZAK',
                        identificatie=Nil,
                        heeft=zkn_factory['GeefZaakStatus-ZAKSTT-vraagScope'](
                            entiteittype='ZAKSTT',
                            indicatieLaatsteStatus=Nil,
                            datumStatusGezet=Nil,
                            gerelateerde=zkn_factory['GeefZaakStatus-STT-vraag'](
                                entiteittype='STT',
                                volgnummer=Nil,
                            )
                        )
                    ),
                },
                gelijk=zkn_factory['GeefZaakStatus-ZAK-vraagSelectie'](
                    entiteittype='ZAK',
                    identificatie=self.zaak.zaakidentificatie,
                    heeft=zkn_factory['GeefZaakStatus-ZAKSTT-vraagSelectie'](
                        entiteittype='ZAKSTT',
                        indicatieLaatsteStatus=JaNee.ja,
                    )
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
        Test that the root element in soapenv:Body is called geefZaakstatus_ZakLa01
        and has the namespace 'http://www.stufstandaarden.nl/koppelvlak/zds0120'
        """
        result = self._do_simple_request(raw_response=True)
        root = etree.fromstring(result.content)
        self._assert_xpath_results(root, self.antwoord_xpath, 1, namespaces=self.nsmap)

    def test_stuurgegevens_element(self):
        """
        Test that in the geefZaakstatus_ZakLa01 element there is an element
        called stuurgegevens which has the namespace 'http://www.egem.nl/StUF/sector/zkn/0310'
        """
        result = self._do_simple_request(raw_response=True)
        root = etree.fromstring(result.content)
        self._assert_xpath_results(self._get_body_root(root), 'zkn:stuurgegevens', 1, namespaces=self.nsmap)
        self._assert_xpath_results(self._get_body_root(root), 'zkn:stuurgegevens/stuf:berichtcode[text()="La01"]', 1, namespaces=self.nsmap)
        self._assert_xpath_results(self._get_body_root(root), 'zkn:stuurgegevens/stuf:entiteittype[text()="ZAK"]', 1, namespaces=self.nsmap)

    def test_antwoord_element(self):
        """
        Test that in the geefZaakstatus_ZakLa01 element there is an element
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


class geefZaakstatus_Fo02BerichtTests(BaseSoapTests):
    antwoord_xpath = '/soap11env:Envelope/soap11env:Body/soap11env:Fault/detail/stuf:Fo02Bericht'

    def test_validation_error_message(self):
        client = self._get_client('BeantwoordVraag', strict=False)

        self.status = StatusFactory.create(indicatie_laatst_gezette_status=JaNee.ja)
        self.zaak = self.status.zaak

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
            response = client.service.geefZaakstatus_ZakLv01(
                stuurgegevens=stuf_factory['ZAK-StuurgegevensLv01'](
                    berichtcode='Lv01',
                    entiteittype='AAA'),
                parameters=stuf_factory['ZAK-parametersVraagSynchroon'](
                    sortering=99,  # Is too high.
                    indicatorVervolgvraag=False),
                scope={
                    'object': zkn_factory['GeefZaakStatus-ZAK-vraagScope'](
                        entiteittype='ZAK',
                        identificatie=Nil,
                        heeft=zkn_factory['GeefZaakStatus-ZAKSTT-vraagScope'](
                            entiteittype='ZAKSTT',
                            indicatieLaatsteStatus=Nil,
                            datumStatusGezet=Nil,
                            gerelateerde=zkn_factory['GeefZaakStatus-STT-vraag'](
                                entiteittype='STT',
                                volgnummer=Nil,
                            )
                        )
                    ),
                },
                gelijk=zkn_factory['GeefZaakStatus-ZAK-vraagSelectie'](
                    entiteittype='ZAK',
                    identificatie=self.zaak.zaakidentificatie,
                    heeft=zkn_factory['GeefZaakStatus-ZAKSTT-vraagSelectie'](
                        entiteittype='ZAKSTT',
                        indicatieLaatsteStatus=JaNee.ja,
                    )
                )
            )
        root = etree.fromstring(response.content)
        #
        # These should be part of spyne's testsuite.
        #
        self._assert_xpath_results(root, '/soap11env:Envelope/soap11env:Body/soap11env:Fault/detail', 1, namespaces=self.nsmap)
        self.pretty_print(root)

        expected_once = [
            'stuf:stuurgegevens',
            'stuf:stuurgegevens/stuf:berichtcode[text()="Fo02"]',
            'stuf:body',
            'stuf:body/stuf:code[text()="StUF055"]',
            'stuf:body/stuf:plek[text()="client"]',
        ]
        for expectation in expected_once:
            self._assert_xpath_results(self._get_body_root(root), expectation, 1, namespaces=self.nsmap)


class STPgeefZaakstatus_ZakLv01Tests(BaseTestPlatformTests):
    """
    Note that all three 'vraag bestanden' are equal, except the parameter 'genereerzaakident_identificatie_<NR>',
    so the three tests ask for different items, for checking the content of the response, we have to make these three
    different items accordingly with the factories.
    """
    maxDiff = None
    test_files_subfolder = 'stp_geefZaakstatus'
    porttype = 'BeantwoordVraag'

    def setUp(self):
        super().setUp()

        self.status = StatusFactory.create(indicatie_laatst_gezette_status=JaNee.ja, statustoelichting='hello world')
        self.zaak = self.status.zaak

        for i in range(1, 3):
            StatusFactory.create(
                indicatie_laatst_gezette_status=JaNee.nee, zaak=self.zaak,
                datum_status_gezet=stuf_date(datetime.today() - timedelta(days=i)))

    def _test_response(self, response):
        self.assertEquals(response.status_code, 200, response.content)

        response_root = etree.fromstring(response.content)
        response_berichtcode = response_root.xpath('//zkn:stuurgegevens/stuf:berichtcode', namespaces=self.nsmap)[0].text
        self.assertEqual(response_berichtcode, BerichtcodeChoices.la01, response.content)

        response_object_element = response_root.xpath('//zkn:antwoord/zkn:object', namespaces=self.nsmap)[0]

        response_zaak_id = response_object_element.xpath('zkn:identificatie', namespaces=self.nsmap)[0].text
        self.assertEqual(response_zaak_id, self.zaak.zaakidentificatie, response.content)

        response_status_toelichting = response_object_element.xpath('zkn:heeft/zkn:toelichting', namespaces=self.nsmap)[0].text
        self.assertEqual(response_status_toelichting, self.status.statustoelichting, response.content)

        response_status_type_omschrijving = response_object_element.xpath('zkn:heeft/zkn:gerelateerde/zkn:omschrijving', namespaces=self.nsmap)[0].text
        self.assertEqual(response_status_type_omschrijving, self.status.status_type.statustypeomschrijving, response.content)

        # response_zaak_type_omschrijving = response_object_element.xpath('zkn:heeft/zkn:gerelateerde/zkn:zkt.omschrijving', namespaces=self.nsmap)[0].text
        # self.assertEqual(response_zaak_type_omschrijving, self.status.status_type.zaaktype.zaaktypeomschrijving, response.content)

    def test_geefZaakstatus_ZakLv01_01(self):
        vraag = 'geefZaakstatus_ZakLv01_01.xml'
        context = {
            'referentienummer': self.genereerID(10),
            'gemeentecode': '',
            'genereerzaakident_identificatie_2': self.zaak.zaakidentificatie,
        }
        response = self._do_request(self.porttype, vraag, context)

        self._test_response(response)

    def test_geefZaakstatus_ZakLv01_03(self):
        vraag = 'geefZaakstatus_ZakLv01_03.xml'
        context = {
            'referentienummer': self.genereerID(10),
            'gemeentecode': '',
            'genereerzaakident_identificatie_4': self.zaak.zaakidentificatie,
        }
        response = self._do_request(self.porttype, vraag, context)

        self._test_response(response)

    def test_geefZaakstatus_ZakLv01_05(self):
        vraag = 'geefZaakstatus_ZakLv01_05.xml'
        context = {
            'referentienummer': self.genereerID(10),
            'gemeentecode': '',
            'genereerzaakident_identificatie_6': self.zaak.zaakidentificatie,
        }
        response = self._do_request(self.porttype, vraag, context)

        self._test_response(response)
