from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.db import models

from zaakmagazijn.cmis.models import CMISMixin
from zaakmagazijn.utils import stuf_datetime
from zaakmagazijn.utils.fields import StUFDateField, StUFDateTimeField

from ...rsgb.choices import AdelijkeTitel, NaamGebruik
from ...rsgb.models.mixins import BereikenMixin
from ..choices import (
    AardRelatieVerzending, IndicatieMachtiging, Rolomschrijving,
    RolomschrijvingGeneriek
)
from ..validators import validate_non_negative_string
from .basemodels import (
    NietNatuurlijkPersoonBaseClass, Object, OrganisatorischeEenheidBaseClass
)
from .mixins import (
    AfwijkendeCorrespondentieMixin, BSNMixin, GeslachtsAanduidingMixin,
    RekeningnummerMixin, TijdstipRegistratieMixin, TijdvakGeldigheidMixin,
    TijdvakRelatieMixin, TypeMixin
)


class Betrokkene(Object):
    """
    Een SUBJECT, zijnde een NATUURLIJK PERSOON, NIET-NATUURLIJK PERSOON
    of VESTIGING, ORGANISATORISCHE EENHEID (binnen een vestiging van de
    zaak-behandelende niet-natuurlijk persoon), of MEDEWERKER (van die
    organisatorische eenheid) die een rol kan spelen bij een ZAAK.
    """
    zaken = models.ManyToManyField('rgbz.Zaak', through='rgbz.Rol')

    _betrokkenetype_model = models.CharField(max_length=50, null=True, blank=True)
    betrokkenetype = models.CharField(max_length=3, default='???')

    class Meta:
        mnemonic = 'BTR'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._save_child_model('Betrokkene', '_betrokkenetype_model')
        self._save_type('Betrokkene', 'betrokkenetype')

    def is_type(self):
        return self._determine_type('Betrokkene', '_betrokkenetype_model')

    # return alle zaken
    def heeft_rol_in(self):
        """
        :return: De taken, rechten en/of verplichtingen die een specifieke
        betrokkene heeft ten aanzien van een specifieke zaak.
        """
        return self.zaken.all()

    def heeft_verzonden_of_ontvangen(self):
        return self.informatieobjecten.all()

    def adres_binnenland(self):
        return self.is_type().adres_gegevens_binnenland()

    def adres_buitenland(self):
        return self.is_type().adres_gegevens_buitenland()


