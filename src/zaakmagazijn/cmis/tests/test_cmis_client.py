import base64
import os
from datetime import datetime
from io import BytesIO
from unittest import skipIf

from django.test import TestCase, override_settings

from cmislib.exceptions import ObjectNotFoundException, UpdateConflictException
from iso8601 import UTC
from spyne import File

from zaakmagazijn.api.stuf.models import BinaireInhoud
from zaakmagazijn.rgbz.choices import JaNee, Rolomschrijving
from zaakmagazijn.rgbz.tests.factory_models import (
    EnkelvoudigInformatieObjectFactory, NatuurlijkPersoonFactory, RolFactory,
    ZaakFactory
)
from zaakmagazijn.utils.tests import on_jenkins, should_skip_cmis_tests

from ..client import CMISDMSClient
from ..exceptions import (
    DocumentConflictException, DocumentExistsError, DocumentLockedException
)

TEST_FILES_DIR = os.path.dirname(os.path.abspath(__file__))


def _create_binaire_inhoud(binary_data, filename=None):
    inhoud = BinaireInhoud(
        data=File.Value(data=BytesIO(binary_data)),
        bestandsnaam=filename
    )
    return inhoud


def _stuffdate_to_datetime(value):
    year, month, day = value[0:4], value[4:6], value[6:8]
    return datetime(int(year), int(month), int(day)).replace(tzinfo=UTC)


class DMSMixin:
    def setUp(self):
        super().setUp()

        self.client = CMISDMSClient()
        self.addCleanup(lambda: self._removeTree('/Zaken'))
        self.addCleanup(lambda: self._removeTree('/Sites/archief/documentLibrary'))
        self.addCleanup(lambda: self._removeTree('/_temp'))
        self.addCleanup(lambda: self._removeTree('/Unfiled'))

    def _removeTree(self, path):
        try:
            root_folder = self.client._repo.getObjectByPath(path)
        except ObjectNotFoundException:
            return
        root_folder.deleteTree()

    def assertExpectedProps(self, obj, expected: dict):
        for prop, expected_value in expected.items():
            with self.subTest(prop=prop, expected_value=expected_value):
                self.assertEqual(obj.properties[prop], expected_value)


