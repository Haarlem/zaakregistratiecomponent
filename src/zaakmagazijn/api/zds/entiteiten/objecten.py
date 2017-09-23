from zaakmagazijn.api.zds.entiteiten.besluiten import BesluitEntiteit
from zaakmagazijn.api.zds.entiteiten.betrokkene import (
    MedewerkerEntiteit, VestigingEntiteit
)
from zaakmagazijn.rgbz.models import (
    BuurtObject, EnkelvoudigInformatieObject,
    GemeentelijkeOpenbareRuimteObject, GemeenteObject, HuishoudenObject,
    InrichtingsElementObject, KadastraalPerceelObject, KunstwerkDeelObject,
    MaatschappelijkeActiviteitObject, NatuurlijkPersoon, NietNatuurlijkPersoon,
    OpenbareRuimteObject, OrganisatorischeEenheid,
    OverigeAdresseerbaarObjectAanduidingObject, OverigGebouwdObject,
    PandObject, SamengesteldInformatieObject, SpoorbaanDeelObject, Status,
    TerreinDeelObject, WaterdeelObject, WegdeelObject, WijkObject,
    WoonplaatsObject, WozdeelObject, WozObject, WozWaardeObject, Zaak,
    ZaakObject, ZakelijkRechtObject
)
from zaakmagazijn.rsgb.models import AdresMetPostcode, KadastraleAanduiding

from ...stuf import (
    ForeignKeyRelation, OneToManyRelation, StUFEntiteit, StUFGegevensgroep,
    StUFKerngegevens
)
from .betrokkene import (
    NatuurlijkPersoonEntiteit, NietNatuurlijkPersoonEntiteit
)


class ZaakKerngegevens(StUFKerngegevens):
    mnemonic = 'ZAK'
    model = Zaak
    field_mapping = (
        ('identificatie', 'zaakidentificatie'),
        ('bronorganisatie', 'bronorganisatie'),
        ('omschrijving', 'omschrijving'),
        # TODO: [COMPAT] (ZAK) In ZDS 1.2 is "isVan" een relatie-entiteit met een gerelateerde, in ZKN 03.20 is dit platgeslagen.
        ('zkt.omschrijving', 'zaaktype__zaaktypeomschrijving'),
        ('zkt.identificatie', 'zaaktype__zaaktypeidentificatie'),
    )

    matching_fields = [
        'identificatie',
        'bronorganisatie',
        'omschrijving',
        # TODO: [COMPAT] In ZDS 1.2 is 'isVan' hier ook opgegenomen. Maar in ZKN 3.2 bestaat
        # dit niet meer, mogelijk moet zkt.identificatie en zkt.omschrijving hier ook opgenomen
        # worden.
    ]


class AdresObjectEntiteit(StUFEntiteit):
    namespace = 'http://www.egem.nl/StUF/sector/bg/0310'
    mnemonic = 'AOA'
    model = OverigeAdresseerbaarObjectAanduidingObject
    field_mapping = (
        ('identificatie', 'identificatie'),
        # ('authentiek', ?),
        ('wpl.woonplaatsNaam', 'woonplaatsnaam'),
        ('gor.openbareRuimteNaam', 'naam_openbare_ruimte'),
        ('huisnummer', 'huisnummer'),
        ('huisletter', 'huisletter'),
        ('huisnummertoevoeging', 'huisnummertoevoeging'),
        # ('postcode', '?'),
        # ('num.indicatieHoofdadres', '?'),
        ('ingangsdatumObject', 'datum_begin_geldigheid_adresseerbaar_object_aanduiding'),
        ('einddatumObject', 'datum_einde_geldigheid_adresseerbaar_object_aanduiding'),
        # (<stuf:extraElementen>       ?)
    )
    matching_fields = (
        "identificatie",
        # "authentiek",
        # "typering",
        "wpl.woonplaatsNaam",
        "gor.openbareRuimteNaam",
        "huisnummer",
        "huisletter",
        "huisnummertoevoeging",
        "postcode",
    )


