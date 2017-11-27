from zaakmagazijn.rgbz_mapping.models import BesluitProxy

from ...stuf import StUFEntiteit
from ...stuf.models import BSL_parametersVraagSynchroon


class BesluitEntiteit(StUFEntiteit):
    mnemonic = 'BSL'
    model = BesluitProxy

    field_mapping = (
        ('identificatie', 'besluitidentificatie'),
        ('bst.omschrijving', 'besluittype__besluittypeomschrijving'),
        ('datumBeslissing', 'besluitdatum'),
    )
    input_parameters = BSL_parametersVraagSynchroon
    matching_fields = [
        'identificatie',
        'bst.omschrijving',
        'datumBeslissing',
    ]
