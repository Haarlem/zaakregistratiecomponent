from spyne import ServiceBase, rpc

from ...rgbz.models import Besluit
from ..utils import create_unique_id
from ..zds.vrijeberichten import (
    GenereerIdentificatieInputBuilder, GenereerIdentificatieOutputBuilder
)

input_builder = GenereerIdentificatieInputBuilder('genereerBesluitidentificatie', 'gbi')
output_builder = GenereerIdentificatieOutputBuilder('genereerBesluitidentificatie', 'gbi', 'besluit', 'BSL')


class GenereerBesluitIdentificatie(ServiceBase):
    """
    De "Genereer Besluitidentificatie"-service biedt ZSC's de mogelijkheid om
    een uniek en geldige Besluitidentificatie op te halen. De ZSC stuurt
    hiervoor een vrij bericht naar het ZS en ontvangt synchroon als reactie een
    geldige Besluitidentificatie.

    Zie: ZDS 1.2, paragraaf 4.1.9
    """
    input_model = input_builder.create_model()
    output_model = output_builder.create_model()

    @rpc(input_model, _body_style="bare", _out_message_name="genereerBesluitIdentificatie_Du02", _returns=output_model)
    def genereerBesluitIdentificatie_Di02(ctx, data):

        # Eisen aan ZS:
        #
        # * De uitgegeven Besluitidentificatie wordt gereserveerd en wordt
        #   eenmalig uitgegeven;
        # * De uitgegeven Besluitidentificatie is uniek binnen de gemeente;
        # * Er wordt direct (synchroon) een Besluitidentificatie teruggestuurd.

        # Interactie tussen ZSC en ZS:
        #
        # De interactie tussen ZSC en ZS is gebaseerd op vrije berichten. Het
        # inkomende bericht (genereerBesluitIdentificatie_Di02) heeft naast de
        # stuurgegevens geen verplichte elementen. Wel dient het stuurgegeven
        # "functie" de waarde "genereerBesluitidentificatie" te hebben.
        #
        # De serviceprovider dient als reactie op het inkomende bericht met
        # functie "genereerBesluitidentificatie" te antwoorden met een vrij
        # bericht (Du02). Ook in dit bericht is het stuurgegeven "functie"
        # gevuld met de waarde “genereerBesluitidentificatie”. Na de
        # stuurgegevens volgt een element besluit met attribuut
        # StUF:entiteittype="BSL". Binnen besluit is één verplicht element
        # opgenomen namelijk de Besluitidentificatie.

        # Find an unused uuid. Hopefully this does never go trough more than 1 iteration.
        while True:
            identificatie = create_unique_id()
            if not Besluit.objects.filter(identificatie=identificatie).exists():
                break

        return output_builder.create_data(data, identificatie)
