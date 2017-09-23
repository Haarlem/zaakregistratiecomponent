from unittest.mock import patch

from django.db import transaction
from django.test import TransactionTestCase

from zaakmagazijn.rgbz.tests.factory_models import ZaakFactory


@patch('zaakmagazijn.cmis.signals.client')
class InteractionTests(TransactionTestCase):
    """
    Tests interaction between the ZS and DMS, such as folder creation on
    zaak-creation.
    """

    def test_folder_created(self, mock_client):
        zaak = ZaakFactory.create()
        mock_client.creeer_zaakfolder.assert_called_once_with(zaak)

    def test_existing_zaak(self, mock_client):
        zaak = ZaakFactory.create()
        mock_client.creeer_zaakfolder.assert_called_once_with(zaak)

        zaak.save()
        self.assertEqual(mock_client.creeer_zaakfolder.call_count, 1)

        # act as if it's new object to verify those get processed correctly
        zaak.pk = None
        zaak.zaakidentificatie = 'iets nieuws'
        zaak.save()
        self.assertEqual(mock_client.creeer_zaakfolder.call_count, 2)

    def test_zaakcreatie_faalt_geen_folder_gemaakt(self, mock_client):
        """
        If the Zaak creation fails later in the transaction, this may not
        lead to the folder being created in the DMS.
        """
        def inner():
            zaak = ZaakFactory.create()
            self.assertIsNotNone(zaak.pk)
            raise Exception('Something went horribly wrong')

        try:
            with transaction.atomic():
                inner()
        except Exception:
            pass

        mock_client.creeer_zaakfolder.assert_not_called()
