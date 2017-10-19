from .choices import CMISObjectType


def get_cmis_object_id_parts(cmis_object_id):
    """
    Returns the actual object ID, version and path, if present.

    :param object_id: A `CmisId`.
    :return: A `tuple` containing the actual object Id, version and path as strings.
    """
    parts = cmis_object_id.split(';')

    version = None
    if len(parts) == 2:
        version = parts[1]

    parts = parts[0].rsplit('/')
    object_id = parts[-1]

    path = None
    if len(parts) == 2:
        path = parts[0]

    return object_id, version, path


def get_cmis_object_id(cmis_object_id):
    """
    Returns the actual object ID.

    :param object_id: A `CmisId`.
    :return: The actual CMIS Id as string.
    """
    return get_cmis_object_id_parts(cmis_object_id)[0]


class FolderConfig:
    __slots__ = ['type', 'name']

    def __init__(self, type_=None, name=None):
        assert type_ or name, "Either type or name is required"
        self.type = type_
        self.name = name

    def __repr__(self):
        return "<{} type_={!r} name={!r}>".format(self.__class__.__name__, self.type, self.name)


def upload_to(zaak) -> list:
    """
    Return the fully qualified upload path for the zaak, generic case.

    Each item from the return list is a FolderConfig object with either a
    type, name or both defined. If a name is defined, this name will be used
    for the folder name. The type is required to be able to generate the
    appropriate cmis properties.

    :param zaak: :class:`zaakmagazijn.rgbz.models.Zaak` instance.
    :return: list of FolderConfig objects, in order of root -> leaf
    """
    return [
        FolderConfig(name='Zaken', type_=CMISObjectType.zaken),
        FolderConfig(type_=CMISObjectType.zaaktype),
        FolderConfig(type_=CMISObjectType.zaak_folder),
    ]


def upload_to_date_based(zaak) -> list:
    """
    Return the fully qualified upload path for the zaak, Haarlem variant.

    Each item from the return list is a FolderConfig object with either a
    type, name or both defined. If a name is defined, this name will be used
    for the folder name. The type is required to be able to generate the
    appropriate cmis properties.

    :param zaak: :class:`zaakmagazijn.rgbz.models.Zaak` instance.
    :return: list of FolderConfig objects, in order of root -> leaf
    """
    assert len(zaak.startdatum) == 8, "Zaak.startdatum moet volledig bekend zijn"
    year, month, day = (
        zaak.startdatum[0:4],
        zaak.startdatum[4:6],
        zaak.startdatum[6:8]
    )
    return [
        FolderConfig(name='Sites'),
        FolderConfig(name='archief'),
        FolderConfig(name='documentLibrary', type_=CMISObjectType.zaken),
        FolderConfig(type_=CMISObjectType.zaaktype),
        FolderConfig(name=year),
        FolderConfig(name=month),
        FolderConfig(name=day),
        FolderConfig(type_=CMISObjectType.zaak_folder),
    ]
