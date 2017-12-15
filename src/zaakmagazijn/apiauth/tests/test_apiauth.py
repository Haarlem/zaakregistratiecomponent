import io
from contextlib import redirect_stdout

from django.conf import settings
from django.test import TestCase, override_settings

from lxml import etree
from zeep.xsd.const import Nil

from ...api.tests.base import BaseSoapTests
from ...rgbz.choices import JaNee
from ...rgbz.tests.factory_models import StatusFactory
from ..models import ServiceOperation
from ..signals import update_service_operations
from .factory_models import (
    ApplicationFactory, ApplicationGroupFactory, ServiceOperationFactory
)


class AuthorizationTests(BaseSoapTests):
    """
    Test the <zender> element to have access to the ZS.
    """

    def setUp(self):
        super().setUp()

        self.client = self._get_client('BeantwoordVraag', strict=False)

        self.status = StatusFactory.create(indicatie_laatst_gezette_status=JaNee.ja)
        self.zaak = self.status.zaak

    def _simple_request(self, zaak_id=None, zender=None, ontvanger=None):
        if zaak_id is None:
            zaak_id = self.zaak.zaakidentificatie
        if zender is None:
            zender = {
                'organisatie': 'Maykin Media',
                'applicatie': 'Test',
                'administratie': 'Support',
                'gebruiker': 'john.doe@example.com',
            }
        if ontvanger is None:
            ontvanger = settings.ZAAKMAGAZIJN_SYSTEEM

        with self.client.options(raw_response=True):
            stuf_factory, zkn_factory, zds_factory = self._get_type_factories(self.client)
            response = self.client.service.geefZaakstatus_ZakLv01(
                stuurgegevens=stuf_factory['ZAK-StuurgegevensLv01'](
                    berichtcode='Lv01',
                    entiteittype='ZAK',
                    zender=zender,
                    ontvanger=ontvanger,
                ),
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
                    identificatie=zaak_id,
                    heeft=zkn_factory['GeefZaakStatus-ZAKSTT-vraagSelectie'](
                        entiteittype='ZAKSTT',
                        indicatieLaatsteStatus=JaNee.ja,
                    )
                )
            )
        return etree.fromstring(response.content)

    def test_service_operations_created(self):
        service_operation = ServiceOperation.objects.filter(operation_name='geefZaakstatus_ZakLv01').first()
        self.assertIsNotNone(service_operation)

    @override_settings(ZAAKMAGAZIJN_OPEN_ACCESS=False)
    def test_unknown_sender(self):
        zender = {
            'organisatie': 'Maykin Media',
            'applicatie': 'Test',
            'administratie': 'Support',
            'gebruiker': 'john.doe@example.com',
        }

        application = ApplicationFactory.create(name=zender['applicatie'])
        group = ApplicationGroupFactory.create(name='No-Access')
        application.groups.add(group)

        xml = self._simple_request()

        fault_xpath = '*/soap11env:Fault/detail/stuf:Fo02Bericht/stuf:body/stuf:code[text()="StUF052"]'.format()
        self._assert_xpath_results(xml, fault_xpath, 1, namespaces=self.nsmap)

    @override_settings(ZAAKMAGAZIJN_OPEN_ACCESS=False)
    def test_not_authorized(self):
        xml = self._simple_request()

        fault_xpath = '*/soap11env:Fault/detail/stuf:Fo02Bericht/stuf:body/stuf:code[text()="StUF013"]'.format()
        self._assert_xpath_results(xml, fault_xpath, 1, namespaces=self.nsmap)

    @override_settings(ZAAKMAGAZIJN_OPEN_ACCESS=True)
    def test_open_access(self):
        xml = self._simple_request()

        fault_xpath = '/soap11env:Envelope/soap11env:Body/soap11env:Fault'
        self._assert_xpath_results(xml, fault_xpath, 0, namespaces=self.nsmap)

    @override_settings(ZAAKMAGAZIJN_OPEN_ACCESS=False)
    def test_authorized_sender(self):
        zender = {
            'organisatie': 'Maykin Media',
            'applicatie': 'Test',
            'administratie': 'Support',
            'gebruiker': 'john.doe@example.com',
        }

        service_operation = ServiceOperation.objects.filter(operation_name='geefZaakstatus_ZakLv01').first()

        application = ApplicationFactory.create(name=zender['applicatie'])
        group = ApplicationGroupFactory.create(name='Read-only')
        group.service_operations.add(service_operation)
        application.groups.add(group)

        xml = self._simple_request(zender=zender)

        fault_xpath = '/soap11env:Envelope/soap11env:Body/soap11env:Fault'
        self._assert_xpath_results(xml, fault_xpath, 0, namespaces=self.nsmap)

    @override_settings(ZAAKMAGAZIJN_OPEN_ACCESS=False)
    def test_unknown_recipient(self):
        ontvanger = {
            'organisatie': 'Maykin Media',
            'applicatie': 'Test',
            'administratie': 'Support',
            'gebruiker': 'john.doe@example.com',
        }

        service_operation = ServiceOperation.objects.filter(operation_name='geefZaakstatus_ZakLv01').first()

        application = ApplicationFactory.create(name='Test')
        group = ApplicationGroupFactory.create(name='Read-only')
        group.service_operations.add(service_operation)
        application.groups.add(group)

        xml = self._simple_request(ontvanger=ontvanger)

        fault_xpath = '*/soap11env:Fault/detail/stuf:Fo02Bericht/stuf:body/stuf:code[text()="StUF010"]'.format()
        self._assert_xpath_results(xml, fault_xpath, 1, namespaces=self.nsmap)


class ServiceOperationSignalTests(TestCase):

    def setUp(self):
        ServiceOperation.objects.all().delete()

    def _call_update_service_operations(self):
        f = io.StringIO()
        with redirect_stdout(f) as foo:
            update_service_operations(self)
        return foo.getvalue()

    def test_nothing_changed(self):
        self._call_update_service_operations()
        original_pks = list(ServiceOperation.objects.values_list('pk', flat=True))

        out = self._call_update_service_operations()
        current_pks = list(ServiceOperation.objects.values_list('pk', flat=True))

        self.assertEqual(out, '')
        self.assertListEqual(original_pks, current_pks)

    def test_create_service_operation(self):
        original_count = ServiceOperation.objects.count()
        self.assertEqual(original_count, 0)

        out = self._call_update_service_operations()
        current_count = ServiceOperation.objects.count()

        self.assertGreater(current_count, 0)
        self.assertIn('Service operations created: {}, removed: {}, total count: {}.'.format(
            current_count, 0, current_count
        ), out)

    def test_update_existing_service_operation(self):
        self._call_update_service_operations()
        original_pks = list(ServiceOperation.objects.values_list('pk', flat=True))

        ServiceOperation.objects.all().update(namespace='foobar')

        out = self._call_update_service_operations()
        current_pks = list(ServiceOperation.objects.exclude(namespace='foobar').values_list('pk', flat=True))

        self.assertEqual(out, '')
        self.assertListEqual(original_pks, current_pks)

    def test_delete_old_service_operation(self):
        ServiceOperationFactory.create()

        original_count = ServiceOperation.objects.count()
        self.assertEqual(original_count, 1)

        out = self._call_update_service_operations()
        current_count = ServiceOperation.objects.count()

        self.assertGreater(current_count, 0)
        self.assertIn('Service operations created: {}, removed: {}, total count: {}.'.format(
            current_count, 1, current_count
        ), out)
