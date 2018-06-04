import datetime

from django.test import override_settings

from freezegun import freeze_time
from lxml import etree

from zaakmagazijn.api.tests.base import BaseSoapTests
from zaakmagazijn.utils import stuf_datetime

from ..models import IncrementalYearId
from ..utils import create_incremental_year_id


class IncrementalYearIdTestCase(BaseSoapTests):

    def test_model_value(self):
        obj = IncrementalYearId.objects.create(year=2017, number=1)
        self.assertEqual(obj.value, '2017-0000001')

    @freeze_time(datetime.date(2015, 1, 1))
    def test_manager_create_unique(self):
        obj = IncrementalYearId.objects.create_unique()
        obj.refresh_from_db()

        self.assertEqual(obj.year, 2015)
        self.assertEqual(obj.number, 1)

    @freeze_time(datetime.date(2015, 1, 1))
    def test_manager_increment(self):
        IncrementalYearId.objects.create_unique()
        obj_2 = IncrementalYearId.objects.create_unique()
        obj_2.refresh_from_db()

        self.assertEqual(obj_2.year, 2015)
        self.assertEqual(obj_2.number, 2)

    @freeze_time(datetime.date(2017, 1, 1))
    def test_create_incremental_year_id(self):
        val = create_incremental_year_id()
        self.assertEqual(val, '2017-0000001')

    @freeze_time(datetime.date(2017, 1, 1))
    @override_settings(ZAAKMAGAZIJN_ZAAK_ID_GENERATOR='zaakmagazijn.contrib.idgenerator.utils.create_incremental_year_id')
    def test_service_request_create_incremental_year_id(self):
        client = self._get_client('VerwerkSynchroonVrijBericht')
        stuf_factory = client.type_factory('http://www.egem.nl/StUF/StUF0301')

        with client.options(raw_response=True):
            result = client.service.genereerZaakIdentificatie_Di02(
                stuurgegevens=stuf_factory['Di02-Stuurgegevens-gzi'](
                    berichtcode='Di02',
                    referentienummer='123',
                    tijdstipBericht=stuf_datetime.now(),
                    functie='genereerZaakidentificatie'
                )
            )

        response_root = etree.fromstring(result.content)
        response_identificatie = response_root.xpath('//zds:zaak/zkn:identificatie', namespaces=self.nsmap)[0].text

        self.assertEqual(response_identificatie, '2017-0000001')

    @freeze_time(datetime.date(2017, 1, 1))
    @override_settings(
        ZAAKMAGAZIJN_ZAAK_ID_GENERATOR='zaakmagazijn.contrib.idgenerator.utils.create_incremental_year_with_org_id',
        ZAAKMAGAZIJN_SYSTEEM={'organisatie': '0392', 'applicatie': 'ZSH', 'administratie': '', 'gebruiker': ''}
    )
    def test_service_request_create_incremental_year_with_org_id(self):
        client = self._get_client('VerwerkSynchroonVrijBericht')
        stuf_factory = client.type_factory('http://www.egem.nl/StUF/StUF0301')

        with client.options(raw_response=True):
            result = client.service.genereerZaakIdentificatie_Di02(
                stuurgegevens=stuf_factory['Di02-Stuurgegevens-gzi'](
                    berichtcode='Di02',
                    referentienummer='123',
                    tijdstipBericht=stuf_datetime.now(),
                    functie='genereerZaakidentificatie',
                    ontvanger={
                        'applicatie': 'ZSH',
                        'organisatie': '0392',
                    }
                )
            )

        response_root = etree.fromstring(result.content)
        response_identificatie = response_root.xpath('//zds:zaak/zkn:identificatie', namespaces=self.nsmap)[0].text

        self.assertEqual(response_identificatie, '0392-2017-0000001')

    @freeze_time(datetime.date(2017, 1, 1))
    @override_settings(
        ZAAKMAGAZIJN_ZAAK_ID_GENERATOR='zaakmagazijn.contrib.idgenerator.utils.create_incremental_year_with_org_id',
        ZAAKMAGAZIJN_SYSTEEM={'organisatie': '0392', 'applicatie': 'ZSH', 'administratie': '', 'gebruiker': ''}
    )
    def test_service_request_create_incremental_year_with_org_id_without_org(self):
        client = self._get_client('VerwerkSynchroonVrijBericht')
        stuf_factory = client.type_factory('http://www.egem.nl/StUF/StUF0301')

        with client.options(raw_response=True):
            result = client.service.genereerZaakIdentificatie_Di02(
                stuurgegevens=stuf_factory['Di02-Stuurgegevens-gzi'](
                    berichtcode='Di02',
                    referentienummer='123',
                    tijdstipBericht=stuf_datetime.now(),
                    functie='genereerZaakidentificatie',
                )
            )

        response_root = etree.fromstring(result.content)
        error_message = response_root.xpath('//stuf:Fo02Bericht/stuf:body/stuf:details', namespaces=self.nsmap)[0].text

        self.assertEqual(error_message, 'Ontvangende organisatie is verplicht in de stuurgegevens voor het genereren van identificaties.')
