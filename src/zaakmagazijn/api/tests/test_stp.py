from os import path
from unittest import skip

from django.core.management import call_command
from django.test import override_settings

from lxml import etree

from .base import BaseTestPlatformTests


class DMSMockMixin:
    extra_client_mocks = [
        'zaakmagazijn.cmis.fields.dms_client',
        'zaakmagazijn.api.services.maak_zaakdocument.dms_client',
        'zaakmagazijn.api.services.voeg_zaakdocument_toe.dms_client',
    ]

    @property
    def _dms_client(self):
        return self._extra_mocked_dms_clients[0]

    @property
    def _service_dms_client(self):
        return self._extra_mocked_dms_clients[1]


@skip('The StUF testplatform currently has too many inconsistencies to run these.')
class STPFull(BaseTestPlatformTests):
    """
    Try to emulate the STP as much as possible.
    """

    def setUp(self):
        super().setUp()
        self.context = {
            'tijdstipBericht': self.genereerdatumtijd(),  # genereerdatumtijd(0, "yyyyMMddHHmmss")

            'zenderOrganisatie': 'KING',
            'zenderApplicatie': 'STP',
            'ontvangerOrganisatie': 'ORG',
            'ontvangerApplicatie': 'TTA',

            'gemeentecode': '1234',
            'referentienummer': self.genereerID(10, "Numeriek"),

            'datumEergisteren': self.genereerdatum(-2),  # genereerdatumtijd(2, "yyyyMMdd")
            'datumGisteren': self.genereerdatum(-1),
            'datumVandaag': self.genereerdatum(),  # genereerdatumtijd(0, "yyyyMMdd")
            'tijdstipRegistratie': self.genereerdatumtijd(),

            'zds_zaaktype_omschrijving': 'Aanvraag burgerservicenummer behandelen',
            'zds_zaaktype_datum': '20171001',
            'zds_zaaktype_code': '12345678',

            # creeer volgnummer 01
            'genereerbesluitident_identificatie_2': '123',
            'genereerzaakident_identificatie_2': self.genereerID(10),

            # creeer volgnummer 03
            'genereerzaakident_identificatie_4': self.genereerID(10),
            # creeer volgnummer 05
            'genereerzaakident_identificatie_6': self.genereerID(10),
            # creeer volgnummer 07
            'creerzaak_identificatie_7': self.genereerID(10, "Numeriek"),  # 1234creeer_id7
            # creeer volgnummer 09
            'creerzaak_identificatie_9': self.genereerID(10, "Numeriek"),  # 1234creeer_id9
            # creeer volgnummer 11
            'creerzaak_identificatie_11': self.genereerID(10, "Numeriek"),  # 1234creeer_id11
            # creeer volgnummer 13
            'creerzaak_identificatie_13': self.genereerID(10, "Numeriek"),  # 1234creeer_id13

            # actualiseerZaakstatus
            'datumStatusGezet': self.genereerdatumtijd(),

            # Maak zaak document
            'maakzaakdocument_identificatie_1': self.genereerID(10, "Numeriek"),
            'maakzaakdocument_identificatie_3': self.genereerID(10, "Numeriek"),
            'maakzaakdocument_identificatie_5': self.genereerID(10, "Numeriek"),

            'voegzaakdocumenttoe_identificatie_1': self.genereerID(10, "Numeriek"),
            'voegzaakdocumenttoe_identificatie_3': self.genereerID(10, "Numeriek"),
            'voegzaakdocumenttoe_identificatie_5': self.genereerID(10, "Numeriek"),
            'voegzaakdocumenttoe_identificatie_7': self.genereerID(10, "Numeriek"),
            'voegzaakdocumenttoe_identificatie_9': self.genereerID(10, "Numeriek"),

            'zds_zaakstatus_code': '12345678',
            'zds_zaakstatus_omschrijving': 'Intake afgerond',
            'zds_zaakstatus_datum': '20170901',

            'zds_zaakstatus_code_2': '87651234',
            'zds_zaakstatus_omschrijving_2': 'Afgerekend',
            'zds_zaakstatus_datum2': '20170902',

            'zds_zaakstatus_code_3': '78563412',
            'zds_zaakstatus_omschrijving_3': 'Product opgesteld',
            'zds_zaakstatus_datum3': '20170903',

            'zds_zaakstatus_code_4': '87126534',
            'zds_zaakstatus_omschrijving_4': 'Zaak afgerond',
            'zds_zaakstatus_datum4': '20170904',

            'voegbesluittoe_identificatie_5': self.genereerID(10, "Numeriek"),  # 12345voegBSltoe_id5
            'voegbesluittoe_identificatie_7': self.genereerID(10, "Numeriek"),  # 12345voegBSltoe_id7
            'voegbesluittoe_identificatie_9': self.genereerID(10, "Numeriek"),
        }

        call_command('create_test_data')

    @override_settings(CMIS_CLIENT_CLASS='zaakmagazijn.cmis.client.DummyDMSClient')
    def test_zaak_document_services_1_2(self):
        genereer_zaak_identificatie_tests = [
            'genereerZaakIdentificatie_Di02_01.orig.xml',
            'genereerZaakIdentificatie_Di02_03.orig.xml',
            'genereerZaakIdentificatie_Di02_05.orig.xml',
            'genereerZaakIdentificatie_Di02_05.orig.xml',
        ]
        for file_name in genereer_zaak_identificatie_tests:
            self._validate_response(self._do_request('VerwerkSynchroonVrijBericht', path.join('stp_genereerZaakIdentificatie', file_name), self.context, stp_syntax=True))

        creeer_zaak_tests = [
            'creeerZaak_ZakLk01_01.orig.xml',
            'creeerZaak_ZakLk01_03.orig.xml',
            'creeerZaak_ZakLk01_05.orig.xml',
            'creeerZaak_ZakLk01_07.orig.xml',
            'creeerZaak_ZakLk01_09.orig.xml',
            'creeerZaak_ZakLk01_11.orig.xml',
            'creeerZaak_ZakLk01_13.orig.xml',
        ]
        for file_name in creeer_zaak_tests:
            self._validate_response(self._do_request('OntvangAsynchroon', path.join('stp_creeerZaak', file_name), self.context, stp_syntax=True))

        genereer_document_identificatie_tests = [
            'genereerDocumentIdentificatie_Di02.orig.xml',
        ]
        for file_name in genereer_document_identificatie_tests:
            self._validate_response(self._do_request('VerwerkSynchroonVrijBericht', path.join('stp_genereerDocumentIdentificatie', file_name), self.context, stp_syntax=True))

        maak_zaak_document_tests = [
            'maakZaakdocument_EdcLk01_01.orig.xml',
            'maakZaakdocument_EdcLk01_03.orig.xml',
            'maakZaakdocument_EdcLk01_05.orig.xml',
        ]
        for file_name in maak_zaak_document_tests:
            self._validate_response(self._do_request('OntvangAsynchroon', path.join('stp_maakZaakdocument', file_name), self.context, stp_syntax=True))

        voeg_zaak_document_toe_tests = [
            'voegZaakdocumentToe_EdcLk01_01.orig.xml',
            'voegZaakdocumentToe_EdcLk01_03.orig.xml',
            'voegZaakdocumentToe_EdcLk01_05.orig.xml',
            'voegZaakdocumentToe_EdcLk01_07.orig.xml',
            'voegZaakdocumentToe_EdcLk01_09.orig.xml',
        ]
        for file_name in voeg_zaak_document_toe_tests:
            self._validate_response(self._do_request('OntvangAsynchroon', path.join('stp_voegZaakdocumentToe', file_name), self.context, stp_syntax=True))

        update_zaak_tests = [
            'updateZaak_ZakLk01_01.orig.xml',
            'updateZaak_ZakLk01_03.orig.xml',
            'updateZaak_ZakLk01_05.orig.xml',
            'updateZaak_ZakLk01_07.orig.xml',
        ]
        for file_name in update_zaak_tests:
            self._validate_response(self._do_request('OntvangAsynchroon', path.join('stp_updateZaak', file_name), self.context, stp_syntax=True))

        actualiseer_zaak_status_tests = [
            'actualiseerZaakstatus_ZakLk01_01.orig.xml',
            'actualiseerZaakstatus_ZakLk01_03.orig.xml',
            'actualiseerZaakstatus_ZakLk01_05.orig.xml',
            'actualiseerZaakstatus_ZakLk01_07.orig.xml',
        ]
        for file_name in actualiseer_zaak_status_tests:
            self._validate_response(self._do_request('OntvangAsynchroon', path.join('stp_actualiseerZaakstatus', file_name), self.context, stp_syntax=True), msg=file_name)

        genereer_besluit_identificatie_tests = [
            'genereerBesluitIdentificatie_Di02.orig.xml',
        ]
        for file_name in genereer_besluit_identificatie_tests:
            self._validate_response(self._do_request('VerwerkSynchroonVrijBericht', path.join('stp_genereerBesluitIdentificatie', file_name), self.context, stp_syntax=True), msg=file_name)

        voeg_besluit_toe_tests = [
            'voegBesluitToe_Di01_01.orig.xml',
            'voegBesluitToe_Di01_03.orig.xml',
            'voegBesluitToe_Di01_05.orig.xml',
            'voegBesluitToe_Di01_07.orig.xml',
            'voegBesluitToe_Di01_09.orig.xml',
        ]
        for file_name in voeg_besluit_toe_tests:
            self._validate_response(self._do_request('OntvangAsynchroon', path.join('stp_voegBesluitToe', file_name), self.context, stp_syntax=True), msg=file_name)

        update_besluit_tests = [
            'updateBesluit_BslLk01_1.orig.xml',
            'updateBesluit_BslLk01_3.orig.xml',
            'updateBesluit_BslLk01_5.orig.xml',
        ]
        for file_name in update_besluit_tests:
            self._validate_response(self._do_request('OntvangAsynchroon', path.join('stp_updateBesluit', file_name), self.context, stp_syntax=True), msg=file_name)

        geef_zaak_status_tests = [
            'geefZaakstatus_ZakLv01_01.orig.xml',
            'geefZaakstatus_ZakLv01_03.orig.xml',
            'geefZaakstatus_ZakLv01_05.orig.xml',
        ]
        for file_name in geef_zaak_status_tests:
            self._validate_response(self._do_request('BeantwoordVraag', path.join('stp_geefZaakstatus', file_name), self.context, stp_syntax=True), msg=file_name)

        geef_zaak_details_tests = [
            ('geefZaakdetails_ZakLv01_01.orig.xml', 'geefZaakdetails_ZakLa01_02.orig.xml'),
            ('geefZaakdetails_ZakLv01_03.orig.xml', 'geefZaakdetails_ZakLa01_04.orig.xml'),
            ('geefZaakdetails_ZakLv01_05.orig.xml', 'geefZaakdetails_ZakLa01_06.orig.xml'),
            ('geefZaakdetails_ZakLv01_07.orig.xml', 'geefZaakdetails_ZakLa01_08.orig.xml'),
            ('geefZaakdetails_ZakLv01_09.orig.xml', 'geefZaakdetails_ZakLa01_10.orig.xml'),
            ('geefZaakdetails_ZakLv01_11.orig.xml', 'geefZaakdetails_ZakLa01_12.orig.xml'),
            ('geefZaakdetails_ZakLv01_13.orig.xml', 'geefZaakdetails_ZakLa01_14.orig.xml'),
            ('geefZaakdetails_ZakLv01_15.orig.xml', 'geefZaakdetails_ZakLa01_16.orig.xml'),
        ]
        files_path = path.join(path.dirname(__file__), 'files')

        for file_name, example_file_name in geef_zaak_details_tests:
            response = self._do_request('BeantwoordVraag', path.join('stp_geefZaakdetails', file_name), self.context, stp_syntax=True)

            example_content = self._build_template(path.join('stp_geefZaakdetails', example_file_name), self.context, stp_syntax=True)

            response_tree = etree.fromstring(response.content)
            example_response_tree = etree.fromstring(example_content)

            # For unknown reasons 'identifcatie' fields aren't compared.
            self.xml_remove_element(response_tree, '//zkn:identificatie')
            self.xml_remove_element(example_response_tree, '//zkn:identificatie')

            self.assert_xml_equal(
                self.xml_get_element(response_tree, '//zkn:object'),
                self.xml_get_element(example_response_tree, '//zkn:object'),
                example_file_name
            )

            self._validate_response(response, msg=file_name)