@skipIf(on_jenkins() or should_skip_cmis_tests(), "Skipped while there's no Alfresco running on Jenkins")
class CMISClientTests(DMSMixin, TestCase):
    def test_boomstructuur(self):
        """
        Test dat de boomstructuur Zaken -> Zaaktype -> Zaak gemaakt wordt.
        """
        with self.assertRaises(ObjectNotFoundException):
            self.client._repo.getObjectByPath('/Zaken')

        zaak = ZaakFactory.create(
            status_set__indicatie_laatst_gezette_status=JaNee.ja,
            zaakidentificatie='123456789',
            einddatum='20171231',
            zaaktype__zaaktypeidentificatie='998877',
            zaaktype__zaaktypeomschrijving='SOAP is leuk',
        )
        self.client.creeer_zaakfolder(zaak)

        # Zaken root folder
        root_folder = self.client._repo.getObjectByPath('/Zaken')

        children = [child for child in root_folder.getChildren()]
        self.assertEqual(len(children), 1)

        # zaaktype subfolder
        zaak_type_folder = children[0]
        self.assertEqual(
            zaak_type_folder.name,
            str(zaak.zaaktype.zaaktypeidentificatie)
        )
        self.assertExpectedProps(zaak_type_folder, {
            'cmis:objectTypeId': 'F:zsdms:zaaktype',
            'cmis:baseTypeId': 'cmis:folder',
            'cmis:path': '/Zaken/998877',
            'zsdms:Zaaktype-omschrijving': 'SOAP is leuk',
        })

        children = [child for child in zaak_type_folder.getChildren()]
        self.assertEqual(len(children), 1)

        # zaak subfolder
        zaak_folder = children[0]
        self.assertEqual(zaak_folder.name, '123456789')
        self.assertExpectedProps(zaak_folder, {
            'cmis:objectTypeId': 'F:zsdms:zaak',
            'cmis:baseTypeId': 'cmis:folder',
            'cmis:path': '/Zaken/998877/123456789',
            # 'zsdms:zaakidentificatie': '123456789',  # apparently, this is now in policies/aspects
            'zsdms:startdatum': _stuffdate_to_datetime(zaak.startdatum),
            'zsdms:einddatum': _stuffdate_to_datetime(zaak.einddatum),
            'zsdms:zaakniveau': None,  # TODO
            'zsdms:deelzakenindicatie': None,  # TODO
            'zsdms:registratiedatum': _stuffdate_to_datetime(zaak.registratiedatum),
            'zsdms:archiefnominatie': None,
            # 'zsdms:resultaattypeomschrijving': None,  # TODO
            'zsdms:datumVernietigDossier': None,
        })

    @override_settings(CMIS_UPLOAD_TO='zaakmagazijn.cmis.utils.upload_to_date_based')
    def test_boomstructuur_date_based(self):
        self.client = CMISDMSClient()
        self.assertEqual(self.client.upload_to.__name__, 'upload_to_date_based')

        zaak = ZaakFactory.create(
            status_set__indicatie_laatst_gezette_status=JaNee.ja,
            zaakidentificatie='123456789',
            startdatum='20170814',
            einddatum=None,
            zaaktype__zaaktypeidentificatie='998877',
            zaaktype__zaaktypeomschrijving='SOAP is leuk',
        )
        self.client.creeer_zaakfolder(zaak)

        # Zaken root folder
        root_folder = self.client._repo.getObjectByPath('/Sites/archief/documentLibrary')

        children = [child for child in root_folder.getChildren()]
        self.assertEqual(len(children), 1)

        # zaaktype subfolder
        zaak_type_folder = children[0]
        self.assertEqual(
            zaak_type_folder.name,
            str(zaak.zaaktype.zaaktypeidentificatie)
        )
        self.assertExpectedProps(zaak_type_folder, {
            'cmis:objectTypeId': 'F:zsdms:zaaktype',
            'cmis:baseTypeId': 'cmis:folder',
            'cmis:path': '/Sites/archief/documentLibrary/998877',
            'zsdms:Zaaktype-omschrijving': 'SOAP is leuk',
        })

        children = [child for child in zaak_type_folder.getChildren()]
        self.assertEqual(len(children), 1)

        # zaak subfolder
        date_folder = self.client._repo.getObjectByPath('/Sites/archief/documentLibrary/998877/2017/08/14/')
        children = [child for child in date_folder.getChildren()]
        self.assertEqual(len(children), 1)

        zaak_folder = children[0]
        self.assertEqual(zaak_folder.name, '123456789')
        self.assertExpectedProps(zaak_folder, {
            'cmis:objectTypeId': 'F:zsdms:zaak',
            'cmis:baseTypeId': 'cmis:folder',
            'cmis:path': '/Sites/archief/documentLibrary/998877/2017/08/14/123456789',
            # 'zsdms:zaakidentificatie': '123456789',  # apparently, this is now in policies/aspects
            'zsdms:startdatum': _stuffdate_to_datetime(zaak.startdatum),
            'zsdms:einddatum': None,
            'zsdms:zaakniveau': None,  # TODO
            'zsdms:deelzakenindicatie': None,  # TODO
            'zsdms:registratiedatum': _stuffdate_to_datetime(zaak.registratiedatum),
            'zsdms:archiefnominatie': None,
            # 'zsdms:resultaattypeomschrijving': None,  # TODO
            'zsdms:datumVernietigDossier': None,
        })

    def test_initiator_attributes_natuurlijk_persoon(self):
        zaak = ZaakFactory.create(
            status_set__indicatie_laatst_gezette_status=JaNee.ja,
            zaakidentificatie=123456789,
            einddatum=None,
            zaaktype__zaaktypeidentificatie=987654,
            zaaktype__zaaktypeomschrijving='SOAP is leuk',
        )
        np = NatuurlijkPersoonFactory.create(
            # nummer_ander_natuurlijk_persoon='anp 01',
            burgerservicenummer='135798642',
            naam_voorvoegsel_geslachtsnaam_voorvoegsel='van',
            naam_geslachtsnaam='Druten',
        )
        RolFactory.create(
            zaak=zaak,
            rolomschrijving=Rolomschrijving.initiator,
            betrokkene__vestiging=None,
            betrokkene=np
        )
        folder = self.client.creeer_zaakfolder(zaak)
        self.assertExpectedProps(folder, {
            # 'zsdms:voorvoegselGeslachtsnaam': 'van',
            # TODO [KING]: ZDS has plural version
            # 'zsdms:voorvoegselsGeslachtsnaam': 'van',
            # 'zsdms:geslachtsnaam': 'Druten',
            'zsdms:inp.bsn': '135798642',
            # 'zsdms:ann.identificatie': 'anp 01',
        })

    def test_maak_zaakdocument(self):
        """
        4.3.5.3 - test dat het aanmaken van een zaakdocument mogelijk is.
        """
        zaak = ZaakFactory.create(
            status_set__indicatie_laatst_gezette_status=JaNee.ja,
            zaakidentificatie='123456789',
            einddatum=None,
            zaaktype__zaaktypeidentificatie='998877',
            zaaktype__zaaktypeomschrijving='SOAP is leuk',
        )
        self.client.creeer_zaakfolder(zaak)

        document = EnkelvoudigInformatieObjectFactory.create(
            zaak=zaak,
            titel='testnaam',
            informatieobjectidentificatie='31415926535',
            ontvangstdatum='20170101',
            beschrijving='Een beschrijving',

        )
        cmis_doc = self.client.maak_zaakdocument(document, zaak)
        # no actual binary data is added
        # we have to set an (empty) stream, otherwise cmislib blocks us from setting/reading the stream
        # self.assertIsNone(cmis_doc.properties['cmis:contentStreamFileName'])

        # verify that it identifications are unique
        with self.assertRaises(DocumentExistsError):
            self.client.maak_zaakdocument(document, zaak)

        # verify expected props
        self.assertExpectedProps(cmis_doc, {
            # when no contentstreamfilename is provided, it is apparently set to the document name
            'cmis:contentStreamFileName': 'testnaam',
            # 'cmis:contentStreamId': None,
            'cmis:contentStreamLength': 0,  # because we created an empty object
            'cmis:contentStreamMimeType': 'application/binary',  # the default if it couldn't be determined
            # 'zsdms:dct.categorie': document.informatieobjecttype.informatieobjectcategorie,
            'zsdms:dct.omschrijving': document.informatieobjecttype.informatieobjecttypeomschrijving,
            'zsdms:documentIdentificatie': '31415926535',
            'zsdms:documentauteur': None,
            'zsdms:documentbeschrijving': 'Een beschrijving',
            'zsdms:documentcreatiedatum': _stuffdate_to_datetime(document.creatiedatum),
            # 'zsdms:documentformaat': None,
            'zsdms:documentLink': document.link,
            'zsdms:documentontvangstdatum': _stuffdate_to_datetime(document.ontvangstdatum),
            'zsdms:documentstatus': None,
            'zsdms:documenttaal': document.taal,
            'zsdms:documentversie': None,
            'zsdms:documentverzenddatum': None,
            'zsdms:vertrouwelijkaanduiding': None
        })

        document.refresh_from_db()
        self.assertEqual(
            document._object_id,
            cmis_doc.properties['cmis:objectId'].rsplit(';')[0]
        )

    def test_lees_document(self):
        """
        Ref #83: geefZaakdocumentLezen vraagt een kopie van het bestand op.

        Van het bestand uit het DMS wordt opgevraagd: inhoud, bestandsnaam.
        """
        zaak = ZaakFactory.create(status_set__indicatie_laatst_gezette_status=JaNee.ja)
        self.client.creeer_zaakfolder(zaak)
        document = EnkelvoudigInformatieObjectFactory.create(informatieobjectidentificatie='123456', zaak=zaak)
        cmis_doc = self.client.maak_zaakdocument(document, zaak)

        # empty by default
        filename, file_obj = self.client.geef_inhoud(document)

        self.assertEqual(filename, document.titel)
        self.assertEqual(file_obj.read(), b'')

        cmis_doc.setContentStream(BytesIO(b'some content'), 'text/plain')

        filename, file_obj = self.client.geef_inhoud(document)

        self.assertEqual(filename, document.titel)
        self.assertEqual(file_obj.read(), b'some content')

    def test_voeg_zaakdocument_toe(self):
        """
        4.3.4.3 Interactie tussen ZS en DMS

        Het ZS zorgt ervoor dat het document dat is aangeboden door de DSC wordt vastgelegd in het DMS.
        Hiervoor maakt het ZS gebruik van de CMIS-services die aangeboden worden door het DMS. Hierbij
        gelden de volgende eisen:
        - Het document wordt gerelateerd aan de juiste Zaakfolder (Zie 5.1)
        - Het document wordt opgeslagen als objecttype EDC (Zie 5.2)
        - Minimaal de vereiste metadata voor een EDC wordt vastgelegd in de daarvoor gedefinieerde
        objectproperties. In Tabel 3 is een mapping aangegeven tussen de StUF-ZKN-elementen en
        CMIS-objectproperties.
        """
        zaak = ZaakFactory.create(status_set__indicatie_laatst_gezette_status=JaNee.ja)
        document = EnkelvoudigInformatieObjectFactory.create(
            titel='testnaam', informatieobjectidentificatie='31415926535',
            beschrijving='Een beschrijving', zaak=zaak
        )
        self.client.maak_zaakdocument(document)
        document.refresh_from_db()

        result = self.client.zet_inhoud(document, BytesIO(b'some content'), content_type='text/plain')

        self.assertIsNone(result)
        filename, file_obj = self.client.geef_inhoud(document)
        self.assertEqual(file_obj.read(), b'some content')

    def test_relateer_aan_zaak(self):
        zaak = ZaakFactory.create(status_set__indicatie_laatst_gezette_status=JaNee.ja)
        document = EnkelvoudigInformatieObjectFactory.create(
            titel='testnaam', informatieobjectidentificatie='31415926535',
            beschrijving='Een beschrijving', zaak=zaak
        )
        zaak_folder = self.client.creeer_zaakfolder(zaak)
        self.client.maak_zaakdocument(document)
        document.refresh_from_db()

        result = self.client.relateer_aan_zaak(document, zaak)

        self.assertIsNone(result)
        cmis_doc = self.client._get_cmis_doc(document)
        parents = [parent.id for parent in cmis_doc.getObjectParents()]
        self.assertEqual(parents, [zaak_folder.id])

    def test_update_zaakdocument_only_props(self):
        zaak = ZaakFactory.create(
            status_set__indicatie_laatst_gezette_status=JaNee.ja,
            zaakidentificatie='123456789',
            einddatum=None,
            zaaktype__zaaktypeidentificatie='998877',
            zaaktype__zaaktypeomschrijving='SOAP is leuk',
        )
        self.client.creeer_zaakfolder(zaak)
        document = EnkelvoudigInformatieObjectFactory.create(
            titel='testnaam', informatieobjectidentificatie='31415926535',
            beschrijving='Een beschrijving', zaak=zaak
        )
        cmis_doc = self.client.maak_zaakdocument(document, zaak)
        # Update the document
        document.titel = 'nieuwe naam'
        document.beschrijving = 'Andere beschrijving'
        document.save()

        result = self.client.update_zaakdocument(document)

        self.assertIsNone(result)
        cmis_doc = cmis_doc.getLatestVersion()
        self.assertExpectedProps(
            cmis_doc, {
                'cmis:contentStreamLength': 0,
                'zsdms:documentIdentificatie': '31415926535',
                'cmis:versionSeriesCheckedOutId': None,
                'cmis:name': 'nieuwe naam',
                'zsdms:documentbeschrijving': 'Andere beschrijving',
            }
        )

    def test_update_zaakdocument_content(self):
        zaak = ZaakFactory.create(
            status_set__indicatie_laatst_gezette_status=JaNee.ja,
            zaakidentificatie='123456789',
            einddatum=None,
            zaaktype__zaaktypeidentificatie='998877',
            zaaktype__zaaktypeomschrijving='SOAP is leuk',
        )
        self.client.creeer_zaakfolder(zaak)
        document = EnkelvoudigInformatieObjectFactory.create(
            titel='testnaam', informatieobjectidentificatie='31415926535',
            beschrijving='Een beschrijving', zaak=zaak
        )
        cmis_doc = self.client.maak_zaakdocument(document, zaak)
        inhoud = _create_binaire_inhoud(b'leaky abstraction...', filename='andere bestandsnaam.txt')

        result = self.client.update_zaakdocument(document, inhoud=inhoud)

        self.assertIsNone(result)
        filename, content = self.client.geef_inhoud(document)
        self.assertEqual(filename, 'andere bestandsnaam.txt')
        self.assertEqual(content.read(), b'leaky abstraction...')

        cmis_doc = cmis_doc.getLatestVersion()
        self.assertExpectedProps(
            cmis_doc, {
                'cmis:contentStreamLength': 20,
                'zsdms:documentIdentificatie': '31415926535',
                'cmis:versionSeriesCheckedOutId': None,
                'cmis:name': 'andere bestandsnaam.txt',
            }
        )

    def test_update_checked_out_zaakdocument(self):
        zaak = ZaakFactory.create(
            status_set__indicatie_laatst_gezette_status=JaNee.ja,
            zaakidentificatie='123456789',
            einddatum=None,
            zaaktype__zaaktypeidentificatie='998877',
            zaaktype__zaaktypeomschrijving='SOAP is leuk',
        )
        self.client.creeer_zaakfolder(zaak)
        document = EnkelvoudigInformatieObjectFactory.create(
            titel='testnaam', informatieobjectidentificatie='31415926535',
            beschrijving='Een beschrijving', zaak=zaak
        )
        cmis_doc = self.client.maak_zaakdocument(document, zaak)
        cmis_doc.checkout()
        inhoud = _create_binaire_inhoud(b'leaky abstraction...', filename='andere bestandsnaam.txt')

        with self.assertRaises(DocumentConflictException):
            self.client.update_zaakdocument(document, inhoud=inhoud)

    def test_update_checked_out_zaakdocument_with_checkout_id(self):
        zaak = ZaakFactory.create(
            status_set__indicatie_laatst_gezette_status=JaNee.ja,
            zaakidentificatie='123456789',
            einddatum=None,
            zaaktype__zaaktypeidentificatie='998877',
            zaaktype__zaaktypeomschrijving='SOAP is leuk',
        )
        self.client.creeer_zaakfolder(zaak)
        document = EnkelvoudigInformatieObjectFactory.create(
            titel='testnaam', informatieobjectidentificatie='31415926535',
            beschrijving='Een beschrijving', zaak=zaak
        )
        cmis_doc = self.client.maak_zaakdocument(document, zaak)
        pwc = cmis_doc.checkout()
        pwc.reload()
        checkout_id = pwc.properties['cmis:versionSeriesCheckedOutId']
        inhoud = _create_binaire_inhoud(b'leaky abstraction...', filename='andere bestandsnaam.txt')

        result = self.client.update_zaakdocument(document, checkout_id=checkout_id, inhoud=inhoud)

        self.assertIsNone(result)
        filename, content = self.client.geef_inhoud(document)
        self.assertEqual(filename, 'andere bestandsnaam.txt')
        self.assertEqual(content.read(), b'leaky abstraction...')

        # check that it's checked in again
        new_pwc = cmis_doc.getPrivateWorkingCopy()
        self.assertIsNone(new_pwc)

    def test_update_checked_out_zaakdocument_with_incorrect_checkout_id(self):
        zaak = ZaakFactory.create(
            status_set__indicatie_laatst_gezette_status=JaNee.ja,
            zaakidentificatie='123456789',
            einddatum=None,
            zaaktype__zaaktypeidentificatie='998877',
            zaaktype__zaaktypeomschrijving='SOAP is leuk',
        )
        self.client.creeer_zaakfolder(zaak)
        document = EnkelvoudigInformatieObjectFactory.create(
            titel='testnaam', informatieobjectidentificatie='31415926535',
            beschrijving='Een beschrijving', zaak=zaak
        )
        cmis_doc = self.client.maak_zaakdocument(document, zaak)
        cmis_doc.checkout()
        inhoud = _create_binaire_inhoud(b'leaky abstraction...', filename='andere bestandsnaam.txt')

        with self.assertRaises(DocumentConflictException):
            self.client.update_zaakdocument(document, checkout_id='definitely not right', inhoud=inhoud)

    def test_checkout(self):
        """
        Assert that checking out a document locks it and returns the PWC ID
        """
        zaak = ZaakFactory.create(
            status_set__indicatie_laatst_gezette_status=JaNee.ja,
            zaakidentificatie='123456789',
            einddatum=None,
            zaaktype__zaaktypeidentificatie='998877',
            zaaktype__zaaktypeomschrijving='SOAP is leuk',
        )
        self.client.creeer_zaakfolder(zaak)
        document = EnkelvoudigInformatieObjectFactory.create(
            titel='testnaam', informatieobjectidentificatie='31415926535',
            beschrijving='Een beschrijving', zaak=zaak
        )
        cmis_doc = self.client.maak_zaakdocument(document, zaak)

        checkout_id, checkout_by = self.client.checkout(document)

        pwc = cmis_doc.getPrivateWorkingCopy()
        self.assertEqual(
            checkout_id,
            pwc.properties['cmis:versionSeriesCheckedOutId']
        )
        self.assertEqual(checkout_by, 'admin')

    def test_checkout_checked_out_doc(self):
        zaak = ZaakFactory.create(
            status_set__indicatie_laatst_gezette_status=JaNee.ja,
            zaakidentificatie='123456789',
            einddatum=None,
            zaaktype__zaaktypeidentificatie='998877',
            zaaktype__zaaktypeomschrijving='SOAP is leuk',
        )
        self.client.creeer_zaakfolder(zaak)
        document = EnkelvoudigInformatieObjectFactory.create(
            titel='testnaam', informatieobjectidentificatie='31415926535',
            beschrijving='Een beschrijving', zaak=zaak
        )
        cmis_doc = self.client.maak_zaakdocument(document, zaak)
        cmis_doc.checkout()

        with self.assertRaises(DocumentLockedException):
            self.client.checkout(document)

    def test_cancel_checkout(self):
        zaak = ZaakFactory.create(
            status_set__indicatie_laatst_gezette_status=JaNee.ja,
            zaakidentificatie='123456789',
            einddatum=None,
            zaaktype__zaaktypeidentificatie='998877',
            zaaktype__zaaktypeomschrijving='SOAP is leuk',
        )
        self.client.creeer_zaakfolder(zaak)
        document = EnkelvoudigInformatieObjectFactory.create(
            titel='testnaam', informatieobjectidentificatie='31415926535',
            beschrijving='Een beschrijving', zaak=zaak
        )
        self.client.maak_zaakdocument(document, zaak)
        checkout_id, checkout_by = self.client.checkout(document)

        result = self.client.cancel_checkout(document, checkout_id)

        self.assertIsNone(result)
        # if the doc cannot be checked out, it was not unlocked
        cmis_doc = self.client._get_cmis_doc(document)
        try:
            cmis_doc.checkout()
        except UpdateConflictException:
            self.fail("Could not lock document after checkout cancel, it is still locked")

    def test_cancel_checkout_invalid_checkout_id(self):
        zaak = ZaakFactory.create(
            status_set__indicatie_laatst_gezette_status=JaNee.ja,
            zaakidentificatie='123456789',
            einddatum=None,
            zaaktype__zaaktypeidentificatie='998877',
            zaaktype__zaaktypeomschrijving='SOAP is leuk',
        )
        self.client.creeer_zaakfolder(zaak)
        document = EnkelvoudigInformatieObjectFactory.create(
            titel='testnaam', informatieobjectidentificatie='31415926535',
            beschrijving='Een beschrijving', zaak=zaak
        )
        self.client.maak_zaakdocument(document, zaak)
        checkout_id, checkout_by = self.client.checkout(document)

        with self.assertRaises(DocumentConflictException):
            self.client.cancel_checkout(document, '')

    def test_ontkoppel_zaakdocument(self):
        zaak = ZaakFactory.create(
            status_set__indicatie_laatst_gezette_status=JaNee.ja,
            zaakidentificatie='123456789',
            einddatum=None,
            zaaktype__zaaktypeidentificatie='998877',
            zaaktype__zaaktypeomschrijving='SOAP is leuk',
        )
        cmis_folder = self.client.creeer_zaakfolder(zaak)
        document = EnkelvoudigInformatieObjectFactory.create(
            titel='testnaam', informatieobjectidentificatie='31415926535',
            beschrijving='Een beschrijving', zaak=zaak
        )
        self.client.maak_zaakdocument(document, zaak)

        result = self.client.ontkoppel_zaakdocument(document, zaak)

        self.assertIsNone(result)
        # check that the zaakfolder is empty
        self.assertFalse(cmis_folder.getChildren())

    def test_check_lock_status_unlocked(self):
        zaak = ZaakFactory.create(
            status_set__indicatie_laatst_gezette_status=JaNee.ja,
            zaakidentificatie='123456789',
            einddatum=None,
            zaaktype__zaaktypeidentificatie='998877',
            zaaktype__zaaktypeomschrijving='SOAP is leuk',
        )
        self.client.creeer_zaakfolder(zaak)
        document = EnkelvoudigInformatieObjectFactory.create(
            titel='testnaam', informatieobjectidentificatie='31415926535',
            beschrijving='Een beschrijving', zaak=zaak
        )
        self.client.maak_zaakdocument(document, zaak)

        result = self.client.is_locked(document)

        self.assertFalse(result)

    def test_check_lock_status_locked(self):
        zaak = ZaakFactory.create(
            status_set__indicatie_laatst_gezette_status=JaNee.ja,
            zaakidentificatie='123456789',
            einddatum=None,
            zaaktype__zaaktypeidentificatie='998877',
            zaaktype__zaaktypeomschrijving='SOAP is leuk',
        )
        self.client.creeer_zaakfolder(zaak)
        document = EnkelvoudigInformatieObjectFactory.create(
            titel='testnaam', informatieobjectidentificatie='31415926535',
            beschrijving='Een beschrijving', zaak=zaak
        )
        self.client.maak_zaakdocument(document, zaak)
        self.client.checkout(document)

        result = self.client.is_locked(document)

        self.assertTrue(result)

    def test_verwijder_document(self):
        zaak = ZaakFactory.create(
            status_set__indicatie_laatst_gezette_status=JaNee.ja,
            zaakidentificatie='123456789',
            einddatum=None,
            zaaktype__zaaktypeidentificatie='998877',
            zaaktype__zaaktypeomschrijving='SOAP is leuk',
        )
        zaak_folder = self.client.creeer_zaakfolder(zaak)
        document = EnkelvoudigInformatieObjectFactory.create(
            titel='testnaam', informatieobjectidentificatie='31415926535',
            beschrijving='Een beschrijving', zaak=zaak
        )
        self.client.maak_zaakdocument(document, zaak)

        result = self.client.verwijder_document(document)

        self.assertIsNone(result)
        # check that it's gone
        trash_folder, _ = self.client._get_or_create_folder(self.client.TRASH_FOLDER)
        self.assertEqual(len(trash_folder.getChildren()), 0)
        self.assertEqual(len(zaak_folder.getChildren()), 0)


