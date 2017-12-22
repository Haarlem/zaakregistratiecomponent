from django.db import models

from zaakmagazijn.rgbz.choices import (
    IndicatieMachtiging as RGBZ2IndicatieMachtiging,
    RolomschrijvingGeneriek as RGBZ2RolomschrijvingGeneriek
)
from zaakmagazijn.rgbz.models import (
    Betrokkene, Medewerker, NatuurlijkPersoon, NietNatuurlijkPersoon,
    OrganisatorischeEenheid, Rol, Vestiging,
    VestigingVanZaakBehandelendeOrganisatie
)

from ..base import ModelProxy, ProxyField, ProxyForeignKey
from ..choices import Rolomschrijving as RGBZ1Rolomschrijving, Subjecttypering
from ..manager import ProxyManager
from ..registry import proxy_registry


class BetrokkeneProxy(ModelProxy):
    model = Betrokkene
    fields = (
        ProxyField('identificatie', 'identificatie'),
    )
    objects = ProxyManager()

    def is_type(self):
        django_obj = self.to_django_obj()
        child_obj = django_obj.is_type()
        child_proxy_model = proxy_registry.get_proxy_model(child_obj.__class__)

        return child_proxy_model.from_django_obj(child_obj)


class MedewerkerProxy(ModelProxy):
    model = Medewerker
    fields = (
        ProxyField('medewerkeridentificatie', 'medewerkeridentificatie'),
        ProxyField('achternaam', 'achternaam'),
        ProxyField('voorletters', 'voorletters'),
        ProxyField('voorvoegsel_achternaam', 'voorvoegsel_achternaam'),
        ProxyField('geslachtsaanduiding', 'geslachtsaanduiding'),
        ProxyField('functie', 'functie'),
        ProxyField('roepnaam', 'roepnaam'),  # Not in ZDS 1.2
        ProxyField('datum_uit_dienst', 'datum_uit_dienst'),
        ProxyForeignKey('organisatorische_eenheid', 'organisatorische_eenheid', 'zaakmagazijn.rgbz_mapping.models.OrganisatorischeEenheidProxy'),
    )
    objects = ProxyManager()


