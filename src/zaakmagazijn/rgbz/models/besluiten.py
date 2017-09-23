from django.core.validators import MaxValueValidator
from django.db import models

from ...utils.fields import StUFDateField
from ..choices import JaNee, VervalRedenen
from .basemodels import Object
from .mixins import TijdstipRegistratieMixin


class BesluitType(models.Model):
    """
    De aan de ZTC ontleende gegevens van een BESLUITTYPE zoals die in het RGBZ gebruikt
    worden. Zie voor de specificaties van deze gegevens het ZTC.
    """
    besluittypeomschrijving = models.CharField(
        max_length=80, null=True, blank=True, help_text='Omschrijving van de aard van BESLUITen van het BESLUITTYPE.')
    domein = models.CharField(
        max_length=5, help_text='Een afkorting waarmee wordt aangegeven voor welk domein in de CATALOGUS'
                                ' ZAAKTYPEn zijn uitgewerkt.')
    # Niet gespecificeerd in ZTC 2.0, wel in RGBZ 2.0.
    rsin = models.PositiveIntegerField(
        help_text='Het door een kamer toegekend uniek nummer voor de INGESCHREVEN NIET-NATUURLIJK PERSOON'
    )
    besluittypeomschrijving_generiek = models.CharField(
        max_length=80, null=True, blank=True, help_text='Algemeen gehanteerde omschrijving van de aard van '
        'BESLUITen van het BESLUITTYPE')
    besluitcategorie = models.CharField(
        max_length=40, null=True, blank=True, help_text='Typering van de aard van BESLUITen van het BESLUITTYPE.'
    )
    reactietermijn = models.PositiveSmallIntegerField(
        help_text='Het aantal dagen, gerekend vanaf de verzend- of publicatiedatum, '
                  'waarbinnen verweer tegen een besluit van het besluittype mogelijk is.',
        validators=[MaxValueValidator(999)]
    )
    publicatie_indicatie = models.CharField(max_length=1, choices=JaNee.choices,
                                            help_text='Aanduiding of BESLUITen van dit BESLUITTYPE gepubliceerd moeten worden.'
                                            )
    publicatietekst = models.TextField(null=True, blank=True,
                                       max_length=1000, help_text='De generieke tekst van de publicatie van BESLUITen van dit BESLUITTYPE')
    publicatietermijn = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text='Het aantal dagen, gerekend vanaf de verzend- of publicatiedatum, dat BESLUITen van dit '
                  'BESLUITTYPE gepubliceerd moeten blijven.',
        validators=[MaxValueValidator(999)]
    )
    datum_begin_geldigheid_besluittype = StUFDateField()
    datum_einde_geldigheid_besluittype = StUFDateField(null=True, blank=True)

    class Meta:
        mnemonic = 'BST'


# TODO: [TECH] This can be replaced by using the 'self' relation name in StUFEntiteiten.
class BesluitInformatieObject(models.Model):
    """ Added as alternative to ZaakInformatieObject, empty m2m-through tabel """
    besluit = models.ForeignKey('rgbz.Besluit', on_delete=models.CASCADE)
    informatieobject = models.ForeignKey('rgbz.InformatieObject', on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'BesluitInformatieObjecten'
        mnemonic = 'BDC'  # TODO: This is wrong, there is no such mnmemonic in RGBZ 2.0.


class Besluit(TijdstipRegistratieMixin, Object):
    besluitdatum = StUFDateField(
        help_text='De beslisdatum (AWB) van het besluit'
    )
    besluittoelichting = models.TextField(
        help_text='Toelichting bij het besluit.',
        max_length=1000, null=True, blank=True)
    bestuursorgaan = models.CharField(
        help_text='Een orgaan van een rechtspersoon krachtens publiekrecht ingesteld of een persoon of college, '
                  'met enig openbaar gezag bekleed onder wiens verantwoordelijkheid het besluit vastgesteld is.',
        max_length=50, null=True, blank=True)
    ingangsdatum = StUFDateField(
        help_text='Ingangsdatum van de werkingsperiode van het besluit.')
    vervaldatum = StUFDateField(
        null=True, blank=True,
        help_text='Datum waarop de werkingsperiode van het besluit eindigt.')
    vervalreden = models.CharField(
        max_length=40, null=True, blank=True, choices=VervalRedenen.choices,
        help_text='De omschrijving die aangeeft op grond waarvan het besluit is of komt te vervallen.')
    publicatiedatum = StUFDateField(
        null=True, blank=True,
        help_text='Datum waarop het besluit gepubliceerd wordt.')
    verzenddatum = StUFDateField(
        null=True, blank=True,
        help_text='Datum waarop het besluit verzonden is')
    uiterlijke_reactiedatum = StUFDateField(
        null=True, blank=True,
        help_text='De datum tot wanneer verweer tegen het besluit mogelijk is.')
    besluittype = models.ForeignKey('rgbz.BesluitType', on_delete=models.CASCADE)
    zaak = models.ForeignKey(
        'rgbz.Zaak', help_text='Aanduiding van de ZAAK waarbinnen het BESLUIT genomen is.')
    informatieobject = models.ManyToManyField('rgbz.InformatieObject', blank=True, through='rgbz.BesluitInformatieObject')

    @property
    def besluitidentificatie(self):
        # from ..validators import AlphanumericExcludingDiacritic
        # besluitidentificatie = models.CharField(
        # help_text='Identificatie van het besluit.',
        # max_length=50, validators=[AlphanumericExcludingDiacritic(start=5)])
        return self.identificatie

    def is_uitkomst_van(self):
        return self.zaak

    def is_van(self):
        return self.besluittype

    def kan_vastgelegd_zijn_als(self):
        return self.informatieobject.all()

    def is_vastgelegd_in(self):
        return self.besluitinformatieobject_set, {}

    class Meta:
        verbose_name_plural = 'Besluiten'
        mnemonic = 'BSL'