class BuurtObjectEntiteit(StUFEntiteit):
    """
    in xsd: ['buurtCode', 'buurtNaam', 'gem.gemeenteCode', 'wyk.wijkCode']
    """
    namespace = 'http://www.egem.nl/StUF/sector/bg/0310'
    mnemonic = 'BRT'
    model = BuurtObject
    field_mapping = (
        ('buurtCode', 'buurtcode'),
        ('buurtNaam', 'buurtnaam'),
        ('geometrie', 'geometrie'),
        ('gem.gemeenteCode', 'gemeentecode'),
        ('wyk.wijkCode', 'wijkcode'),
        ('ingangsdatumObject', 'datum_begin_geldigheid_buurt'),
        ('einddatumObject', 'datum_einde_geldigheid_buurt'),
        # (<stuf:extraElementen>       ?)
    )
    matching_fields = (
        "buurtCode",
        "buurtNaam",
        "gem.gemeenteCode",
        "wyk.wijkCode",
    )


class EnkelvoudigInformatieObjectEntiteit(StUFEntiteit):
    """
    in xsd: ['identificatie', 'dct.omschrijving', 'titel']
    """
    mnemonic = 'EDC'
    model = EnkelvoudigInformatieObject
    # model has unique together on informatieobjectidentificatie and bronorganisatie
    # i assume 'identificatie' from xsd is the combination of those two
    field_mapping = (
        # ('identificatie', 'identificatie'),

        # RGBZ 2.0 requires two identification fields:
        ('informatieobjectidentificatie', 'informatieobjectidentificatie'),
        ('bronorganisatie', 'bronorganisatie'),

        ('dct.omschrijving', 'informatieobjecttype__informatieobjecttypeomschrijving'),
        # TODO: [TECH] Not supported yet.
        # ('dct.omschrijvingGeneriek', 'informatieobjecttype__informatieobjecttypeomschrijving_generiek__informatieobjecttypeomschrijving_generiek'),
        ('creatiedatum', 'creatiedatum'),
        ('ontvangstdatum', 'ontvangstdatum'),
        ('titel', 'titel'),
    )
    matching_fields = (
        "identificatie",
        "dct.omschrijving",
        "titel",
    )


class GemeenteObjectEntiteit(StUFEntiteit):
    """
    in xsd: ['gemeenteCode', 'gemeenteNaam']
    """
    namespace = 'http://www.egem.nl/StUF/sector/bg/0310'
    mnemonic = 'GEM'
    model = GemeenteObject
    field_mapping = (
        ('gemeenteCode', 'identificatie'),
        ('gemeenteNaam', 'gemeentenaam'),
        ('ingangsdatumObject', 'datum_begin_geldigheid_gemeente'),
        ('einddatumObject', 'datum_einde_geldigheid_gemeente'),
    )
    matching_fields = (
        'gemeenteCode',
        'gemeenteNaam',
    )


class GemeentelijkeOpenbareRuimteEntiteit(StUFEntiteit):
    mnemonic = 'GOR'
    model = GemeentelijkeOpenbareRuimteObject
    field_mapping = (
        ('identificatie', 'identificatie'),
        # ('authentiek', '?'),
        ('gem.gemeenteCode', 'gemeentecode'),
        ('openbareRuimteNaam', 'naam_openbare_ruimte'),
        ('geometrie', 'geometrie'),
        ('type', 'type_openbare_ruimte'),
        ('ingangsdatumObject', 'datum_begin_geldigheid_gemeentelijke_openbare_ruimte'),
        ('einddatumObject', 'datum_einde_geldigheid_gemeentelijke_openbare_ruimte'),
    )
    matching_fields = (
        "identificatie",
        # "authentiek",
        "gem.gemeenteCode",
        "openbareRuimteNaam",
    )


class InrichtingselementEntiteit(StUFEntiteit):
    mnemonic = 'IRE'
    namespace = 'http://www.egem.nl/StUF/sector/bg/0310'
    model = InrichtingsElementObject

    field_mapping = (
        ('type', 'inrichtingselementtype'),
        ('identificatie', 'identificatie'),
        ('naam', 'naam'),
        ('geometrie', 'geometrie'),
        ('ingangsdatumObject', 'datum_begin_geldigheid_inrichtingselement'),
        ('einddatumObject', 'datum_einde_geldigheid_inrichtingselement'),
    )
    matching_fields = (
        "type",
        "identificatie",
        "naam",
    )


