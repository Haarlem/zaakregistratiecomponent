from djchoices import ChoiceItem, DjangoChoices


class JaNee(DjangoChoices):
    ja = ChoiceItem('J', 'Ja')
    nee = ChoiceItem('N', 'Nee')


class GeslachtsAanduiding(DjangoChoices):
    man = ChoiceItem('M', 'Man')
    vrouw = ChoiceItem('V', 'Vrouw')
    onbekend = ChoiceItem('O', 'Onbekend')


class VervalRedenen(DjangoChoices):
    """
    De omschrijving die aangeeft op grond waarvan het besluit is of komt te vervallen.
    """
    besluit_met_tijdelijke_werking = ChoiceItem('Besluit met tijdelijke werking', 'Besluit met tijdelijke werking')
    besluit_ingetrokken_door_overheid = ChoiceItem('Besluit ingetrokken door overheid',
                                                   'Besluit ingetrokken door overheid')
    besluit_ingetrokken_ovv_belanghebbende = ChoiceItem('Besluit ingetrokken o.v.v belanghebbende',
                                                        'Besluit ingetrokken o.v.v belanghebbende')


class InformatieObjectStatus(DjangoChoices):
    """
    Aanduiding van de stand van zaken van een INFORMATIEOBJECT
    """
    # De waarden ‘in bewerking’ en ‘ter vaststelling’ komen niet voor als de attribuutsoort Ontvangstdatum van een
    # waarde is voorzien.
    in_bewerking = ChoiceItem('in bewerking', 'in bewerking')
    ter_vaststelling = ChoiceItem('ter vaststelling ', 'ter vaststelling')
    definitief = ChoiceItem('definitief', 'definitief')
    gearchiveerd = ChoiceItem('gearchiveerd', 'gearchiveerd')
    # De waarden ‘vernietigd’ en ‘overgedragen’ komen niet voor als de attribuutsoort Archiefnominatie
    # de waarde ‘conform zaak’ heeft.
    vernietigd = ChoiceItem('vernietigd', 'vernietigd')
    overgedragen = ChoiceItem('overgedragen', 'overgedragen')


class Vertrouwelijkaanduiding(DjangoChoices):
    """
    Aanduiding van de mate waarin het INFORMATIEOBJECT voor de openbaarheid bestemd is.
    """
    zeer_geheim = ChoiceItem('ZEER GEHEIM', 'ZEER GEHEIM')
    geheim = ChoiceItem('GEHEIM', 'GEHEIM')
    confidentieel = ChoiceItem('CONFIDENTIEEL', 'CONFIDENTIEEL')
    vertrouwelijk = ChoiceItem('VERTROUWELIJK', 'VERTROUWELIJK')
    zaakvertrouwelijk = ChoiceItem('ZAAKVERTROUWELIJK', 'ZAAKVERTROUWELIJK')
    intern = ChoiceItem('INTERN', 'INTERN')
    beperkt_openbaar = ChoiceItem('BEPERKTOPENBAAR', 'BEPERKTOPENBAAR')
    openbaar = ChoiceItem('OPENBAAR', 'OPENBAAR')


class OmschrijvingVoorwaarden(DjangoChoices):
    geen_gebruiksrechten = ChoiceItem('Geen gebruiksrechten', 'Geen gebruiksrechten')
    hergebruik_onder_voorwaarden = ChoiceItem('Hergebruik onder voorwaarden', 'Hergebruik onder voorwaarden')
    verbod_op_hergebruik = ChoiceItem('Verbod op hergebruik', 'Verbod op hergebruik')


class ArchiefNominatie(DjangoChoices):
    vernietigen = ChoiceItem('Vernietigen', 'Vernietigen')
    blijvend_bewaren = ChoiceItem('Blijvend bewaren', 'Blijvend bewaren')


class InformatieObjectArchiefNominatie(ArchiefNominatie):
    conform_zaak = ChoiceItem('Conform zaak', 'Conform zaak')


