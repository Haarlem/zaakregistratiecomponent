from zaakmagazijn.api.stuf.models import Authentiek
from zaakmagazijn.api.zds.entiteiten.besluiten import BesluitEntiteit
from zaakmagazijn.api.zds.entiteiten.betrokkene import (
    MedewerkerEntiteit, VestigingEntiteit
)
from zaakmagazijn.rgbz_mapping.models import (
    AdresMetPostcodeProxy, BuurtObjectProxy, EnkelvoudigDocumentProxy,
    GemeentelijkeOpenbareRuimteObjectProxy, GemeenteObjectProxy,
    HuishoudenObjectProxy, InrichtingsElementObjectProxy,
    KadastraalPerceelObjectProxy, KadastraleAanduidingProxy,
    KunstwerkDeelObjectProxy, MaatschappelijkeActiviteitObjectProxy,
    OpenbareRuimteObjectProxy, OverigeAdresseerbaarObjectAanduidingObjectProxy,
    OverigGebouwdObjectProxy, PandObjectProxy,
    SamengesteldInformatieObjectProxy, SpoorbaanDeelObjectProxy, StatusProxy,
    TerreinDeelObjectProxy, WaterdeelObjectProxy, WegdeelObjectProxy,
    WijkObjectProxy, WoonplaatsObjectProxy, WozdeelObjectProxy, WozObjectProxy,
    WozWaardeObjectProxy, ZaakObjectProxy, ZaakProxy, ZaakTypeProxy,
    ZakelijkRechtObjectProxy
)

