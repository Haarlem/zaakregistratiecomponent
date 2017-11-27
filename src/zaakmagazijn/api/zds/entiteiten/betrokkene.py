from zaakmagazijn.rgbz_mapping.models import (
    ContactpersoonProxy, CorrespondentieadresProxy, LocatieadresProxy,
    MedewerkerProxy, NatuurlijkPersoonProxy, NietNatuurlijkPersoonProxy,
    OrganisatorischeEenheidProxy, PostAdresProxy, RolProxy,
    VerblijfBuitenlandProxy, VestigingProxy,
    VestigingVanZaakBehandelendeOrganisatieProxy
)

from ...stuf import (
    ForeignKeyRelation, OneToManyRelation, StUFEntiteit, StUFGegevensgroep
)


class VestigingVerblijfsAdresGegevensGroep(StUFGegevensgroep):
    """
    NOTE: The mapping here is a bit weird. In the XSD this is called 'verblijfsadres',
    in the RGBZ i've mapped it to 'locatie-adres', since there is nothing else.
    """
    model = LocatieadresProxy
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
        # ('inp.locatiebeschrijving', '?')
    )


class VerblijfBuitenlandGegevensGroep(StUFGegevensgroep):
    model = VerblijfBuitenlandProxy
    namespace = "http://www.egem.nl/StUF/sector/bg/0310"

    field_mapping = (
        ('lnd.landnaam', 'land__landnaam'),
        ('sub.adresBuitenland1', 'adres_buitenland_1'),
        ('sub.adresBuitenland2', 'adres_buitenland_2'),
        ('sub.adresBuitenland3', 'adres_buitenland_3'),
    )


class CorrespondentieadresGegevensGroep(StUFGegevensgroep):
    model = CorrespondentieadresProxy
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
    model = NatuurlijkPersoonProxy
    field_mapping = (
        ('inp.bsn', 'burgerservicenummer'),
        ('anp.identificatie', 'nummer_ander_natuurlijk_persoon'),
        ('geslachtsnaam', 'geslachtsnaam'),
        ('voorvoegselGeslachtsnaam', 'voorvoegsels_geslachtsnaam'),
        ('voorletters', 'voorletters'),
        ('voornamen', 'voornamen'),
        ('aanhefAanschrijving', 'aanhef_aanschrijving'),
        ('voornamenAanschrijving', 'voornamen_aanschrijving'),
        ('geslachtsnaamAanschrijving', 'geslachtsnaam_aanschrijving'),
        ('geslachtsaanduiding', 'geslachtsaanduiding'),
        ('geboortedatum', 'geboortedatum'),
        ('overlijdensdatum', 'overlijdensdatum'),
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
        'voorvoegselGeslachtsnaam',
        'voorletters',
        'voornamen',
        'geslachtsaanduiding',
        'geboortedatum',
        # TODO [TECH]: Add support for this.
        # 'verblijfsadres',
        # 'sub.verblijfBuitenland',
    )


class NietNatuurlijkPersoonEntiteit(StUFEntiteit):
    """
    in xsd: ['inn.nnpId', 'authentiek', 'ann.identificatie', 'statutaireNaam', 'inn.rechtsvorm', 'bezoekadres', 'sub.verblijfBuitenland']
    """
    namespace = 'http://www.egem.nl/StUF/sector/bg/0310'
    mnemonic = "NNP"
    model = NietNatuurlijkPersoonProxy
    field_mapping = (
        ('inn.nnpId', 'nnpid'),
        ('ann.identificatie', 'nummer_ander_buitenlands_nietnatuurlijk_persoon'),
        # ('sub.typering', '?'),
        ('statutaireNaam', 'statutaire_naam'),
        # ('inn.rechtsvorm', '')
        ('datumAanvang', 'datum_aanvang'),
        ('datumEinde', 'datum_beeindiging')
    )

    gegevensgroepen = (
        ForeignKeyRelation('sub.correspondentieAdres', 'correspondentieadres', CorrespondentieadresGegevensGroep),
        # TODO [TECH]: This is for 'Ingeschreven niet natuurlijk persoon.'
        # ForeignKeyRelation('bezoekadres', '', ),
        ForeignKeyRelation('sub.verblijfBuitenland', 'verblijf_buitenland', VerblijfBuitenlandGegevensGroep),
    )

    matching_fields = (
        # Choice (
        "inn.nnpId",
        "authentiek",
        # ,
        "ann.identificatie",
        # )
        "statutaireNaam",
        "inn.rechtsvorm",
        # Choice (
        "bezoekadres",
        # ,
        "sub.verblijfBuitenland",
        # )
    )