class SoortRechtsvorm(DjangoChoices):
    besloten_vennootschap = ChoiceItem(
        'Besloten Vennootschap', 'Besloten Vennootschap')
    cooperatie_europees_economische_samenwerking = ChoiceItem(
        'Cooperatie, Europees Economische Samenwerking', 'Cooperatie, Europees Economische Samenwerking')
    europese_cooperatieve_vennootschap = ChoiceItem(
        'Europese Cooperatieve Venootschap', 'Europese Cooperatieve Venootschap')
    europese_naamloze_vennootschap = ChoiceItem(
        'Europese Naamloze Vennootschap', 'Europese Naamloze Vennootschap')
    kerkelijke_organisatie = ChoiceItem(
        'Kerkelijke Organisatie', 'Kerkelijke Organisatie')
    naamloze_vennootschap = ChoiceItem(
        'Naamloze Vennootschap', 'Naamloze Vennootschap')
    onderlinge_waarborg_maatschappij = ChoiceItem(
        'Onderlinge Waarborg Maatschappij', 'Onderlinge Waarborg Maatschappij')
    overig_privaatrechtelijke_rechtspersoon = ChoiceItem(
        'Overig privaatrechtelijke rechtspersoon', 'Overig privaatrechtelijke rechtspersoon')
    stichting = ChoiceItem(
        'Stichting', 'Stichting')
    vereniging = ChoiceItem(
        'Vereniging', 'Vereniging')
    vereniging_van_eigenaars = ChoiceItem(
        'Vereniging van Eigenaars', 'Vereniging van Eigenaars')
    publiekrechtelijke_rechtspersoon = ChoiceItem(
        'Publiekrechtelijke Rechtspersoon', 'Publiekrechtelijke Rechtspersoon')
    vennootschap_onder_firma = ChoiceItem(
        'Vennootschap onder Firma', 'Vennootschap onder Firma')
    maatschap = ChoiceItem(
        'Maatschap', 'Maatschap')
    rederij = ChoiceItem(
        'Rederij', 'Rederij')
    commanditaire_vennootschap = ChoiceItem(
        'Commanditaire vennootschap', 'Commanditaire vennootschap')
    kapitaalvennootschap_binnen_eer = ChoiceItem(
        'Kapitaalvennootschap binnen EER', 'Kapitaalvennootschap binnen EER')
    overige_buitenlandse_rechtspersoon_vennootschap = ChoiceItem(
        'Overige buitenlandse rechtspersoon vennootschap', 'Overige buitenlandse rechtspersoon vennootschap')
    kapitaalvennootschap_buiten_eer = ChoiceItem(
        'Kapitaalvennootschap buiten EER', 'Kapitaalvennootschap buiten EER')


class TyperingInrichtingselement(DjangoChoices):
    bak = ChoiceItem('Bak', 'Bak')
    bord = ChoiceItem('Bord', 'Bord')
    installatie = ChoiceItem('Installatie', 'Installatie')
    kast = ChoiceItem('Kast', 'Kast')
    mast = ChoiceItem('Mast', 'Mast')
    paal = ChoiceItem('Paal', 'Paal')
    sensor = ChoiceItem('Sensor', 'Sensor')
    straatmeubilair = ChoiceItem('Straatmeubilair', 'Straatmeubilair')
    waterinrichtingselement = ChoiceItem('Waterinrichtingselement', 'Waterinrichtingselement')
    weginrichtingselement = ChoiceItem('Weginrichtingselement', 'Weginrichtingselement')


class TyperingKunstwerk(DjangoChoices):
    keermuur = ('Keermuur', 'Keermuur')
    overkluizing = ('Overkluizing', 'Overkluizing')
    duiker = ('Duiker', 'Duiker')
    faunavoorziening = ('Faunavoorziening', 'Faunavoorziening')
    vispassage = ('Vispassage', 'Vispassage')
    bodemval = ('Bodemval', 'Bodemval')
    coupure = ('Coupure', 'Coupure')
    ponton = ('Ponton', 'Ponton')
    voorde = ('Voorde', 'Voorde')
    hoogspanningsmast = ('Hoogspanningsmast', 'Hoogspanningsmast')
    gemaal = ('Gemaal', 'Gemaal')
    perron = ('Perron', 'Perron')
    sluis = ('Sluis', 'Sluis')
    strekdam = ('Strekdam', 'Strekdam')
    steiger = ('Steiger', 'Steiger')
    stuw = ('Stuw', 'Stuw')


