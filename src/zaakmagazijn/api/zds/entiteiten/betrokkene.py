from ....rgbz.models import (
    Klantcontact, Medewerker, NatuurlijkPersoon, NietNatuurlijkPersoon,
    OrganisatorischeEenheid, Rol, Status, Vestiging,
    VestigingVanZaakBehandelendeOrganisatie as VestigingVanZaakBehandelendeOrganisatieModel
)
from ....rsgb.models import (
    AdresMetPostcode, Correspondentieadres, PostAdres, VerblijfAdres,
    VerblijfBuitenland
)
from ...stuf import (
    ForeignKeyRelation, OneToManyRelation, StUFEntiteit, StUFGegevensgroep
)
from ...stuf.constants import STUF_XML_NS
from ...stuf.models import ExtraElementen


class VestigingVerblijfsAdresGegevensGroep(StUFGegevensgroep):
    """
    NOTE: The mapping here is a bit weird. In the XSD this is called 'verblijfsadres',
    in the RGBZ i've mapped it to 'locatie-adres', since there is nothing else.
    """
    model = AdresMetPostcode
    namespace = "http://www.egem.nl/StUF/sector/bg/0310"

    field_mapping = (
        # ('aoa.identificatie', ''),
        # ('authentiek', '')
        ('wpl.woonplaatsNaam', 'woonplaatsnaam'),
        ('gor.openbareRuimteNaam', 'naam_openbare_ruimte'),
        # TODO: [COMPAT] I think this exists in RGBZ, but does not in the model.
        # ('gor.straatnaam', '?'),
        ('aoa.postcode', 'postcode'),
        ('aoa.huisnummer', 'huisnummer'),
        ('aoa.huisletter', 'huisletter'),
        ('aoa.huisnummertoevoeging', 'huisnummertoevoeging'),
        # ('inp.locatiebeschrijving', '?')
    )


class VerblijfBuitenlandGegevensGroep(StUFGegevensgroep):
    model = VerblijfBuitenland
    namespace = "http://www.egem.nl/StUF/sector/bg/0310"

    field_mapping = (
        ('lnd.landnaam', 'land__landnaam'),
        ('sub.adresBuitenland1', 'adres_buitenland_1'),
        ('sub.adresBuitenland2', 'adres_buitenland_2'),
        ('sub.adresBuitenland3', 'adres_buitenland_3'),
    )


class VestigingEntiteit(StUFEntiteit):
    """
    in xsd: ['vestigingsNummer', 'authentiek', 'handelsnaam', 'verblijfsadres', 'sub.verblijfBuitenland']
    """
    namespace = 'http://www.egem.nl/StUF/sector/bg/0310'
    mnemonic = 'VES'
    model = Vestiging

    field_mapping = (
        ('vestigingsNummer', 'identificatie'),
        ('handelsnaam', 'handelsnaam'),

        # TODO: [TECH] 'authentiek' in xsd, niet in model
        # ('authentiek', ''),
    )
    gegevensgroepen = (
        ForeignKeyRelation('verblijfsadres', 'locatieadres', VestigingVerblijfsAdresGegevensGroep),
        ForeignKeyRelation('sub.verblijfBuitenland', 'verblijf_buitenland', VerblijfBuitenlandGegevensGroep),
    )
    matching_fields = (
        'vestigingsNummer',
        # 'authentiek'
        'handelsnaam',
        # TODO: [TECH] Not supported yet.
        # 'verblijfsadres',
        # 'sub.verblijfBuitenland'
    )


class VZOVESEntiteit(StUFEntiteit):
    mnemonic = 'VZOVES'
    model = VestigingVanZaakBehandelendeOrganisatieModel

    gerelateerde = ('vestiging_ptr', VestigingEntiteit)
    field_mapping = ()

    matching_fields = (
        'gerelateerde',
    )


class VestigingVanZaakBehandelendeOrganisatie(StUFEntiteit):
    # namespace = 'http://www.egem.nl/StUF/sector/bg/0310'
    mnemonic = 'VZO'
    model = VestigingVanZaakBehandelendeOrganisatieModel

    field_mapping = ()

    related_fields = (
        OneToManyRelation('isEen', 'self', VZOVESEntiteit, min_occurs=1, max_occurs=1),
    )

    matching_fields = (
        # TODO: [KING] See https://discussie.kinggemeenten.nl/comment/5295#comment-5295
    )


