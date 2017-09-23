from django.conf import settings

from spyne import ServiceBase, rpc

from zaakmagazijn.api.utils import create_unique_id

from ...utils import stuf_datetime
from ..stuf.choices import BerichtcodeChoices, ServerFoutChoices
from ..stuf.faults import StUFFault
from ..stuf.models import Bv03Bericht
from ..stuf.utils import to_django_value
from ..utils import create_unique_id
from ..zds.entiteiten.zaken import ZaakEntiteit
from ..zds.kennisgevingsberichten import Lk01Builder, process_create

input_builder = Lk01Builder(ZaakEntiteit, 'CreeerZaak')


class CreeerZaak(ServiceBase):
    """
    De "creëer Zaak"-service biedt ZSC's de mogelijkheid om een lopende zaak
    toe te voegen in het ZS middels een kennisgevingsbericht. Er dient altijd
    een geldige Zaakidentificatie aangeleverd te worden. De ZSC kan hiervoor
    zelf een zaakidentificatie genereren of de ZSC kan gebruik maken van de
    "genereerZaakIdentificatie"-service om een geldige zaakidentificatie op te
    vragen.

    Zie: ZDS 1.2, paragraaf 4.1.4
    """
    input_model = input_builder.create_model()
    output_model = Bv03Bericht

    @rpc(input_model, _body_style="bare", _out_message_name="Bv03Bericht", _returns=Bv03Bericht)
    def creeerZaak_ZakLk01(ctx, data):
        """
        Er is een nieuwe zaak ontvangen.
        """

        # Eisen aan ZS:
        #
        # * Het ontstaan van de zaak wordt gesynchroniseerd met het DMS.
        #   Hiervoor voert het ZS de benodigde CMIS-operaties "near real time"
        #   uit.
        # * Het ZS controleert of toegestuurde zaakidentificaties uniek zijn
        #   en voldoen aan het RGBZ

        # Interactie tussen ZSC en ZS:
        #
        # De ZSC stuurt een kennisgeving naar het ZS waarin aangegeven wordt
        # dat er een nieuwe zaak aan de zakenregistratie toegevoegd moet
        # worden.

        # Interactie tussen ZS en DMS:
        #
        # Het ZS voert CMIS-operaties uit, zodat:
        # * In het DMS een Zaaktype-object gecreëerd wordt indien deze nog niet
        #   bestaat. Het gecreeerde Zaaktype moet aanwezig zijn in de lijst met
        #   vastgelegde Zaaktypes;
        # * In het DMS een Zaakfolder-object gecreëerd wordt;

        process_create(ZaakEntiteit, data)

        return {
            'stuurgegevens': {
                'berichtcode': BerichtcodeChoices.bv03,
                'zender': settings.ZAAKMAGAZIJN_SYSTEEM,
                'ontvanger': data.stuurgegevens.zender,
                'referentienummer': create_unique_id(),
                'tijdstipBericht': stuf_datetime.now()
            },
        }
