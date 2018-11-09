import base64
from io import BytesIO

from django.test import override_settings

from lxml import etree
from zeep.xsd.const import Nil

from ...rgbz.choices import JaNee
from ...rgbz.tests.factory_models import (
    EnkelvoudigInformatieObjectFactory, ZaakFactory,
    ZaakInformatieObjectFactory,
    InformatieObjectTypeFactory,
    InformatieObjectTypeOmschrijvingGeneriekFactory)
from ..stuf.choices import BerichtcodeChoices
from ..stuf.constants import STUF_XML_NS
from ..stuf.ordering import EDCSortering
from .base import BaseSoapTests, BaseTestPlatformTests


class DMSMockMixin:
    extra_client_mocks = ['zaakmagazijn.cmis.fields.dms_client']

    @property
    def _dms_client(self):
        return self._extra_mocked_dms_clients[0]


class geefZaakdocumentLezen_EdcLv01Tests(DMSMockMixin, BaseSoapTests):

    def setUp(self):
        super().setUp()
        self._dms_client.geef_inhoud.return_value = ('doc 1', BytesIO())

    def test_gelijk(self):
        zaak = ZaakFactory.create(status_set__indicatie_laatst_gezette_status=JaNee.ja)

        edc1 = EnkelvoudigInformatieObjectFactory.create(
            titel='doc 1',
            # below two fields are the unique identifiers
            informatieobjectidentificatie='12345',
            bronorganisatie='6789',
        )
        edc2 = EnkelvoudigInformatieObjectFactory.create(
            titel='doc 2',
            # below two fields are the unique identifiers
            informatieobjectidentificatie='98765',
            bronorganisatie='4321',
        )

        ZaakInformatieObjectFactory.create(zaak=zaak, informatieobject=edc1)
        ZaakInformatieObjectFactory.create(zaak=zaak, informatieobject=edc2)

        client = self._get_client('BeantwoordVraag')
        stuf_factory, zkn_factory, zds_factory = self._get_type_factories(client)
        response = client.service.geefZaakdocumentLezen_EdcLv01(
            # http://www.egem.nl/StUF/StUF0301:EDC-StuurgegevensLv01
            stuurgegevens=stuf_factory['EDC-StuurgegevensLv01'](
                berichtcode='Lv01',
                entiteittype='EDC',
            ),
            # http://www.egem.nl/StUF/StUF0301:EDC-parametersVraagSynchroon
            parameters=stuf_factory['EDC-parametersVraagSynchroon'](
                sortering=1,
                indicatorVervolgvraag=False
            ),
            scope={
                # http://www.egem.nl/StUF/sector/zkn/0310:GeefZaakdocumentLezen-EDC-vraagScope
                'object': zkn_factory['GeefZaakdocumentLezen-EDC-vraagScope'](**{
                    'entiteittype': 'EDC',
                    'identificatie': Nil,  # v
                    # http://www.egem.nl/StUF/sector/zkn/0310:GeefZaakdocumentLezen-EDCZAK-vraagScope
                    'isRelevantVoor': zkn_factory['GeefZaakdocumentLezen-EDCZAK-vraagScope'](
                        entiteittype='EDCZAK',
                        # NOTE: the example WSDL specifies gerelateerdeVraagScope
                        # http://www.egem.nl/StUF/sector/zkn/0310:GeefZaakdocumentLezen-ZAK-gerelateerdeVraagScope
                        gerelateerde=zkn_factory['GeefZaakdocumentLezen-ZAK-gerelateerdeVraagScope'](
                            entiteittype='ZAK',
                            identificatie=Nil  # v
                        )
                    ),
                    # 'dct.omschrijving': Nil,
                    # 'dct.category': Nil,
                    'titel': Nil,
                    'creatiedatum': Nil,
                    # 'ontvangstdatum': Nil,
                    # 'beschrijving': Nil,
                    # 'verzenddatum': Nil,
                    'vertrouwelijkAanduiding': Nil,
                    'auteur': Nil,
                    'formaat': Nil,
                    'taal': Nil,
                    # 'versie': Nil,
                    # 'status': Nil,
                    'inhoud': Nil,
                    # 'link': Nil,
                })
            },
            # http://www.egem.nl/StUF/sector/zkn/0310:GeefZaakdocumentLezen-EDC-vraagSelectie
            gelijk=zkn_factory['GeefZaakdocumentLezen-EDC-vraagSelectie'](
                entiteittype='EDC',
                identificatie=edc1.informatieobjectidentificatie,
            )
        )
        self.assertEqual(len(response.antwoord), 1)
        self.assertEqual(len(response.antwoord.object.isRelevantVoor), 1)
        self.assertEqual(response.antwoord.object.identificatie._value_1, edc1.informatieobjectidentificatie)
        self.assertEqual(response.antwoord.object.titel._value_1, 'doc 1')

    def test_sortering(self):
        """
        Test all sortering options to give back a response. The order itself
        is not checked.
        """
        document = EnkelvoudigInformatieObjectFactory.create(
            titel='doc 1',
            informatieobjectidentificatie='12345',
            bronorganisatie='6789',
        )

        client = self._get_client('BeantwoordVraag')
        stuf_factory, zkn_factory, zds_factory = self._get_type_factories(client)

        for i in EDCSortering.keys():
            with client.options(raw_response=True):
                response = client.service.geefZaakdocumentLezen_EdcLv01(
                    stuurgegevens=stuf_factory['EDC-StuurgegevensLv01'](
                        berichtcode='Lv01',
                        entiteittype='EDC',
                    ),
                    parameters=stuf_factory['EDC-parametersVraagSynchroon'](
                        sortering=i,
                        indicatorVervolgvraag=False
                    ),
                    scope={
                        'object': zkn_factory['GeefZaakdocumentLezen-EDC-vraagScope'](**{
                            'entiteittype': 'EDC',
                            'identificatie': Nil,  # v
                        })
                    },
                    gelijk=zkn_factory['GeefZaakdocumentLezen-EDC-vraagSelectie'](
                        entiteittype='EDC',
                        identificatie=document.informatieobjectidentificatie,
                    )

                )

            response_root = etree.fromstring(response.content)
            response_berichtcode = response_root.xpath(
                '//zkn:stuurgegevens/stuf:berichtcode',
                namespaces=self.nsmap
            )[0].text
            self.assertEqual(response_berichtcode, BerichtcodeChoices.la01, response.content)

            response_object_element = response_root.xpath('//zkn:antwoord/zkn:object', namespaces=self.nsmap)[0]
            response_edc_identificatie = response_object_element.xpath('zkn:identificatie', namespaces=self.nsmap)[0].text

            self.assertEqual(response_edc_identificatie, document.informatieobjectidentificatie)


