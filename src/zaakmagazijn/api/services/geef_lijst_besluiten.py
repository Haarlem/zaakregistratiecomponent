from spyne import ServiceBase, rpc

from zaakmagazijn.rgbz.models import Besluit, Zaak

from ..stuf import OneToManyRelation, StUFEntiteit
from ..stuf.models import ZAK_parametersVraagSynchroon
from ..zds import La01Builder, Lv01Builder

# class BesluitTypeEntiteit(StUFEntiteit):
#     mnemonic = 'BST'
#     model = BesluitType
#     field_mapping = (
#         ('beginGeldigheid', 'datum_begin_geldigheid_besluittype'),  # o
#         ('eindGeldigheid', 'datum_einde_geldigheid_besluittype'),  # o
#     )


class BesluitEntiteit(StUFEntiteit):
    mnemonic = 'BSL'
    model = Besluit
    field_mapping = (
        ('identificatie', 'identificatie'),  # v
        ('datumBeslissing', 'besluitdatum'),  # v
        ('bst.omschrijving', 'besluittype__besluittypeomschrijving'),  # o
        ('toelichting', 'besluittoelichting'),  # o
        ('ingangsdatumWerking', 'ingangsdatum'),  # v
        ('einddatumWerking', 'vervaldatum'),  # o
        ('vervalreden', 'vervalreden'),  # o
        ('datumPublicatie', 'publicatiedatum'),  # o
        ('datumVerzending', 'verzenddatum'),  # o
        ('datumUiterlijkeReactie', 'uiterlijke_reactiedatum'),  # o
        # TODO: [KING] Taiga #230
        ('tijdstipRegistratie', 'tijdstip_registratie'),  # o
    )
    # filter_fields = ('identificatie', )
    begin_geldigheid = 'besluittype__datum_begin_geldigheid_besluittype'
    eind_geldigheid = 'besluittype__datum_einde_geldigheid_besluittype'


class ZAKBSLEntiteit(StUFEntiteit):
    mnemonic = 'ZAKBSL'
    model = Zaak
    field_mapping = []
    gerelateerde = ('self', BesluitEntiteit)


class BesluitLijstEntiteit(StUFEntiteit):
    mnemonic = 'ZAK'
    model = Zaak
    field_mapping = (
        ('identificatie', 'zaakidentificatie'),
    )
    filter_fields = ('identificatie', )
    input_parameters = ZAK_parametersVraagSynchroon
    related_fields = (
        OneToManyRelation('leidtTot', 'besluit_set', ZAKBSLEntiteit),
    )


input_builder = Lv01Builder(BesluitLijstEntiteit, 'GeefLijstBesluiten')
output_builder = La01Builder(BesluitLijstEntiteit, 'GeefLijstBesluiten')


class GeefLijstBesluiten(ServiceBase):
    """
    De "geef LijstBesluiten"-service biedt ZSC's de mogelijkheid om een lijst
    met referenties op te vragen naar besluiten behorende bij een lopende zaak
    middels een vraag-/antwoordinteractie. In het antwoordbericht staan alle
    besluiten die bekend zijn bij het ZS.

    Zie: ZDS 1.2, paragraaf 4.1.11
    """
    input_model = input_builder.create_model()
    output_model = output_builder.create_model()

    @rpc(input_model, _body_style="bare", _out_message_name="geefLijstBesluiten_ZakLa01",
         _returns=output_model)
    def geefLijstBesluiten_ZakLv01(ctx, data):

        # Eisen aan ZS:
        #
        # * Het ZS is de authentieke bron voor de aan de ZAAK gerelateerde
        #   besluiten;
        # * Het ZS retourneert alle voor hem bekende besluit relaties in het
        #   antwoordbericht.

        # Interactie tussen ZSC en ZS:
        #
        # Tussen ZSC en ZS is een vraag-/antwoordinteractie.

        return output_builder.create_data(data, GeefLijstBesluiten.output_model)