class NatuurlijkPersoonProxy(ModelProxy):
    model = NatuurlijkPersoon
    fields = (
        # INGESCHREVEN PERSOON.Burgerservicenummer -> RSGB.INGESCHREVEN NATUURLIJK PERSOON.Burgerservicenummer
        ProxyField('burgerservicenummer', 'burgerservicenummer'),  # inp.bsn
        # ANDER NATUURLIJK PERSOON.Nummer ander natuurlijk persoon -> RSGB.ANDER NATUURLIJK PERSOON.Nummer ander natuurlijk persoon
        ProxyField('nummer_ander_natuurlijk_persoon', 'nummer_ander_natuurlijk_persoon'),  # anp.identificatie

        # Geslachtsnaam -> RSGB.Naam NATUURLIJK PERSOON.Geslachtsnaam
        ProxyField('geslachtsnaam', 'naam_geslachtsnaam'),  # geslachtsnaam
        # Voornamen   RSGB.Naam NATUURLIJK PERSOON.Voornamen
        ProxyField('voornamen', 'naam_voornamen'),  # voornamen
        # Voorvoegsels geslachtsnaam -> RSGB.Naam NATUURLIJK PERSOON.Voorvoegsel geslachtsnaam
        ProxyField('voorvoegsels_geslachtsnaam', 'naam_voorvoegsel_geslachtsnaam_voorvoegsel'),  # voorvoegselGeslachtsnaam
        # Voorletters (Geen vertaling voor gedefineerd)
        ProxyField('voorletters', 'naam_aanschrijving_voorletters_aanschrijving'),  # voorletters


        # Aanhef aanschrijving -> RSGB.Naam aanschrijving NATUURLIJK PERSOON.Geslachtsnaam aanschrijving
        ProxyField('aanhef_aanschrijving', 'naam_aanschrijving_aanhef_aanschrijving'),  # aanhefAanschrijving
        # Voorletters aanschrijving -> RSGB.Naam aanschrijving NATUURLIJK PERSOON.Voorletters aanschrijving
        ProxyField('voorletters', 'naam_aanschrijving_voorletters_aanschrijving'),
        # Voornamen aanschrijving  -> RSGB.Naam aanschrijving NATUURLIJK PERSOON.Voornamen aanschrijving
        ProxyField('voornamen_aanschrijving', 'naam_aanschrijving_voornamen_aanschrijving'),  # voornamenAanschrijving
        # Geslachtsnaam aanschrijving -> RSGB.Naam aanschrijving NATUURLIJK PERSOON.Aanhef aanschrijving
        ProxyField('geslachtsnaam_aanschrijving', 'naam_aanschrijving_geslachtsnaam_aanschrijving'),  # geslachtsnaamAanschrijving

        # Geslachtsaanduiding -> RSGB.NATUURLIJK PERSOON.Geslachtsaanduiding
        ProxyField('geslachtsaanduiding', 'geslachtsaanduiding'),  # geslachtsaanduiding
        # TODO [KING]: I think this is meant as an 'OR' between either.
        # Geboortedatum -> RSGB.Geboorte INGESCHREVEN NATUURLIJK PERSOON.Geboortedatum
        # Geboortedatum   RSGB.ANDER NATUURLIJK PERSOON.Geboortedatum
        ProxyField('geboortedatum', 'geboortedatum_ingeschreven_persoon'),
        # TODO [KING]: I think this is meant as an 'OR' between either.
        # Overlijdensdatum    RSGB.Overlijden INGESCHREVEN NATUURLIJK PERSOON.Overlijdensdatum
        # Overlijdensdatum    RSGB.ANDER NATUURLIJK PERSOON.Overlijdensdatum
        ProxyField('overlijdensdatum', 'overlijdensdatum_ingeschreven_persoon'),
        # INGESCHREVEN PERSOON . Verblijfsplaats    Verblijfadres NATUURLIJK PERSOON
        ProxyForeignKey('verblijfadres', 'verblijfadres', 'zaakmagazijn.rgbz_mapping.models.CorrespondentieadresProxy'),
        # SUBJECT . Verblijf buitenland   Verblijf buitenland SUBJECT
        ProxyForeignKey('verblijf_buitenland', 'verblijf_buitenland', 'zaakmagazijn.rgbz_mapping.models.VerblijfBuitenlandProxy'),
        # SUBJECT heeft als correspondentieadres ADRESSEERBAAR OBJECT AANDUIDING  Correspondentieadres SUBJECT
        ProxyForeignKey('correspondentieadres', 'correspondentieadres', 'zaakmagazijn.rgbz_mapping.models.CorrespondentieadresProxy'),
    )
    objects = ProxyManager()


class NietNatuurlijkPersoonProxy(ModelProxy):
    model = NietNatuurlijkPersoon
    fields = (
        # NNP-ID RSGB.INGESCHREVEN NIET-NATUURLIJK PERSOON.RSIN
        ProxyField('nnpid', 'rsin'),
        # ANDER BUITENLANDS NIET-NATUURLIJK PERSOON .  Nummer ander buitenlands niet-natuurlijk persoon RSGB.ANDER BUITENLANDS NIET-NATUURLIJK PERSOON.Nummer ander buitenlands niet-natuurlijk persoon
        ProxyField('nummer_ander_buitenlands_nietnatuurlijk_persoon', 'nummer_ander_buitenlands_nietnatuurlijk_persoon'),
        # SUBJECT . Subjecttypering   -   Vervallen   N.v.t.
        ProxyField('subjecttypering', None, rgbz1_field=models.CharField(
            verbose_name='subjecttypering', max_length=1, choices=Subjecttypering.choices,
            null=False, blank=False)),
        # (Statutaire) Naam RSGB.NIET-NATUURLIJK PERSOON.(Statutaire) Naam
        ProxyField('statutaire_naam', 'statutaire_naam'),
        # Datum aanvang   RSGB.NIET-NATUURLIJK PERSOON.Datum aanvang
        ProxyField('datum_aanvang', 'datum_aanvang'),
        # Datum beëindiging   RSGB.NIET-NATUURLIJK PERSOON.Datum beeindiging
        ProxyField('datum_beeindiging', 'datum_beeindiging'),
        ProxyForeignKey('correspondentieadres', 'correspondentieadres', 'zaakmagazijn.rgbz_mapping.models.CorrespondentieadresProxy'),
        ProxyForeignKey('verblijf_buitenland', 'verblijf_buitenland', 'zaakmagazijn.rgbz_mapping.models.VerblijfBuitenlandProxy'),
    )
    objects = ProxyManager()

    @classmethod
    def to_rgbz1_subjecttypering(cls, obj):
        """"
        Waarde ="21" of "23" indien het een Ingeschreven niet-natuurlijk persoon resp. Ander buitenlands niet-natuurlijk persoon betreft
        """
        return Subjecttypering.innp


