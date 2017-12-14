import os
from unittest import skipIf

from django.core.exceptions import FieldDoesNotExist
from django.test import TransactionTestCase

from cmislib.exceptions import ObjectNotFoundException

from zaakmagazijn.api.utils import create_unique_id
from zaakmagazijn.cmis.utils import get_cmis_object_id
from zaakmagazijn.utils import stuf_datetime
from zaakmagazijn.utils.fields import StUFDateField

from ...api.stuf.utils import get_model_field, get_model_value
from ...rgbz.choices import (
    InformatieObjectStatus, JaNee, Vertrouwelijkaanduiding
)
from ...rgbz.models import EnkelvoudigInformatieObject
from ...rgbz.tests.factory_models import StatusFactory, ZaakFactory
from ...utils.tests import on_jenkins, should_skip_cmis_tests
from ..choices import ChangeLogStatus, CMISObjectType
from ..client import CMISDMSClient
from ..models import ChangeLog

TEST_FILES_DIR = os.path.dirname(os.path.abspath(__file__))


def _cmis_stuf_datetime(value):
    return "{year}-{month}-{day}".format(
        year=value[0:4],
        month=value[4:6],
        day=value[6:8],
    )


@skipIf(on_jenkins() or should_skip_cmis_tests(), "Skipped while there's no Alfresco running on Jenkins")
class CMISClientTests(TransactionTestCase):

    def setUp(self):
        self.client = CMISDMSClient()
        self.addCleanup(self._removeTree)

        # Create zaak
        self.zaak = ZaakFactory.create(
            zaakidentificatie='123456789',
            einddatum=None,
        )
        StatusFactory.create(zaak=self.zaak, indicatie_laatst_gezette_status=JaNee.ja)

        # Create zaak folder
        self.client.creeer_zaakfolder(self.zaak)

    def _removeTree(self):
        """
        Remove the created Zaak root folder and all children from the DMS.
        """
        try:
            root_folder = self.client._repo.getObjectByPath('/Zaken')
        except ObjectNotFoundException:
            return
        root_folder.deleteTree()

    def _create_document(self, zaak, properties=None, title=None):
        """
        Simply creates a document in the DMS for given `zaak` with given `properties` and  title .

        :param zaak: The `Zaak` instance.
        :param properties: A `dict` with properties. If `None`, a set of default properties is used.
        :param titel: The title for the document. If `None`, the property "cmis:name" wil be taken.

        :return: A `tuple` of the `AtomPubDocument`, the `properties` used to create the document and the `title`.
        """
        zaakfolder = self.client._get_zaakfolder(zaak)
        if properties is None:
            properties = {
                # 'cmis:contentStreamFileName': 'volledige_bestandsnaam',
                # 'cmis:contentStreamMimeType': 'formaat',  # v
                'zsdms:documenttaal': 'Nederlands',
                'zsdms:documentLink': 'http://www.example.com',
                'cmis:name': 'Een titel',
                'zsdms:zaakidentificatie': zaak.zaakidentificatie,
                'zsdms:documentIdentificatie': create_unique_id(),
                'zsdms:documentcreatiedatum': _cmis_stuf_datetime(stuf_datetime.today()),
                'zsdms:documentontvangstdatum': _cmis_stuf_datetime(stuf_datetime.today()),
                'zsdms:documentbeschrijving': 'Een document omschrijving...',
                'zsdms:documentverzenddatum': _cmis_stuf_datetime(stuf_datetime.today()),
                'zsdms:vertrouwelijkaanduiding': Vertrouwelijkaanduiding.openbaar,
                'zsdms:documentauteur': 'John Doe',
                'zsdms:documentversie': '1.0',
                'zsdms:documentstatus': InformatieObjectStatus.in_bewerking,
                'zsdms:dct.omschrijving': 'iot omschrijving',
                # 'zsdms:dct.categorie': 'iot categorie',
            }

        if title is None:
            title = properties.get('cmis:name', 'no-name')

        properties['cmis:objectTypeId'] = CMISObjectType.edc
        doc = zaakfolder.createDocument(title, properties)
        return doc, properties, title

    def _make_zs_up_to_date(self):
        """
        Call this function to set the initial state of the ZS. It simply creates a `ChangeLog` entry as if the ZS was
        up to date with all changes in the DMS and any action after this would be seen as a change.
        """
        self.client._repo.reload()
        dms_change_log_token = int(self.client._repo.info['latestChangeLogToken'])
        ChangeLog.objects.create(token=dms_change_log_token, status=ChangeLogStatus.completed)

    def assertCorrectValues(self, edc, props):
        for dms_prop, field_name in EnkelvoudigInformatieObject.CMIS_MAPPING.items():
            try:
                model_field = get_model_field(edc.__class__, field_name)
            except FieldDoesNotExist:
                model_field = None
            model_value = get_model_value(edc, field_name)
            dms_value = props[dms_prop]
            if isinstance(model_field, StUFDateField):
                dms_value = dms_value.replace('-', '')

            self.assertEqual(
                model_value, dms_value,
                '{}="{}", expected "{}"'.format(field_name, model_value, dms_value)
            )

    def test_sync_no_changes(self):
        self._make_zs_up_to_date()
        self.assertEqual(ChangeLog.objects.count(), 1)

        result = self.client.sync()
        for action, count in result.items():
            self.assertEqual(count, 0, '{}={}, expected {}'.format(action, count, 0))

        self.assertEqual(ChangeLog.objects.count(), 2)
        self.assertEqual(ChangeLog.objects.last().token, ChangeLog.objects.first().token)

    def test_sync_updated_document(self):
        # Create document in the DMS and the ZS
        doc, props, title = self._create_document(self.zaak)
        self._make_zs_up_to_date()
        # Use doc.properties to include the CMIS objectId.
        object_id = get_cmis_object_id(doc.properties.get('cmis:objectId'))
        edc = EnkelvoudigInformatieObject.objects.create_from_cmis_properties(doc.properties, self.zaak, object_id)

        # Verify initial status
        self.assertEqual(ChangeLog.objects.count(), 1)
        self.assertEqual(EnkelvoudigInformatieObject.objects.count(), 1)

        # Update the document in the DMS.
        new_props = {
            'zsdms:vertrouwelijkaanduiding': Vertrouwelijkaanduiding.beperkt_openbaar,
            'zsdms:documentauteur': 'Jane Doe',
            'zsdms:documentversie': '2.0',
        }
        doc.updateProperties(new_props)

        # Sync
        self.client.sync()

        self.assertEqual(ChangeLog.objects.count(), 2)
        self.assertEqual(EnkelvoudigInformatieObject.objects.count(), 1)

        updated_props = props.copy()
        updated_props.update(new_props)

        edc = EnkelvoudigInformatieObject.objects.get()
        self.assertCorrectValues(edc, updated_props)

    def test_sync_deleted_document(self):
        # Create document in the DMS and the ZS
        doc, props, title = self._create_document(self.zaak)
        self._make_zs_up_to_date()
        # Use doc.properties to include the CMIS objectId.
        object_id = get_cmis_object_id(doc.properties.get('cmis:objectId'))
        EnkelvoudigInformatieObject.objects.create_from_cmis_properties(doc.properties, self.zaak, object_id)

        # Verify initial status
        self.assertEqual(ChangeLog.objects.count(), 1)
        self.assertEqual(EnkelvoudigInformatieObject.objects.count(), 1)

        # Delete the document from the DMS
        doc.delete()

        # Sync
        self.client.sync()

        self.assertEqual(ChangeLog.objects.count(), 2)
        # self.assertEqual(EnkelvoudigInformatieObject.objects.count(), 0)

    def test_sync_created_document(self):
        self._make_zs_up_to_date()

        # Verify initial status
        self.assertEqual(ChangeLog.objects.count(), 1)
        self.assertEqual(EnkelvoudigInformatieObject.objects.count(), 0)

        # Create document in the DMS
        doc, props, title = self._create_document(self.zaak)

        # Sync
        self.client.sync()

        # It's almost impossible to test the changelog itself, since Alfresco caches the changelog token and even a
        # reload doesn't refresh it.
        # for action, count in result.items():
        #     self.assertEqual(
        #         count, 0,
        #         '{}={}, expected {}'.format(action, count, 1 if action == CMISChangeType.created else 0)
        #     )

        self.assertEqual(ChangeLog.objects.count(), 2)
        self.assertEqual(EnkelvoudigInformatieObject.objects.count(), 1)

        edc = EnkelvoudigInformatieObject.objects.get()
        self.assertCorrectValues(edc, props)