from ...stuf import (
    ForeignKeyRelation, OneToManyRelation, StUFEntiteit, StUFGegevensgroep,
    StUFKerngegevens
)
from .betrokkene import (
    NatuurlijkPersoonEntiteit, NietNatuurlijkPersoonEntiteit,
    OrganisatorischeEenheidEntiteit
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


class ZaakKerngegevens(StUFKerngegevens):
    mnemonic = 'ZAK'
    model = ZaakProxy
    field_mapping = (
        ('identificatie', 'zaakidentificatie'),
        ('omschrijving', 'omschrijving'),
    )
    related_fields = (
        ForeignKeyRelation('isVan', 'zaaktype', ZAKZKTEntiteit),
    )
    matching_fields = [
        'identificatie',
        'omschrijving',
        'isVan',
    ]
    fields = (
        'identificatie',
        'omschrijving',
        # TODO [TECH]: Matching fields by relation are not supported yet.
        # 'isVan',
    )


class AdresObjectEntiteit(StUFEntiteit):
    namespace = 'http://www.egem.nl/StUF/sector/bg/0310'
    mnemonic = 'AOA'
    model = OverigeAdresseerbaarObjectAanduidingObjectProxy
    field_mapping = (
        ('identificatie', 'identificatie'),
        ('wpl.woonplaatsNaam', 'woonplaatsnaam'),
        ('gor.openbareRuimteNaam', 'naam_openbare_ruimte'),
        ('huisnummer', 'huisnummer'),
        ('huisletter', 'huisletter'),
        ('huisnummertoevoeging', 'huisnummertoevoeging'),
        ('postcode', 'postcode'),
        # ('num.indicatieHoofdadres', '?'),
        # TODO [KING]: STP seems not to expect these:
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
    custom_fields = (
        ('authentiek', Authentiek, {'data': 'N'}),
    )
    fields = (
        'identificatie',
        'authentiek',
        'wpl.woonplaatsNaam',
        'gor.openbareRuimteNaam',
        'huisnummer',
        'huisletter',
        'huisnummertoevoeging',
        'postcode',
    )


class BuurtObjectEntiteit(StUFEntiteit):
    """
    in xsd: ['buurtCode', 'buurtNaam', 'gem.gemeenteCode', 'wyk.wijkCode']
    """
    namespace = 'http://www.egem.nl/StUF/sector/bg/0310'
    mnemonic = 'BRT'
    model = BuurtObjectProxy
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


class EnkelvoudigDocumentEntiteit(StUFEntiteit):
    """
    in xsd: ['identificatie', 'dct.omschrijving', 'titel']
    """
    mnemonic = 'EDC'
    model = EnkelvoudigDocumentProxy
    field_mapping = (
        ('identificatie', 'identificatie'),
        ('dct.omschrijving', 'documenttype__documenttypeomschrijving'),
        ('creatiedatum', 'documentcreatiedatum'),
        ('ontvangstdatum', 'documentontvangstdatum'),
        ('titel', 'documenttitel'),
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
    model = GemeenteObjectProxy
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
    model = GemeentelijkeOpenbareRuimteObjectProxy
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
    model = InrichtingsElementObjectProxy

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
    model = KadastraleAanduidingProxy
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
    model = KadastraalPerceelObjectProxy

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
        # TODO [TECH]: Matching fields by relation are not supported yet.
        # "kadastraleAanduiding",
    )


class HuishoudenObjectEntiteit(StUFEntiteit):
    """
    in xsd: ['nummer', 'isGehuisvestIn']
    """
    mnemonic = 'HHD'
    model = HuishoudenObjectProxy
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
    model = KunstwerkDeelObjectProxy
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
    model = MaatschappelijkeActiviteitObjectProxy
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
    model = OpenbareRuimteObjectProxy  # TODO [TECH]: heeft identificatie
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


class PandObjectEntiteit(StUFEntiteit):
    """
    in xsd: ['identificatie', 'authentiek']
    """
    mnemonic = 'PND'
    namespace = 'http://www.egem.nl/StUF/sector/bg/0310'
    model = PandObjectProxy
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
    model = SamengesteldInformatieObjectProxy
    field_mapping = (
        ('identificatie', 'identificatie'),
        ('dct.omschrijving', 'documenttype__documenttypeomschrijving'),
        # TODO [TECH]: Not supported yet
        # ('dct.omschrijvingGeneriek', 'informatieobjecttype__informatieobjecttypeomschrijving_generiek__informatieobjecttypeomschrijving_generiek'),
        ('creatiedatum', 'documentcreatiedatum'),
        ('ontvangstdatum', 'documentontvangstdatum'),
        ('titel', 'documenttitel'),
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
    model = SpoorbaanDeelObjectProxy
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
    model = StatusProxy
    gerelateerde = ('zaak', ZaakKerngegevens)
    field_mapping = ()


class StatusEntiteit(StUFEntiteit):
    """
    in xsd: ['stt.volgnummer', 'datumStatusGezet', 'isVan']
    """
    mnemonic = 'STA'
    model = StatusProxy
    field_mapping = (
        ('stt.volgnummer', 'status_type__volgnummer'),
        ('stt.omschrijving', 'status_type__omschrijving'),
        ('datumStatusGezet', 'datum_status_gezet'),
    )
    related_fields = (
        OneToManyRelation('isVan', 'self', STAZAKEntiteit, min_occurs=1, max_occurs=1),
    )
    matching_fields = (
        "stt.volgnummer",
        "datumStatusGezet",
        # TODO [TECH]: Matching fields by relation are not supported yet.
        # "isVan",
    )


class TerreinDeelObjectEntiteit(StUFEntiteit):
    """
    in xsd: ['type', 'identificatie', 'naam']
    """
    mnemonic = 'TDL'
    namespace = 'http://www.egem.nl/StUF/sector/bg/0310'
    model = TerreinDeelObjectProxy
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
    model = AdresMetPostcodeProxy
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
    model = OverigGebouwdObjectProxy

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
    model = WaterdeelObjectProxy

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
    model = WegdeelObjectProxy
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
    model = WijkObjectProxy
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
    model = WoonplaatsObjectProxy
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
    model = WozdeelObjectProxy
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
    model = WozObjectProxy
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
    model = WozWaardeObjectProxy  # heeft identificatie
    field_mapping = (
        ('waardepeildatum', 'waardepeildatum'),
        # TODO [KING]: in xsd, niet in model
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
    model = ZakelijkRechtObjectProxy
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
    model = ZaakObjectProxy
    field_mapping = (
        ('omschrijving', 'relatieomschrijving'),
    )
    gerelateerde = ('object', (
        ('adres', AdresObjectEntiteit),
        ('besluit', BesluitEntiteit),
        ('buurt', BuurtObjectEntiteit),
        ('enkelvoudigDocument', EnkelvoudigDocumentEntiteit),
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
        ('organisatorischeEenheid', OrganisatorischeEenheidEntiteit),
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
    fields = (
        'gerelateerde',
        'omschrijving'
    )
