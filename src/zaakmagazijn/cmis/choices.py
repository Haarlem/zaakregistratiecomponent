from django.utils.translation import ugettext as _

from djchoices import ChoiceItem, DjangoChoices


class CMISChangeType(DjangoChoices):
    created = ChoiceItem('created', _('Created'))
    updated = ChoiceItem('updated', _('Updated'))
    deleted = ChoiceItem('deleted', _('Deleted'))
    security = ChoiceItem('security', _('Security'))


class CMISObjectType(DjangoChoices):
    zaken = ChoiceItem('F:zsdms:zaken', _('Zaken hoofd folder'))
    zaaktype = ChoiceItem('F:zsdms:zaaktype', _('Zaak type folder'))
    zaak_folder = ChoiceItem('F:zsdms:zaak', _('Zaak folder'))
    edc = ChoiceItem('D:zsdms:document', _('Enkelvoudig document'))


class CMISCapabilities(DjangoChoices):
    """
    http://docs.oasis-open.org/cmis/CMIS/v1.0/cmis-spec-v1.0.html
    """
    changes = ChoiceItem('Changes', _('Indicates what level of changes (if any) the repository exposes via the "change log" service.'))
    all_versions_searchable = ChoiceItem('AllVersionsSearchable', _('Ability of the Repository to include all versions of document. If False, typically either the latest or the latest major version will be searchable.'))
    content_stream_updatability = ChoiceItem('ContentStreamUpdatability', _('Indicates the support a repository has for updating a document\'s content stream.'))
    pwc_updatable = ChoiceItem('PWCUpdatable', _('Ability for an application to update the "Private Working Copy" of a checked-out document.'))
    pwc_searchable = ChoiceItem('PWCSearchable', _('Ability of the Repository to include the "Private Working Copy" of checked-out documents in query search scope; otherwise PWC\'s are not searchable'))
    unfiling = ChoiceItem('Unfiling', _('Ability for an application to leave a document or other file-able object not filed in any folder.'))
    multifiling = ChoiceItem('Multifiling', _('Ability for an application to file a document or other file-able object in more than one folder.'))
    version_specific_filing = ChoiceItem('VersionSpecificFiling', _('Ability for an application to file individual versions (i.e., not all versions) of a document in a folder.'))
    renditions = ChoiceItem('Renditions', _('Indicates whether or not the repository exposes renditions of document or folder objects.'))
    query = ChoiceItem('Query', _('Indicates the types of queries that the Repository has the ability to fulfill.'))
    get_folder_tree = ChoiceItem('GetFolderTree', _('Ability for an application to retrieve the folder tree via the getFolderTree service.'))
    acl = ChoiceItem('ACL', _('Indicates the level of support for ACLs by the repository.'))
    join = ChoiceItem('Join', _(' Indicates the types of JOIN keywords that the Repository can fulfill in queries.'))


class CMISCapabilityContentStreamUpdatability(DjangoChoices):
    none = ChoiceItem('none', _(' The content stream may never be updated.'))
    anytime = ChoiceItem('anytime', _(' The content stream may be updated any time.'))
    pwconly = ChoiceItem('pwconly', _(' The content stream may be updated only when checked out.'))


class CMISCapabilityRenditions(DjangoChoices):
    read = ChoiceItem('read', _(' Renditions are provided by the repository and readable by the client.'))
    none = ChoiceItem('none', _(' The repository does not expose renditions at all.'))


class CMISCapabilityQuery(DjangoChoices):
    none = ChoiceItem('none', _(' No queries of any kind can be fulfilled.'))
    metadataonly = ChoiceItem('metadataonly', _(' Only queries that filter based on object properties can be fulfilled. Specifically, the CONTAINS() predicate function is not supported.'))
    fulltextonly = ChoiceItem('fulltextonly', _(' Only queries that filter based on the full-text content of documents can be fulfilled. Specifically, only the CONTAINS() predicate function can be included in the WHERE clause.'))
    bothseparate = ChoiceItem('bothseparate', _(' The repository can fulfill queries that filter EITHER on the full-text content of documents OR on their properties, but NOT if both types of filters are included in the same query.'))
    bothcombined = ChoiceItem('bothcombined', _(' The repository can fulfill queries that filter on both the full-text content of documents and their properties in the same query.'))


class CMISCapabilityChanges(DjangoChoices):
    none = ChoiceItem('none', _(' The repository does not support the change log feature.'))
    objectidsonly = ChoiceItem('objectidsonly', _(' The change log can return only the ObjectIDs for changed objects in the repository and an indication of the type of change, not details of the actual change.'))
    properties = ChoiceItem('properties', _(' The change log can return properties and the ObjectID for the changed objects'))
    all = ChoiceItem('all', _(' The change log can return the ObjectIDs for changed objects in the repository and more information about the actual change'))


class CMISCapabilityACL(DjangoChoices):
    none = ChoiceItem('none', _(' The repository does not support ACL services'))
    discover = ChoiceItem('discover', _(' The repository supports discovery of ACLs (getACL and other services)'))
    manage = ChoiceItem('manage', _(' The repository supports discovery of ACLs AND applying ACLs (getACL and applyACL services)'))


class ChangeLogStatus(DjangoChoices):
    completed = ChoiceItem('completed', _('Completed'))
    in_progress = ChoiceItem('in_progress', _('In progress'))
