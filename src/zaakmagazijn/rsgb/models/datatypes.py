# Alle 'complexe datatypes', zoals gedefineerd in RSGB, zijn hier overgenomen
# compositeID
from django.core.validators import MaxValueValidator, RegexValidator
from django.db import models

from zaakmagazijn.rgbz.choices import JaNee
from zaakmagazijn.utils import stuf_datetime
from zaakmagazijn.utils.fields import StUFDateField

from ..choices import TypeObjectCode


def validate_most_text_cases(value='([A-Za-z0-9_\-,\.])+'):
    return RegexValidator(regex=value)


class ComplexDataTypeMixin(models.Model):
    namespace = models.TextField(validators=[validate_most_text_cases])  # Maximale lengte niet bekend
    lokaal_id = models.TextField(validators=[validate_most_text_cases])
    versie = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True


class TypeLabelpositie(models.Model):
    pass


class TypeLabel(models.Model):
    labelTekst = models.TextField()
    labelPositie = models.ForeignKey('rsgb.TypeLabelpositie')


class CompositeID(ComplexDataTypeMixin):
    """
    Wordt gebruikt als complex DataType voor RSGB klasse velden, of RGBZ klasse welke velden van RSGB klasses overnemen.
    Zie RSGB 3.0 deel 2, hoofdstuk 2.5.2 voor meer informatie
    """
    # pattern:([A-Za-z0-9_\-,\.])+
    namespace = models.TextField(validators=[validate_most_text_cases])  # Maximale lengte niet bekend
    lokaal_id = models.TextField(validators=[validate_most_text_cases])
    versie = models.TextField(null=True, blank=True)


class NEN360ID(ComplexDataTypeMixin):
    """
    Wordt gebruikt als complex DataType voor RSGB klasse vleden, of RGBZ klasse welke velden van RSGB klasses overnemen.
    """
    pass


class AkrKadastraleGemeentecode(models.Model):
    code_akr_kadastrale_gemeentecode = models.CharField(
        max_length=5, help_text='Een volgens de Dienst van het Kadaster unieke code behorende bij de '
                                'ARK code kadastrale gemeente.')
    akr_code = models.TextField(
        help_text='De AKR code van kadastrale gemeente volgens de Dienst van het Kadaster.')
    begindatum_geldigheid_akr_code = StUFDateField(
        help_text='De datum waarop de AKR code kadastrale gemeente is ontstaan.')
    einddatum_geldigheid_akr_code = StUFDateField(
        blank=True, help_text='De datum waarop de AKR code kadastrale gemeente is opgeheven.')


class BAGObjectnummering(models.Model):
    gemeentecode = models.CharField(max_length=4)
    objecttypecode = models.CharField(choices=TypeObjectCode.choices, max_length=40)
    objectvolgnummer = models.CharField(max_length=10, validators=[RegexValidator(r'^\d{1,10}$')])
    # natuurlijk getal met verloop nullen


class TypeKadastraleAanduiding(models.Model):
    kadastrale_gemeentecode = models.ForeignKey('rsgb.AkrKadastraleGemeentecode', on_delete=models.CASCADE)
    perceelnummer = models.PositiveSmallIntegerField()
    sectie = models.CharField(max_length=2)
    appartementsrechtvolgnummer = models.PositiveSmallIntegerField(validators=[MaxValueValidator(9999)])


class AcademischeTitel(models.Model):
    academische_titelcode = models.CharField(
        max_length=3, validators=[RegexValidator('([A-Z,a-z])\w+')],
        help_text='Een code die aangeeft welke academische titel behoort tot de naam.')
    omschrijving_academische_titel = models.CharField(
        max_length=80, help_text='De omschrijving behorende bij NEN-tabel Academische titelcode.')
    # TODO [KING]: De keuzes van attribuut "positie_academische_titel_tov_naam" van AcademischeTitel staan niet in het RGBZ
    positie_academische_titel_tov_naam = models.CharField(
        max_length=1, choices=JaNee.choices,
        help_text='Aanduiding of de academische titel voorafgaand '
                  'aan de voornamen of achter de geslachtsnaam wordt geplaatst.')
    datum_begin_geldigheid_titel = StUFDateField(
        default=stuf_datetime.today,
        help_text='De datum waarop de ACADEMISCHE TITEL is ontstaan.')
    datum_einde_geldigheid_titel = StUFDateField(
        help_text='De datum waarop de ACADEMISCHE TITEL is opgeheven.', blank=True)


class Deelobjectcode(models.Model):
    deelobjectcode = models.CharField(max_length=4)
    naam_deelobjectcode = models.TextField()
    begindatum_geldigheid_deelobjectcode = StUFDateField()
    einddatum_geldigheid_deelobjectcode = StUFDateField(blank=True)


class SoortWOZObject(models.Model):
    soort_objectcode = models.CharField(max_length=4)
    naam_soort_objectocde = models.TextField()
    opmerking_soort_objectcode = models.TextField()
    begindatum_geldigheid_soort_objectcode = StUFDateField()
    einddatum_geldigheid_soort_objectcode = StUFDateField(blank=True)


class AardZakelijkRecht(models.Model):
    code_aard_zakelijk_recht = models.PositiveSmallIntegerField(validators=[MaxValueValidator(99)])
    naam_aard_zakelijk_recht = models.TextField()
    begindatum_geldigheid_aard_zakelijk_recht = StUFDateField()
    einddatum_geldigheid_aard_zakelijk_recht = StUFDateField(blank=True)


class LandGebied(models.Model):
    landcode = models.CharField(
        max_length=4,
        help_text='De code, behorende bij de landnaam, zoals opgenomen in de Land/Gebied-tabel van de BRP.'
    )
    landnaam = models.CharField(
        max_length=40, help_text='De naam van het land, zoals opgenomen in de Land/Gebied-tabel van de BRP.'
    )
    ingangsdatum_land = StUFDateField(
    )
    einddatum_land = StUFDateField(blank=True)
    landcode_iso = models.CharField(
        max_length=2, null=True, blank=True
    )
