from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.validators import MaxValueValidator
from django.db import models

from ...cmis.models import CMISMixin
from ...utils.fields import StUFDateField, StUFDateTimeField
from ..choices import (
    AardRelatieZakenRelatie, ArchiefNominatie, ArchiefStatus,
    IndicatieMachtiging, JaNee, Rolomschrijving, RolomschrijvingGeneriek,
    Vertrouwelijkaanduiding
)
from ..validators import (
    alphanumeric_excluding_diacritic, validate_non_negative_string
)
from .basemodels import Object


class ZaakType(CMISMixin, models.Model):
    """

    """
    zaaktypeidentificatie = models.PositiveIntegerField(
        help_text='Unieke identificatie van het ZAAKTYPE binnen de CATALOGUS waarin het ZAAKTYPE voorkomt.',
        validators=[MaxValueValidator(99999)], unique=True)
    zaaktypeomschrijving = models.CharField(
        max_length=80, help_text='Omschrijving van de aard van ZAAKen van het ZAAKTYPE.')
    domein = models.CharField(
        max_length=5, help_text='Een afkorting waarmee wordt aangegeven voor welk domein in de CATALOGUS'
                                ' ZAAKTYPEn zijn uitgewerkt.')
    zaaktypeomschrijving_generiek = models.CharField(
        max_length=80, help_text='Algemeen gehanteerde omschrijving van de aard van ZAAKen van het ZAAKTYPE',
        null=True, blank=True)
    rsin = models.PositiveIntegerField(
        help_text='Het door een kamer toegekend uniek nummer voor de INGESCHREVEN NIET-NATUURLIJK PERSOON'
    )
    trefwoord = ArrayField(models.CharField(
        max_length=30), help_text='Een verzameling van trefwoorden waarmee ZAAKen '
                                  'van het ZAAKTYPE kunnen worden gekarakteriseerd.', null=True, blank=True) # Multivalue field
    # In het RGBZ staat dat dit een groepsattribuut soort is binnen het ZTC,
    # Echter staat er in het ZTC dat dit veld een N3 is. Omdat de definitie van dit veld verwijst naar het ZTC,
    # wordt deze als leidend geacht.
    doorlooptijd_behandeling = models.PositiveSmallIntegerField(
        help_text='De periode waarbinnen volgens wet- en regelgeving een ZAAK van het ZAAKTYPE afgerond dient te zijn.',
        validators=[MaxValueValidator(999)])
    servicenorm_behandeling = models.PositiveSmallIntegerField(
        help_text='De periode waarbinnen verwacht wordt dat een ZAAK van het ZAAKTYPE afgerond wordt '
                  'conform de geldende servicenormen van de zaakbehandelende organisatie(s)',
        validators=[MaxValueValidator(999)], null=True, blank=True)
    # De classificatiecode in het gehanteerde archiveringsclassificatiestelsel, gevolgd door een spatie en –
    # tussen haakjes - de gebruikelijke afkorting van de naam van het gehanteerde classificatiestelsel.
    archiefclassificatiecode = models.CharField(
        max_length=20, null=True, blank=True, help_text='De systematische identificatie van zaakdossiers van dit '
        'ZAAKTYPE overeenkomstig logisch gestructureerde '
        'conventies, methoden en procedureregels.')
    vertrouwelijk_aanduiding = models.CharField(
        max_length=20, choices=Vertrouwelijkaanduiding.choices,
        help_text='Aanduiding van de mate waarin zaakdossiers van ZAAKen van dit ZAAKTYPE voor de '
                  'openbaarheid bestemd zijn.')
    publicatie_indicatie = models.CharField(max_length=1, choices=JaNee.choices,
                                            help_text='Aanduiding of (het starten van) een ZAAK van dit ZAAKTYPE gepubliceerd moet worden.'
                                            )
    zaakcategorie = models.CharField(
        max_length=40, null=True, blank=True, help_text='Typering van de aard van ZAAKen van het ZAAKTYPE.'
    )
    publicatietekst = models.TextField(
        max_length=1000, null=True, blank=True, help_text='De generieke tekst van de publicatie van ZAAKen van dit ZAAKTYPE.')
    datum_begin_geldigheid_zaaktype = StUFDateField(
        help_text='Datum begin geldigheid zaaktype')
    datum_einde_geldigheid_zaaktype = StUFDateField(
        help_text='De datum waarop het ZAAKTYPE is opgeheven', blank=True)
    organisatorische_eenheid = models.ForeignKey(
        'rgbz.OrganisatorischeEenheid', on_delete=models.SET_NULL, null=True, blank=True)
    medewerker = models.ForeignKey(
        'rgbz.Medewerker', on_delete=models.SET_NULL, null=True, blank=True)

    CMIS_MAPPING = {
        'zsdms:Zaaktype-omschrijving': 'zaaktypeomschrijving',
    }

    class Meta:
        verbose_name_plural = 'Zaak types'
        mnemonic = 'ZKT'

    def verantwoordelijke(self):
        return self.organisatorische_eenheid or self.medewerker

    def heeft(self):
        return self.statustype_set.all()

    def clean(self):
        # Verzeker dat er minimaal en maximaal 1 verantwoordelijke (medewerker of organisatorische_eenheid) is gekozen
        if not self.medewerker and self.organisatorische_eenheid or self.medewerker and self.organisatorische_eenheid:
            raise ValidationError('Objecttype Zaaktype moet een medewerker OF organisatorische_eenheid'
                                  ' hebben als verantwoordelijke')