@skipIf(on_jenkins() or should_skip_cmis_tests(), "Skipped while there's no Alfresco running on Jenkins")
class EndToEndTests(DMSMixin, TestCase):
    """
    Intended for tests that verify responses from one client method can be
    used as input for others.
    """

    def test_create_lock_update_flow(self):
        """
        Assert that it's possible to create an empty document, lock it for
        update and then effectively set the content thereby unlocking it.
        """
        # data setup
        zaak = ZaakFactory.create(
            status_set__indicatie_laatst_gezette_status=JaNee.ja,
            zaakidentificatie='123456789',
            einddatum=None,
            zaaktype__zaaktypeidentificatie='998877',
            zaaktype__zaaktypeomschrijving='SOAP is leuk',
        )
        self.client.creeer_zaakfolder(zaak)

        document = EnkelvoudigInformatieObjectFactory.create(
            titel='testnaam', informatieobjectidentificatie='31415926535',
            beschrijving='Een beschrijving', zaak=zaak
        )
        inhoud = _create_binaire_inhoud(b'leaky abstraction...', filename='bestand.txt')

        # flow
        self.client.maak_zaakdocument(document, zaak)  # create empty doc
        checkout_id, checkout_by = self.client.checkout(document)  # lock for update
        self.client.update_zaakdocument(document, checkout_id, inhoud=inhoud)
        filename, file_obj = self.client.geef_inhoud(document)

        # make assertions about the results
        self.assertEqual(filename, 'bestand.txt')
        self.assertEqual(file_obj.read(), b'leaky abstraction...')

        # verify expected props
        cmis_doc = self.client._get_cmis_doc(document)
        self.assertExpectedProps(cmis_doc, {
            'cmis:contentStreamFileName': 'bestand.txt',
            'cmis:contentStreamLength': 20,
            'cmis:contentStreamMimeType': 'application/binary',  # the default if it couldn't be determined
            # 'zsdms:dct.categorie': document.informatieobjecttype.informatieobjectcategorie,
            'zsdms:dct.omschrijving': document.informatieobjecttype.informatieobjecttypeomschrijving,
            'zsdms:documentIdentificatie': '31415926535',
            'zsdms:documentauteur': None,
            'zsdms:documentbeschrijving': 'Een beschrijving',
            'zsdms:documentcreatiedatum': _stuffdate_to_datetime(document.creatiedatum),
            # 'zsdms:documentformaat': None,
            'zsdms:documentLink': document.link,
            'zsdms:documentontvangstdatum': None,
            'zsdms:documentstatus': None,
            'zsdms:documenttaal': document.taal,
            'zsdms:documentversie': None,
            'zsdms:documentverzenddatum': None,
            'zsdms:vertrouwelijkaanduiding': None
        })

        # the doc must be unlocked after update, easy check -> lock it
        try:
            cmis_doc.checkout()
        except UpdateConflictException:
            self.fail("Could not lock document after update, it was already/still locked")
