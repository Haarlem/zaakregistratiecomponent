from django.apps import AppConfig
from django.core.checks import Error, Tags, register


class CMISConfig(AppConfig):
    name = 'zaakmagazijn.cmis'
    verbose_name = "CMIS"

    def ready(self):
        from . import signals  # noqa
        register(check_cmis, Tags.compatibility, deploy=True)


def check_cmis(app_configs, **kwargs):
    """
    ZDS 1.2.01, hoofdstuk 5:
    Ten behoeve van de integratie met het ZS en het vastleggen van
    zaakdocumenten dient het DMS aan de volgende eisen te voldoen:

        * Het DMS wordt ontsloten als een CMIS 1.0 repository;
        * De CMIS-interface dient minimaal navolgende opties te ondersteunen:
            - "Multi-filing";
            - "Change Log", met registratie van Change Events voor
              filing/unfiling/moving van de objecten documenten en folders;
            - Nieuwe CMIS-objecttypes van het Base Type "cmis:document" en
              "cmis:folder" worden ondersteund;
        * De CMIS-changelog is toegankelijk voor het ZS.

    :param app_configs:
    :param kwargs:
    :return:
    """
    from .client import default_client as client
    from .choices import CMISCapabilities, CMISCapabilityChanges

    errors = []

    try:
        capabilities = client._repo.capabilities
    except Exception:
        errors.append(
            Error(
                'Could not communicate with the DMS.',
                hint='Make sure the authentication and host settings are correct.'
            )
        )
        return errors

    multifiling = capabilities.get(CMISCapabilities.multifiling, None)
    if not multifiling:
        errors.append(
            Error('The DMS does not support Multifiling, or it\'s disabled.')
        )

    # TODO [KING]: cmislib requires unfiling to be enabled to be able to call folder.removeObject
    # (removeObjectFromFolder CMIS operation), but this is not explicitly mentioned in the spec
    unfiling = capabilities.get(CMISCapabilities.unfiling, None)
    if not unfiling:
        errors.append(
            Error('The DMS does not support Unfiling or it\'s disabled.')
        )

    changes = capabilities.get(CMISCapabilities.changes, None)
    if not changes or changes == CMISCapabilityChanges.none:
        errors.append(
            Error(
                'The DMS does not support Change Log, or it\'s disabled.',
                hint='In case you\'re running Alfresco, make sure to add the relevant audit.* properties.'
            )
        )

    return errors