class VestigingProxy(ModelProxy):
    model = Vestiging
    fields = (
        ProxyField('vestigingsnummer', 'identificatie'),
        ProxyField('handelsnaam', 'handelsnaam'),
        ProxyField('verkorte_naam', 'verkorte_naam'),
        ProxyField('datum_aanvang', 'datum_aanvang'),
        ProxyField('datum_beeindiging', 'datum_beeindiging'),
        ProxyForeignKey('locatieadres', 'locatieadres', 'zaakmagazijn.rgbz_mapping.models.LocatieadresProxy'),
        ProxyForeignKey('verblijf_buitenland', 'verblijf_buitenland', 'zaakmagazijn.rgbz_mapping.models.VerblijfBuitenlandProxy'),
    )
    objects = ProxyManager()


class VestigingVanZaakBehandelendeOrganisatieProxy(ModelProxy):
    model = VestigingVanZaakBehandelendeOrganisatie
    fields = (
        ProxyForeignKey('is_specialisatie_van', 'is_specialisatie_van', VestigingProxy),
    )
    objects = ProxyManager()


class OrganisatorischeEenheidProxy(ModelProxy):
    model = OrganisatorischeEenheid
    fields = (
        ProxyField('organisatieidentificatie', 'organisatieeenheididentificatie'),
        ProxyField(None, 'organisatieidentificatie'),
        ProxyField('datum_ontstaan', 'datum_ontstaan'),
        ProxyField('datum_opheffing', 'datum_opheffing'),
        ProxyField('emailadres', 'emailadres'),
        ProxyField('faxnummer', 'faxnummer'),
        ProxyField('naam', 'naam'),
        ProxyField('naam_verkort', 'naam_verkort'),
        ProxyField('omschrijving', 'omschrijving'),
        ProxyField('telefoonnummer', 'telefoonnummer'),
        ProxyField('toelichting', 'toelichting'),
        ProxyForeignKey('gevestigd_in', 'gevestigd_in', VestigingVanZaakBehandelendeOrganisatieProxy),
    )
    objects = ProxyManager()

    @classmethod
    def to_rgbz2_organisatieidentificatie(cls, rgbz1_kwargs):
        try:
            int(rgbz1_kwargs['organisatieidentificatie'][:4])
        except ValueError:
            return 0


# Klantcontact


# KlantContactpersoon