class VestigingEntiteit(StUFEntiteit):
    """
    in xsd: ['vestigingsNummer', 'authentiek', 'handelsnaam', 'verblijfsadres', 'sub.verblijfBuitenland']
    """
    namespace = 'http://www.egem.nl/StUF/sector/bg/0310'
    mnemonic = 'VES'
    model = VestigingProxy

    field_mapping = (
        ('vestigingsNummer', 'vestigingsnummer'),
        ('handelsnaam', 'handelsnaam'),

        # TODO [TECH]: 'authentiek' in xsd, niet in model
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
        'verblijfsadres',
        'sub.verblijfBuitenland'
    )
    fields = (
        'vestigingsNummer',
        'handelsnaam',
        'verblijfsadres',
        'sub.verblijfBuitenland',
    )


class VZOVESEntiteit(StUFEntiteit):
    mnemonic = 'VZOVES'
    model = VestigingVanZaakBehandelendeOrganisatieProxy

    gerelateerde = ('is_specialisatie_van', VestigingEntiteit)
    field_mapping = ()

    matching_fields = (
        'gerelateerde',
    )


class VestigingVanZaakBehandelendeOrganisatieEntiteit(StUFEntiteit):
    # namespace = 'http://www.egem.nl/StUF/sector/bg/0310'
    mnemonic = 'VZO'
    model = VestigingVanZaakBehandelendeOrganisatieProxy

    field_mapping = ()

    related_fields = (
        OneToManyRelation('isEen', 'self', VZOVESEntiteit, min_occurs=1, max_occurs=1),
    )

    matching_fields = (
        'isEen',
    )

    @classmethod
    def add_extra_obj_kwargs(cls, spyne_obj, obj):
        spyne_vestiging = spyne_obj.isEen.gerelateerde
        obj.update({
            'is_specialisatie_van__vestigingsnummer': spyne_vestiging.vestigingsNummer,
            'is_specialisatie_van__handelsnaam': spyne_vestiging.handelsnaam,
            # TODO [KING]:         'verblijfsadres', 'sub.verblijfBuitenland',
        })
        return obj


class OEHVZOEntiteit(StUFEntiteit):
    model = OrganisatorischeEenheidProxy
    mnemonic = 'OEHVZO'
    gerelateerde = ('self', VestigingVanZaakBehandelendeOrganisatieEntiteit)
    field_mapping = ()

    matching_fields = (
        'gerelateerde'
    )

    @classmethod
    def add_extra_obj_kwargs(cls, spyne_obj, obj):
        spyne_vestiging = spyne_obj.gerelateerde.isEen.gerelateerde
        obj.update({
            'gevestigd_in__is_specialisatie_van__vestigingsnummer': spyne_vestiging.vestigingsNummer,
            'gevestigd_in__is_specialisatie_van__handelsnaam': spyne_vestiging.handelsnaam,
            # TODO [KING]:         'verblijfsadres', 'sub.verblijfBuitenland',

        })
        return obj


class OrganisatorischeEenheidEntiteit(StUFEntiteit):
    mnemonic = 'OEH'
    model = OrganisatorischeEenheidProxy

    field_mapping = (
        ('identificatie', 'organisatieidentificatie'),
        ('naam', 'naam'),
        ('naamVerkort', 'naam_verkort'),
        ('omschrijving', 'omschrijving'),
        ('toelichting', 'toelichting'),
        ('telefoonnummer', 'telefoonnummer'),
        ('faxnummer', 'faxnummer'),
        ('emailadres', 'emailadres'),
    )

    # TODO [TECH]: Should be done: ingangsdatumObject, einddatumObject, bestaatUit,
    # heeftAlsVerantwoordelijke, heeftAlsContactpersoon,
    related_fields = (
        ForeignKeyRelation('isGehuisvestIn', 'gevestigd_in', OEHVZOEntiteit),
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
        'naam',
        'isGehuisvestIn',
    )

    @classmethod
    def add_extra_obj_kwargs(cls, spyne_obj, obj):
        if spyne_obj.isGehuisvestIn:
            spyne_vestiging = spyne_obj.isGehuisvestIn.gerelateerde.isEen.gerelateerde
            obj.update({
                'gevestigd_in__is_specialisatie_van__vestigingsnummer': spyne_vestiging.vestigingsNummer,
                'gevestigd_in__is_specialisatie_van__handelsnaam': spyne_vestiging.handelsnaam,
                # TODO [KING]:         'verblijfsadres', 'sub.verblijfBuitenland',

            })
        return obj