class Medewerker(CMISMixin, GeslachtsAanduidingMixin, BereikenMixin, Betrokkene):
    """
    Een MEDEWERKER van de organisatie die zaken behandelt uit hoofde van
    zijn of haar functie binnen een ORGANISATORISCHE EENHEID.

    Combinatie van (achtereenvolgens) de Organisatie-identificatie van
    ORGANISATORISCHE EENHEID waarvan de MEDEWERKER deel uit maakt met
    Medewerkeridentificatie.
    """
    medewerkeridentificatie = models.CharField(
        max_length=24, help_text='Een korte unieke aanduiding van de MEDEWERKER.')
    achternaam = models.CharField(
        max_length=200, help_text='De achternaam zoals de MEDEWERKER die in het dagelijkse verkeer gebruikt.'
    )
    # Alle geldige datums zowel op, voor of na de huidige datum en tijd
    datum_uit_dienst = StUFDateField(
        null=True, blank=True,
        help_text="Een aanduiding van de datum waarop dearbeidsplaatsvervulling eindigt."
    )

    functie = models.CharField(
        max_length=50, help_text='De aanduiding van de taken, rechten en plichten die de MEDEWERKER '
                                 'heeft of heeft gehad binnen de zaakbehandelende organisatie.')
    voorletters = models.CharField(
        max_length=20, help_text='De verzameling letters die gevormd wordt door de eerste letter van '
                                 'alle in volgorde voorkomende voornamen.')
    # voorvoegseltabel GBA (tabel 36
    voorvoegsel_achternaam = models.CharField(
        max_length=10, null=True,
        blank=True, help_text='Dat deel van de geslachtsnaam dat voorkomt in Tabel 36 (GBA), '
                              'voorvoegseltabel, en door een spatie van de geslachtsnaam is')
    organisatorische_eenheid = models.ForeignKey(
        'rgbz.OrganisatorischeEenheid', on_delete=models.CASCADE,
        blank=True, null=True)

    medewerkertoelichting = models.TextField(
        max_length=1000, null=True, blank=True, help_text='Toelichting bij en/of over de medewerker.')
    roepnaam = models.CharField(
        max_length=30, help_text='Naam waarmee de werknemer wordt aangesproken.')
    faxnummer = None

    CMIS_MAPPING = {
        'zsdms:medewerkeridentificatie': 'medewerkeridentificatie',  # v
        # TODO [TECH]: is this correct?
        # 'zsdms:voorvoegsel': 'voorvoegsel_achternaam',  # o
        # 'zsdms:achternaam': 'achternaam',  # o
    }

    class Meta:
        unique_together = ('organisatorische_eenheid', 'medewerkeridentificatie')
        mnemonic = 'MDW'

    def is_verantwoordelijk_voor(self) -> tuple:
        return (
            self.organisatorische_eenheid_verantwoordelijke,
            self.zaaktype_set.all()
        )

    def is_contactpersoon_voor(self):
        return self.organisatorische_eenheid_contactpersoon

    def hoort_bij(self):
        return self.organisatorische_eenheid

    def create_identificatie(self):
        if self.organisatorische_eenheid:
            id_prefix = self.organisatorische_eenheid.organisatieeenheididentificatie
        else:
            # TODO [KING]: 'organisatorische_eenheid' can be blank, do we want to prefix with something ???? / 0000 / '    '
            id_prefix = ''

        return '{}{}'.format(
            id_prefix, self.medewerkeridentificatie,
        )


