from django.core.validators import MaxValueValidator
from django.db import models

from zaakmagazijn.utils.fields import GMLField, StUFDateField

from ..choices import (
    AardRelatieGerelateerdeExterneZaak, JaNee, OmschrijvingVoorwaarden
)
from ..validators import (
    validate_continuous_numbers, validate_non_negative_string,
    validate_physical_file_name
)


class GebruiksRechten(models.Model):
    """
    Datamodel afwijking, model representatie van de Groepattribuutsoort 'GebruiksRechten'
    """
    einddatum_gebruiksrechten = StUFDateField(
        null=True, blank=True, help_text='Einddatum van de periode waarin de gebruiksrechtvoorwaarden '
        'van toepassing zijn')
    omschrijving_voorwaarden = models.CharField(
        max_length=30, choices=OmschrijvingVoorwaarden.choices, default=OmschrijvingVoorwaarden.geen_gebruiksrechten,
        help_text='Omschrijving van de van toepassing zijndevoorwaarden aan het gebruik anders dan raadpleging')
    startdatum_gebruiksrechten = StUFDateField(
        help_text='Begindatum van de periode waarin de gebruiksrechtvoorwaarden van toepassing zijn')


class Ondertekening(models.Model):
    """
    Datamodel afwijking, model representatie van de Groepattribuutsoort 'Ondertekening'
    """
    ondertekeningsoort = models.CharField(max_length=10,
                                          help_text='Aanduiding van de wijze van ondertekening van het INFORMATIEOBJECT')
    ondertekeningdatum = StUFDateField(help_text='De datum waarop de ondertekening van het INFORMATIEOBJECT heeft '
                                                 'plaatsgevonden')


class Bestandsnaam(models.Model):
    """
    Datamodel afwijking, model representatie van de Groepattribuutsoort 'Bestandsnaam'
    """
    naam = models.CharField(max_length=255, help_text='De naam van het fysieke bestand zonder aanduiding van het '
                                                      'formaat in een extensie.',
                            validators=[validate_physical_file_name, ])
    extensie = models.CharField(max_length=5, null=True, blank=True, help_text='Aanduiding van het format van het bestand.')


class Integriteit(models.Model):
    """
    Informatiemodel afwijking, model representatie van de Groepattribuutsoort 'Integriteit'
    """
    algoritme = models.TextField(
        max_length=1000,
        help_text='Aanduiding van algoritme, gebruikt om de checksum te maken.')
    waarde = models.TextField(
        max_length=1000,
        help_text='De waarde van de checksum.',
        validators=[validate_continuous_numbers, ])
    datum = StUFDateField(help_text='Datum waarop de checksum is gemaakt.')


class ZaakKenmerk(models.Model):
    """
    Datamodel afwijking, odel representatie van de Groepattribuutsoort 'Kenmerk'

    """
    zaak = models.ForeignKey('rgbz.Zaak')
    kenmerk = models.CharField(
        max_length=40, help_text='Identificeert uniek de zaak in een andere administratie.')
    kenmerk_bron = models.CharField(
        max_length=40, help_text='De aanduiding van de administratie waar het kenmerk op slaat.')

    class Meta:
        verbose_name_plural = 'Zaak kenmerken'


class ZaakOpschorting(models.Model):
    """
    Gegevens omtrent het tijdelijk opschorten van de behandeling van de ZAAK
    Datamodel afwijking, model representatie van de Groepattribuutsoort 'Opschorting'
    """

    zaak = models.ForeignKey('rgbz.Zaak')
    # TODO [KING]: De keuzes voor attribuut "indicatie opschorting" op ZaakOpschorting staan nergens gespecificeerd.
    indicatie_opschorting = models.CharField(max_length=1, choices=JaNee.choices,
                                             help_text='Aanduiding of de behandeling van de ZAAK tijdelijk is opgeschort.')
    reden_opschorting = models.CharField(
        null=True, blank=True, max_length=200,
        help_text='Omschrijving van de reden voor het opschorten van de behandeling van de zaak.')

    class Meta:
        verbose_name_plural = 'Zaak opschortingen'


class ZaakVerlenging(models.Model):
    """
    Datamodel afwijking, model representatie van de Groepattribuutsoort 'Verlenging'

    Gegevens omtrent het verlengen van de doorlooptijd van de
    behandeling van de ZAAK
    """
    zaak = models.ForeignKey('rgbz.Zaak')
    reden_verlenging = models.CharField(
        max_length=200, help_text='Omschrijving van de reden voor het verlengen van de behandeling van de zaak.')
    duur_verlenging = models.SmallIntegerField(
        help_text='Het aantal werkbare dagen waarmee de doorlooptijd van de behandeling van de ZAAK is verlengd '
                  '(of verkort) ten opzichte van de eerder gecommuniceerde doorlooptijd.',
        validators=[MaxValueValidator(999)])

    class Meta:
        verbose_name_plural = 'Zaak verlengingen'


