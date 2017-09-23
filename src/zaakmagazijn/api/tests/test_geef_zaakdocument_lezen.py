import base64
from io import BytesIO

from lxml import etree
from zeep.xsd.const import Nil

from zaakmagazijn.rgbz.choices import JaNee
from zaakmagazijn.rgbz.tests.factory_models import (
    EnkelvoudigInformatieObjectFactory, ZaakFactory,
    ZaakInformatieObjectFactory
)

from .base import BaseSoapTests


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

        client = self._get_client('Beantwoordvraag')
        stuf_factory, zkn_factory, zds_factory = self._get_type_factories(client)
        response = client.service.geefZaakdocumentLezen_EdcLv01(
            stuurgegevens=stuf_factory.EDC_StuurgegevensGeefZaakdocumentLezenLv01(
                berichtcode='Lv01',
                entiteittype='EDC',
            ),
            parameters=stuf_factory.EDC_parametersVraagSynchroon(
                sortering=1,
                indicatorVervolgvraag=False
            ),
            scope=zkn_factory.GeefZaakdocumentLezen_vraagScope(
                object=zkn_factory.GeefZaakdocumentLezen_EDC_vraagScope(**{
                    'identificatie': Nil,  # v
                    'isRelevantVoor': zkn_factory.GeefZaakdocumentLezen_EDCZAK_vraagScope(
                        # NOTE: the example WSDL specifies gerelateerdeVraagScope
                        gerelateerde=zkn_factory.GeefZaakdocumentLezen_ZAK_vraagScope(
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
            ),
            gelijk=zkn_factory.GeefZaakdocumentLezen_EDC_vraagSelectie(
                identificatie='123456789',
            )
        )
        self.assertEqual(len(response.antwoord.object), 1)
        self.assertEqual(len(response.antwoord.object[0].isRelevantVoor), 1)
        self.assertEqual(response.antwoord.object[0].identificatie, '123456789')
        self.assertEqual(response.antwoord.object[0].titel, 'doc 1')


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
        client = self._get_client('Beantwoordvraag')
        stuf_factory, zkn_factory, zds_factory = self._get_type_factories(client)

        with client.options(**options):
            return client.service.geefZaakdocumentLezen_EdcLv01(
                stuurgegevens=stuf_factory.EDC_StuurgegevensGeefZaakdocumentLezenLv01(
                    berichtcode='Lv01',
                    entiteittype='EDC',
                ),
                parameters=stuf_factory.EDC_parametersVraagSynchroon(
                    sortering=1,
                    indicatorVervolgvraag=False
                ),
                scope=zkn_factory.GeefZaakdocumentLezen_vraagScope(
                    object=zkn_factory.GeefZaakdocumentLezen_EDC_vraagScope(**{
                        'identificatie': Nil,  # v
                        'isRelevantVoor': zkn_factory.GeefZaakdocumentLezen_EDCZAK_vraagScope(
                            # NOTE: the example WSDL specifies gerelateerdeVraagScope
                            gerelateerde=zkn_factory.GeefZaakdocumentLezen_ZAK_vraagScope(
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
                ),
                gelijk=zkn_factory.GeefZaakdocumentLezen_EDC_vraagSelectie(
                    identificatie=self.document.identificatie,
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

        response = self._do_simple_request()

        root = etree.fromstring(response.content)
        body_root = self._get_body_root(root)
        inhoud = body_root.xpath('zkn:antwoord/zkn:object/zkn:inhoud', namespaces=self.nsmap)[0]
        self.assertEqual(
            inhoud.text,
            base64.b64encode(b'foobarbaz').decode('utf-8')
        )
        self.assertEqual(inhoud.attrib['bestandsnaam'], 'doc 1')
        self._dms_client.geef_inhoud.assert_called_once_with(self.document)

    def test_namespace_response(self):
        """
        Verify that the namespace of the response is as expected.
        """
        self._dms_client.geef_inhoud.return_value = ('empty', BytesIO())

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

        response = self._do_simple_request()

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