class NatuurlijkPersoon(CMISMixin, BereikenMixin, GeslachtsAanduidingMixin, RekeningnummerMixin, Betrokkene):
    """
    De aan het RSGB ontleende gegevens van een NATUURLIJK PERSOON die in het RGBZ gebruikt
    worden. Zie voor de specificaties van deze gegevens het RSGB.
    """

    """
    Mixin voor een Burgerservicenummer veld, opgenomen als mixin om redudantie te voorkomen.

    Alle nummers waarvoor geldt dat, indien aangeduid als (s0 s1 s2 s3 s4
    s5 s6 s7 s8), het resultaat van (9*s0) + (8*s1) + (7*s2) +...+ (2*s7) -
    (1*s8) deelbaar is door elf.
    """
    burgerservicenummer = models.CharField(null=True, blank=True, max_length=9, validators=[validate_non_negative_string, ],
                                           help_text='Het burgerservicenummer, bedoeld in artikel 1.1 van de Wet algemene bepalingen burgerservicenummer.')
    nummer_ander_natuurlijk_persoon = models.CharField(
        null=True, blank=True, max_length=17, help_text='Het door de gemeente uitgegeven unieke nummer voor een ANDER NATUURLIJK PERSOON'
    )

    verblijfadres = models.ForeignKey(
        'rsgb.VerblijfAdres', on_delete=models.SET_NULL, null=True, blank=True,
        help_text='De gegevens over het verblijf en adres van de NATUURLIJK PERSOON',
        related_name='verblijfadres'
    )

    """
    Following is the RGBZ 2.0 Group attribute 'Naam'
    """
    naam_voornamen = models.CharField(
        null=True, blank=True, max_length=200, help_text='Voornamen bij de naam die de persoon wenst te voeren.'
    )
    naam_geslachtsnaam = models.CharField(
        max_length=200, help_text='De stam van de geslachtsnaam.')
    naam_adelijke_titel = models.CharField(
        null=True, blank=True, max_length=1, choices=AdelijkeTitel.choices)
    """
    Following is the RGBZ 2.0 Group attribute 'Voorvoegsel' within the Group attribute 'Naam'
    """
    # Required in RGBZ 2.0 (when a Voorvoegsel geslachtsnaam is set)
    # naam_voorvoegsel_geslachtsnaam_voorvoegselnummer = models.CharField(
    #     null=True, max_length=3, validators=[RegexValidator(r'^\d{1,10}$')],
    #     help_text='Het identificerende nummer van het voorvoegsel'
    # )
    # Required in RGBZ 2.0 (when a Voorvoegsel geslachtsnaam is set)
    # naam_voorvoegsel_geslachtsnaam_lo3_voorvoegsel = models.CharField(
    #     null=True, max_length=80)
    # # Required in RGBZ 2.0 (when a Voorvoegsel geslachtsnaam is set)
    naam_voorvoegsel_geslachtsnaam_voorvoegsel = models.CharField(
        null=True, blank=True, max_length=80)
    # Required in RGBZ 2.0 (when a Voorvoegsel geslachtsnaam is set)
    # naam_voorvoegsel_geslachtsnaam_scheidingsteken = models.CharField(
    #     null=True, max_length=1)

    academische_titel = models.ForeignKey(
        'rsgb.AcademischeTitel', null=True, blank=True)
    aanduiding_naamgebruik = models.CharField(
        max_length=1, null=True, blank=True, choices=NaamGebruik.choices,
        help_text='Een aanduiding voor de wijze van aanschrijving van de NATUURLIJKe PERSOON.')
    geboortedatum_ingeschreven_persoon = StUFDateField()
    geboortedatum_ander_natuurlijk_persoon = StUFDateField(null=True, blank=True)

    """
    Following is the RGBZ 2.0 Group attribute 'Naam aanschrijving'
    """
    naam_aanschrijving_voorletters_aanschrijving = models.CharField(
        max_length=20, null=True, blank=True,
        help_text='De voorletters waarmee een persoon aangeschreven wil worden.')
    naam_aanschrijving_voornamen_aanschrijving = models.CharField(
        max_length=200, null=True, blank=True,
        help_text='Voornamen bij de naam die de persoon wenst te voeren.'
    )
    naam_aanschrijving_geslachtsnaam_aanschrijving = models.CharField(
        null=True, blank=True, max_length=200, help_text='Geslachtsnaam die de persoon wenst te voeren'
    )
    naam_aanschrijving_aanhef_aanschrijving = models.CharField(
        null=True, blank=True, max_length=50, help_text='De aanhef waarmee de persoon aangeschreven wil worden.'
    )

    overlijdensdatum_ingeschreven_persoon = StUFDateField(null=True, blank=True)
    overlijdensdatum_ander_natuurlijk_persoon = StUFDateField(null=True, blank=True)
    correspondentieadres = models.ForeignKey(
        'rsgb.Correspondentieadres', on_delete=models.SET_NULL, null=True, blank=True, related_name='correspondentieadres')
    verblijf_buitenland = models.ForeignKey(
        'rsgb.VerblijfBuitenland', null=True, blank=True,
        help_text='De gegevens over het verblijf in het buitenland')
    postadres = models.ForeignKey(
        'rsgb.PostAdres', on_delete=models.SET_NULL, null=True, blank=True)

    CMIS_MAPPING = {
        # TODO [KING]: ZDS has plural version
        # 'zsdms:voorvoegselsGeslachtsnaam': vv_geslachtsnaam,  # o
        # 'zsdms:voorvoegselGeslachtsnaam': 'naam_voorvoegsel_geslachtsnaam_voorvoegsel',  # o
        # 'zsdms:geslachtsnaam': 'naam_geslachtsnaam',  # o
        'zsdms:inp.bsn': 'burgerservicenummer',  # v
        'zsdms:ann.identificatie': 'nummer_ander_natuurlijk_persoon',  # v
    }

    class Meta:
        mnemonic = 'NPS'

    # FIXME: Mag het voorkomen dat er geen velden worden ge-returned?
    def adres_gegevens_binnenland(self):
        # The order below is not defined anywhere, we made a best-effort assumption.
        return [
            gegeven for gegeven in [self.verblijfadres, self.correspondentieadres, self.postadres]
            if gegeven is not None
        ]

    def adres_gegevens_buitenland(self):
        # The order below is not defined anywhere, we made a best-effort assumption.
        return [
            gegeven for gegeven in [self.verblijfadres, self.postadres, self.verblijf_buitenland]
            if gegeven is not None
        ]

    def create_identificatie(self):
        return self.burgerservicenummer or self.nummer_ander_natuurlijk_persoon

    def clean(self):
        if not (bool(self.burgerservicenummer) ^ bool(self.nummer_ander_natuurlijk_persoon)):
            raise ValidationError('Het is alleen mogelijk om een burgerservicenummer '
                                  'of een nummer ander natuurlijk persoon in te vullen.')
        return super().clean()

    def save(self, *args, **kwargs):
        assert (bool(self.burgerservicenummer) ^ bool(self.nummer_ander_natuurlijk_persoon)), \
            'Either \'burgerservicenummer\' or \'nummer_ander_natuurlijk_persoon\' should be set. Not both.'
        super().save(*args, **kwargs)


