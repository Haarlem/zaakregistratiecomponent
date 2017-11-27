
from spyne import ServiceBase, rpc

from zaakmagazijn.rgbz_mapping.models import ZaakProxy, ZaakTypeProxy

from ..stuf import ForeignKeyRelation, OneToManyRelation, StUFEntiteit
from ..stuf.models import Bv03Bericht, ZAK_parametersVraagSynchroon
from ..stuf.utils import get_bv03_stuurgegevens
from ..zds.entiteiten.betrokkene import (
    ZAKBTRBLHEntiteit, ZAKBTRGMCEntiteit, ZAKBTRINIEntiteit, ZAKBTROVREntiteit,
    ZAKBTRUTVEntiteit, ZAKBTRVRAEntiteit
)
from ..zds.entiteiten.group_attributes import (
    AnderZaakObjectGegevensgroep, KenmerkGegevensgroep,
    OpschortingGegevensgroep, ResultaatGegevensgroep, VerlengingGegevensgroep
)
from ..zds.entiteiten.objecten import ZaakKerngegevens, ZaakObjectEntiteit
from ..zds.kennisgevingsberichten import Lk01Builder, process_create


class ZKTEntiteit(StUFEntiteit):
    model = ZaakTypeProxy
    mnemonic = 'ZKT'

    field_mapping = (
        ('omschrijving', 'zaaktypeomschrijving'),
        ('code', 'zaaktypecode'),
        # TODO [KING]: This is not part of ZDS, but expected by STP.
        ('ingangsdatumObject', 'datum_begin_geldigheid_zaaktype'),
    )
    matching_fields = (
        'omschrijving',
        'code',
        'ingangsdatumObject',
    )


class ZAKZKTEntiteit(StUFEntiteit):
    model = ZaakProxy
    mnemonic = 'ZAKZKT'
    field_mapping = ()
    gerelateerde = ('self', ZKTEntiteit)
    matching_fields = (
        'gerelateerde',
    )

# TODO [KING]: Not part of ZDS 1.2 but needed by RGBZ mapping: https://discussie.kinggemeenten.nl/discussie/gemma/stuf-testplatform/deelzaakindicatie-creeerzaak-volgnr-1-staat-onterecht-op-j
# class ZAKZAKDELEntiteit(StUFEntiteit):
#     mnemonic = 'ZAKZAKDEL'
#     model = ZaakProxy
#     field_mapping = ()
#     gerelateerde = ('self', ZaakKerngegevens)
#     matching_fields = (
#         'gerelateerde',
#     )