class KadastraleAanduidingGegevensGroep(StUFGegevensgroep):
    model = KadastraleAanduiding
    namespace = 'http://www.egem.nl/StUF/sector/bg/0310'
    field_mapping = (
        ('kadastraleGemeentecode', 'kadastralegemeentecode'),
        ('kadastraleSectie', 'sectie'),
        ('kadastraalPerceelnummer', 'perceelnummer'),
        # ('kdp.deelperceelNummer', '?'),
        ('apr.appartementsIndex', 'appartementsrechtvolgnummer'),
    )


class KadastraleOnroerendeZaakEntiteit(StUFEntiteit):
    mnemonic = 'KOZ'
    namespace = 'http://www.egem.nl/StUF/sector/bg/0310'
    model = KadastraalPerceelObject

    field_mapping = (
        ('kadastraleIdentificatie', 'identificatie'),
        # ('authentiek', '?')
        # ('typering', '?')
        ('kdp.begrenzing', 'begrenzing_perceel'),
        ('ingangsdatumObject', 'datum_begin_geldigheid_kadastrale_onroerende_zaak'),
        ('einddatumObject', 'datum_einde_geldigheid_kadastrale_onroerende_zaak'),
        # (<stuf:extraElementen>       ?)
    )

    gegevensgroepen = (
        ForeignKeyRelation('kadastraleAanduiding', 'kadastrale_aanduiding', KadastraleAanduidingGegevensGroep),
    )

    fields = (
        'kadastraleIdentificatie',
        # 'authentiek',
        # 'typering',
        'kadastraleAanduiding',
        'kdp.begrenzing',
        'ingangsdatumObject',
        'einddatumObject',
        # 'extraElementen',
    )

    matching_fields = (
        "kadastraleIdentificatie",
        # "authentiek",
        # TODO: [COMPAT] Not supported.
        # "kadastraleAanduiding",
    )


class HuishoudenObjectEntiteit(StUFEntiteit):
    """
    in xsd: ['nummer', 'isGehuisvestIn']
    """
    mnemonic = 'HHD'
    model = HuishoudenObject
    field_mapping = (
        ('nummer', 'huishoudennummer'),
    )
    matching_fields = (
        "nummer",
        # "isGehuisvestIn",
    )


class KunstwerkDeelObjectEntiteit(StUFEntiteit):
    """
    in xsd: ['type', 'identificatie', 'naam']
    """
    mnemonic = 'KWD'
    namespace = 'http://www.egem.nl/StUF/sector/bg/0310'
    model = KunstwerkDeelObject
    field_mapping = (
        ('type', 'type_kunstwerk'),
        ('identificatie', 'identificatie'),
        ('naam', 'naam_kunstwerkdeel'),
        ('geometrie', 'geometrie'),
        ('ingangsdatumObject', 'datum_begin_geldigheid_kunstwerkdeel'),
        ('einddatumObject', 'datum_einde_geldigheid_kunstwerkdeel'),
    )
    matching_fields = (
        "type",
        "identificatie",
        "naam",
    )


class MaatschappelijkeActiviteitObjectEntiteit(StUFEntiteit):
    """
    in xsd: ['kvkNummer', 'authentiek', 'handelsnaam']
    """
    mnemonic = 'MAC'
    namespace = 'http://www.egem.nl/StUF/sector/bg/0310'
    model = MaatschappelijkeActiviteitObject
    field_mapping = (
        ('kvkNummer', 'identificatie'),
        # ('authentiek', ?),
        ('datumAanvang', 'datum_aanvang'),
        ('datumEinde', 'datum_beeindiging'),
        ('handelsnaam', 'eerste_handelsnaam'),
        # ('extraElementen', '?'),
    )
    matching_fields = (
        "kvkNummer",
        # "authentiek",
        "handelsnaam",
    )