class StatusType(models.Model):
    """
    """
    statustypeomschrijving = models.CharField(
        max_length=80, help_text='Een korte, voor de initiator van de zaak relevante, '
                                 'omschrijving van de aard van de STATUS van zaken van een ZAAKTYPE.')
    statustypevolgnummer = models.PositiveSmallIntegerField(
        help_text='Een volgnummer voor statussen van het STATUSTYPE binnen een zaak.',
        validators=[MaxValueValidator(9999)]
    )
    # In het RGBZ staat dat dit een groepsattribuut soort is binnen het ZTC,
    # Echter staat er in het ZTC dat dit veld een N3 is. Omdat de definitie van dit veld verwijst naar het ZTC,
    # wordt deze als leidend geacht.
    doorlooptijd_status = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MaxValueValidator(999)])
    statustypeomschrijving_generiek = models.CharField(
        max_length=80, null=True, blank=True, help_text='Algemeen gehanteerde omschrijving '
        'van de aard van STATUSsen van het STATUSTYPE')
    datum_begin_geldigheid_statustype = StUFDateField(
        help_text='De datum waarop het STATUSTYPE is ontstaan.'
    )
    datum_einde_geldigheid_statustype = StUFDateField(
        null=True, blank=True, help_text='De datum waarop het STATUSTYPE is opgeheven.')

    # relaties
    zaaktype = models.ForeignKey('rgbz.ZaakType', on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Status types'
        mnemonic = 'STT'


class Zaak(CMISMixin, models.Model):
    """
    Een samenhangende hoeveelheid werk met een welgedefinieerde aanleiding
    en een welgedefinieerd eindresultaat, waarvan kwaliteit en doorlooptijd
    bewaakt moeten worden.
    """

    zaakidentificatie = models.CharField(
        max_length=40, unique=True,
        help_text='De unieke identificatie van de ZAAK binnen de organisatie die '
                  'verantwoordelijk is voor de behandeling van de ZAAK.',
        validators=[alphanumeric_excluding_diacritic, ]
    )
    # TODO: [KING] Taiga #275: In de KING documentatie staat N9
    bronorganisatie = models.CharField(max_length=9, validators=[validate_non_negative_string, ],
                                       help_text='Het RSIN van de Niet-natuurlijk persoon zijnde de '
                                       'organisatie die de zaak heeft gecreeerd.'
                                       )
    omschrijving = models.CharField(max_length=80, null=True, blank=True, help_text='Een korte omschrijving van de zaak.')
    toelichting = models.TextField(max_length=1000, null=True, blank=True, help_text='Een toelichting op de zaak.')
    registratiedatum = StUFDateField(
        help_text='De datum waarop de zaakbehandelende organisatie de ZAAK heeft geregistreerd')  # JJJJ-MM-DD
    verantwoordelijke_organisatie = models.CharField(max_length=9, validators=[validate_non_negative_string, ],
                                                     help_text='Het RSIN van de Niet-natuurlijk persoon zijnde de organisatie die eindverantwoordelijk is voor '
                                                     'de behandeling van de zaak.')
    einddatum = StUFDateField(
        help_text='De datum waarop volgens de planning verwacht wordt dat de zaak afgerond wordt.',
        null=True, blank=True
    )  # JJJJ-MM-DD
    startdatum = StUFDateField(help_text='De datum waarop met de uitvoering van de zaak is gestart')  # JJJJ-MM-DD
    einddatum_gepland = StUFDateField(
        help_text='De datum waarop volgens de planning verwacht wordt dat de zaak afgerond wordt.',
        null=True, blank=True
    )  # JJJJ-MM-DD
    uiterlijke_einddatum_afdoening = StUFDateField(
        help_text='De laatste datum waarop volgens wet- en regelgeving de zaak afgerond dient te zijn.',
        null=True, blank=True
    )

    resultaatomschrijving = models.CharField(max_length=80, null=True, blank=True, help_text='Een korte omschrijving wat het '
                                                                                             'resultaat van de zaak inhoudt.')
    resultaattoelichting = models.TextField(max_length=1000, help_text='Een toelichting op wat het resultaat van de '
                                                                       'zaak inhoudt.', null=True, blank=True)
    publicatiedatum = StUFDateField(null=True, blank=True, help_text='Datum waarop (het starten van) de zaak gepubliceerd is of wordt.') # Format staat niet gedefineerd

    archiefnominatie = models.CharField(max_length=16, null=True, blank=True, choices=ArchiefNominatie.choices,
                                        help_text='Aanduiding of het zaakdossier blijvend bewaard of na een '
                                                  'bepaalde termijn vernietigd moet worden.')
    archiefstatus = models.CharField(max_length=20, choices=ArchiefStatus.choices,
                                     help_text='De fase waarin het zaakdossier zich qua archivering bevindt')

    # Dit attribuutsoort moet van een waarde voorzien zijn als de attribuutsoort ‘Archiefstatus’ een waarde ongelijk
    # "Nog te archiveren" heeft.
    archiefactiedatum = StUFDateField(
        null=True, blank=True, help_text='De datum waarop het gearchiveerde zaakdossier vernietigd moet worden'
        ' dan wel overgebracht moet worden naar een archiefbewaarplaats.')

    betalingsindicatie = models.CharField(
        max_length=12, null=True, blank=True,
        help_text='Indicatie of de, met behandeling van de zaak gemoeide, kosten'
                  ' betaald zijn door de desbetreffende betrokkene.'
    )
    # Tijdstip
    laatste_betaaldatum = StUFDateTimeField(
        blank=True, help_text='De datum waarop de meest recente betaling is verwerkt van kosten'
        ' die gemoeid zijn met behandeling van de zaak.')

    zaakgeometrie = models.TextField(null=True, blank=True)

    # indien dit groepsattribuut soort niet van een waarde is voorzien, dan moet er minimaal sprake zijn van een waarde
    # voor de attribuutsoort ‘Zaakgeometrie’, één relatie ‘ZAAK heeft betrekking op OBJECTen’, één relatie ‘ZAAK heeft
    # betrekking op andere ZAAKen’ of één relatie ‘ZAAK is deelzaak van ZAAK’.
    gerelateerd_met = models.ManyToManyField(
        'rgbz.Zaak', blank=True, related_name='gerelateerdezaken',
        through='rgbz.ZakenRelatie')
    hoofdzaak = models.ForeignKey(
        'rgbz.Zaak', null=True, blank=True,
        help_text='De verwijzing naar de ZAAK, waarom verzocht is door de initiator daarvan, '
                  'die behandeld wordt in twee of meer separate ZAAKen waarvan de onderhavige ZAAK er één is.',
        related_name='deelzaken'
    )

    zaaktype = models.ForeignKey('rgbz.ZaakType', on_delete=models.CASCADE)

    informatieobjecten = models.ManyToManyField(
        'rgbz.InformatieObject', related_name='informatieobjecten', through='rgbz.ZaakInformatieObject'
    )

    """
    Bij een ZAAK kan maximaal één ROL met als Rolomschrijving
    generiek 'Initiator' voor komen.
    Bij een ZAAK kan maximaal één ROL met als Rolomschrijving
    generiek 'Zaakcoördinator' voor komen.
    """

    CMIS_MAPPING = {
        'cmis:name': 'zaakidentificatie',  # v
        'zsdms:zaakidentificatie': 'zaakidentificatie',  # v
        'zsdms:startdatum': 'startdatum',  # v
        'zsdms:einddatum': 'einddatum',  # o
        # TODO: [COMPAT] Missing in RGBZ?
        # 'zsdms:zaakniveau': 'zaakniveau',  # v
        # TODO: [COMPAT] Missing in RGBZ? Or is this just "has one or more deelzaken?"
        # 'zsdms:deelzakenindicatie': 'Deelzakenindicatie',  # v
        'zsdms:registratiedatum': 'registratiedatum',  # v
        'zsdms:archiefnominatie': 'archiefnominatie',  # v
        # TODO: [DMS] unknown, resultaattypeomschrijving is in the XML though
        # 'zsdms:resultaatomschrijving': 'resultaatomschrijving',  # v
        # TODO: [COMPAT] ZDS indicates it should map to datumVernietigingDossier
        'zsdms:datumVernietigDossier': 'archiefactiedatum',  # o
    }

    class Meta:
        unique_together = ('zaakidentificatie', 'bronorganisatie')
        verbose_name_plural = 'Zaken'
        mnemonic = 'ZAK'

    def get_cmis_properties(self):
        props = super().get_cmis_properties()

        initiator_rol = self.rol_set.filter(rolomschrijving=Rolomschrijving.initiator).first()  # can be maximum one
        if initiator_rol:
            initiator = initiator_rol.betrokkene.is_type()
            props.update(initiator.get_cmis_properties())

        return props

    def get_current_status(self):
        return self.status_set.get(indicatie_laatst_gezette_status=JaNee.ja)

    def save(self, *args, **kwargs):
        self.clean_fields()
        return super().save(*args, **kwargs)

    def kent(self):
        """
        De relatie tussen een ZAAK en een of meerdere INFORMATIEOBJECT(en) dat
        relevant is voor de behandeling van die ZAAK en/of gecreëerd is in
        het kader van de behandeling van die ZAAK
        :return:
        """
        return self.informatieobjecten.all()

    def heeft(self):
        return self.status_set.all()

    def is_van(self):
        return self.zaaktype

    def heeft_gerelateerde(self):
        """
        :return: De andere ZAAKen die relevant zijn voor de ZAAK.
        """
        return self.gerelateerd_met, {}

    def is_deelzaak_van(self):
        """
        De verwijzing naar de ZAAK, waarom verzocht is door de initiator
        daarvan, die behandeld wordt in twee of meer separate ZAAKen
        waarvan de onderhavige ZAAK er één is.
        :return:
        """
        return self.hoofdzaak

    def groep_kenmerken(self):
        return self.zaakkenmerk_set, {}

    def groep_anderzaakobject(self):
        return self.anderzaakobject_set, {}

    def groep_zaakopschorting(self):
        return self.zaakopschorting_set, {}

    def groep_zaakverlenging(self):
        return self.zaakverlenging_set, {}

    def heeft_deelzaken(self):
        return self.deelzaken, {}

    def eigenschappen(self):
        """
        Lijkt vreemd, maar zo staat het in de documentatie
        Alle eigenschappen relevant aan de Zaak
        :return:
        """
        return self.eigenschap.all()

    def heeft_als_betrokkene(self):
        return self.rol_set, {}

    """
    All relations with 'Rol'
    """

    def heeft_als_adviseur(self):
        return self.rol_set, self.rol_set.model.get_rol_defaults(Rolomschrijving.adviseur)

    def heeft_als_belanghebbende(self):
        return self.rol_set, self.rol_set.model.get_rol_defaults(Rolomschrijving.belanghebbende)

    def heeft_als_behandelaar(self):
        return self.rol_set, self.rol_set.model.get_rol_defaults(Rolomschrijving.behandelaar)

    def heeft_als_beslisser(self):
        return self.rol_set, self.rol_set.model.get_rol_defaults(Rolomschrijving.beslisser)

    def heeft_als_initiator(self):
        return self.rol_set, self.rol_set.model.get_rol_defaults(Rolomschrijving.initiator)

    def heeft_als_klantcontacter(self):
        return self.rol_set, self.rol_set.model.get_rol_defaults(Rolomschrijving.klantcontacter)

    # TODO: [TECH] Mede-initiator

    def heeft_als_zaakcoordinator(self):
        return self.rol_set, self.rol_set.model.get_rol_defaults(Rolomschrijving.zaakcoordinator)

    def heeft_als_gemachtigde(self):
        return self.rol_set, {'indicatie_machtiging': IndicatieMachtiging.gemachtigde}

    def leidt_tot(self):
        return self.besluit_set, {'zaak': self}


class Eigenschap(models.Model):
    zaak = models.ForeignKey('rgbz.Zaak', on_delete=models.CASCADE, related_name='eigenschap')
    data = models.TextField()
    # TODO: [KING] Dit aanpassen als er duidelijkheid is over wat er mee moet gebeuren

    class Meta:
        verbose_name_plural = 'Eigenschappen'


class Status(Object):
    """
    Een aanduiding van de stand van zaken van een ZAAK op basis van
    betekenisvol behaald resultaat voor de initiator van de ZAAK.
    """
    # Op één dag kan een zaak meerdere statussen doorlopen. Om te kunnen bepalen wat de laatst gezette status is of in
    # welke volgorde de statussen bereikt zijn, wordt de datum tot op de minuut vastgelegd.
    # Tijdstip
    datum_status_gezet = StUFDateTimeField(
        help_text='De datum waarop de ZAAK de status heeft verkregen.'
    )
    statustoelichting = models.TextField(
        max_length=1000, null=True, blank=True, help_text='Een, voor de initiator van de zaak relevante, toelichting '
        'op de status van een zaak.')
    # Het gegeven is afleidbaar uit de historie van de attribuutsoort Datum status gezet van van alle statussen
    # bij de desbetreffende zaak.
    indicatie_laatst_gezette_status = models.CharField(max_length=1, choices=JaNee.choices,
                                                       default=JaNee.nee, help_text='Aanduiding of het de laatst bekende bereikte status betreft.')

    # relaties
    status_type = models.ForeignKey('rgbz.StatusType')

    # De zaak waar de status over gaat, een zaak kan in 1 dag meerdere statusen hebben
    zaak = models.ForeignKey('rgbz.Zaak', on_delete=models.CASCADE)
    rol = models.ForeignKey('rgbz.Rol')

    class Meta:
        unique_together = ('zaak', 'datum_status_gezet')
        verbose_name_plural = 'Statussen'
        mnemonic = 'STA'

    def is_gezet_door(self):
        assert self.rol.zaak == self.zaak
        return self.rol.betrokkene

    def heeft_relevant(self):
        # TODO: [KING] This filtering is an assumption, it isn't described anywhere as far as I know.
        return self.zaak.informatieobjecten.filter(informatieobject_status=self), {}

    def is_van(self):
        return self.status_type

    def create_identificatie(self):
        # Unieke aanduiding van de gerelateerde ZAAK in combinatie met de Datum
        # status gezet.
        return '{}{}'.format(self.zaak.zaakidentificatie, self.datum_status_gezet)


class ZaakInformatieObject(models.Model):
    zaak = models.ForeignKey('rgbz.Zaak', on_delete=models.CASCADE)
    informatieobject = models.ForeignKey('rgbz.InformatieObject', on_delete=models.CASCADE)

    titel = models.CharField(
        max_length=200, help_text='De naam waaronder het INFORMATIEOBJECT binnen de ZAAK bekend is.')
    beschrijving = models.TextField(
        max_length=1000, null=True,
        blank=True, help_text='Een op de zaak gerichte beschrijving van de '
                              'inhoud van het INFORMATIEOBJECT.')
    registratiedatum = StUFDateField(
        'De datum waarop de zaakbehandelende organisatie het INFORMATIEOBJECT heeft geregistreerd bij de ZAAK.')
    status = models.ForeignKey('rgbz.Status', on_delete=models.CASCADE)

    def is_relevant_voor(self):
        return self.status

    def save(self, *args, **kwargs):
        if not self.id and self.zaak:
            self.status = self.zaak.get_current_status()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'ZaakInformatieObjecten'
        mnemonic = 'ZDC'


class ZaakObject(models.Model):
    zaak = models.ForeignKey('rgbz.Zaak')
    object = models.ForeignKey('rgbz.Object')
    relatieomschrijving = models.CharField(
        max_length=80, null=True, blank=True, help_text='Omschrijving van de betrekking tussen deZAAK en het OBJECT')

    class Meta:
        mnemonic = 'ZOB'


class ZakenRelatie(models.Model):
    """
    De relevantie van de andere ZAAK voor de ZAAK.
    """
    aard_relatie = models.CharField(
        max_length=10, choices=AardRelatieZakenRelatie.choices)
    onderhanden_zaak = models.ForeignKey('rgbz.Zaak', help_text='Zaak waar de zaak relevant voor is',
                                         on_delete=models.CASCADE)
    andere_zaak = models.ForeignKey(
        'rgbz.Zaak', on_delete=models.CASCADE, related_name='andere_zaak')