class ZaakEntiteit(StUFEntiteit):
    mnemonic = 'ZAK'
    model = ZaakProxy
    field_mapping = (
        ('identificatie', 'zaakidentificatie'),
        ('einddatum', 'einddatum'),
        ('einddatumGepland', 'einddatum_gepland'),
        ('omschrijving', 'omschrijving'),
        # kenmerk
        # resultaat
        ('startdatum', 'startdatum'),
        ('toelichting', 'toelichting'),
        ('uiterlijkeEinddatum', 'uiterlijke_einddatum_afdoening'),
        ('zaakniveau', 'zaakniveau'),
        ('deelzakenIndicatie', 'deelzakenindicatie'),
        ('registratiedatum', 'registratiedatum'),
        ('publicatiedatum', 'publicatiedatum'),
        ('archiefnominatie', 'archiefnominatie'),
        ('datumVernietigingDossier', 'datum_vernietiging_dossier'),
        ('betalingsIndicatie', 'betalingsindicatie'),
        ('laatsteBetaaldatum', 'laatste_betaaldatum'),
        # opschorting
        # verlenging
        # anderZaakObject
        # heeftBetrekkingOp
        # heeftAlsBelanghebbende
        # heeftAlsGemachtigde
        # heeftAlsUitvoerende
        # heeftAlsVerantwoordelijke
        # heeftAlsOverigBetrokkene
        # heeftAlsInitiator
        # isVan
    )
    filter_fields = ('identificatie', )
    input_parameters = ZAK_parametersVraagSynchroon
    gegevensgroepen = (
        OneToManyRelation('kenmerk', 'groep_kenmerken', KenmerkGegevensgroep),
        ForeignKeyRelation('resultaat', 'self', ResultaatGegevensgroep),
        OneToManyRelation('verlenging', 'groep_zaakverlenging', VerlengingGegevensgroep, min_occurs=0, max_occurs=1),
        OneToManyRelation('opschorting', 'groep_zaakopschorting', OpschortingGegevensgroep, min_occurs=0, max_occurs=1),
        OneToManyRelation('anderZaakObject', 'groep_anderzaakobject', AnderZaakObjectGegevensgroep),
    )
    related_fields = (
        ForeignKeyRelation('isVan', 'zaaktype', ZAKZKTEntiteit),
        OneToManyRelation('heeftBetrekkingOp', 'zaakobject_set', ZaakObjectEntiteit),
        OneToManyRelation('heeftAlsBelanghebbende', 'heeft_als_belanghebbende', ZAKBTRBLHEntiteit),
        OneToManyRelation('heeftAlsGemachtigde', 'heeft_als_gemachtigde', ZAKBTRGMCEntiteit),
        OneToManyRelation('heeftAlsInitiator', 'heeft_als_initiator', ZAKBTRINIEntiteit, min_occurs=1, max_occurs=1),
        OneToManyRelation('heeftAlsUitvoerende', 'heeft_als_uitvoerende', ZAKBTRUTVEntiteit),
        OneToManyRelation('heeftAlsVerantwoordelijke', 'heeft_als_verantwoordelijke', ZAKBTRVRAEntiteit),
        OneToManyRelation('heeftAlsOverigBetrokkene', 'heeft_als_overig_betrokkene', ZAKBTROVREntiteit),
        # TODO [KING]: Not part of ZDS 1.2 but needed by RGBZ mapping: https://discussie.kinggemeenten.nl/discussie/gemma/stuf-testplatform/deelzaakindicatie-creeerzaak-volgnr-1-staat-onterecht-op-j
        # OneToManyRelation('heeftAlsDeelzaak', 'heeft_deelzaken', ZAKZAKDELEntiteit)
    )
    fields = (
        'identificatie',
        'omschrijving',
        'toelichting',
        'kenmerk',
        'anderZaakObject',
        'resultaat',
        'startdatum',
        'registratiedatum',
        'publicatiedatum',
        'einddatumGepland',
        'uiterlijkeEinddatum',
        'einddatum',
        'opschorting',
        'verlenging',
        'betalingsIndicatie',
        'laatsteBetaaldatum',
        'archiefnominatie',
        'datumVernietigingDossier',
        'zaakniveau',
        'deelzakenIndicatie',
        # tijdvakgeldigheid
        # tijdstipregistratie
        # extraElementen
        'isVan',
        'heeftBetrekkingOp',
        'heeftAlsBelanghebbende',
        'heeftAlsGemachtigde',
        'heeftAlsInitiator',
        'heeftAlsUitvoerende',
        'heeftAlsVerantwoordelijke',
        'heeftAlsOverigBetrokkene',
        # TODO [KING]: Not part of ZDS 1.2 but needed by RGBZ mapping: https://discussie.kinggemeenten.nl/discussie/gemma/stuf-testplatform/deelzaakindicatie-creeerzaak-volgnr-1-staat-onterecht-op-j
        # 'heeftAlsDeelzaak',
    )
    matching_fields = (
        'identificatie',
        'omschrijving',
        # TODO [TECH]: Matching fields by relation are not supported yet.
        # 'isVan',
    )
    begin_geldigheid = 'begin_geldigheid'
    eind_geldigheid = 'eind_geldigheid'
    tijdstip_registratie = 'tijdstip_registratie'


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

    @rpc(input_model, _body_style="bare", _out_message_name="{http://www.egem.nl/StUF/StUF0301}Bv03Bericht", _returns=Bv03Bericht)
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
            'stuurgegevens': get_bv03_stuurgegevens(data),
        }