class OpenbareRuimteObjectEntiteit(StUFEntiteit):
    """
    in xsd: ['identificatie', 'authentiek', 'wpl.woonplaatsNaam', 'gor.openbareRuimteNaam']
    """
    mnemonic = 'OPR'
    namespace = 'http://www.egem.nl/StUF/sector/bg/0310'
    model = OpenbareRuimteObject  # TODO: [TECH] heeft identificatie
    field_mapping = (
        ('identificatie', 'identificatie'),
        # ('authentiek', ''),
        ('wpl.woonplaatsNaam', 'woonplaatsnaam'),
        ('gor.openbareRuimteNaam', 'naam_openbare_ruimte'),
        ('gor.type', 'type_openbare_ruimte'),
        ('ingangsdatumObject', 'datum_begin_geldigheid_openbare_ruimte'),
        ('einddatumObject', 'datum_einde_geldigheid_openbare_ruimte'),
        # ('extraElementen', ''),
    )
    matching_fields = (
        "identificatie",
        # "authentiek",
        "wpl.identificatie",
        "wpl.woonplaatsNaam",
        "gor.openbareRuimteNaam",
    )


class OrganisatorischeEenheidObjectEntiteit(StUFEntiteit):
    """
    in xsd: ['identificatie', 'naam', 'isGehuisvestIn']

    'isGehuisvestIn' is nested structure: FK isEen FK verstigingsnummer / verblijdsadres etc
    """
    mnemonic = 'OEH'
    model = OrganisatorischeEenheid
    field_mapping = (
        # Organisatorisch Eenheid has unique together 'organisatieidentificatie', 'organisatieeenheididentificatie'
        # I assume 'identificatie' from xsd is the combination of those two
        # ('identificatie', 'identificatie'),
        ('identificatie', 'organisatieeenheididentificatie'),
        ('organisatieidentificatie', 'organisatieidentificatie'),
        ('naam', 'naam'),
        ('isGehuisvestIn', 'gevestigd_in'),  # FK, _id?
    )
    matching_fields = (
        "identificatie",
        "organisatieidentificatie",
        "naam",
        "isGehuisvestIn",
    )


class PandObjectEntiteit(StUFEntiteit):
    """
    in xsd: ['identificatie', 'authentiek']
    """
    mnemonic = 'PND'
    namespace = 'http://www.egem.nl/StUF/sector/bg/0310'
    model = PandObject
    field_mapping = (
        ('identificatie', 'identificatie'),
        # ('authentiek', ''),
        ('geometrie', 'geometrie'),
        ('ingangsdatumObject', 'datum_begin_geldigheid_pand'),
        ('einddatumObject', 'datum_einde_geldigheid_pand'),
    )
    matching_fields = (
        "identificatie",
        "authentiek",
    )


class SamengesteldInformatieoObjectEntiteit(StUFEntiteit):
    """
    in xsd: ['identificatie', 'dct.omschrijving', 'titel']
    """
    mnemonic = 'SDC'
    model = SamengesteldInformatieObject
    field_mapping = (
        ('identificatie', 'identificatie'),
        ('dct.omschrijving', 'informatieobjecttype__informatieobjecttypeomschrijving'),
        # TODO: [TECH] Not supported yet
        # ('dct.omschrijvingGeneriek', 'informatieobjecttype__informatieobjecttypeomschrijving_generiek__informatieobjecttypeomschrijving_generiek'),
        ('creatiedatum', 'creatiedatum'),
        ('ontvangstdatum', 'ontvangstdatum'),
        ('titel', 'titel'),
    )
    matching_fields = (
        "identificatie",
        "dct.omschrijving",
        "titel",
    )


class SpoorbaanDeelObjectEntiteit(StUFEntiteit):
    """
    in xsd: ['type', 'identificatie', 'naam']
    """
    mnemonic = 'SBD'
    namespace = 'http://www.egem.nl/StUF/sector/bg/0310'
    model = SpoorbaanDeelObject
    field_mapping = (
        ('type', 'type_spoorbaan'),
        ('identificatie', 'identificatie'),
        ('naam', 'naam'),
        ('geometrie', 'geometrie'),
        ('ingangsdatumObject', 'datum_begin_geldigheid_spoorbaandeel'),
        ('einddatumObject', 'datum_einde_geldigheid_spoorbaandeel'),
        # ('extraElementen', ''),
    )


