import logging
from collections import OrderedDict
from io import BytesIO

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import transaction
from django.utils.functional import LazyObject
from django.utils.module_loading import import_string

from cmislib import CmisClient
from cmislib.atompub.binding import AtomPubDocument, AtomPubFolder
from cmislib.exceptions import ObjectNotFoundException, UpdateConflictException

from zaakmagazijn.api.stuf.models import BinaireInhoud

from ..rgbz.models.zaken import Zaak
from .choices import ChangeLogStatus, CMISChangeType, CMISObjectType
from .exceptions import (
    DocumentConflictException, DocumentDoesNotExistError, DocumentExistsError,
    DocumentLockedException, SyncException
)
from .models import ChangeLog
from .utils import FolderConfig, get_cmis_object_id

logger = logging.getLogger(__name__)


class CMISQuery:
    """
    Small, not feature-complete utility class for building CMIS queries with
    escaping built in.

    Usage:
    >>> query = CMSQuery("SELECT * FROM cmis:document WHERE cmis:objectTypeId = '%s'")
    >>> query('zsdms:document')
    "SELECT * FROM cmis:document WHERE cmis:objectTypeId = 'zsdms:document';"
    """

    def __init__(self, query):
        self.query = query

    def __call__(self, *args):
        args = tuple(self.escape(arg) for arg in args)
        return self.query % args

    def escape(self, value):
        """
        Escapes the characters in value for the CMIS queries.

        Poor documentation references:
          * https://community.alfresco.com/docs/DOC-5898-cmis-query-language#Literals
          * http://docs.alfresco.com/community/concepts/rm-searchsyntax-literals.html
        """
        value = value.replace("'", "\\'")
        value = value.replace('"', '\\"')
        return value


class DMSClient:
    """
    Abstract base class for DMS interaction.
    """
    TEMP_FOLDER_NAME = '_temp'
    TRASH_FOLDER = 'Unfiled'

    def creeer_zaakfolder(self, zaak: Zaak):
        raise NotImplementedError  # noqa

    def maak_zaakdocument(self, document, zaak: Zaak=None, filename: str=None, sender: str=None) -> AtomPubDocument:
        raise NotImplementedError  # noqa

    def maak_zaakdocument_met_inhoud(self, document, zaak: Zaak=None, filename: str=None, sender: str=None,
                                     stream: BytesIO=None, content_type=None) -> AtomPubDocument:
        raise NotImplementedError  # noqa

    def geef_inhoud(self, document) -> tuple:
        raise NotImplementedError  # noqa

    def zet_inhoud(self, document, stream: BytesIO, content_type=None, checkout_id: str=None) -> None:
        raise NotImplementedError  # noqa

    def relateer_aan_zaak(self, document, zaak: Zaak) -> None:
        raise NotImplementedError  # noqa

    def update_zaakdocument(self, document, checkout_id: str=None, inhoud: BinaireInhoud=None) -> None:
        raise NotImplementedError  # noqa

    def checkout(self, document) -> tuple:
        raise NotImplementedError  # noqa

    def cancel_checkout(self, document, checkout_id: str) -> None:
        raise NotImplementedError  # noqa

    def ontkoppel_zaakdocument(self, document, zaak: Zaak) -> None:
        raise NotImplementedError  # noqa

    def is_locked(self, document) -> bool:
        raise NotImplementedError  # noqa

    def verwijder_document(self, document) -> None:
        raise NotImplementedError  # noqa

    def sync(self, dryrun=False) -> OrderedDict:
        raise NotImplementedError  # noqa


