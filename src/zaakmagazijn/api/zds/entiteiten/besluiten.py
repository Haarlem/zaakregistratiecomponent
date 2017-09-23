from zaakmagazijn.rgbz.models import Besluit

from ...stuf import StUFEntiteit
from ...stuf.models import BSL_parametersVraagSynchroon


class BesluitEntiteit(StUFEntiteit):
    """
    in xsd: ['identificatie', 'bst.omschrijving', 'datumBeslissing']
    """
    mnemonic = 'BSL'
    model = Besluit

    field_mapping = (
        # TODO: [COMPAT] In ZKN 3.2 this is called besluitidentificatie
        ('identificatie', 'identificatie'),
        # TODO: [KING] In ZKN 3.2, but not in RGBZ 2.0, Ufff
        # ('verantwoordelijkeOrganisatie', '')
        ('bst.omschrijving', 'besluittype__besluittypeomschrijving'),
        ('datumBeslissing', 'besluitdatum'),  # Called besluitdatum in ZKN 3.2

        # TODO: [COMPAT] onderstaande staat niet in de xsd maar is wel verplicht
        ('ingangsdatumWerking', 'ingangsdatum'),
        ('einddatumWerking', 'vervaldatum'),
    )
    input_parameters = BSL_parametersVraagSynchroon
    matching_fields = [
        'identificatie',
        # 'verantwoordelijkeOrganisatie',
        'datumBeslissing',
    ]