class STAZAKEntiteit(StUFEntiteit):
    mnemonic = 'STAZAK'
    model = Status
    gerelateerde = ('zaak', ZaakKerngegevens)
    field_mapping = ()


class StatusEntiteit(StUFEntiteit):
    """
    in xsd: ['stt.volgnummer', 'datumStatusGezet', 'isVan']
    """
    mnemonic = 'STA'
    model = Status
    field_mapping = (
        ('stt.volgnummer', 'status_type__statustypevolgnummer'),
        ('stt.omschrijving', 'status_type__statustypeomschrijving'),
        ('datumStatusGezet', 'datum_status_gezet'),
    )
    related_fields = (
        OneToManyRelation('isVan', 'self', STAZAKEntiteit, min_occurs=1, max_occurs=1),
    )
    matching_fields = (
        "stt.volgnummer",
        "datumStatusGezet",
        # TODO: [COMPAT] Not supported yet.
        # "isVan",
    )


class TerreinDeelObjectEntiteit(StUFEntiteit):
    """
    in xsd: ['type', 'identificatie', 'naam']
    """
    mnemonic = 'TDL'
    namespace = 'http://www.egem.nl/StUF/sector/bg/0310'
    model = TerreinDeelObject
    field_mapping = (
        ('type', 'type_terrein'),
        ('identificatie', 'identificatie'),
        ('naam', 'naam'),
        ('geometrie', 'geometrie'),
        ('ingangsdatumObject', 'datum_begin_geldigheid_terreindeel'),
        ('einddatumObject', 'datum_einde_geldigheid_terreindeel'),
        # ('extraElementen', ''),
    )


class AdresAanduidingGrp(StUFGegevensgroep):
    model = AdresMetPostcode
    namespace = 'http://www.egem.nl/StUF/sector/bg/0310'
    field_mapping = (
        # ('num.identificatie', ?),
        # ('oao.identificatie', ?),
        # ('authentiek>N</bg:authentiek>  ', ?),
        ('wpl.woonplaatsNaam', 'woonplaatsnaam'),
        ('gor.openbareRuimteNaam', 'naam_openbare_ruimte'),
        ('aoa.postcode', 'postcode'),
        ('aoa.huisnummer', 'huisnummer'),
        ('aoa.huisletter', 'huisletter'),
        ('aoa.huisnummertoevoeging', 'huisnummertoevoeging'),
        # ('ogo.locatieAanduiding', ?),
    )


class TerreinGebouwdObjectEntiteit(StUFEntiteit):
    mnemonic = 'TGO'
    namespace = 'http://www.egem.nl/StUF/sector/bg/0310'
    model = OverigGebouwdObject

    field_mapping = (
        # ('identificatie', ?),
        # ('authentiek', ?),
        ('gbo.puntGeometrie', 'geometrie'),
        # ('vlakGeometrie', ?),
        ('ingangsdatumObject', 'datum_begin_geldigheid'),
        ('einddatumObject', 'datum_einde_geldigheid'),
    )

    gegevensgroepen = (
        ForeignKeyRelation('adresAanduidingGrp', 'locatieadres', AdresAanduidingGrp),
    )

    matching_fields = (
        # 'identificatie',
        # 'authentiek',
        # 'typering',
        # 'adresAanduidingGrp',
    )


class WaterdeelObjectEntiteit(StUFEntiteit):
    """
    in xsd: ['type', 'identificatie', 'naam']
    """
    mnemonic = 'WDL'
    namespace = 'http://www.egem.nl/StUF/sector/bg/0310'
    model = WaterdeelObject

    field_mapping = (
        ('type', 'type_waterdeel'),
        ('identificatie', 'identificatie'),
        ('naam', 'naam'),
        ('geometrie', 'geometrie'),
        ('ingangsdatumObject', 'datum_begin_geldigheid_waterdeel'),
        ('einddatumObject', 'datum_einde_geldigheid_waterdeel'),
    )
    matching_fields = (
        "type",
        "identificatie",
        "naam",
    )