class MDWOEHLIDEntiteit(StUFEntiteit):
    mnemonic = 'MDWOEHLID'
    model = MedewerkerProxy

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
    model = MedewerkerProxy

    field_mapping = (
        ('identificatie', 'medewerkeridentificatie'),
        ('achternaam', 'achternaam'),
        ('voorletters', 'voorletters'),
        ('voorvoegselAchternaam', 'voorvoegsel_achternaam'),
        ('geslachtsaanduiding', 'geslachtsaanduiding'),
        ('functie', 'functie'),
        ('datumUitDienst', 'datum_uit_dienst'),
    )
    matching_fields = (
        "identificatie",
        # TODO [KING]: See https://discussie.kinggemeenten.nl/discussie/gemma/stuf-testplatform/medewerker-123456789
        # "achternaam",
        # "voorletters",
        # "voorvoegselAchternaam",
    )
    related_fields = (
        OneToManyRelation('hoortBij', 'self', MDWOEHLIDEntiteit, min_occurs=0, max_occurs=1),
    )


class ContactpersoonEntiteit(StUFEntiteit):
    model = ContactpersoonProxy
    field_mapping = (
    )


# heeftAlsAanspreekpunt
class ZAKBTRVRACTPEntiteit(StUFEntiteit):
    model = RolProxy
    gerelateerde = ('contactpersoon', ContactpersoonEntiteit)
    field_mapping = (
    )


class AfwijkendCorrespondentieAdresGegevensGroep(StUFGegevensgroep):
    model = PostAdresProxy
    namespace = "http://www.egem.nl/StUF/sector/bg/0310"

    field_mapping = (
        ('postcode', 'postadres_postcode'),
        ('sub.postadresType', 'postadrestype'),
        ('sub.postadresNummer', 'postbus_of_antwoordnummer'),
    )


class ZAKBTRBTREntiteit(StUFEntiteit):
    model = RolProxy
    mnemonic = 'ZAKBTRBTR'
    custom_fields = (
        # ('extraElementen', ExtraElementen.customize(sub_ns=STUF_XML_NS, ref='extraElementen')),
    )
    field_mapping = (
        # ('code', '?'),
        ('omschrijving', 'rolomschrijving'),
        ('toelichting', 'roltoelichting'),
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
        # 'code'
        'omschrijving',
        'toelichting',
        'tijdvakRelatie',
        'tijdvakGeldigheid',
        'tijdstipRegistratie',
        # 'extraElementen',
    )
    matching_fields = (
        'gerelateerde'
    )

    begin_geldigheid = 'begin_geldigheid'
    eind_geldigheid = 'eind_geldigheid'
    begin_relatie = 'begin_relatie'
    eind_relatie = 'eind_relatie'
    tijdstip_registratie = 'tijdstip_registratie'


class ZAKBTRBLHEntiteit(ZAKBTRBTREntiteit):
    # heeftAlsBelanghebbende
    model = RolProxy
    mnemonic = 'ZAKBTRBLH'


class ZAKBTRGMCEntiteit(ZAKBTRBTREntiteit):
    # heeftAlsGemachtigde
    model = RolProxy
    mnemonic = 'ZAKBTRGMC'


class ZAKBTRINIEntiteit(ZAKBTRBTREntiteit):
    # heeftAlsInitiator
    model = RolProxy
    mnemonic = 'ZAKBTRINI'


class ZAKBTRUTVEntiteit(ZAKBTRBTREntiteit):
    # heeftAlsUitvoerende
    model = RolProxy
    mnemonic = 'ZAKBTRUTV'


class ZAKBTRVRAEntiteit(ZAKBTRBTREntiteit):
    # heeftAlsVerantwoordelijke
    model = RolProxy
    mnemonic = 'ZAKBTRVRA'


class ZAKBTROVREntiteit(ZAKBTRBTREntiteit):
    # heeftAlsOverigBetrokkene
    model = RolProxy
    mnemonic = 'ZAKBTROVR'