class CMISDMSClient(DMSClient):
    """
    DMS client implementation using the CMIS protocol.
    """

    document_query = CMISQuery("SELECT * FROM zsdms:document WHERE zsdms:documentIdentificatie = '%s'")

    def __init__(self, url=None, user=None, password=None):
        """
        Connect to the CMIS repository and store the root folder for further
        operations.

        :param url: string, CMIS provider url.
        :param user: string, username to login on the document store
        :param password: string, password to login on the document store
        """
        if url is None:
            url = settings.CMIS_CLIENT_URL
        if user is None:
            user = settings.CMIS_CLIENT_USER
        if password is None:
            password = settings.CMIS_CLIENT_USER_PASSWORD

        _client = CmisClient(url, user, password)
        self._repo = _client.getDefaultRepository()
        self._root_folder = self._repo.getObjectByPath('/')

        self.upload_to = import_string(settings.CMIS_UPLOAD_TO)

    def _get_or_create_folder(self, name: str, properties: dict=None, parent: AtomPubFolder=None) -> tuple:
        """
        Get or create the folder with :param:`name` in :param:`parent`.

        :param name: string, the name of the folder to create.
        :param properties: dictionary with cmis and/or custom properties to
          pass to the folder object
        :param parent: parent folder to create the folder in as subfolder.
          Defaults to the root folder
        :return: a tuple of (folder, boolean) where the folder is the retrieved or created folder, and
          the boolean indicates whether the folder was created or not.
        """
        if parent is None:
            parent = self._root_folder

        # check if it exists. Note that cmis:name is not guaranteed to be unique!
        # NOTE: we're using getChildren, which MAY return files as well. However,
        # the ZS/DMS spec does not allow for tree structures like that.
        # NOTE: we return the first match by name - if there are more with the same
        # name, we cannot decide which one would be the 'right' one
        existing = next(
            (child for child in parent.getChildren() if child.name == name),
            None
        )
        if existing is not None:
            # NOTE: properties may differ - we're not doing update actions here
            return (existing, False)

        # create the folder, since it didn't exist yet
        # NOTE: concurrency may cause this to throw UpdateConflictException if
        # another process creates the same folder name at the same time
        return (parent.createFolder(name, properties=properties or {}), True)

    def get_folder_name(self, zaak: Zaak, folder_config: FolderConfig) -> str:
        name = ''
        if folder_config.type == CMISObjectType.zaaktype:
            name = str(zaak.zaaktype.zaaktypeidentificatie)
        elif folder_config.type == CMISObjectType.zaak_folder:
            name = str(zaak.zaakidentificatie)
        elif not folder_config.name:
            raise ValueError("Could not determine a folder name for zaak {:d}".format(zaak.id))
        return folder_config.name or name

    def _get_zaakfolder(self, zaak: Zaak) -> AtomPubFolder:
        upload_to = self.upload_to(zaak)
        bits = [self.get_folder_name(zaak, folder_config) for folder_config in upload_to]
        path = '/' + '/'.join(bits)
        return self._repo.getObjectByPath(path)

    def _get_cmis_doc(self, document, checkout_id: str=None) -> AtomPubDocument:
        """
        Given a document instance, retrieve the underlying AtomPubDocument object.

        :param document: :class:`InformatieObject` instance.
        :return: :class:`AtomPubDocument` object
        """
        query = self.document_query(document.informatieobjectidentificatie)
        result_set = self._repo.query(query)
        if not len(result_set):
            raise DocumentDoesNotExistError(
                "Document met identificatie {} bestaat niet in het DMS".format(
                    document.informatieobjectidentificatie
                )
            )

        # NOTE: there should only be one document with this identification, but multiple versions can exist
        doc = [item for item in result_set][0]
        doc = doc.getLatestVersion()

        if checkout_id is not None:
            # refresh and get the currently active private working copy
            # any changes because the checkout_id is not right will lead to UpdateConflictException
            # and in turn to DocumentConflictException when trying to update properties
            pwc = doc.getPrivateWorkingCopy()
            if not pwc or not pwc.properties['cmis:versionSeriesCheckedOutId'] == checkout_id:
                raise DocumentConflictException("Foutieve 'pwc id' meegestuurd")
        return doc

    def _build_cmis_doc_properties(self, document, filename: str=None) -> dict:
        # build up the properties
        properties = document.get_cmis_properties()
        properties['cmis:objectTypeId'] = CMISObjectType.edc

        if filename is not None:
            properties['cmis:name'] = filename

        return properties

    def creeer_zaakfolder(self, zaak: Zaak) -> AtomPubFolder:
        """
        Maak de zaak folder aan in het DMS.

        :param zaak: :class:`zaakmagazijn.rgbz.models.Zaak` instantie om de map
          voor aan te maken.
        :return: :class:`cmslib.atompub_binding.AtomPubFolder` object - de
          cmslib representatie van de (aangemaakte) zaakmap.
        """
        upload_to = self.upload_to(zaak)

        # apparently in the latest model, F:zsdms:zaken is not guaranteed to exist...
        # FIXME: this mutates state and is waaaay dirty...
        if not settings.CMIS_ZAKEN_TYPE_ENABLED:
            for folder_config in upload_to:
                if folder_config.type == CMISObjectType.zaken:
                    folder_config.type = 'cmis:folder'

        # create the folders according to the `upload_to` configuration
        parent = None
        for folder_config in upload_to:
            properties = {
                'cmis:objectTypeId': folder_config.type,
            } if folder_config.type else {}

            name = self.get_folder_name(zaak, folder_config)

            if folder_config.type == CMISObjectType.zaaktype:
                properties.update(zaak.zaaktype.get_cmis_properties())
            elif folder_config.type == CMISObjectType.zaak_folder:
                properties.update(zaak.get_cmis_properties())

            parent, _ = self._get_or_create_folder(name, properties, parent=parent)

        zaak_folder = parent
        return zaak_folder

    def maak_zaakdocument(self, document, zaak: Zaak=None, filename: str=None, sender: str=None) -> AtomPubDocument:
        """
        4.3.5.3: Maak een EDC object aan zonder binaire inhoud.

        Het ZS zorgt ervoor dat in het DMS een EDC-object wordt aangemaakt zonder binaire inhoud.
        Hiervoor maakt het ZS gebruik van de CMIS-services die aangeboden worden door het DMS. Hierbij
        gelden de volgende eisen:
        - Er wordt een object aangemaakt van het objecttype EDC (Zie 5.1);
        - Het EDC-object wordt gerelateerd aan de juiste Zaakfolder (Zie 5.1);
        - Tenminste de minimaal vereiste metadata voor een EDC wordt vastgelegd in de daarvoor
        gedefinieerde objectproperties. In Tabel 3 is een mapping aangegeven tussen de StUF-ZKN-
        elementen en CMIS-objectproperties.

        :param zaak: Zaak instantie waarvoor een document wordt aangemaakt
        :param document: EnkelvoudigInformatieObject instantie die de
          meta-informatie van het document bevat
        :param filename: Bestandsnaam van het aan te maken document.
        :param sender: De afzender.

        :return: AtomPubDocument instance die aangemaakt werd.
        :raises: DocumentExistsError wanneer er al een document met dezelfde
            identificatie bestaat, binnen de zaakfolder.
        """
        return self.maak_zaakdocument_met_inhoud(document, zaak, filename, sender)

    def maak_zaakdocument_met_inhoud(self, document, zaak: Zaak=None, filename: str=None, sender: str=None,
                                     stream: BytesIO=None, content_type=None) -> AtomPubDocument:
        """
        In afwijking van de KING specificatie waarbij het document aanmaken
        en het document van inhoud voorzien aparte stappen zijn, wordt in deze
        functie in 1 stap het document aangemaakt met inhoud. Dit voorkomt dat
        er in het DMS direct een versie 1.1 ontstaat, waarbij versie 1.0 een
        leeg document betreft, en versie 1.1 het eigenlijke document pas is.

        :param zaak: Zaak instantie waarvoor een document wordt aangemaakt
        :param document: EnkelvoudigInformatieObject instantie die de
          meta-informatie van het document bevat
        :param filename: Bestandsnaam van het aan te maken document.
        :param sender: De afzender.
        :param stream: Inhoud van het document.
        :param content_type: Aanduiding van het document type.

        :return: AtomPubDocument instance die aangemaakt werd.
        :raises: DocumentExistsError wanneer er al een document met dezelfde
            identificatie bestaat, binnen de zaakfolder.
        """
        # short-circuit if the identification is not unique
        try:
            self._get_cmis_doc(document)
        except DocumentDoesNotExistError:
            pass  # exactly what we want
        else:
            # not an unique identification
            raise DocumentExistsError(
                "Document identificatie {} is niet uniek".format(document.informatieobjectidentificatie)
            )

        if stream is None:
            stream = BytesIO()

        # the document can be created in two ways: an explicit call to create
        # a document, for which the :param:`zaak` is known upfront, or via
        # the other services where the content is provided before the connection
        # to the Zaak is made. In that case, :param:`zaak` will be ``None``
        # and the service will place the document in the right folder.
        if zaak is None:
            # use a temporary directory
            zaakfolder, _ = self._get_or_create_folder(self.TEMP_FOLDER_NAME)
        else:
            # bij het aanmaken van een zaak moet een zaakfolder aangemaakt worden
            # we kunnen er dus van uit gaan dat de zaakfolder bestaat, en path
            # uniqueness wordt afgedwongen via :method:`self._get_or_create`
            zaakfolder = self._get_zaakfolder(zaak)

        # build up the properties
        properties = self._build_cmis_doc_properties(document, filename=filename)

        # set the sender property if provided
        if settings.CMIS_SENDER_PROPERTY:
            properties[settings.CMIS_SENDER_PROPERTY] = sender

        # Passing empty content is a dirty hack to ensure a contentStreamId exists.
        # See `self.geef_inhoud`. However, this appears to be the recommended way in Alfresco
        # at least...
        _doc = self._repo.createDocument(
            name=document.titel, properties=properties,
            contentFile=stream, contentType=content_type,
            parentFolder=zaakfolder
        )
        # the objectId contains the version, which we strip off to always get the latest version back
        document._object_id = _doc.getObjectId().rsplit(';')[0]
        document.save(update_fields=['_object_id'])
        return _doc

    def geef_inhoud(self, document) -> tuple:
        """
        Retrieve the document via its identifier from the DMS.

        :param document: EnkelvoudigInformatieObject instance
        :return: tuple of (filename, BytesIO()) with the stream filename and the binary content
        """
        try:
            doc = self._get_cmis_doc(document)
        except DocumentDoesNotExistError:
            return (None, BytesIO())

        # this is an implementation detail - cmslib complains loudly if there's not atom:content
        # since it doesn't know which url to retrieve then. We create documents with empty
        # content, that make it then impossible to set the content later, because that
        # content url is missing.
        # TODO [TECH]: find a way to replace a non-existing stream with an actual stream
        filename = doc.properties['cmis:name']
        empty = doc.properties['cmis:contentStreamId'] is None
        if empty:
            return (filename, BytesIO())
        return (filename, doc.getContentStream())

    def zet_inhoud(self, document, stream: BytesIO, content_type=None, checkout_id: str=None) -> None:
        """
        Calls setContentStream to fill the contents of an existing document. This will update the
        version of the document in the DMS.

        :param document: EnkelvoudigInformatieObject instance
        :param stream: Inhoud van het document.
        :param content_type: Aanduiding van het document type.
        :param checkout_id:
        """
        cmis_doc = self._get_cmis_doc(document, checkout_id=checkout_id)
        cmis_doc = cmis_doc if not checkout_id else cmis_doc.getPrivateWorkingCopy()
        cmis_doc.setContentStream(stream, content_type)

    def update_zaakdocument(self, document, checkout_id: str=None, inhoud: BinaireInhoud=None) -> None:
        cmis_doc = self._get_cmis_doc(document, checkout_id=checkout_id)
        cmis_doc = cmis_doc if not checkout_id else cmis_doc.getPrivateWorkingCopy()

        # build up the properties
        current_properties = cmis_doc.properties
        new_properties = self._build_cmis_doc_properties(
            document, filename=inhoud.bestandsnaam if inhoud else None
        )
        diff_properties = {
            key: value for key, value in new_properties.items()
            if current_properties.get(key) != new_properties.get(key)
        }
        try:
            cmis_doc.updateProperties(diff_properties)
        except UpdateConflictException as exc:
            # node locked!
            raise DocumentConflictException from exc

        if inhoud is not None:
            content = inhoud.to_cmis()
            # TODO [TECH]: support content type
            self.zet_inhoud(document, content, None, checkout_id=checkout_id)

        # all went well so far, so if we have a checkout_id, we must check the document back in
        if checkout_id:
            cmis_doc.checkin()

    def relateer_aan_zaak(self, document, zaak: Zaak) -> None:
        """
        Wijs het document aan :param:`zaak` toe.

        Verplaatst het document van de huidige folder naar de zaakfolder.
        """
        cmis_doc = self._get_cmis_doc(document)
        zaakfolder = self._get_zaakfolder(zaak)
        # NOTE: can this ever be more than one entry?
        parent = [parent for parent in cmis_doc.getObjectParents()][0]
        cmis_doc.move(parent, zaakfolder)

    def checkout(self, document) -> tuple:
        """
        Checkout (lock) the requested document and return the PWC ID + check out username.

        :param document: :class:`EnkelvoudigInformatieObject` instance.
        """
        cmis_doc = self._get_cmis_doc(document)
        try:
            pwc = cmis_doc.checkout()
        except UpdateConflictException as exc:
            raise DocumentLockedException("Document was already checked out") from exc
        pwc.reload()
        checkout_id = pwc.properties['cmis:versionSeriesCheckedOutId']
        checkout_by = pwc.properties['cmis:versionSeriesCheckedOutBy']
        return checkout_id, checkout_by

    def cancel_checkout(self, document, checkout_id: str) -> None:
        cmis_doc = self._get_cmis_doc(document, checkout_id=checkout_id)
        cmis_doc.cancelCheckout()

    def ontkoppel_zaakdocument(self, document, zaak: Zaak) -> None:
        cmis_doc = self._get_cmis_doc(document)
        cmis_folder = self._get_zaakfolder(zaak)

        # Alfresco doesn't seem to support unfiling properly, so let's do it manually
        # on top of that, we currently don't support multi-filing from the services, so we
        # 'know' that a file only belongs to a single folder. Unfiling can then
        # be done manually by moving the file to the Trash folder, away from the
        # zaak folder, hereby effectively 'ontkoppelen'.

        # cmis_folder.removeObject(cmis_doc)
        trash_folder, _ = self._get_or_create_folder(self.TRASH_FOLDER)
        cmis_doc.move(cmis_folder, trash_folder)

    def is_locked(self, document) -> bool:
        cmis_doc = self._get_cmis_doc(document)
        pwc = cmis_doc.getPrivateWorkingCopy()
        return pwc is not None

    def verwijder_document(self, document) -> None:
        cmis_doc = self._get_cmis_doc(document)
        cmis_doc.delete()

    @transaction.atomic
    def sync(self, dryrun=False) -> OrderedDict:
        """
        De zaakdocument registratie in het DMS wordt gesynchroniseerd met het
        ZS door gebruik te maken van de CMIS-changelog. Het ZS vraagt deze op
        bij het DMS door gebruik te maken van de CMISservice
        getContentChanges(), die het DMS biedt. Het ZS dient door middel van de
        latestChangeLogToken te bepalen welke wijzigingen in de CMIS-changelog
        nog niet zijn verwerkt in het ZS. Indien er wijzigingen zijn die nog
        niet zijn verwerkt in het ZS dienen deze alsnog door het ZS verwerkt te
        worden.

        Zie: ZDS 1.2, paragraaf 4.4

        De sync-functie, realiseert ook "Koppel Zaakdocument aan Zaak":

        Een reeds bestaand document wordt relevant voor een lopende zaak.

        De "Koppel Zaakdocument aan Zaak"-service biedt de mogelijkheid aan
        DSC's om een "los" document achteraf aan een zaak te koppelen waardoor
        het een zaakgerelateerd document wordt. Het betreft hier documenten
        die reeds bestonden en in het DMS waren vastgelegd voordat een ZAAK is
        ontstaan.

        Een document wordt binnen het DMS gekoppeld aan een lopende zaak door
        het document te relateren aan een Zaakfolder-object.

        Zie: ZDS 1.2, paragraaf 5.4.2

        :param dryrun: Retrieves all content changes from the DMS but doesn't
                       update the ZS.
        :return: A `OrderedDict` with all `CMISChangeType`s as key and the
                 number of actions as value.
        """
        from zaakmagazijn.rgbz.models import EnkelvoudigInformatieObject  # circular import

        # Eisen aan ZS:
        #
        # * De CMIS-changelog dient met een configureerbare tijdsinterval
        #   opgehaald te worden uit het DMS;
        # * Wijzigingen in de CMIS-changelog die nog niet verwerkt zijn in het
        #   ZS dienen direct verwerkt te worden in het ZS;
        # * Wijzigingen in het ZS mogen niet tot nieuwe wijzigingen in het DMS
        #   leiden (een oneindige loop van updateberichten);

        # TODO [TECH]: We should prolly update the ZS changelog token after WE update the DMS ourselves to prevent duplicate updates?
        self._repo.reload()
        try:
            dms_change_log_token = int(self._repo.info['latestChangeLogToken'])
        except KeyError:
            raise ImproperlyConfigured('Could not retrieve the latest change log token from the DMS.')

        if not dryrun:
            change_log = ChangeLog.objects.create(token=dms_change_log_token)
            if ChangeLog.objects.exclude(pk=change_log.pk).filter(status=ChangeLogStatus.in_progress).count() > 0:
                change_log.delete()
                raise SyncException('A synchronization process is already running.')
        else:
            change_log = None

        # Check the last change log.
        last_change_log = ChangeLog.objects.filter(status=ChangeLogStatus.completed).last()
        # If no entry is found, assume this is the very first time to retrieve the change log.
        last_zs_change_log_token = last_change_log.token if last_change_log else 0
        # Determine the max items to retrieve to prevent the token from updating since the last retrieval.
        max_items = dms_change_log_token - last_zs_change_log_token
        # If the last ZS token, and the DMS token are the same, no updates are found.
        if max_items < 0:
            raise SyncException('The DMS change log token is older than our records.')
        elif max_items == 0:
            return {}

        created, updated, deleted, security, failed = 0, 0, 0, 0, 0
        cache = set()

        result_set = self._repo.getContentChanges(
            changeLogToken=last_zs_change_log_token,
            includeProperties=True,
            maxItems=max_items
        )
        for change_entry in result_set:
            change_type = change_entry.changeType
            object_id = get_cmis_object_id(change_entry.objectId)

            # Skip already processed objects that have the same action.
            cache_key = '{}-{}'.format(object_id, change_type)
            if cache_key in cache:
                continue
            cache.add(cache_key)

            try:
                if change_type in [CMISChangeType.created, CMISChangeType.updated]:
                    try:
                        dms_document = self._repo.getObject(object_id)
                    except ObjectNotFoundException as e:
                        logger.error(
                            '[%s-%s] Object was %s but could not be found in the DMS.',
                            change_entry.id, object_id, change_type
                        )
                        failed += 1
                        continue

                    dms_object_type = dms_document.properties.get('cmis:objectTypeId')
                    if dms_object_type == CMISObjectType.edc:
                        if change_type == CMISChangeType.updated:
                            # Update
                            try:
                                zs_document_id = dms_document.properties.get('zsdms:documentIdentificatie')
                                edc = EnkelvoudigInformatieObject.objects.get(
                                    informatieobjectidentificatie=zs_document_id
                                )
                            except EnkelvoudigInformatieObject.DoesNotExist as e:
                                logger.error(
                                    '[%s-%s] Object was %s but could not be found in the ZS.',
                                    change_entry.id, object_id, change_type
                                )
                                failed += 1
                            else:
                                edc.update_cmis_properties(dms_document.properties, commit=not dryrun)
                                updated += 1
                        else:
                            # Create ("Koppel Zaakdocument aan Zaak")
                            zaak_folder = dms_document.getPaths()[0].split('/')[-2]
                            zaak = Zaak.objects.get(zaakidentificatie=zaak_folder)
                            if not dryrun:
                                EnkelvoudigInformatieObject.objects.create_from_cmis_properties(
                                    dms_document.properties, zaak, object_id
                                )
                            created += 1
                    else:
                        # The specification only indicates to synchronize EDC
                        # properties from the DMS to the ZS.
                        pass
                elif change_type == CMISChangeType.deleted:
                    # Delete
                    if not dryrun:
                        delete_count = EnkelvoudigInformatieObject.objects.filter(_object_id=object_id).delete()
                        if delete_count[0] == 0:
                            logger.warning(
                                '[%s-%s] Object was %s but could not be found in the ZS.',
                                change_entry.id, object_id, change_type
                            )
                            failed += 1
                        else:
                            deleted += 1
                elif change_type == CMISChangeType.security:
                    logger.info('[%s-%s] Security changes are not processed.', change_entry.id, object_id)
                    security += 1
                else:
                    logger.error('[%s-%s] Unsupported change type: %s', change_entry.id, object_id, change_type)
                    failed += 1
            except Exception as e:
                failed += 1
                logger.exception(
                    '[%s-%s] Could not process "%s" in ZS: %s',
                    change_entry.id, object_id, change_type, e,
                    exc_info=True
                )

        if not dryrun:
            change_log.status = ChangeLogStatus.completed
            change_log.save()

        return OrderedDict([
            (CMISChangeType.created, created),
            (CMISChangeType.updated, updated),
            (CMISChangeType.deleted, deleted),
            (CMISChangeType.security, security),
            ('failed', failed),
        ])