class geefZaakdocumentLezen_EdcLa01Tests(DMSMockMixin, BaseSoapTests):
    antwoord_xpath = '/soap11env:Envelope/soap11env:Body/zds:geefZaakdocumentLezen_EdcLa01'

    def setUp(self):
        super().setUp()
        # also creates the zaak folder in the DMS
        self.zaak = ZaakFactory.create(status_set__indicatie_laatst_gezette_status=JaNee.ja)
        # setup a file in the DMS
        self.document = EnkelvoudigInformatieObjectFactory.create(
            titel='doc 1',
            informatieobjectidentificatie='12345',
            bronorganisatie='6789',
        )
        self.assertEqual(self.document.identificatie, '123456789')

    def _do_simple_request(self, **options):
        client = self._get_client('BeantwoordVraag')
        stuf_factory, zkn_factory, zds_factory = self._get_type_factories(client)

        with client.options(**options):
            return client.service.geefZaakdocumentLezen_EdcLv01(
                stuurgegevens=stuf_factory['EDC-StuurgegevensLv01'](
                    berichtcode='Lv01',
                    entiteittype='EDC',
                ),
                parameters=stuf_factory['EDC-parametersVraagSynchroon'](
                    sortering=1,
                    indicatorVervolgvraag=False
                ),
                scope={
                    'object': zkn_factory['GeefZaakdocumentLezen-EDC-vraagScope'](**{
                        'entiteittype': 'EDC',
                        'identificatie': Nil,  # v
                        'isRelevantVoor': zkn_factory['GeefZaakdocumentLezen-EDCZAK-vraagScope'](
                            entiteittype='EDCZAK',
                            # NOTE: the example WSDL specifies gerelateerdeVraagScope
                            gerelateerde=zkn_factory['GeefZaakdocumentLezen-ZAK-gerelateerdeVraagScope'](
                                entiteittype='ZAK',
                                identificatie=Nil  # v
                            )
                        ),
                        # 'dct.omschrijving': Nil,
                        # 'dct.category': Nil,
                        'titel': Nil,
                        'creatiedatum': Nil,
                        # 'ontvangstdatum': Nil,
                        # 'beschrijving': Nil,
                        # 'verzenddatum': Nil,
                        'vertrouwelijkAanduiding': Nil,
                        'auteur': Nil,
                        'formaat': Nil,
                        'taal': Nil,
                        # 'versie': Nil,
                        # 'status': Nil,
                        'inhoud': Nil,
                        # 'link': Nil,
                    })
                },
                gelijk=zkn_factory['GeefZaakdocumentLezen-EDC-vraagSelectie'](
                    entiteittype='EDC',
                    identificatie=self.document.informatieobjectidentificatie,
                )
            )

    def test_read_file_dms(self):
        """
        Assert that files are correctly read from the DMS.

        Setup a file in the DMS for ``self.zaak``, and then make a service call.
        Verify in the response that the binary content matches the uploaded file.
        """
        ZaakInformatieObjectFactory.create(zaak=self.zaak, informatieobject=self.document)
        self._dms_client.geef_inhoud.return_value = ('doc 1', BytesIO(b'foobarbaz'))

        response = self._do_simple_request(raw_response=True)

        root = etree.fromstring(response.content)
        body_root = self._get_body_root(root)
        inhoud = body_root.xpath('zkn:antwoord/zkn:object/zkn:inhoud', namespaces=self.nsmap)[0]
        self.assertEqual(
            inhoud.text,
            base64.b64encode(b'foobarbaz').decode('utf-8')
        )
        self.assertEqual(inhoud.attrib['{{{}}}bestandsnaam'.format(STUF_XML_NS)], 'doc 1')
        self._dms_client.geef_inhoud.assert_called_once_with(self.document)

    def test_namespace_response(self):
        """
        Verify that the namespace of the response is as expected.
        """
        self._dms_client.geef_inhoud.return_value = ('doc 1', BytesIO(b'foobarbaz'))
        result = self._do_simple_request(raw_response=True)
        root = etree.fromstring(result.content)
        namespaces = {ns for el in root.iterdescendants() for ns in el.nsmap.values()}

        self.assertIn('http://www.egem.nl/StUF/sector/zkn/0310', namespaces)
        self.assertIn('http://www.egem.nl/StUF/StUF0301', namespaces)
        self.assertIn('http://www.stufstandaarden.nl/koppelvlak/zds0120', namespaces)

    def test_root_element(self):
        """
        Test that the root element in soapenv:Body is called geefZaakdocumentLezen_EdcLa01
        and has the namespace 'http://www.stufstandaarden.nl/koppelvlak/zds0120'
        """
        self._dms_client.geef_inhoud.return_value = ('empty', BytesIO())

        result = self._do_simple_request(raw_response=True)

        root = etree.fromstring(result.content)
        self._assert_xpath_results(root, self.antwoord_xpath, 1, namespaces=self.nsmap)

    def test_stuurgegevens_element(self):
        """
        Test that in the geefLijstZaakdocumenten_ZakLa01 element there is an element
        called stuurgegevens which has the namespace 'http://www.egem.nl/StUF/sector/zkn/0310'
        """
        self._dms_client.geef_inhoud.return_value = ('empty', BytesIO())

        result = self._do_simple_request(raw_response=True)

        root = etree.fromstring(result.content)
        self._assert_xpath_results(self._get_body_root(root), 'zkn:stuurgegevens', 1, namespaces=self.nsmap)
        self._assert_xpath_results(
            self._get_body_root(root), 'zkn:stuurgegevens/stuf:berichtcode[text()="La01"]',
            1, namespaces=self.nsmap
        )
        self._assert_xpath_results(
            self._get_body_root(root), 'zkn:stuurgegevens/stuf:entiteittype[text()="EDC"]',
            1, namespaces=self.nsmap
        )

    def test_antwoord_element(self):
        """
        Test that in the geefLijstZaakdocumenten_ZakLa01 element there is an element
        called antwoord which has the namespace 'http://www.egem.nl/StUF/sector/zkn/0310'
        """
        self._dms_client.geef_inhoud.return_value = ('empty', BytesIO())

        result = self._do_simple_request(raw_response=True)

        root = etree.fromstring(result.content)
        self._assert_xpath_results(self._get_body_root(root), 'zkn:antwoord', 1, namespaces=self.nsmap)

    def test_object_element(self):
        """
        Test that in the antwoord element there is an element
        called object which has the namespace 'http://www.egem.nl/StUF/sector/zkn/0310'
        """
        self._dms_client.geef_inhoud.return_value = ('empty', BytesIO())

        result = self._do_simple_request(raw_response=True)

        root = etree.fromstring(result.content)
        self._assert_xpath_results(self._get_body_root(root), 'zkn:antwoord/zkn:object', 1, namespaces=self.nsmap)

    def test_entiteittype_attribute(self):
        """
        Test that the object element has an attribute entiteittype and has the
        namespace 'http://www.egem.nl/StUF/StUF0301'
        """
        self._dms_client.geef_inhoud.return_value = ('empty', BytesIO())

        result = self._do_simple_request(raw_response=True)

        root = etree.fromstring(result.content)
        self._assert_xpath_results(
            self._get_body_root(root), 'zkn:antwoord/zkn:object[@stuf:entiteittype]',
            1, namespaces=self.nsmap
        )

    def test_gerelateerde(self):
        """
        Test that the related zaken are returned.
        """
        self._dms_client.geef_inhoud.return_value = ('empty', BytesIO())
        zaak2 = ZaakFactory.create(status_set__indicatie_laatst_gezette_status=JaNee.ja)
        ZaakInformatieObjectFactory.create(zaak=self.zaak, informatieobject=self.document)
        ZaakInformatieObjectFactory.create(zaak=zaak2, informatieobject=self.document)

        response = self._do_simple_request(raw_response=True)

        root = etree.fromstring(response.content)
        body_root = self._get_body_root(root)
        self._assert_xpath_results(
            body_root, 'zkn:antwoord/zkn:object/zkn:isRelevantVoor',
            2, namespaces=self.nsmap
        )

        self._assert_xpath_results(
            body_root,
            'zkn:antwoord/zkn:object/zkn:isRelevantVoor/zkn:gerelateerde/zkn:identificatie[text()="{}"]'.format(
                self.zaak.zaakidentificatie),
            1,
            namespaces=self.nsmap
        )

        self._assert_xpath_results(
            body_root,
            'zkn:antwoord/zkn:object/zkn:isRelevantVoor/zkn:gerelateerde/zkn:identificatie[text()="{}"]'.format(
                zaak2.zaakidentificatie),
            1,
            namespaces=self.nsmap
        )