class NietNatuurlijkPersoon(CMISMixin, BereikenMixin, NietNatuurlijkPersoonBaseClass, RekeningnummerMixin, Betrokkene):
    naam = models.CharField(
        max_length=200, null=True,
        blank=True, help_text='De benaming van de BETROKKENE indien dit een (NIET) NATUURLIJK PERSOON,'
                              ' VESTIGING of specialisatie daarvan is.')
    nummer_ander_buitenlands_nietnatuurlijk_persoon = models.CharField(
        max_length=17, help_text='Het door de gemeente uitgegeven uniekenummer voor een ANDER NIET-NATUURLIJK PERSOON')

    correspondentieadres = models.ForeignKey(
        'rsgb.Correspondentieadres', on_delete=models.SET_NULL, null=True, blank=True,
        help_text=''
    )
    postadres = models.ForeignKey(
        'rsgb.PostAdres', on_delete=models.SET_NULL, null=True, blank=True)

    CMIS_MAPPING = {
        'zsdms:inn.nnpId': 'rsin',  # v
        # 'zsdms:statutairenaam': 'statutaire_naam',  # o
        'zsdms:ann.identificatie': 'nummer_ander_buitenlands_nietnatuurlijk_persoon',  # v
    }

    class Meta:
        mnemonic = 'NNP'

    def adres_gegevens_binnenland(self):
        # The order below is not defined anywhere, we made a best-effort assumption.
        return [self.correspondentieadres, self.postadres]

    def adres_gegevens_buitenland(self):
        # The order below is not defined anywhere, we made a best-effort assumption.
        return [self.postadres, self.verblijf_buitenland]


