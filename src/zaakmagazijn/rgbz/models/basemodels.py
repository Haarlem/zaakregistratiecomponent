from django.db import models

from zaakmagazijn.utils import stuf_datetime
from zaakmagazijn.utils.fields import GMLField, StUFDateField

from .mixins import BSNMixin, GeslachtsAanduidingMixin, TypeMixin


class OrganisatorischeEenheidBaseClass(models.Model):
    """
    Minimaal aanwezige velden voor een Organisatorisch Eenheid Object
    """
    organisatieidentificatie = models.PositiveIntegerField(
        db_index=True,
        help_text='Het RSIN van de organisatie zijnde een Niet-natuurlijk '
                  'persoon waarvan de ORGANISATORISCHE EENHEID deel uit maakt.'
    )
    datum_ontstaan = StUFDateField(
        default=stuf_datetime.today,
        help_text='De datum waarop de organisatorische eenheid is ontstaan.')
    datum_opheffing = StUFDateField(
        null=True, blank=True, help_text='De datum waarop de organisatorische eenheid is opgeheven.')

    naam = models.CharField(
        max_length=50, help_text='De feitelijke naam van de organisatorische eenheid.'
    )

    class Meta:
        abstract = True


class NietNatuurlijkPersoonBaseClass(models.Model):
    """
    Basis klasse voor alle 'NietNatuurlijkPersoon' klasse die leven binnen de applicatie.
    """
    rsin = models.CharField(
        help_text='Het door een kamer toegekend uniek nummer voor de INGESCHREVEN NIET-NATUURLIJK PERSOON',
        max_length=17,  # BsVesNummerOfId
    )
    statutaire_naam = models.TextField(
        max_length=500, null=True, blank=True,
        help_text='Naam van de niet-natuurlijke persoon zoals deze is vastgelegd in de statuten (rechtspersoon) of '
                  'in de vennootschapsovereenkomst is overeengekomen (Vennootschap onder firma of Commanditaire '
                  'vennootschap).')
    datum_aanvang = StUFDateField(
        default=stuf_datetime.today,
        help_text='De datum van aanvang van de NIET-NATUURLIJK PERSOON'
    )
    datum_beeindiging = StUFDateField(
        null=True, blank=True, help_text='De datum van beëindiging van de NIET-NATUURLIJK PERSOON.'
    )
    verblijf_buitenland = models.ForeignKey('rsgb.VerblijfBuitenland', null=True, blank=True,
                                            help_text='De gegevens over het verblijf in het buitenland')

    class Meta:
        abstract = True


class ObjectMixin(models.Model):
    naam = models.TextField(
        max_length=500, null=True, blank=True,
        help_text='De benaming van het OBJECT indien dit een SUBJECT of specialisatie daarvan is.')
    # TODO [KING]: Volgens Michiel Verhoef kan RGBZ 2.0 niet 1 op 1 mappen op de velden in de Berichten van Zaak-
    # en Documentservices 1.2. De volgende 2 velden staan wel in het UML schema, maar niet in de specificatie:
    # adres_binnenland = models.ForeignKey(adres, null=True, blank=True)
    # adres_buitenland = models.ForeignKey(adres, null=True, blank=True)
    adres = models.ForeignKey('rsgb.Adres', null=True, blank=True)
    kadastrale_aanduiding = models.ForeignKey(
        'rsgb.KadastraleAanduiding', help_text='De kadastrale aanduiding van het OBJECT',
        null=True, blank=True)
    geometrie = GMLField(
        null=True, blank=True, help_text='De minimaal tweedimensionale geometrische representatie van het OBJECT.'
    )

    class Meta:
        abstract = True


class Object(TypeMixin, models.Model):
    identificatie = models.CharField(
        db_index=True,
        max_length=100, help_text='De unieke identificatie van het OBJECT')
    object_zaken = models.ManyToManyField('rgbz.Zaak', related_name='gerelateerde_aan',
                                          through='rgbz.ZaakObject')

    _objecttype_model = models.CharField(max_length=50, null=True, blank=True)
    objecttype = models.CharField(max_length=3, default='???')

    class Meta:
        unique_together = ('identificatie', 'objecttype')  # what about objecttypes that stay blank/'???' ?
        abstract = False
        mnemonic = ''

    def __str__(self):
        return '{}'.format(self.identificatie)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Automatically fill in the 'identificatie' field for any model that inherits from
        # Object. If a method called 'create_identificatie' exists it is called and used
        # to create a 'identificatie' string which is then stored.
        if hasattr(self, 'create_identificatie'):
            self.identificatie = self.create_identificatie()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._save_child_model('Object', '_objecttype_model')
        self._save_type('Object', 'objecttype')

    def is_type(self):
        return self._determine_type('Object', '_objecttype_model')

    def betreft(self):
        return self.object_zaken.first()


class IngezeteneBaseClass(GeslachtsAanduidingMixin, BSNMixin, Object):
    """
    Basis klasse voor alle 'Ingezetenen' klasse die leven binnen de applicatie.
    """
    verblijfadres = models.ForeignKey(
        'rsgb.VerblijfAdres', on_delete=models.SET_NULL, null=True, blank=True,
        help_text='De gegevens over het verblijf en adres van de INGESCHREVEN NATUURLIJK PERSOON',
        related_name='%(class)s_verblijfadres'
    )
    geboortedatum = StUFDateField(
        help_text='De datum waarop de ander natuurlijk persoon is geboren.', null=True, blank=True
    )
    overlijdensdatum = StUFDateField(
        help_text='De datum van overlijden van een ANDER NATUURLIJK PERSOON', null=True, blank=True
    )
    naamaanschrijving = models.ForeignKey(
        'rsgb.NaamAanschrijving', on_delete=models.CASCADE
    )
    correspondentieadres = models.ForeignKey(
        'rsgb.Correspondentieadres', on_delete=models.SET_NULL, null=True, blank=True)
    postadres = models.ForeignKey(
        'rsgb.PostAdres', on_delete=models.SET_NULL, null=True, blank=True)
    verblijf_buitenland = models.ForeignKey('rsgb.VerblijfBuitenland', null=True, blank=True)

    class Meta:
        abstract = True