class WegdeelObjectEntiteit(StUFEntiteit):
    """
    in xsd: ['type', 'identificatie', 'naam']
    """
    mnemonic = 'WGD'
    namespace = 'http://www.egem.nl/StUF/sector/bg/0310'
    model = WegdeelObject
    field_mapping = (
        # ('type', ''),
        ('identificatie', 'identificatie'),
        # ('naam', ''),
        ('geometrie', 'geometrie'),
        ('ingangsdatumObject', 'datum_begin_geldigheid_wegdeel'),
        ('einddatumObject', 'datum_einde_geldigheid_wegdeel'),
        # ('extraElementen', ''),
    )
    matching_fields = (
        # "type",
        "identificatie",
        # "naam",
    )


class WijkObjectEntiteit(StUFEntiteit):
    """
    in xsd: ['wijkCode', 'wijkNaam', 'gem.gemeenteCode']
    """
    mnemonic = 'WYK'
    namespace = 'http://www.egem.nl/StUF/sector/bg/0310'
    model = WijkObject
    field_mapping = (
        ('wijkCode', 'wijkcode'),
        ('wijkNaam', 'wijknaam'),
        ('geometrie', 'geometrie'),
        ('gem.gemeenteCode', 'gemeentecode'),
        ('ingangsdatumObject', 'datum_begin_geldigheid_wijk'),
        ('einddatumObject', 'datum_eind_geldigheid_wijk'),
        # ('extraElementen', '')
    )
    matching_fields = (
        "wijkCode",
        "wijkNaam",
        "gem.gemeenteCode",
    )


class WoonplaatsObjectEntiteit(StUFEntiteit):
    """
    in xsd: ['identificatie', 'authentiek', 'woonplaatsNaam']
    """
    mnemonic = 'WPL'
    namespace = 'http://www.egem.nl/StUF/sector/bg/0310'
    model = WoonplaatsObject
    field_mapping = (
        ('identificatie', 'identificatie'),
        # ('authentiek', ''),
        ('woonplaatsNaam', 'woonplaatsnaam'),
        ('geometrie', 'geometrie'),
        ('ingangsdatumObject', 'datum_begin_geldigheid_woonplaats'),
        ('einddatumObject', 'datum_einde_geldigheid_woonplaats'),
        # ('extraElementen', '')
    )
    matching_fields = (
        "identificatie",
        # "authentiek",
        "woonplaatsNaam",
    )


class WozdeelObjectEntiteit(StUFEntiteit):
    """
    in xsd: ['nummerWOZDeelObject', 'isOnderdeelVan']
    """
    mnemonic = 'WDO'
    namespace = 'http://www.egem.nl/StUF/sector/bg/0310'
    model = WozdeelObject
    field_mapping = (
        ('nummerWOZDeelObject', 'nummer_wozdeelobject'),
        ('codeWOZDeelObject', 'code_wozdeelobject__deelobjectcode'),
        ('ingangsdatumObject', 'datum_begin_geldigheid_deelobject'),
        ('einddatumObject', 'datum_einde_geldigheid_deelobject'),
    )

    matching_fields = (
        "nummerWOZDeelObject",
        # "isOnderdeelVan",
        # "bestaatUit",
        # "bestaatUitPand",
    )


class WozObjectEntiteit(StUFEntiteit):
    """
    in xsd: ['wozObjectNummer', 'authentiek', 'aanduidingWOZobject']
    """
    mnemonic = 'WOZ'
    namespace = 'http://www.egem.nl/StUF/sector/bg/0310'
    model = WozObject
    field_mapping = (
        ('wozObjectNummer', 'identificatie'),
        # <bg:authentiek>N</bg:authentiek>
        ('wozObjectGeometrie', 'geometrie'),
        ('soortObjectCode', 'soortobjectcode__soort_objectcode'),
        ('ingangsdatumObject', 'datum_begin_geldigheid_wozobject'),
        ('einddatumObject', 'datum_einde_geldigheid_wozobject'),
    )
    gegevensgroepen = (
        ForeignKeyRelation('aanduidingWOZobject', 'adresaanduiding', AdresAanduidingGrp),
    )
    matching_fields = (
        "wozObjectNummer",
        # "authentiek",
        "aanduidingWOZobject",
    )

    fields = (
        'wozObjectNummer',
        # 'authentiek',
        'aanduidingWOZobject',
        'wozObjectGeometrie',
        'soortObjectCode',
        'ingangsdatumObject',
        'einddatumObject',
    )