class Vestiging(CMISMixin, BereikenMixin, RekeningnummerMixin, Betrokkene):
    """
    Een gebouw of complex van gebouwen waar duurzame uitoefening van de activiteiten
    van een onderneming of rechtspersoon plaatsvindt.

    Unieke aanduiding Vestigingsnummer
    """
    naam = models.CharField(
        max_length=200, null=True,
        blank=True, help_text='De benaming van de BETROKKENE indien dit een (NIET) NATUURLIJK PERSOON,'
                              ' VESTIGING of specialisatie daarvan is.')
    # Alléén vestigingen van het type "Commerciele vestiging" hebben één of meer handelsna(a)m(en).
    # In alle andere gevallen heeft een vestiging slechts één naam.
    handelsnaam = ArrayField(models.TextField(
        max_length=625, help_text='De naam van de vestiging waaronder gehandeld wordt.'))

    verkorte_naam = models.CharField(
        max_length=45, null=True,
        blank=True, help_text='De administratieve naam in het handelsregister indien de naam '
                              'langer is dan 45 karakters'
    )
    # TODO [KING]: This is 'null' = False in RGBZ 2.0. But the kennisgevingsbericht code can't deal with this yet.
    locatieadres = models.ForeignKey(
        'rsgb.Locatieadres', on_delete=models.SET_NULL, related_name='locatieadres', null=True, blank=True)
    correspondentieadres = models.ForeignKey(
        'rsgb.Correspondentieadres', on_delete=models.SET_NULL, null=True, blank=True,
        help_text=''
    )
    postadres = models.ForeignKey(
        'rsgb.PostAdres', on_delete=models.SET_NULL, null=True, blank=True, related_name='postadress')

    verblijf_buitenland = models.ForeignKey(
        'rsgb.VerblijfBuitenland', null=True, blank=True, help_text='De gegevens over het verblijf in het buitenland'
    )
    datum_aanvang = StUFDateField(
        default=stuf_datetime.today,
        help_text='De datum van aanvang van de vestiging.'
    )
    datum_beeindiging = StUFDateField(
        null=True, blank=True, help_text='De datum van beëindiging van de vestiging'
    )

    _vestigingtype_model = models.CharField(max_length=50, null=True, blank=True)

    CMIS_MAPPING = {
        'zsdms:vestigingsNummer': 'identificatie',  # v
    }

    class Meta:
        mnemonic = 'VES'

    def is_type(self):
        return self._determine_type('Vestiging', '_vestigingtype_model')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._save_child_model('Vestiging', '_vestigingtype_model')

    @property
    def vestigingsnummer(self):
        # vestigingsnummer = models.CharField(
        #     max_length=12,
        #     help_text='Landelijk uniek identificerend administratienummer van een VESTIGING zoals toegewezen'
        #               'door de Kamer van Koophandel (KvK).')
        return self.identificatie

    def adres_gegevens_binnenland(self):
        # The order below is not defined anywhere, we made a best-effort assumption.
        return [
            gegeven for gegeven in [self.locatieadres, self.correspondentieadres, self.postadres]
            if gegeven is not None
        ]

    def adres_gegevens_buitenland(self):
        # The order below is not defined anywhere, we made a best-effort assumption.
        return [
            gegeven for gegeven in [self.locatieadres, self.postadres, self.verblijf_buitenland]
            if gegeven is not None
        ]


class VestigingVanZaakBehandelendeOrganisatie(models.Model):
    """
    Een VESTIGING van een onderneming of rechtspersoon zijnde de zaakbehandelende organisatie.

    Unieke aanduiding SUBJECT.Subjecttypering gevolgd door het Vestigingsnummer
    """
    is_specialisatie_van = models.ForeignKey(Vestiging, on_delete=models.CASCADE)

    class Meta:
        mnemonic = 'VZO'

    def __str__(self):
        return '{}'.format(self.is_specialisatie_van)


