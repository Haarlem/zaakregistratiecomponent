from django.conf import settings

from spyne import ServiceBase, rpc

from ...utils import stuf_datetime
from ..stuf.choices import BerichtcodeChoices
from ..stuf.models import Bv03Bericht
from ..utils import create_unique_id
from ..zds import Lk01Builder
from ..zds.entiteiten.zaken import ZaakEntiteit
from ..zds.kennisgevingsberichten import process_update

input_builder = Lk01Builder(ZaakEntiteit, 'UpdateZaak', update=True)


class UpdateZaak(ServiceBase):
    """
    De "update Zaak"-service biedt ZSC's de mogelijkheid om attributen van een
    bestaande lopende zaak en gerelateerde objecten in het ZS te muteren
    middels een kennisgeving. Bij ontvangst van de kennisgeving zorgt het ZS
    dat alle aangeleverde attributen worden gemuteerd met uitzondering van
    zaakidentificatie en zaaktype. Deze laatste attributen mogen niet gemuteerd
    worden.

    Zie: ZDS 1.2, paragraaf 4.1.5
    """
    input_model = input_builder.create_model()
    output_model = Bv03Bericht

    @rpc(input_model, _body_style="bare", _out_message_name="Bv03Bericht", _returns=output_model)
    def updateZaak_ZakLk01(ctx, data):
        """
        Gegevens van een lopende zaak zijn gewijzigd.
        """

        # Eisen aan ZS:
        #
        # Er gelden geen aanvullende eisen.

        # Interactie tussen ZSC en ZS:
        #
        # StUF schrijft voor dat alle kerngegevens van het te wijzigen object
        # verplicht zijn opgenomen in het bericht. Daarnaast zijn de te
        # wijzigen gegevens opgenomen volgens de StUF standaard.

        # Opmerkingen:
        #
        # In een UpdateZaak bericht mogen ook niet-authentieke contactgegevens
        # opgenomen worden.

        process_update(ZaakEntiteit, data)

        return {
            'stuurgegevens': {
                'berichtcode': BerichtcodeChoices.bv03,
                'zender': settings.ZAAKMAGAZIJN_SYSTEEM,
                'ontvanger': data.stuurgegevens.zender,
                'referentienummer': create_unique_id(),
                'tijdstipBericht': stuf_datetime.now()
            },
        }