class STPgeefZaakdocumentlezen_EdcLv01Tests(DMSMockMixin, BaseTestPlatformTests):
    """
    Precondities:
    Scenario's voegZaakdocumentToe (P), maakZaakdocument (P) en updateZaakdocument (P) zijn succesvol uitgevoerd.

    Dit scenario bevraagt documenten die in scenario's voegZaakdocumentToe (P) en maakZaakdocument (P)
    zijn toegevoegd en (deels) in scenario updateZaakdocument (P) zijn gewijzigd.
    """
    porttype = 'BeantwoordVraag'
    maxDiff = None
    test_files_subfolder = 'stp_geefZaakdocumentlezen'

    def setUp(self):
        super().setUp()

        self._dms_client.geef_inhoud.return_value = ('doc 1', BytesIO())

        self.document = EnkelvoudigInformatieObjectFactory.create()
        self.zaak = ZaakFactory.create(status_set__indicatie_laatst_gezette_status=JaNee.ja)
        ZaakInformatieObjectFactory.create(zaak=self.zaak, informatieobject=self.document)

    def _test_response(self, response):
        self.assertEquals(response.status_code, 200, response.content)

        response_root = etree.fromstring(response.content)
        response_berichtcode = response_root.xpath(
            '//zkn:stuurgegevens/stuf:berichtcode',
            namespaces=self.nsmap
        )[0].text
        self.assertEqual(response_berichtcode, BerichtcodeChoices.la01, response.content)

        response_object_element = response_root.xpath('//zkn:antwoord/zkn:object', namespaces=self.nsmap)[0]
        response_edc_identificatie = response_object_element.xpath('zkn:identificatie', namespaces=self.nsmap)[0].text

        self.assertEqual(response_edc_identificatie, self.document.informatieobjectidentificatie)

    def test_geefLijstZaakdocumentenlezen_EdcLv01_01(self):
        vraag = 'geefZaakdocumentLezen_EdcLv01_01.xml'
        context = {
            'voegzaakdocumenttoe_identificatie_1': self.document.informatieobjectidentificatie,
        }
        response = self._do_request(self.porttype, vraag, context)

        self._test_response(response)

    def test_geefLijstZaakdocumentenlezen_EdcLv01_03(self):
        vraag = 'geefZaakdocumentLezen_EdcLv01_03.xml'
        context = {
            'voegzaakdocumenttoe_identificatie_1': self.document.informatieobjectidentificatie,
        }
        response = self._do_request(self.porttype, vraag, context)

        self._test_response(response)

    def test_geefLijstZaakdocumentenlezen_EdcLv01_05(self):
        vraag = 'geefZaakdocumentLezen_EdcLv01_05.xml'
        context = {
            'voegzaakdocumenttoe_identificatie_1': self.document.informatieobjectidentificatie,
        }
        response = self._do_request(self.porttype, vraag, context)

        self._test_response(response)

    def test_geefLijstZaakdocumentenlezen_EdcLv01_07(self):
        vraag = 'geefZaakdocumentLezen_EdcLv01_07.xml'
        context = {
            'voegzaakdocumenttoe_identificatie_1': self.document.informatieobjectidentificatie,
        }
        response = self._do_request(self.porttype, vraag, context)

        self._test_response(response)

    def test_geefLijstZaakdocumentenlezen_EdcLv01_09(self):
        vraag = 'geefZaakdocumentLezen_EdcLv01_09.xml'
        context = {
            'voegzaakdocumenttoe_identificatie_3': self.document.informatieobjectidentificatie,
        }
        response = self._do_request(self.porttype, vraag, context)

        self._test_response(response)

    def test_geefLijstZaakdocumentenlezen_EdcLv01_11(self):
        vraag = 'geefZaakdocumentLezen_EdcLv01_11.xml'
        context = {
            'maakzaakdocument_identificatie_1': self.document.informatieobjectidentificatie,
        }
        response = self._do_request(self.porttype, vraag, context)

        self._test_response(response)

    def test_geefLijstZaakdocumentenlezen_EdcLv01_13(self):
        vraag = 'geefZaakdocumentLezen_EdcLv01_13.xml'
        context = {
            'voegzaakdocumenttoe_identificatie_5': self.document.informatieobjectidentificatie,
        }

        response = self._do_request(self.porttype, vraag, context)

        self._test_response(response)


