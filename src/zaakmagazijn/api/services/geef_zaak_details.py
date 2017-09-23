from spyne import ServiceBase, rpc

from zaakmagazijn.rgbz.models import (
    Besluit, InformatieObject as InformatieObjectModel, Status, StatusType,
    Zaak, ZaakInformatieObject as ZaakInformatieObjectModel, ZaakObject,
    ZaakType
)

from ..stuf import OneToManyRelation, StUFEntiteit, StUFKerngegevens
from ..stuf.models import ZAK_parametersVraagSynchroon
from ..zds import La01Builder, Lv01Builder
from ..zds.entiteiten.betrokkene import (
    ZAKBRTBSSEntiteit, ZAKBTRADVEntiteit, ZAKBTRBHLEntiteit, ZAKBTRBLHEntiteit,
    ZAKBTRBTREntiteit, ZAKBTRGMCEntiteit, ZAKBTRINIEntiteit, ZAKBTRKCREntiteit,
    ZAKBTRZKCEntiteit, ZAKSTTBTREntiteit
)
from ..zds.entiteiten.group_attributes import (
    AnderZaakObjectGegevensgroep, KenmerkGegevensgroep,
    OpschortingGegevensgroep, VerlengingGegevensgroep
)
from ..zds.entiteiten.objecten import ZaakObjectEntiteit
from ..zds.entiteiten.zaken import ZAKBSLEntiteit, ZAKZAKDELEntiteit


class StatusTypeEntiteit(StUFEntiteit):
    """
    Note: This is not really part of ZDS, but every relatie-entiteit needs a
    gerelateerde.
    """
    mnemonic = 'STT'
    model = StatusType
    field_mapping = (
        ('omschrijving', 'statustypeomschrijving'),
        ('volgnummer', 'statustypevolgnummer'),
        ('omschrijvingGeneriek', 'statustypeomschrijving_generiek'),
    )
    matching_fields = [
        'volgnummer',
        'omschrijving',
        'omschrijvingGeneriek',
    ]


