
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
from ..zds.entiteiten.objecten import ZaakObjectEntiteit
from ..zds.kennisgevingsberichten import Lk01Builder, process_update


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
    )
    matching_fields = (
        'identificatie',
        'omschrijving',
        # TODO [TECH]: Matching field on relation not supported yet.
        # 'isVan',
    )


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

    @rpc(input_model, _body_style="bare", _out_message_name="{http://www.egem.nl/StUF/StUF0301}Bv03Bericht", _returns=output_model)
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
            'stuurgegevens': get_bv03_stuurgegevens(data),
        }