class geefZaakdocumentLezen_EdcLv01RegressionTests(DMSMockMixin, BaseTestPlatformTests):
    test_files_subfolder = 'maykin_geefZaakdocumentLezen'
    porttype = 'BeantwoordVraag'

    def setUp(self):
        super().setUp()

        self._dms_client.geef_inhoud.return_value = ('doc 1', BytesIO())

    @override_settings(ZAAKMAGAZIJN_SYSTEEM={'organisatie': '0392', 'applicatie': 'SoapUI', 'administratie': 'test', 'gebruiker': 'David'})
    def test_empty_result_error(self):
        """
        See: https://taiga.maykinmedia.nl/project/haarlem-zaakmagazijn/issue/378
        """
        document = EnkelvoudigInformatieObjectFactory.create(
            informatieobjectidentificatie='03923185840f-7268-44a6-95ba-085c385b0544'
        )
        zaak = ZaakFactory.create(status_set__indicatie_laatst_gezette_status=JaNee.ja)
        ZaakInformatieObjectFactory.create(zaak=zaak, informatieobject=document)

        vraag = 'geefZaakdocumentLezen_EdcLv01_taiga378.xml'
        response = self._do_request(self.porttype, vraag)

        self.assertEquals(response.status_code, 200, response.content)

        response_root = etree.fromstring(response.content)
        response_berichtcode = response_root.xpath(
            '//zkn:stuurgegevens/stuf:berichtcode',
            namespaces=self.nsmap
        )[0].text
        self.assertEqual(response_berichtcode, BerichtcodeChoices.la01, response.content)

        response_object_element = response_root.xpath('//zkn:antwoord/zkn:object', namespaces=self.nsmap)[0]
        response_edc_identificatie = response_object_element.xpath('zkn:identificatie', namespaces=self.nsmap)[0].text

        self.assertEqual(response_edc_identificatie, document.informatieobjectidentificatie)

    @override_settings(ZAAKMAGAZIJN_SYSTEEM={'organisatie': '0392', 'applicatie': 'ZSH', 'administratie': '', 'gebruiker': ''})
    def test_sortering_error(self):
        """
        See: https://taiga.maykinmedia.nl/project/haarlem-zaakmagazijn/issue/399
        """
        document = EnkelvoudigInformatieObjectFactory.create(
            informatieobjectidentificatie='03928623fcfc-86dc-473a-859f-3a6cec2795f3'
        )
        zaak = ZaakFactory.create(status_set__indicatie_laatst_gezette_status=JaNee.ja)
        ZaakInformatieObjectFactory.create(zaak=zaak, informatieobject=document)

        vraag = 'geefZaakdocumentLezen_EdcLv01_taiga399.xml'
        response = self._do_request(self.porttype, vraag)

        self.assertEquals(response.status_code, 200, response.content)

        response_root = etree.fromstring(response.content)
        response_berichtcode = response_root.xpath(
            '//zkn:stuurgegevens/stuf:berichtcode',
            namespaces=self.nsmap
        )[0].text
        self.assertEqual(response_berichtcode, BerichtcodeChoices.la01, response.content)

        response_object_element = response_root.xpath('//zkn:antwoord/zkn:object', namespaces=self.nsmap)[0]
        response_zak_identificatie = response_object_element.xpath('zkn:isRelevantVoor/zkn:gerelateerde/zkn:identificatie', namespaces=self.nsmap)[0].text

        self.assertEqual(response_zak_identificatie, zaak.zaakidentificatie)

    @override_settings(ZAAKMAGAZIJN_SYSTEEM={'organisatie': '0392', 'applicatie': 'SoapUI', 'administratie': 'test', 'gebruiker': 'David'})
    def test_scope_alles_met_generiek_doc_type(self):
        """
        See: https://taiga.maykinmedia.nl/project/haarlem-zaakmagazijn/issue/419
        """
        dct_generiek = InformatieObjectTypeOmschrijvingGeneriekFactory.create()
        dct = InformatieObjectTypeFactory.create(
            informatieobjecttypeomschrijving_generiek=dct_generiek
        )
        document = EnkelvoudigInformatieObjectFactory.create(
            informatieobjectidentificatie='03923185840f-7268-44a6-95ba-085c385b0544',
            informatieobjecttype=dct,
        )
        zaak = ZaakFactory.create(status_set__indicatie_laatst_gezette_status=JaNee.ja)
        ZaakInformatieObjectFactory.create(zaak=zaak, informatieobject=document)

        vraag = 'geefZaakdocumentLezen_EdcLv01_taiga419.xml'
        response = self._do_request(self.porttype, vraag)

        self.assertEquals(response.status_code, 200, response.content)

        response_root = etree.fromstring(response.content)
        response_berichtcode = response_root.xpath(
            '//zkn:stuurgegevens/stuf:berichtcode',
            namespaces=self.nsmap
        )[0].text
        self.assertEqual(response_berichtcode, BerichtcodeChoices.la01, response.content)

        print(response.content)

        response_object_element = response_root.xpath('//zkn:antwoord/zkn:object', namespaces=self.nsmap)[0]
        response_edc_identificatie = response_object_element.xpath('zkn:identificatie', namespaces=self.nsmap)[0].text

        self.assertEqual(response_edc_identificatie, document.informatieobjectidentificatie)