class StatusEntiteit(StUFEntiteit):
    mnemonic = 'ZAKSTT'
    model = Status
    field_mapping = (
        ('toelichting', 'statustoelichting'),
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


class ZaakEntiteit(StUFEntiteit):
    mnemonic = 'ZAK'
    model = Zaak
    field_mapping = (
        ('identificatie', 'zaakidentificatie'),
        # TODO: [COMPAT] (ZAK) Element "bronorganisatie" in creeerZaak ontbreekt in ZDS maar bestaat wel in RGBZ.
        ('bronorganisatie', 'bronorganisatie'),
        # TODO: [COMPAT] (ZAK) Element "archiefstatus" in creeerZaak ontbreekt in ZDS maar bestaat wel in RGBZ.
        ('archiefstatus', 'archiefstatus'),
        # TODO: [COMPAT] (ZAK) Element "verantwoordelijkeOrganisatie" in creeerZaak ontbreekt in ZDS maar bestaat wel in RGBZ.
        ('verantwoordelijkeOrganisatie', 'verantwoordelijke_organisatie'),
        ('einddatum', 'einddatum'),
        ('einddatumGepland', 'einddatum_gepland'),
        ('omschrijving', 'omschrijving'),
        # TODO: [KING] This deviates from the ZDS
        ('resultaatomschrijving', 'resultaatomschrijving'),
        ('resultaattoelichting', 'resultaattoelichting'),
        ('startdatum', 'startdatum'),
        ('toelichting', 'toelichting'),
        # We use the ZKN 0320 name "uiterlijkeEinddatumAfdoening" instead of the 0310 version "uiterlijkeEinddatum"
        ('uiterlijkeEinddatumAfdoening', 'uiterlijke_einddatum_afdoening'),
        # TODO: [COMPAT] Missing from the RGBZ
        # ('zaakniveau', 'zaakniveau'),
        # TODO: [COMPAT] Missing form the RGBZ
        # ('deelzakenIndicatie', 'deelzakenIndicatie'),
        ('registratiedatum', 'registratiedatum'),
        ('publicatiedatum', 'publicatiedatum'),
        ('archiefnominatie', 'archiefnominatie'),
        # TODO: [COMPAT] Missing from RGBZ
        # ('datumVernietigingDossier', 'datumVernietigingDossier'),
        ('betalingsIndicatie', 'betalingsindicatie'),
        ('laatsteBetaaldatum', 'laatste_betaaldatum'),
        ('zkt.omschrijving', 'zaaktype__zaaktypeomschrijving'),
        ('zkt.identificatie', 'zaaktype__zaaktypeidentificatie'),
    )
    filter_fields = ('identificatie', )
    input_parameters = ZAK_parametersVraagSynchroon
    # TODO: [TECH] output_parameters = ???
    related_fields = (
        # TODO: [COMPAT] isVan staat wel in ZDS 1.2, maar bestaat niet meer in ZKN 3.2. in ZKN 3.2, is
        # Zaaktype platgeslagen. isVan is vervangen met (zkt.omschrijving, zkt.identificatie)
        # ('isVan', 'zaaktype', ZaakTypeEntiteit),

        # from ZDS 1.2
        # ('heeftAlsUitvoerende', '', ZAKBTRUTVEntiteit),
        # ('heeftAlsVerantwoordelijke', 'verantwoordelijke', ZAKBTRVRAEntiteit),
        # ('heeftAlsOverigBetrokkene', '', ZAKBTROVREntiteit),

        OneToManyRelation('heeft', 'status_set', StatusEntiteit),
        # 0..n
        OneToManyRelation('heeftBetrekkingOp', 'zaakobject_set', ZaakObjectEntiteit),
        # 0..n
        OneToManyRelation('heeftAlsBetrokkene', 'heeft_als_betrokkene', ZAKBTRBTREntiteit),
        # 0..n
        OneToManyRelation('heeftAlsAdviseur', 'heeft_als_adviseur', ZAKBTRADVEntiteit),
        # 0..n
        OneToManyRelation('heeftAlsBelanghebbende', 'heeft_als_belanghebbende', ZAKBTRBLHEntiteit),
        # 0..n
        OneToManyRelation('heeftAlsBehandelaar', 'heeft_als_behandelaar', ZAKBTRBHLEntiteit),
        # 0..n
        OneToManyRelation('heeftAlsBeslisser', 'heeft_als_beslisser', ZAKBRTBSSEntiteit),
        # 1
        OneToManyRelation('heeftAlsInitiator', 'heeft_als_initiator', ZAKBTRINIEntiteit, min_occurs=1, max_occurs=1),
        # 0..N
        OneToManyRelation('heeftAlsKlantcontacter', 'heeft_als_klantcontacter', ZAKBTRKCREntiteit),
        # TODO: [COMPAT] Rol not defined in ZKN 3.2, but is defined in RGBZ 2.0
        # 0..N
        # OneToManyRelation('heeftAlsGemachtigde', 'heeft_als_gemachtigde', ZAKBTRGMCEntiteit),

        # TODO: [COMPAT] 'heeftAlsMedeInitiator'?
        # 1
        OneToManyRelation('heeftAlsZaakcoordinator', 'heeft_als_zaakcoordinator', ZAKBTRZKCEntiteit, min_occurs=1, max_occurs=1),

        # TODO [KING] Taiga #259 The ZDS specification says nothing about 'leidtTot'
        OneToManyRelation('leidtTot', 'leidt_tot', ZAKBSLEntiteit),

        # Deviates from StUF-ZKN 3.1  # TODO: ontbreekt in ZDS
        OneToManyRelation('heeftAlsDeelzaken', 'heeft_deelzaken', ZAKZAKDELEntiteit),
    )
    gegevensgroepen = (
        # TODO [KING] Taiga #251 In ZKN 3.2 this has a max_occurs of 1, but in ZDS 1.2 this has a max_occurs of unbounded. I'm
        # assuming this was a mistake.
        OneToManyRelation('kenmerk', 'groep_kenmerken', KenmerkGegevensgroep),
        OneToManyRelation('anderZaakObject', 'groep_anderzaakobject', AnderZaakObjectGegevensgroep),
        OneToManyRelation('opschorting', 'groep_zaakopschorting', OpschortingGegevensgroep, min_occurs=0, max_occurs=1),
        OneToManyRelation('verlenging', 'groep_zaakverlenging', VerlengingGegevensgroep, min_occurs=0, max_occurs=1),
    )
    fields = (
        'identificatie',
        'bronorganisatie',
        'archiefstatus',
        'verantwoordelijkeOrganisatie',
        'omschrijving',
        'toelichting',
        'kenmerk',
        'anderZaakObject',
        'resultaatomschrijving',
        'resultaattoelichting',
        'startdatum',
        'registratiedatum',
        'publicatiedatum',
        'einddatumGepland',
        'uiterlijkeEinddatumAfdoening',
        'einddatum',
        'opschorting',
        'verlenging',
        'betalingsIndicatie',
        'laatsteBetaaldatum',
        'archiefnominatie',
        'zkt.omschrijving',
        'zkt.identificatie',
        # datumVernietigingDossier?
        # zaakniveau?
        # deelzaakindicatie?
        # tijdvakgeldigheid
        # tijdstipregistratie
        # extraElementen
        'heeftBetrekkingOp',
        'heeftAlsBetrokkene',
        'heeftAlsAdviseur',
        'heeftAlsBelanghebbende',
        'heeftAlsBehandelaar',
        'heeftAlsBeslisser',
        'heeftAlsInitiator',
        'heeftAlsKlantcontacter',
        'heeftAlsZaakcoordinator',
        'heeftAlsDeelzaken',
        'heeft',
        'leidtTot',
    )

    matching_fields = [
        # TODO: [COMPAT] in ZKN 3.2 this is called 'zaakidentificatie'.
        'identificatie',
        'bronorganisatie',
        'omschrijving',
        # TODO: [COMPAT] In ZDS 1.2 is 'isVan' hier ook opgegenomen. Maar in ZKN 3.2 bestaat
        # dit niet meer, mogelijk moet zkt.identificatie en zkt.omschrijving hier ook opgenomen
        # worden. (Maar in ZKN-3.2. staat dat niet).
    ]


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