class OEHVZOEntiteit(StUFEntiteit):
    model = OrganisatorischeEenheid
    mnemonic = 'OEHVZO'
    gerelateerde = ('gevestigd_in', VestigingVanZaakBehandelendeOrganisatie)
    field_mapping = ()

    matching_fields = (
        'gerelateerde'
    )


class OrganisatorischeEenheidEntiteit(StUFEntiteit):
    mnemonic = 'OEH'
    model = OrganisatorischeEenheid

    field_mapping = (
        ('identificatie', 'organisatieeenheididentificatie'),
        ('naam', 'naam'),
        ('naamVerkort', 'naam_verkort'),
        ('omschrijving', 'omschrijving'),
        ('toelichting', 'toelichting'),
        ('telefoonnummer', 'telefoonnummer'),
        ('faxnummer', 'faxnummer'),
        ('emailadres', 'emailadres'),
    )

    # TODO: [TECH] Should be done: ingangsdatumObject, einddatumObject, bestaatUit,
    # heeftAlsVerantwoordelijke, heeftAlsContactpersoon,
    related_fields = (
        OneToManyRelation('isGehuisvestIn', 'self', OEHVZOEntiteit, min_occurs=0, max_occurs=1),
    )

    fields = (
        'identificatie',
        'naam',
        'naamVerkort',
        'omschrijving',
        'toelichting',
        'telefoonnummer',
        'faxnummer',
        'emailadres',
        'isGehuisvestIn',
    )

    matching_fields = (
        'identificatie',
    )


class MDWOEHLIDEntiteit(StUFEntiteit):
    mnemonic = 'MDWOEHLID'
    model = Medewerker

    gerelateerde = ('organisatorische_eenheid', OrganisatorischeEenheidEntiteit)
    field_mapping = ()
    matching_fields = (
        'gerelateerde',
    )


class MedewerkerEntiteit(StUFEntiteit):
    """
    in xsd: ['identificatie', 'achternaam', 'voorletters', 'voorvoegselAchternaam']
    """
    mnemonic = 'MDW'
    model = Medewerker

    field_mapping = (
        ('medewerkeridentificatie', 'medewerkeridentificatie'),
        ('achternaam', 'achternaam'),
        ('voorletters', 'voorletters'),
        ('voorvoegselAchternaam', 'voorvoegsel_achternaam'),
        ('geslachtsaanduiding', 'geslachtsaanduiding'),
        ('functie', 'functie'),
        ('roepnaam', 'roepnaam'),  # Not in ZDS 1.2
        ('datumUitDienst', 'datum_uit_dienst'),
    )
    matching_fields = (
        "medewerkeridentificatie",
        "achternaam",
        "voorletters",
        "voorvoegselAchternaam",
    )
    related_fields = (
        OneToManyRelation('hoortBij', 'self', MDWOEHLIDEntiteit, min_occurs=0, max_occurs=1),
    )


class VerblijfsAdresGegevensGroep(StUFGegevensgroep):
    model = VerblijfAdres
    namespace = "http://www.egem.nl/StUF/sector/bg/0310"

    field_mapping = (
        # ('aoa.identificatie', ''),
        # ('authentiek', '')
        ('wpl.woonplaatsNaam', 'woonplaatsnaam'),
        ('gor.openbareRuimteNaam', 'naam_openbare_ruimte'),
        ('gor.straatnaam', 'straatnaam'),
        ('aoa.postcode', 'postcode'),
        ('aoa.huisnummer', 'huisnummer'),
        ('aoa.huisletter', 'huisletter'),
        ('aoa.huisnummertoevoeging', 'huisnummertoevoeging'),
        ('inp.locatiebeschrijving', 'locatie_beschrijving')
    )