class WozWaardeObjectEntiteit(StUFEntiteit):
    """
    in xsd: ['waardepeildatum', 'isVoor']
    """
    mnemonic = 'WRD'
    namespace = 'http://www.egem.nl/StUF/sector/bg/0310'
    model = WozWaardeObject  # heeft identificatie
    field_mapping = (
        ('waardepeildatum', 'waardepeildatum'),
        # TODO: [COMPAT] in xsd, niet in model
        # ('isVoor', ''),
    )
    matching_fields = (
        "waardepeildatum",
        "isVoor",
    )


class ZakelijkRechtObjectEntiteit(StUFEntiteit):
    """
    in xsd: ['identificatie', 'avr.aard',
            'heeftBetrekkingOp',  # this is a nested thing (relation)
            'heeftAlsGerechtigde'  # this is a nested thing (relation)
            ]
    """
    mnemonic = 'ZKR'
    namespace = 'http://www.egem.nl/StUF/sector/bg/0310'
    model = ZakelijkRechtObject
    field_mapping = (
        ('identificatie', 'identificatie'),
        ('avr.aard', 'aanduiding_aard_verkregen_recht__code_aard_zakelijk_recht'),
        ('ingangsdatumRecht', 'ingangsdatum_recht'),
        ('einddatumRecht', 'einddatum_recht'),

    )

    # Can't find these in the data model (There is no relation to KOZ, KadastraalPerceelObject)
    # heeftBetrekkingOp
    # heeftAlsGerechtigde

    matching_fields = (
        "identificatie",
        "avr.aard",
        # "heeftBetrekkingOp",
        # "heeftAlsGerechtigde",
    )


class ZaakObjectEntiteit(StUFEntiteit):
    mnemonic = 'ZAKOBJ'
    model = ZaakObject
    field_mapping = (
        ('omschrijving', 'relatieomschrijving'),
    )
    gerelateerde = ('object', (
        ('adres', AdresObjectEntiteit),
        ('besluit', BesluitEntiteit),
        ('buurt', BuurtObjectEntiteit),
        ('enkelvoudigDocument', EnkelvoudigInformatieObjectEntiteit),
        ('gemeente', GemeenteObjectEntiteit),
        ('gemeentelijkeOpenbareRuimte', GemeentelijkeOpenbareRuimteEntiteit),
        ('huishouden', HuishoudenObjectEntiteit),
        ('inrichtingselement', InrichtingselementEntiteit),
        ('kadastraleOnroerendeZaak', KadastraleOnroerendeZaakEntiteit),
        ('kunstwerkdeel', KunstwerkDeelObjectEntiteit),
        ('maatschappelijkeActiviteit', MaatschappelijkeActiviteitObjectEntiteit),
        ('medewerker', MedewerkerEntiteit),
        ('natuurlijkPersoon', NatuurlijkPersoonEntiteit),
        ('nietNatuurlijkPersoon', NietNatuurlijkPersoonEntiteit),
        ('openbareRuimte', OpenbareRuimteObjectEntiteit),
        ('organisatorischeEenheid', OrganisatorischeEenheidObjectEntiteit),
        ('pand', PandObjectEntiteit),
        ('samengesteldDocument', SamengesteldInformatieoObjectEntiteit),
        ('spoorbaandeel', SpoorbaanDeelObjectEntiteit),
        ('status', StatusEntiteit),
        ('terreindeel', TerreinDeelObjectEntiteit),
        ('terreinGebouwdObject', TerreinGebouwdObjectEntiteit),
        ('vestiging', VestigingEntiteit),
        ('waterdeel', WaterdeelObjectEntiteit),
        ('wegdeel', WegdeelObjectEntiteit),
        ('wijk', WijkObjectEntiteit),
        ('woonplaats', WoonplaatsObjectEntiteit),
        ('wozDeelobject', WozdeelObjectEntiteit),
        ('wozObject', WozObjectEntiteit),
        ('wozWaarde', WozWaardeObjectEntiteit),
        ('zakelijkRecht', ZakelijkRechtObjectEntiteit),
    ), )
    matching_fields = (
        'gerelateerde',
    )
