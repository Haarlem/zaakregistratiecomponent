from spyne import ServiceBase, rpc

from zaakmagazijn.rgbz_mapping.models import (
    StatusProxy, StatusTypeProxy, ZaakProxy, ZaakTypeProxy
)

from ..stuf import ForeignKeyRelation, OneToManyRelation, StUFEntiteit
from ..stuf.models import (
    ParametersAntwoordSynchroon, ZAK_parametersVraagSynchroon
)
from ..zds import La01Builder, Lv01Builder
from ..zds.entiteiten.betrokkene import (
    MedewerkerEntiteit, NatuurlijkPersoonEntiteit,
    NietNatuurlijkPersoonEntiteit, OrganisatorischeEenheidEntiteit,
    VestigingEntiteit, ZAKBTRBLHEntiteit, ZAKBTRGMCEntiteit, ZAKBTRINIEntiteit,
    ZAKBTROVREntiteit, ZAKBTRUTVEntiteit, ZAKBTRVRAEntiteit
)
from ..zds.entiteiten.group_attributes import (
    AnderZaakObjectGegevensgroep, KenmerkGegevensgroep,
    OpschortingGegevensgroep, ResultaatGegevensgroep, VerlengingGegevensgroep
)
from ..zds.entiteiten.objecten import ZaakObjectEntiteit


class StatusTypeEntiteit(StUFEntiteit):
    mnemonic = 'STT'
    model = StatusTypeProxy
    field_mapping = (
        ('zkt.omschrijving', 'zaaktype__zaaktypeomschrijving'),
        ('volgnummer', 'volgnummer'),
        ('omschrijving', 'omschrijving'),
    )


class ZAKSTTBTREntiteit(StUFEntiteit):
    model = StatusProxy
    mnemonic = 'ZAKSTTBTR'
    field_mapping = ()
    gegevensgroepen = ()
    # 'is_gezet_door' being a callable will only work for Beantwoordvraag
    # services, not for Kennisgevingsberichten.
    gerelateerde = ('is_gezet_door', (
        ('medewerker', MedewerkerEntiteit),
        ('organisatorischeEenheid', OrganisatorischeEenheidEntiteit),
        ('vestiging', VestigingEntiteit),
        ('natuurlijkPersoon', NatuurlijkPersoonEntiteit),
        ('nietNatuurlijkPersoon', NietNatuurlijkPersoonEntiteit),
    ), )
    fields = (
        'gerelateerde',
        # 'extraElementen',
    )
    matching_fields = (
        'gerelateerde'
    )


class StatusEntiteit(StUFEntiteit):
    mnemonic = 'ZAKSTT'
    model = StatusProxy
    field_mapping = (
        ('toelichting', 'toelichting'),
        ('datumStatusGezet', 'datum_status_gezet'),
        ('indicatieLaatsteStatus', 'indicatie_laatst_gezette_status'),
    )
    related_fields = (
        OneToManyRelation('isGezetDoor', 'self', ZAKSTTBTREntiteit, min_occurs=1, max_occurs=1),
    )
    filter_fields = ('indicatieLaatsteStatus', )
    gerelateerde = ('status_type', StatusTypeEntiteit)
    matching_fields = [
        'gerelateerde'
    ]
    fields = (
        'gerelateerde',
        'toelichting',
        'datumStatusGezet',
        'indicatieLaatsteStatus',
    )
    required_fields = (
        'toelichting',
    )


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
        # Kenmerk
        # Resultaat
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
        # <heeftAlsBelanghebbende,
        # heeftAlsGemachtigde,
        # heeftAlsInitiator,
        # heeftAlsUitvoerende,
        # heeftAlsVerantwoordelijke,
        # heeftAlsOverigBetrokkene>
        # heeft
        # isVan
    )
    filter_fields = ('identificatie', )
    input_parameters = ZAK_parametersVraagSynchroon
    output_parameters = ParametersAntwoordSynchroon
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
        OneToManyRelation('heeft', 'status_set', StatusEntiteit),
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
        'tijdvakGeldigheid',
        'tijdstipRegistratie',
        # extraElementen
        'isVan',
        'heeftBetrekkingOp',
        'heeftAlsBelanghebbende',
        'heeftAlsGemachtigde',
        'heeftAlsInitiator',
        'heeftAlsUitvoerende',
        'heeftAlsVerantwoordelijke',
        'heeftAlsOverigBetrokkene',
        'heeft',
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


input_builder = Lv01Builder(ZaakEntiteit, 'GeefZaakdetails')
output_builder = La01Builder(ZaakEntiteit, 'GeefZaakdetails')


class GeefZaakdetails(ServiceBase):
    """
    De "geef Zaakdetails"-service biedt ZSC's de mogelijkheid om attributen
    van een lopende zaak en gerelateerde objecten op te vragen middels een
    vraag-/antwoordinteractie.

    Zie: ZDS 1.2, paragraaf 4.1.2
    """
    input_model = input_builder.create_model()
    output_model = output_builder.create_model()

    @rpc(input_model, _body_style="bare", _out_message_name="geefZaakdetails_ZakLa01", _returns=output_model)
    def geefZaakdetails_ZakLv01(ctx, data):
        """
        Opvragen meest actuele gegevens van een lopende zaak.
        """

        # Eisen aan ZS:
        #
        # Het ZS retourneert alle attributen waarnaar de ZSC vraagt in het
        # vraagbericht. Eventueel kan het ZS hierbij gebruik maken van het
        # attribuut StUF:noValue, zie StUF 03.01 paragraaf 3.4

        # Interactie tussen ZSC en ZS:
        #
        # Tussen ZSC en ZS is een vraag-/antwoordinteractie.

        # Opmerkingen:
        #
        # Ook voor het GeefZaakDetails bericht is het mogelijk om
        # niet-authentieke contactgegevens op te nemen.

        return output_builder.create_data(data, GeefZaakdetails.output_model)