class CorrespondentieadresGegevensGroep(StUFGegevensgroep):
    model = Correspondentieadres
    namespace = "http://www.egem.nl/StUF/sector/bg/0310"

    field_mapping = (
        ('wpl.woonplaatsNaam', 'woonplaatsnaam'),
        ('postcode', 'postcode'),
        # ('aoa.identificatie', '?'),
        # ('authentiek', '?'),
        ('gor.openbareRuimteNaam', 'naam_openbare_ruimte'),
        ('gor.straatnaam', 'straatnaam'),
        ('aoa.huisnummer', 'huisnummer'),
        ('aoa.huisletter', 'huisletter'),
        ('aoa.huisnummertoevoeging', 'huisnummertoevoeging'),
        # ('sub.postadresType', '?'),
        # ('sub.postadresNummer', '?'),
    )


class NatuurlijkPersoonEntiteit(StUFEntiteit):
    """
    in xsd: ['inp.bsn', 'authentiek', 'anp.identificatie', 'geslachtsnaam', 'voorvoegselGeslachtsnaam', 'voorletters', 'voornamen', 'geslachtsaanduiding', 'geboortedatum', 'verblijfsadres', 'sub.verblijfBuitenland']
    """
    namespace = 'http://www.egem.nl/StUF/sector/bg/0310'
    mnemonic = "NPS"
    model = NatuurlijkPersoon
    field_mapping = (
        ('inp.bsn', 'burgerservicenummer'),
        ('anp.identificatie', 'nummer_ander_natuurlijk_persoon'),
        ('geslachtsnaam', 'naam__geslachtsnaam'),
        # TODO: [TECH] Issue #243 3rd Level mapping is not supported.
        # ('voorvoegselGeslachtsnaam', 'naam__voorvoegsel_geslachtsnaam__voorvoegsel'),
        # ('voorletters', 'naam__voorvoegsel_geslachtsnaam__voorletters'),
        ('voornamen', 'naam__voornamen'),
        ('aanhefAanschrijving', 'naam_aanschrijving__aanhef_aanschrijving'),
        ('voornamenAanschrijving', 'naam_aanschrijving__voornamen_aanschrijving'),
        ('geslachtsnaamAanschrijving', 'naam_aanschrijving__geslachtsnaam_aanschrijving'),
        ('geslachtsaanduiding', 'geslachtsaanduiding'),
        ('geboortedatum', 'geboortedatum_ingeschreven_persoon'),
        ('overlijdensdatum', 'overlijdensdatum_ingeschreven_persoon'),
    )

    gegevensgroepen = (
        ForeignKeyRelation('verblijfsadres', 'verblijfadres', CorrespondentieadresGegevensGroep),
        ForeignKeyRelation('sub.verblijfBuitenland', 'verblijf_buitenland', VerblijfBuitenlandGegevensGroep),
        ForeignKeyRelation('sub.correspondentieAdres', 'correspondentieadres', CorrespondentieadresGegevensGroep),
    )

    matching_fields = (
        'inp.bsn',
        'anp.identificatie',
        # It's unclear what this is.
        # 'inp.a-nummer',
        'geslachtsnaam',
        # 'voorvoegselGeslachtsnaam',
        # 'voorletters',
        'voornamen',
        'geslachtsaanduiding',
        'geboortedatum',
        # TODO: [TECH] Add support for this.
        # 'verblijfsadres',
        # 'sub.verblijfBuitenland',
    )


class NietNatuurlijkPersoonEntiteit(StUFEntiteit):
    """
    in xsd: ['inn.nnpId', 'authentiek', 'ann.identificatie', 'statutaireNaam', 'inn.rechtsvorm', 'bezoekadres', 'sub.verblijfBuitenland']
    """
    namespace = 'http://www.egem.nl/StUF/sector/bg/0310'
    mnemonic = "NNP"
    model = NietNatuurlijkPersoon
    field_mapping = (
        ('inn.nnpId', 'rsin'),
        ('ann.identificatie', 'nummer_ander_buitenlands_nietnatuurlijk_persoon'),
        # ('sub.typering', '?'),
        ('statutaireNaam', 'statutaire_naam'),
        # ('inn.rechtsvorm', '')
        ('datumAanvang', 'datum_aanvang'),
        ('datumEinde', 'datum_beeindiging')
    )

    gegevensgroepen = (
        ForeignKeyRelation('sub.correspondentieAdres', 'correspondentieadres', CorrespondentieadresGegevensGroep),
        # TODO: [TECH] This is for 'Ingeschreven niet natuurlijk persoon.'
        # ForeignKeyRelation('bezoekadres', '', ),
        ForeignKeyRelation('sub.verblijfBuitenland', 'verblijf_buitenland', VerblijfBuitenlandGegevensGroep),
    )