class OrganisatorischeEenheid(CMISMixin, OrganisatorischeEenheidBaseClass, BereikenMixin, Betrokkene):
    """
    Het deel van een functioneel afgebakend onderdeel binnen de organisatie
    dat haar activiteiten uitvoert binnen een VESTIGING VAN
    ZAAKBEHANDELENDE ORGANISATIE en die verantwoordelijk is voor de
    behandeling van zaken.

    Unieke aanduiding Combinatie van (achtereenvolgens) de Organisatie-identificatie met
    Organisatie-eenheid-identificatie.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # TODO [TECH]: Remove this once we have a proper translation layer from RGBZ 1.0 to 2.0
        if self.identificatie:
            try:
                self.organisatieidentificatie = int(self.identificatie[:4])
            except ValueError:
                pass

    organisatieeenheididentificatie = models.CharField(
        max_length=24, help_text='Een korte identificatie van de organisatorische eenheid.')

    naam_verkort = models.CharField(
        max_length=25, null=True, blank=True, help_text='Een verkorte naam voor de organisatorische eenheid.'
    )
    omschrijving = models.CharField(
        max_length=80, null=True, blank=True, help_text='Een omschrijving van de organisatorische eenheid.'
    )
    toelichting = models.TextField(
        max_length=1000, null=True, blank=True, help_text='Toelichting bij de organisatorische eenheid.'
    )

    # relaties
    verantwoordelijke = models.OneToOneField(
        Medewerker, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='organisatorische_eenheid_verantwoordelijke')
    contactpersoon = models.OneToOneField(
        Medewerker, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='organisatorische_eenheid_contactpersoon')

    # gevestigd in
    # TODO [TECH]: Renamed, due to naming collision.
    gevestigd_in = models.ForeignKey(
        'rgbz.VestigingVanZaakBehandelendeOrganisatie', on_delete=models.CASCADE)

    CMIS_MAPPING = {
        'zsdms:organisatieidentificatie': 'organisatieeenheididentificatie',  # v
    }

    class Meta:
        unique_together = ('organisatieidentificatie', 'organisatieeenheididentificatie')
        verbose_name_plural = 'Organisatorische eenheden'
        mnemonic = 'OEH'

    def is_gehuisvest_in(self):
        return self.gevestigd_in

    def is_verantwoordelijk_voor(self):
        return self.zaaktype_set.all()

    def create_identificatie(self):
        return '{}'.format(self.organisatieeenheididentificatie)


class Klantcontact(models.Model):
    """
    Een uniek en persoonlijk contact van een burger of bedrijfsmedewerker met een MEDEWERKER van de zaakbehandelende
    organisatie over een onderhanden of afgesloten ZAAK
    """
    identificatie = models.CharField(
        max_length=14, help_text='De unieke aanduiding van een KLANTCONTACT', unique=True)
    datumtijd = StUFDateTimeField(
        help_text='De datum en het tijdstip waarop het KLANTCONTACT begint'
    )
    kanaal = models.CharField(
        null=True, blank=True, max_length=20,
        help_text='Het communicatiekanaal waarlangs het KLANTCONTACT gevoerd wordt'
    )
    onderwerp = models.CharField(
        max_length=80, help_text='De kern van datgene waar het KLANTCONTACT over gaat.'
    )
    toelichting = models.TextField(
        null=True, blank=True, max_length=1000,
        help_text='Samenvattende beschrijving van de relevante kenmerken van het gevoerde KLANTCONTACT'
    )
    zaak = models.ForeignKey(
        'rgbz.Zaak', on_delete=models.CASCADE, help_text='De ZAAK waarop het KLANTCONTACT betrekking heeft.'
    )
    natuurlijk_persoon = models.ForeignKey(
        'rgbz.NatuurlijkPersoon', on_delete=models.SET_NULL, null=True, blank=True
    )
    vestiging = models.ManyToManyField(
        'rgbz.Vestiging', blank=True, through='rgbz.KlantContactpersoon')
    medewerker = models.ForeignKey(
        'rgbz.Medewerker',
        help_text='De MEDEWERKER die het individuele contact met de klant over een ZAAK heeft gehad.')

    class Meta:
        verbose_name_plural = 'Klantcontacten'
        mnemonic = 'KCT'
        # unique_together = ('identificatie', 'zaak')

    def __str__(self):
        return '{}_{}'.format(self.zaak, self.identificatie)

    def heeft_betrekking_op(self):
        return self.zaak

    def heeft_plaats_gevonden_met(self):
        return self.natuurlijk_persoon, self.vestiging.first()

    def is_gevoerd_door(self):
        return self.medewerker


class KlantContactpersoon(models.Model):
    """
    De gegevens van de MEDEWERKER van een VESTIGING van een onderneming waarmee een KLANTCONTACT plaats vond.
    """
    klantcontact = models.ForeignKey('rgbz.Klantcontact', unique=True)
    vestiging = models.ForeignKey('rgbz.Vestiging')
    contactpersoon = models.ForeignKey('rgbz.Contactpersoon')

    class Meta:
        mnemonic = 'CTP'


class Rol(TijdvakGeldigheidMixin, TijdvakRelatieMixin, TijdstipRegistratieMixin, AfwijkendeCorrespondentieMixin):
    """
    De taken, rechten en/of verplichtingen die een specifieke BETROKKENE heeft
    ten aanzien van een specifieke ZAAK
    """
    betrokkene = models.ForeignKey('rgbz.Betrokkene')
    zaak = models.ForeignKey('rgbz.Zaak', on_delete=models.CASCADE)
    rolomschrijving = models.CharField(
        max_length=80, choices=Rolomschrijving.choices,
        help_text='Algemeen gehanteerde benaming van de aard van de ROL')
    rolomschrijving_generiek = models.CharField(
        max_length=40, choices=RolomschrijvingGeneriek.choices,
        help_text='Algemeen gehanteerde benaming van de aard van de ROL')
    roltoelichting = models.TextField(
        max_length=1000)
    indicatie_machtiging = models.CharField(
        max_length=15, choices=IndicatieMachtiging.choices, null=True, blank=True,
        help_text='Indicatie of de BETROKKENE in de ROL bij de ZAAK '
                  'optreedt als gemachtigde van een andere BETROKKENE bij die ZAAK'
    )
    contactpersoon = models.ForeignKey('rgbz.Contactpersoon', on_delete=models.SET_NULL, null=True, blank=True)
    # Kan binnen een Zaak registreren dat /status/ bereikt is

    class Meta:
        mnemonic = 'ROL'

    @classmethod
    def get_rol_defaults(cls, rol):
        """
        Based on the setting 'ZAAKMAGAZIJN_ROLOMSCHRIJVINGEN' create the
        default kwargs for creating a 'Rol'

        :param rol A rol from Rolomschrijving.choices
        :return Default values which should be used when creation a role relation.
        """
        try:
            setting = settings.ZAAKMAGAZIJN_ROLOMSCHRIJVINGEN
            rol_defaults = setting[rol]
        except (IndexError, AttributeError):
            raise ImproperlyConfigured('The settings: ZAAKMAGAZIJN_ROLOMSCHRIJVINGEN should be defined for rol {}'.format(rol))

        return {
            'rolomschrijving': rol,
            'rolomschrijving_generiek': rol_defaults['generiek'],
            'roltoelichting': rol_defaults['toelichting'],
        }

    def zet_als_betrokkene(self):
        return self.status_set.all()

    def heeft_als_aanspreekpunt(self):
        return self.contactpersoon


class Verzending(AfwijkendeCorrespondentieMixin):
    """
    De BETROKKENE waarvan het INFORMATIEOBJECT is ontvangen en/of waaraan het is verzonden
    """
    betrokkene = models.ForeignKey(
        'rgbz.Betrokkene', on_delete=models.CASCADE)
    informatieobject = models.ForeignKey('rgbz.InformatieObject', on_delete=models.CASCADE)

    aard_relatie = models.CharField(
        max_length=13, choices=AardRelatieVerzending.choices,
        help_text='Omschrijving van de aard van de relatie van de BETROKKENE tot het INFORMATIEOBJECT')
    toelichting = models.CharField(
        max_length=200, null=True, blank=True, help_text='Verduidelijking van de afzender- of geadresseerde-relatie.')
    contactpersoonnaam = models.CharField(
        max_length=40, null=True, blank=True,
        help_text='De opgemaakte naam van de persoon die als aanspreekpunt fungeert voor '
                  'de BETROKKENE inzake het ontvangen of verzonden INFORMATIEOBJECT.')

    class Meta:
        # TODO [KING]: De mnemonic van "Verzending" is "VERZENDING" volgens het RGBZ, dat kan niet kloppen?
        mnemonic = 'VERZENDING'
