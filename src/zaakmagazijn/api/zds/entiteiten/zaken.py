from zaakmagazijn.rgbz.models import (
    Besluit, InformatieObject as InformatieObjectModel, Status, StatusType,
    Zaak, ZaakInformatieObject, ZaakObject, ZaakType
)

from ...stuf import (
    ForeignKeyRelation, OneToManyRelation, StUFEntiteit, StUFKerngegevens
)
from ...stuf.models import ZAK_parametersVraagSynchroon
from .besluiten import BesluitEntiteit
from .betrokkene import (
    KlantcontactEntiteit, ZAKBRTBSSEntiteit, ZAKBTRADVEntiteit,
    ZAKBTRBHLEntiteit, ZAKBTRBLHEntiteit, ZAKBTRBTREntiteit, ZAKBTRGMCEntiteit,
    ZAKBTRINIEntiteit, ZAKBTRKCREntiteit, ZAKBTRZKCEntiteit, ZAKSTTBTREntiteit
)
from .group_attributes import (
    AnderZaakObjectGegevensgroep, KenmerkGegevensgroep,
    OpschortingGegevensgroep, VerlengingGegevensgroep
)
from .objecten import ZaakKerngegevens, ZaakObjectEntiteit


class ZAKBSLEntiteit(StUFEntiteit):
    mnemonic = 'ZAKBSL'
    model = Besluit
    field_mapping = ()
    gerelateerde = ('self', BesluitEntiteit)
    matching_fields = [
        'gerelateerde'
    ]


class ZAKZAKDELEntiteit(StUFEntiteit):
    mnemonic = 'ZAKZAKDEL'
    model = Zaak
    field_mapping = ()

    gerelateerde = ('self', ZaakKerngegevens)
    matching_fields = [
        'gerelateerde'
    ]


#
# These aren't needed by the ZDS specification.
#
# class InformatieObject(StUFEntiteit):
#     mnemonic = 'IOB'
#     model = InformatieObjectModel
#     field_mapping = (
#         # TODO: [KING] I guessed this, since this relation is not described in ZDS
#         # nor in StUF-ZKN. And I don't have a copy of StUF-ZKN 3.2 yet.
#         ('identificatie', 'informatieobjectidentificatie'),
#         ('bronorganisatie', 'bronorganisatie'),
#         ('ontvangstdatum', 'ontvangstdatum'),
#         ('afzender', 'afzender'),
#         ('titel', 'titel'),
#         ('beschrijving', 'beschrijving'),
#         ('versie', 'versie'),
#         ('status', 'status'),
#         ('verzenddatum', 'verzenddatum'),
#         ('geadresseerde', 'geadresseerde'),
#         ('vertrouwlijkaanduiding', 'vertrouwlijkaanduiding'),
#         ('gebruiksrechten', 'gebruiksrechten'),
#         ('archiefnominatie', 'archiefnominatie'),
#         ('archiefactiedatum', 'archiefactiedatum'),
#         ('auteur', 'auteur'),
#         ('ondertekening', 'ondertekening'),
#         ('verschijningsvorm', 'verschijningsvorm'),
#     )
#     matching_fields = [
#         'identificatie',
#         'bronorganisatie',
#     ]


# class ZaakInformatieObjectEntiteit(StUFEntiteit):
#     mnemonic = 'ZAKIOB'
#     model = ZaakInformatieObject
#     field_mapping = (
#         # TODO: [KING] All these fields, I guessed. They are not described anywhere.
#         ('titel', 'titel'),
#         ('beschrijving', 'beschrijving'),
#         ('registratiedatum', 'registratiedatum'),
#         # TODO: [COMPAT] We vermoeden dat ZAKIOB 'platgeslagen' Status elementen (zoals in ZKN 03.20 staat) geprefixed worden met "sta.*"
#         ('sta.toelichting', 'status__statustoelichting'),
#         ('sta.datumStatusGezet', 'status__datum_status_gezet'),
#         ('sta.indicatieLaatsteStatus', 'status__indicatie_laatst_gezette_status'),
#     )
#     gerelateerde = ('informatieobject', InformatieObject)

#     matching_fields = [
#         'gerelateerde',
#     ]


class StatusTypeEntiteit(StUFEntiteit):
    mnemonic = 'STT'
    model = StatusType
    field_mapping = (
        ('omschrijving', 'statustypeomschrijving'),
        ('volgnummer', 'statustypevolgnummer'),
        ('omschrijvingGeneriek', 'statustypeomschrijving_generiek'),
        #
        #
        # TODO: [COMPAT] isVan relatie mist.
    )
    matching_fields = [
        'volgnummer',
        'omschrijving',
        'omschrijvingGeneriek',
        # 'isVan',
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
        # OneToManyRelation('heeftRelevant', 'heeft_relevant', ZaakInformatieObjectEntiteit),
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
        # TODO: [KING] Rol not defined in ZKN 3.2, but is defined in RGBZ 2.0
        # 0..N
        OneToManyRelation('heeftAlsGemachtigde', 'heeft_als_gemachtigde', ZAKBTRGMCEntiteit),

        # TODO: [KING] 'heeftAlsMedeInitiator'?
        # 1
        OneToManyRelation('heeftAlsZaakcoordinator', 'heeft_als_zaakcoordinator', ZAKBTRZKCEntiteit, min_occurs=1, max_occurs=1),
        # 0..N
        OneToManyRelation('heeftGerelateerde', 'heeft_gerelateerde', ZaakKerngegevens),

        # TODO: [KING] 'leidtTot' relatie-entiteit is not defined for updateZaak or
        # creeerZaak in the ZDS, but it does exist in the XSD. However processing
        # it is not mandatory according to the ZDS, but we choice to implement the processing.the
        #
        # See https://discussie.kinggemeenten.nl/discussie/gemma/stuf-testplatform/leidttot-updatezaakzaklk01
        #
        OneToManyRelation('leidtTot', 'leidt_tot', ZAKBSLEntiteit),

        # TODO: [COMPAT] Not part of ZDS 1.2
        OneToManyRelation('heeftContact', 'klantcontact_set', KlantcontactEntiteit),

        # Deviates from StUF-ZKN 3.1  # TODO: [COMPAT] ontbreekt in ZDS
        OneToManyRelation('heeftAlsDeelzaken', 'heeft_deelzaken', ZAKZAKDELEntiteit),

        # Deviates from StUF-ZKN 3.1; Not part of ZDS
        # OneToManyRelation('isDeelzaakVan', 'hoofdzaak', ZaakKerngegevens),  # is_deelzaak_van

        # TODO: [COMPAT] heeftBetrekkingOpAndere -> ZakenRelatie.andere_zaak
        # OneToManyRelation('heeftBetrekkingOpAndere', '', ''),

        # This relation exists in keuzenVerstuffen 2.0, but does not exist in the
        # data model. I haven't checked if it exists in RGBZ 2.0, and was forgotten
        # to be implemented.
        # OneToManyRelation('isGerelateerdAan', ''),

        # TODO: [COMPAT] De isVan relatie is komen te vervallen in KeuzenVerStUFfing RGBZ 2.0
        # versie 0.3. En ZaakType is nu platgeslagen.
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
        'heeftAlsGemachtigde',
        'heeftAlsInitiator',
        'heeftAlsKlantcontacter',
        'heeftAlsZaakcoordinator',
        'heeftGerelateerde',
        'heeftAlsDeelzaken',
        'heeft',
        'leidtTot',
        'heeftContact',
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