class AfwijkendCorrespondentieAdresGegevensGroep(StUFGegevensgroep):
    model = PostAdres
    namespace = "http://www.egem.nl/StUF/sector/bg/0310"

    field_mapping = (
        ('wpl.woonplaatsNaam', 'woonplaatsnaam'),
        ('postcode', 'postadres_postcode'),
        ('sub.postadresType', 'postadrestype'),
        ('sub.postadresNummer', 'postbus_of_antwoordnummer'),
    )


class ZAKBTRBTREntiteit(StUFEntiteit):
    model = Rol
    mnemonic = 'ZAKBTRBTR'
    custom_fields = (
        ('extraElementen', ExtraElementen.customize(sub_ns=STUF_XML_NS, ref='extraElementen')),
    )
    field_mapping = (
        # TODO: [KING] (ZAKBTRBTR) Element "code" staat in de XSD maar niet in het ZDS.
        # ('code', ???)
        # In ZKN 3.2, no fields are specified here.
    )
    gegevensgroepen = (
        ForeignKeyRelation(
            'afwijkendCorrespondentieAdres',
            'afwijkend_correspondentie_postadres',
            AfwijkendCorrespondentieAdresGegevensGroep
        ),
    )
    gerelateerde = ('betrokkene', (
        ('medewerker', MedewerkerEntiteit),
        ('organisatorischeEenheid', OrganisatorischeEenheidEntiteit),
        ('vestiging', VestigingEntiteit),
        ('natuurlijkPersoon', NatuurlijkPersoonEntiteit),
        ('nietNatuurlijkPersoon', NietNatuurlijkPersoonEntiteit),
    ), )
    fields = (
        'gerelateerde',
        'extraElementen',
    )
    matching_fields = (
        'gerelateerde'
    )


class ZAKSTTBTREntiteit(ZAKBTRBTREntiteit):
    model = Status
    mnemonic = 'ZAKSTTBTR'

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


class ZAKBTRADVEntiteit(ZAKBTRBTREntiteit):
    model = Rol
    mnemonic = 'ZAKBTRADV'


class ZAKBTRBLHEntiteit(ZAKBTRBTREntiteit):
    model = Rol
    mnemonic = 'ZAKBTRBLH'


class ZAKBTRBHLEntiteit(ZAKBTRBTREntiteit):
    model = Rol
    mnemonic = 'ZAKBTRBHL'


class ZAKBRTBSSEntiteit(ZAKBTRBTREntiteit):
    model = Rol
    mnemonic = 'ZAKBRTBSS'


class ZAKBTRINIEntiteit(ZAKBTRBTREntiteit):
    model = Rol
    mnemonic = 'ZAKBTRINI'


class ZAKBTRKCREntiteit(ZAKBTRBTREntiteit):
    model = Rol
    mnemonic = 'ZAKBTRKCR'


class ZAKBTRZKCEntiteit(ZAKBTRBTREntiteit):
    model = Rol
    mnemonic = 'ZAKBTRZKC'


class ZAKBTRGMCEntiteit(ZAKBTRBTREntiteit):
    model = Rol
    mnemonic = 'ZAKBTRGMC'


class KlantcontactEntiteit(StUFEntiteit):
    model = Klantcontact
    mnemonic = 'KLC'

    field_mapping = (
        ('identificatie', 'identificatie'),
        ('datumtijd', 'datumtijd'),
        ('kanaal', 'kanaal'),
        ('onderwerp', 'onderwerp'),
        ('toelichting', 'toelichting'),
    )

    matching_fields = (
        'identificatie',
        # TODO: [COMPAT] verantwoordelijkeOrganisatie is specified in ZKN 3.2, but
        # I can't find it in the model.
        # 'verantwoordelijkeOrganisatie',
    )