class RolProxy(ModelProxy):
    model = Rol
    fields = (
        ProxyField('rolomschrijving', 'rolomschrijving'),
        ProxyField('rolomschrijving_generiek', 'rolomschrijving_generiek'),
        ProxyField('roltoelichting', 'roltoelichting'),
        ProxyField(None, 'indicatie_machtiging'),
        ProxyForeignKey('zaak', 'zaak', 'zaakmagazijn.rgbz_mapping.models.ZaakProxy'),
        ProxyForeignKey('betrokkene', 'betrokkene', BetrokkeneProxy),
        ProxyForeignKey('contactpersoon', 'contactpersoon', 'zaakmagazijn.rgbz_mapping.models.ContactpersoonProxy'),

        ProxyField('begin_geldigheid', 'begin_geldigheid'),
        ProxyField('eind_geldigheid', 'eind_geldigheid'),
        ProxyField('begin_relatie', 'begin_relatie'),
        ProxyField('eind_relatie', 'eind_relatie'),
        ProxyField('tijdstip_registratie', 'tijdstip_registratie'),

        ProxyForeignKey(
            'afwijkend_correspondentie_postadres',
            'afwijkend_correspondentie_postadres',
            'zaakmagazijn.rgbz_mapping.models.PostAdresProxy')

    )
    objects = ProxyManager()

    @classmethod
    def _to_rgbz2_rolomschrijving_generiek(cls, rol):
        """
        "Gemachtigde" wordt "Belanghebbende"
        "Overig" wordt "Adviseur"
        "Uitvoerder" wordt "Behandelaar"
        "Verantwoordelijke" wordt "Beslisser"
        Overige rolbenamingen blijven gelijk.
        """
        mapping = {
            RGBZ1Rolomschrijving.belanghebbende: RGBZ2RolomschrijvingGeneriek.belanghebbende,
            RGBZ1Rolomschrijving.gemachtigde: RGBZ2RolomschrijvingGeneriek.belanghebbende,
            RGBZ1Rolomschrijving.initiator: RGBZ2RolomschrijvingGeneriek.initiator,
            RGBZ1Rolomschrijving.overig: RGBZ2RolomschrijvingGeneriek.adviseur,
            RGBZ1Rolomschrijving.uitvoerder: RGBZ2RolomschrijvingGeneriek.behandelaar,
            RGBZ1Rolomschrijving.verantwoordelijke: RGBZ2RolomschrijvingGeneriek.beslisser,
        }
        # TODO [KING]: This fallback is a deviation of the original mapping document. RGBZ 1.0
        # 'rolomschrijving' does not have any constraints.
        return mapping.get(rol, RGBZ2RolomschrijvingGeneriek.adviseur)

    @classmethod
    def to_rgbz2_rolomschrijving(cls, rgbz1_kwargs):
        return cls._to_rgbz2_rolomschrijving_generiek(rgbz1_kwargs['rolomschrijving'])

    @classmethod
    def to_rgbz2_rolomschrijving_generiek(cls, rgbz1_kwargs):
        return cls._to_rgbz2_rolomschrijving_generiek(rgbz1_kwargs['rolomschrijving'])

    @classmethod
    def to_rgbz1_rolomschrijving_generiek(cls, rgbz2_obj):
        """
        Indien 'Indicatie machtiging' de waarde "gemachtigde" heeft, dan "Gemachtigde", anders:
        "Adviseur" wordt "Overig"
        "Behandelaar" wordt "Uitvoerder"
        "Beslisser" wordt "Verantwoordelijke"
        "Klantcontacter" wordt "Overig"
        "Mede-initiator" wordt "Overig"
        "Zaakcoordinator" wordt "Overig"
        Overige rolbenamingen blijven gelijk.
        """

        if rgbz2_obj.indicatie_machtiging == RGBZ2IndicatieMachtiging.gemachtigde:
            return RGBZ1Rolomschrijving.gemachtigde

        mapping = {
            RGBZ2RolomschrijvingGeneriek.adviseur: RGBZ1Rolomschrijving.overig,
            RGBZ2RolomschrijvingGeneriek.behandelaar: RGBZ1Rolomschrijving.uitvoerder,
            RGBZ2RolomschrijvingGeneriek.beslisser: RGBZ1Rolomschrijving.verantwoordelijke,
            RGBZ2RolomschrijvingGeneriek.klantcontacter: RGBZ1Rolomschrijving.overig,
            RGBZ2RolomschrijvingGeneriek.medeinitiator: RGBZ1Rolomschrijving.overig,
            RGBZ2RolomschrijvingGeneriek.zaakcoordinator: RGBZ1Rolomschrijving.overig,
            RGBZ2RolomschrijvingGeneriek.belanghebbende: RGBZ1Rolomschrijving.belanghebbende,
            RGBZ2RolomschrijvingGeneriek.initiator: RGBZ1Rolomschrijving.initiator,
        }

        return mapping[rgbz2_obj.rolomschrijving]

    @classmethod
    def to_rgbz1_rolomschrijving(cls, rgbz2_obj):
        return cls.to_rgbz1_rolomschrijving_generiek(rgbz2_obj)

    @classmethod
    def get_rol_defaults(cls, rol):
        assert rol in dict(RGBZ1Rolomschrijving.choices).keys()

        rgbz2_rol = cls._to_rgbz2_rolomschrijving_generiek(rol)
        rgbz2_rol_defaults = cls.model.get_rol_defaults(rgbz2_rol)
        return {
            'rolomschrijving': rol,
            'rolomschrijving_generiek': rol,
            'roltoelichting': rgbz2_rol_defaults['roltoelichting']
        }

    @classmethod
    def to_rgbz2_indicatie_machtiging(cls, rgbz1_kwargs):
        """
        Indien 'Rolomschrijving generiek' de waarde "Gemachtigde" heeft, dan
        "gemachtigde", anders geen waarde.
        """
        if rgbz1_kwargs['rolomschrijving_generiek'] == RGBZ1Rolomschrijving.gemachtigde:
            return RGBZ2IndicatieMachtiging.gemachtigde
        return ''

# Verzending
