from django.conf import settings
from django.utils.module_loading import import_string

from spyne import ServiceBase, rpc

from ...rgbz.models import Zaak
from ..zds.vrijeberichten import (
    GenereerIdentificatieInputBuilder, GenereerIdentificatieOutputBuilder
)

input_builder = GenereerIdentificatieInputBuilder('genereerZaakidentificatie', 'gzi')
output_builder = GenereerIdentificatieOutputBuilder('genereerZaakidentificatie', 'gzi', 'zaak', 'ZAK')


class GenereerZaakIdentificatie(ServiceBase):
    """
    De "genereer Zaakidentificatie"-service biedt ZSC's de mogelijkheid om een
    uniek en geldige Zaakidentificatie te ontvangen. De ZSC stuurt hiervoor een
    vrij bericht genereerZaakIdentificatie_Di02 naar het ZS en ontvangt
    synchroon als reactie de Zaakidentificatie in een
    genereerZaakIdentificatie_Du02-bericht.

    Zie: ZDS 1.2, paragraaf 4.1.6
    """
    input_model = input_builder.create_model()
    output_model = output_builder.create_model()

    @rpc(input_model, _body_style="bare", _out_message_name="genereerZaakIdentificatie_Du02", _returns=output_model)
    def genereerZaakIdentificatie_Di02(ctx, data):

        # Eisen aan ZS:
        #
        # * De uitgegeven Zaakidentificatie wordt gereserveerd en wordt
        #   eenmalig uitgegeven;
        # * De uitgegeven Zaakidentificatie is uniek binnen de gemeente;
        # * Er wordt direct (synchroon) een Zaakidentificatie teruggestuurd;
        # * Het formaat van de zaakidentificatie voldoet aan het RGBZ
        #   (maximaal 40 alfanumerieke karakters waarvan de eerste vier gevuld
        #   zijn met de gemeentecode van de gemeente die verantwoordelijk is
        #   voor de behandeling van de zaak).

        # Interactie tussen ZSC en ZS:
        #
        # Het inkomende bericht heeft naast de stuurgegevens geen verplichte
        # elementen. Wel dient het stuurgegeven "functie" de waarde
        # "genereerZaakidentificatie" te hebben.
        #
        # Het ZS dient als reactie op het inkomende bericht met functie
        # "genereerZaakidentificatie" te antwoorden met een vrij bericht
        # (Du02). Ook in dit bericht is het stuurgegeven ‘functie’ gevuld met
        # de waarde "genereerZaakidentificatie". Na de stuurgegevens volgt een
        # element zaak met attribuut StUF:entiteittype="ZAK". Binnen zaak is
        # één verplicht element opgenomen, namelijk de zaakidentificatie. Dit
        # bericht is exact beschreven in de bij deze specificatie behorende XML
        # Schema’s.

        func = import_string(settings.ZAAKMAGAZIJN_ZAAK_ID_GENERATOR)

        # Find an unused uuid. Hopefully this does never go trough more than 1 iteration.
        while True:
            zaakidentificatie = func(data)
            if not Zaak.objects.filter(zaakidentificatie=zaakidentificatie).exists():
                break

        return output_builder.create_data(data, zaakidentificatie)