class DummyDMSClient(DMSClient):
    """
    Dummy DMS client which returns a bogus response. Useful for testing purposes.
    """
    def creeer_zaakfolder(self, zaak: Zaak) -> None:
        return None

    def maak_zaakdocument(self, document, zaak: Zaak=None, filename: str=None, sender: str=None) -> dict:
        return self.maak_zaakdocument_met_inhoud(document, zaak, filename, sender)

    def maak_zaakdocument_met_inhoud(self, document, zaak: Zaak=None, filename: str=None, sender: str=None,
                                     stream: BytesIO=None, content_type=None) -> dict:
        return {
            'title': 'some document'
        }

    def geef_inhoud(self, document) -> tuple:
        return (BytesIO(), 'test')

    def zet_inhoud(self, document, stream: BytesIO, content_type=None, checkout_id: str=None) -> None:
        return None

    def relateer_aan_zaak(self, document, zaak: Zaak) -> None:
        return None

    def update_zaakdocument(self, document, checkout_id: str=None, inhoud: BinaireInhoud=None):
        return None

    def checkout(self, document) -> tuple:
        return ('1234', '1234')

    def cancel_checkout(self, document, checkout_id: str) -> None:
        return None

    def ontkoppel_zaakdocument(self, document, zaak: Zaak) -> None:
        return None

    def is_locked(self, document) -> bool:
        return False

    def verwijder_document(self, document) -> None:
        return None

    def sync(self, dryrun=False) -> OrderedDict:
        return OrderedDict()


class DefaultClient(LazyObject):
    def _setup(self):
        client_cls = import_string(settings.CMIS_CLIENT_CLASS)
        self._wrapped = client_cls()


default_client = DefaultClient()
