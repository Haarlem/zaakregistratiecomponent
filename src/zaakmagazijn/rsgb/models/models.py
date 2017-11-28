from django.core.validators import MaxValueValidator
from django.db import models

from zaakmagazijn.utils import stuf_datetime

from ...rgbz.choices import JaNee
from ...utils.fields import StUFDateField
from ..choices import (
    StatusOpenbareRuimte, StatusWoonplaats, TyperingOpenbareRuimte
)


class OpenbareRuimte(models.Model):
    """
    Een door het bevoegde gemeentelijke orgaan als zodanig aangewezen
    en van een naam voorziene buitenruimte die binnen één woonplaats
    is gelegen
    """
    # FIXME Velden die overeenkomen met GemeentelijkeOpenbareRuimte in een mixin?

    identiefcatiecode_openbare_ruimte = models.ForeignKey('rsgb.BAGObjectnummering', on_delete=models.CASCADE)
    # dit is een NEN360ID
    # identiefcatie_imgeoopr = models.CharField(
    #    max_length=25, help_text='ruimte zoals is toegekend in de IMGeo administratie')
    identiefcatie_imgeoopr = models.ForeignKey(
        'rsgb.NEN360ID', help_text='ruimte zoals is toegekend in de IMGeo administratie')

    status_openbare_ruimte = models.CharField(
        max_length=25, choices=StatusOpenbareRuimte.choices
    )
    naam_openbare_ruimte = models.CharField(
        max_length=80, help_text='Een door het bevoegde gemeentelijke orgaan aan een '
                                 'OPENBARE RUIMTE toegekende benaming')
    indicatie_geconstateerde_openbare_ruimte = models.CharField(max_length=1, choices=JaNee.choices)
    type_openbare_ruimte = models.CharField(
        max_length=36, choices=TyperingOpenbareRuimte.choices,
        help_text=''
    )
    straatnaam = models.CharField(
        max_length=24, help_text='De officiële straatnaam zoals door het bevoegd gemeentelijk orgaan is vastgesteld, '
                                 'zo nodig ingekort conform de specificaties van de NEN 5825.'
    )
    huisnummerrange_even_nummers = models.BigIntegerField(validators=[MaxValueValidator(99999999999)])
    huisnummerrange_oneven_nummers = models.BigIntegerField(validators=[MaxValueValidator(99999999999)])
    huisnummerrange_even_en_oneven_nummers = models.BigIntegerField(validators=[MaxValueValidator(99999999999)])
    label_naam_openbare_ruimte = models.ForeignKey('rsgb.TypeLabel')
    # openbare_ruimte_geometrie #gm_multisurface geonovum
    # wegsegment #gm_curve, geonovum
    datum_begin_geldigheid_openbare_ruimte = StUFDateField(default=stuf_datetime.today)
    datum_einde_geldigheid_openbare_ruimte = StUFDateField(null=True, blank=True)

    class Meta:
        mnemonic = 'OPR'


class WoonPlaats(models.Model):
    """
       model aanpassing, opgenomen om woonplaats informatie relevant voor de applicatie op te slaan
       Een door het bevoegde gemeentelijke orgaan als zodanig aangewezen
       en van een naam voorzien gedeelte van het grondgebied van de
       gemeente.
       """
    woonplaatsidentificatie = models.CharField(max_length=4)  # check
    woonplaatsnaam = models.CharField(max_length=80)  # check
    woonplaatsnaam_nen = models.CharField(max_length=24, null=True, blank=True)
    indicatie_geconstanteerde_woonplaats = models.CharField(max_length=1, choices=JaNee.choices)
    woonplaatsstatus = models.CharField(max_length=100, choices=StatusWoonplaats.choices)
    # woonplaatsgeometrie =
    datum_begin_geldigheid_woonplaats = StUFDateField(default=stuf_datetime.today)  # niet nodig?
    datum_einde_geldigheid_woonplaats = StUFDateField(null=True, blank=True)  # niet nodig?

    class Meta:
        mnemonic = 'WPL'


class AdresseerbaarObjectAanduiding(models.Model):
    """
    Een NUMMERAANDUIDING of een OVERIG ADRESSEERBAAR OBJECT AANDUIDING.
    """
    huisletter = models.CharField(max_length=1, null=True, blank=True)
    huisnummer = models.CharField(max_length=5)
    huisnummertoevoeging = models.CharField(max_length=4)
    postcode = models.CharField(max_length=7, null=True, blank=True)
    datum_begin_geldigheid_adresseerbaar_object_aanduiding = StUFDateField(default=stuf_datetime.today)
    datum_einde_geldigheid_adresseerbaar_object_aanduiging = StUFDateField(null=True, blank=True)
    woonplaats = models.ForeignKey('rsgb.WoonPlaats')
    openbareruimte = models.ForeignKey('rsgb.OpenbareRuimte')

    class Meta:
        mnemonic = 'AOA'