class AnderZaakObject(models.Model):
    """
    Datamodel afwijking, model representatie van de Groepattribuutsoort 'Ander zaakobject'

    Aanduiding van het object (of de objecten) waarop de ZAAK betrekking heeft indien dat object (of die objecten) niet
    aangeduid kan worden met de relatie ‘ZAAK heeft betrekking op OBJECT’.
    """
    zaak = models.ForeignKey('rgbz.Zaak')
    ander_zaakobject_aanduiding = models.CharField(max_length=80, help_text='Een identificerende beschrijving')
    ander_zaakobject_omschrijving = models.CharField(
        max_length=80, help_text='Een korte omschrijving over de aard van het andere zaak object')
    ander_zaakobject_lokatie = GMLField(
        null=True, blank=True, help_text='De minimaal tweedimensionale geometrische representatie'
                                         ' van de ligging of de omtrek van het ANDER ZAAKOBJECT.'
    )
    ander_zaakobject_registratie = models.CharField(
        help_text='De naam van de registratie waarin gegevens van het ANDER ZAAKOBJECT worden beheerd.',
        null=True, blank=True, max_length=50)

    class Meta:
        verbose_name_plural = 'Andere zaak objecten'


class GerelateerdeExterneZaak(models.Model):
    """
    Datamodel afwijking, model representatie van de Groepattribuutsoort 'Gerelateerde externe zaak'

    Een ZAAK bij een andere organisatie waarin een bijdrage
    geleverd wordt aan het bereiken van de uitkomst van de
    onderhanden ZAAK.
    """

    zaak = models.ForeignKey('rgbz.Zaak')
    aanvraagdatum = StUFDateField(
        help_text='De datum waarop verzocht is om de behandeling van de gerelateerde ZAAK uit te gaan voeren.')
    aard_relatie = models.CharField(
        max_length=15, choices=AardRelatieGerelateerdeExterneZaak.choices,
        help_text='Aanduiding van de rol van de gerelateerde zaak ten aanzien van de onderhanden ZAAK')
    datum_status_gezet = StUFDateField(
        help_text='De datum waarop de gerelateerde ZAAK de laatst bekende status heeft verkregen.')
    einddatum = StUFDateField(
        null=True, blank=True, help_text='De datum waarop de uitvoering van de gerelateerde ZAAK afgerond is.')
    startdatum = StUFDateField(
        null=True, blank=True, help_text='De datum waarop met de uitvoering van de gerelateerde ZAAK is gestart')
    # Waarden verzameling: Het betreft één van de resultaatomschrijvingen zoals gespecificeerd bij het door beide
    # organisaties overeengekomen zaaktype in de van toepassing zijnde ZaakTypeCatalogus.
    resultaatomschrijving = models.CharField(
        max_length=80, null=True, blank=True,
        help_text='Een korte omschrijving wat het resultaat van de gerelateerde ZAAK inhoudt.')

    # Waarden verzameling: Ontlenen aan het tussen beide organisaties afgesproken zaaktype
    # in de van toepassing zijn ZaakTypeCatalogus.
    statusomschrijving_generiek = models.CharField(
        max_length=80, null=True, blank=True,
        help_text='Algemeen gehanteerde omschrijving van de aard van de laatst bekende status van de gerelateerde ZAAK.')
    verantwoordelijke_organisatie = models.CharField(max_length=9, validators=[validate_non_negative_string, ],
                                                     help_text='Het RSIN van de organisatie die verantwoordelijk is voor de behandeling van de gerelateerde ZAAK.'
                                                     )
    zaakidentificatie = models.CharField(
        max_length=40, null=True, blank=True, help_text='De unieke identificatie van de gerelateerde ZAAK.')  # unique constraint allows multiple null values, but not blank?
    zaaktypeomschrijving_generiek = models.CharField(
        max_length=80, help_text='Algemeen gehanteerde omschrijving van de aard van '
                                 'ZAAKen van het ZAAKTYPE waartoe de gerelateerde zaak behoort.')
    # Waarden verzameling: en waarde voor dit attribuutsoort in de van toepassing zijn ZaakTypeCatalogus.
    zaaktypecode = models.SmallIntegerField(
        help_text='De algemeen gehanteerde code van de aard van ZAAKen '
                  'van het ZAAKTYPE waartoe de gerelateerde zaak behoort')

    class Meta:
        verbose_name_plural = 'Gerelateerde externe zaken'


class Contactpersoon(models.Model):
    contactpersoonnaam = models.CharField(max_length=40)
    contactpersoon_functie = models.CharField(max_length=50, null=True, blank=True)
    contactpersoon_telefoonnummer = models.CharField(max_length=20, null=True, blank=True)
    contactpersoon_emailadres = models.EmailField(null=True, blank=True)


class Rekeningnummer(models.Model):
    """
    De gegevens inzake de bankrekening waarmee het SUBJECT in de regel financieel communiceert.
    """
    iban = models.CharField(
        max_length=34, help_text='Het internationaal bankrekeningnummer, zoals dat door een bankinstelling als '
                                 'identificator aan een overeenkomst tussen de bank en een of meer subjecten wordt'
                                 ' toegekend, op basis waarvan het SUBJECT in de regel internationaal financieel'
                                 ' communiceert.'
    )
    bic = models.CharField(
        max_length=11, help_text='De unieke code van de bankinstelling waar het SUBJECT het bankrekeningnummer heeft '
                                 'waarmee het subject in de regel internationaal financieel communiceert'
    )