class TyperingWater(DjangoChoices):
    zee = ('Zee', 'Zee')
    waterloop = ('Waterloop', 'Waterloop')
    watervlakte = ('Watervlakte', 'Watervlakte')
    greppel_droge_sloot = ('Greppel, droge sloot', 'Greppel, droge sloot')


class Huishoudensoort(DjangoChoices):
    institutioneel = ChoiceItem('1', 'institutioneel huishouden')
    alleenstaand = ChoiceItem('2', 'alleenstaand (inclusief andere personen die in hetzelfde object wonen, maar een eigen huishouding voeren)')
    geen_kinderen = ChoiceItem('3', '2 personen, vaste partners, geen thuiswonende kinderen')
    wel_kinderen = ChoiceItem('4', '2 personen, vaste partners, een of meer thuiswonende kinderen')
    eenoudergezin = ChoiceItem('5', 'eenoudergezin, ouder met een of meer thuiswonende kinderen')
    overig = ChoiceItem('6', 'overig particulier huishouden (samenwoning van personen die geen partnerrelatie onderhouden of een ouder-kindrelatie hebben, maar wel gezamenlijk een huishouding voeren)')


class TypeSpoorbaan(DjangoChoices):
    """
    Komt uit de XSD.
    """
    breedspoor = ChoiceItem('breedspoor')
    normaalspoor = ChoiceItem('normaalspoor')
    smalspoor = ChoiceItem('smalspoor')
    spoorbaan = ChoiceItem('spoorbaan')


class AardRelatieGerelateerdeExterneZaak(DjangoChoices):
    opdrachtgever = ChoiceItem('Opdrachtgever', 'Opdrachtgever')
    opdrachtnemer = ChoiceItem('Opdrachtnemer', 'Opdrachtnemer')


class ArchiefStatus(DjangoChoices):
    """
    Indien het attribuutsoort een waarde ongelijk "Nog te archiveren"
    heeft, dan moet van alle ENKELVOUDIGE INFORMATIEOBJECTen
    die via INFORMATIEOBJECT en de ZAAK-INFORMATIEOBJECT-
    relatie aan de zaak gerelateerd zijn, het attribuutsoort 'Status' de
    waarde "Gearchiveerd" hebben.
    """
    nog_te_archiveren = ChoiceItem('Nog te archiveren', 'Nog te archiveren')
    gearchiveerd = ChoiceItem('Gearchiveerd', 'Gearchiveerd')
    vernietigd = ChoiceItem('Vernietigd', 'Vernietigd')
    overgedragen = ChoiceItem('Overgedragen', 'Overgedragen')


class Rolomschrijving(DjangoChoices):
    """
    Algemeen gehanteerde benaming van de aard van de ROL
    """
    adviseur = ChoiceItem('Adviseur', 'Adviseur')
    behandelaar = ChoiceItem('Behandelaar', 'Behandelaar')
    belanghebbende = ChoiceItem('Belanghebbende', 'Belanghebbende')
    beslisser = ChoiceItem('Beslisser', 'Beslisser')
    initiator = ChoiceItem('initiator', 'Initiator')
    klantcontacter = ChoiceItem('Klantcontacter', 'Klantcontacter')
    zaakcoordinator = ChoiceItem('Zaakcoordinator', 'Zaakcoordinator')


class RolomschrijvingGeneriek(Rolomschrijving):
    medeinitiator = ChoiceItem('Mede-initiator', 'Mede-initiator')


class IndicatieMachtiging(DjangoChoices):
    gemachtigde = ChoiceItem('Gemachtigde', 'Gemachtigde')
    machtiginggever = ChoiceItem('Machtiginggever', 'Machtiginggever')


class AardRelatieVerzending(DjangoChoices):
    afzender = ChoiceItem('Afzender', 'Afzender')
    geadresseerde = ChoiceItem('Geadresseerde', 'Geadresseerde')


class AardRelatieZakenRelatie(DjangoChoices):
    vervolg = ChoiceItem('Vervolg', 'Vervolg')
    onderwerp = ChoiceItem('Onderwerp', 'Onderwerp')
    bijdrage = ChoiceItem('Bijdrage', 'Bijdrage')
