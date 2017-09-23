from unittest.mock import patch


class MockDMSMixin:
    """
    Mixin that mocks away DMS interaction.
    """
    extra_client_mocks = []
    disable_mocks = False

    def setUp(self):
        super().setUp()
        if not self.disable_mocks:
            self._patch_dms()

    def _patch_dms(self):
        # do not attempt to create the zaakfolder on post_save
        patcher = patch('zaakmagazijn.cmis.signals.client')
        self._mocked_dms_client = patcher.start()
        self.addCleanup(patcher.stop)

        self._extra_mocked_dms_clients = []
        for path in self.extra_client_mocks:
            patcher = patch(path)
            self._extra_mocked_dms_clients.append(patcher.start())
            self.addCleanup(patcher.stop)
