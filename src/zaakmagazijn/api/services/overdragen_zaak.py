
from spyne import ServiceBase, rpc

from ..stuf.models import Bv03Bericht
from ..stuf.utils import get_bv03_stuurgegevens
from ..zds.entiteiten.overdragen_zaak import (
    DI01_overdragenZaak, Du01_overdragenZaak
)


class OverdragenZaak(ServiceBase):
    """
    Wanneer de afhandeling van een zaak plaatsvindt bij een Zaakservice
    consumer dan dient deze consumer tevens provider te zijn van de Overdragen
    te behandelen Zaak service. Het ZS kan de behandeling van een zaak via deze
    service overdragen aan de Zaakservice consumer.

    Zie: ZDS 1.2, paragraaf 4.2
    """
    @rpc(Du01_overdragenZaak, _body_style="bare", _out_message_name="{http://www.egem.nl/StUF/StUF0301}Bv03Bericht", _returns=Bv03Bericht)
    def overdragenZaak_Du01(ctx, data):
        # Undocumented but technically, a ZSC can tell us it accepted or denied
        # the Zaak.

        if data.object.antwoord == 'Overdracht geaccepteerd':
            # TODO [KING]: Taiga #237 Het is onduidelijk wat een ZS moet doen als een ZSC een zaak overdracht accepteerd of weigert.
            pass

        return {
            'stuurgegevens': get_bv03_stuurgegevens(data),
        }

    # Capital I as per spec...
    @rpc(DI01_overdragenZaak, _body_style="bare", _out_message_name="{http://www.egem.nl/StUF/StUF0301}Bv03Bericht", _returns=Bv03Bericht)
    def overdragenZaak_Di01(ctx, data):
        """
        De "Overdragen te behandelen Zaak" service biedt het ZS de mogelijkheid
        om de behandeling van een zaak over te dragen aan een Zaakservice
        consumer (meestal een sectorspecifieke backoffice applicatie). De
        identificerende gegevens van de over te dragen zaak worden door het ZS
        verstuurd naar Zaakservice consumer. Deze geeft aan of de behandeling
        wordt overgenomen of dat deze wordt geweigerd. De Zaakservice consumer
        kan vervolgens via de geefZaakdetails service aanvullende gegevens over
        de zaak ophalen bij het ZS.
        """

        # NOTE:
        #
        # This endpoint is only used by tests. We will never get a zaak
        # transfered to us. We therefore intentionally do nothing in this
        # function, except returning a response.

        # Eisen aan ZSC:
        #
        # De ZSC verwerkt berichten asynchroon en direct ("near realtime");

        return {
            'stuurgegevens': get_bv03_stuurgegevens(data),
        }
