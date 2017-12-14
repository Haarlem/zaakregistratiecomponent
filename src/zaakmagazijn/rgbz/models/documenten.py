from datetime import datetime

from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models

from ...api.stuf.utils import set_model_value
from ...cmis.fields import DMSField
from ...cmis.models import CMISMixin
from ...utils import stuf_datetime
from ...utils.fields import StUFDateField
from ..choices import InformatieObjectArchiefNominatie, Vertrouwelijkaanduiding
from ..validators import (
    alphanumeric_excluding_diacritic, validate_non_negative_string
)
from .basemodels import Object
from .managers import EnkelvoudigInformatieObjectManager


class InformatieObject(Object):
    """
    Geheel van gegevens met een eigen identiteit ongeacht zijn vorm, met de
    bijbehorende metadata ontvangen of opgemaakt door een natuurlijke en/of
    rechtspersoon bij de uitvoering van taken, zijnde een ENKELVOUDIG
    INFORMATIEOBJECT of een SAMENGESTELD INFORMATIEOBJECT.

    Unieke aanduiding De combinatie van ‘Bronorganisatie’ en ‘Informatieobjectidentificatie’
    """

    informatieobjectidentificatie = models.CharField(
        max_length=40, help_text='Een binnen een gegeven context ondubbelzinnige referentie naar het INFORMATIEOBJECT.',
        validators=[alphanumeric_excluding_diacritic, ])
    # TODO [KING]: Attribuut bronorganisatie in IOT bestaat niet in ZDS maar is verplicht
    # TODO [KING]: Taiga #275: In de KING documentatie staat N9
    bronorganisatie = models.CharField(max_length=9, validators=[validate_non_negative_string, ],
                                       blank=True, null=True,
                                       help_text='Het RSIN van de Niet-natuurlijk persoon zijnde de organisatie die het informatieobject '
                                       'heeft gecreëerd of heeft ontvangen en als eerste in een samenwerkingsketen heeft vastgelegd.')
    creatiedatum = StUFDateField(
        help_text='Een datum of een gebeurtenis in de levenscyclus van het INFORMATIEOBJECT.')

    # Verplicht te registreren voor INFORMATIEOBJECTen die van buiten de zaakbehandelende organisatie(s) ontvangen zijn
    ontvangstdatum = StUFDateField(null=True, blank=True,
                                   help_text='De datum waarop het INFORMATIEOBJECT ontvangen is.')

    # De attribuutsoort kan alleen van een waarde voorzien zijn indien er bij het INFORMATIEOBJECT geen relatie
    # ‘INFORMATIEOBJECT.is ontvangen van of verzonden aan BETROKKENE’ is waarvan de eigenschap ‘Aard relatie’ gelijk
    # is aan ‘afzender’ en indien de attribuutsoort Ontvangstdatum van een waarde is voorzien.
    afzender = models.CharField(max_length=200, null=True, blank=True,
                                help_text='De persoon of organisatie waarvan het informatieobject is ontvangen.')
    titel = models.CharField(max_length=200,
                             help_text='De naam waaronder het INFORMATIEOBJECT formeel bekend is.')

    beschrijving = models.TextField(max_length=1000, null=True, blank=True,
                                    help_text='Een generieke beschrijving van de inhoud van het INFORMATIEOBJECT.')

    # Het gaat hier om een versienummer zoals ‘0.2’ en 1.0’. Ofschoon we er voor gekozen hebben om zowel dit
    # attribuuttype als het attribuuttype Status optioneel te verklaren, ware het aan te bevelen bij elk documemt in
    # ieder geval één van beide attributen van een waarde te voorzien. Nb: De attribuutsoort is in versie 2.0 verplaatst
    # van ENKELVOUDIG INFORMATIEOBJECT naar INFORMATIEOBJECT.
    versie = models.CharField(max_length=5, null=True, blank=True,
                              help_text='Aanduiding van de bewerkingsfase van het INFORMATIEOBJECT')

    # Zie InformatieObjectStatus voor de keuze constraints
    # In RGBZ is dit 'status', en is veranderd vanwege een reverse name collision.
    # TODO [KING]: In RGBZ 1.0 there was no restriction of allowed values, while in RGBZ 2.0 there is. For now,
    # comment out the comment choices.
    informatieobject_status = models.CharField(max_length=20, null=True, blank=True,
                                               # choices=InformatieObjectStatus.choices,
                                               help_text='Aanduiding van de stand van zaken van een INFORMATIEOBJECT')
    verzenddatum = StUFDateField(null=True, blank=True)
    geadresseerde = models.CharField(max_length=200, null=True, blank=True,
                                     help_text='De persoon of organisatie waarnaar het informatieobject is verzonden.')
    vertrouwlijkaanduiding = models.CharField(max_length=20, choices=Vertrouwelijkaanduiding.choices,
                                              help_text='Aanduiding van de mate waarin het INFORMATIEOBJECT voor de '
                                                        'openbaarheid bestemd is.')
    gebruiksrechten = models.ForeignKey('rgbz.GebruiksRechten', null=True, blank=True)

    archiefnominatie = models.CharField(
        max_length=16, null=True, blank=True, choices=InformatieObjectArchiefNominatie.choices,
        help_text='Aanduiding of het INFORMATIEOBJECT blijvend bewaard '
                  'of na een bepaalde termijn vernietigd moet worden.')
    archiefactiedatum = StUFDateField(
        null=True, blank=True,
        help_text='De datum waarop het gearchiveerde INFORMATIEOBJECT vernietigd moet '
                  'worden dan wel overgebracht moet worden naar een archiefbewaarplaats.')
    auteur = models.CharField(
        max_length=200, help_text='De persoon of organisatie die in de eerste plaats verantwoordelijk '
                                  'is voor het creëren van de inhoud van het INFORMATIEOBJECT.')
    # mag niet van een waarde zijn voorzien als de attribuutsoort ‘Status’ de waarde ‘in bewerking’ of
    # ‘ter vaststelling’ heeft.
    # TODO [KING]: In het informatiemodel UML schema zijn de velden uit Ondertekening direct opgenomen in dit model.
    ondertekening = models.ForeignKey('rgbz.Ondertekening', null=True, blank=True,
                                      help_text='Aanduiding van de rechtskracht van een informatieobject.')
    verschijningsvorm = models.TextField(
        null=True, blank=True,
        help_text='De essentiële opmaakaspecten van een INFORMATIEOBJECT.'
    )

    betrokkene = models.ManyToManyField('rgbz.Betrokkene', through='rgbz.Verzending', blank=True,
                                        related_name='informatieobjecten')

    informatieobjecttype = models.ForeignKey(
        'rgbz.InformatieObjectType',
        help_text='Aanduiding van de aard van het INFORMATIEOBJECT zoals gehanteerd '
                  'door de zaakbehandelende organisatie.')

    _informatieobjecttype_model = models.CharField(max_length=50, null=True, blank=True)

    _inhoud = DMSField()

    class Meta:
        # bronorganisatie is an integer field with null=True...
        unique_together = ('informatieobjectidentificatie', 'bronorganisatie')
        verbose_name_plural = 'Informatie objecten'
        mnemonic = 'DOC'

    def __str__(self):
        return self.informatieobjectidentificatie

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._save_child_model('InformatieObject', '_informatieobjecttype_model')

    def full_clean(self, exclude=None, validate_unique=True):
        """
        The '_inhoud' field shouldn't be cleaned. It would be quite a waste of resources.
        """
        exclude = list(exclude or ())
        exclude.append('_inhoud')
        return super().full_clean(exclude=exclude, validate_unique=validate_unique)

    def is_type(self):
        return self._determine_type('InformatieObject', '_informatieobjecttype_model')

    def is_ontvangen_van_of_verzonden_aan(self):
        return self.betrokkene.all()

    def is_van(self):
        return self.informatieobjecttype

    # Momenteel niet in gebruik maar zal wss van pas komen bij CMIS integratie
    def is_edc(self):
        """ Return if this object is an EIO/EDC or SDC """
        if hasattr(self, 'enkelvoudiginformatieobject'):
            return True
        return False

    def edc_formaat(self):
        if self.is_edc():
            return self.enkelvoudiginformatieobject.formaat
        return ""

    def edc_link(self):
        if self.is_edc():
            return self.enkelvoudiginformatieobject.link
        return ""

    def edc_taal(self):
        if self.is_edc():
            return self.enkelvoudiginformatieobject.taal
        return ""

    def is_relevant_voor(self):
        return self.zaakinformatieobject_set, {}

    def create_identificatie(self):
        return '{}{}'.format(self.informatieobjectidentificatie, self.bronorganisatie)


class SamengesteldInformatieObject(InformatieObject):
    """
    Een INFORMATIEOBJECT waarbinnen twee of meer ENKELVOUDIGe
    INFORMATIEOBJECTen onderscheiden worden die vanwege gezamenlijke
    vervaardiging en/of ontvangst en/of vanwege aard en/of omvang als één
    geheel beschouwd moeten worden dan wel behandeld worden.,
    """
    class Meta:
        mnemonic = 'SDC'

    def omvat(self):
        if len(self.enkelvoudiginformatieobject_set.all()) >= 2:
            return self.enkelvoudiginformatieobject_set.all()
        else:
            raise ValidationError('Een samengesteld informatie object moet '
                                  'minimaal uit 2 enkelvoudige informatieobjecten bestaan')

    def is_specialisatie_van(self):
        return self.informatieobject_ptr


class EnkelvoudigInformatieObject(CMISMixin, InformatieObject):
    """
    Een INFORMATIEOBJECT waarvan aard, omvang en/of vorm aanleiding geven
    het als één geheel te behandelen en te beheren.
    """
    # String: Mime-types en subtypes conform IANA
    # Het Formaat moet van een waarde voorzien zijn indien:
    # - de attribuutsoort Inhoud van een waarde is voorzien (d.w.z. het betreft een digitaal bestand), of
    # - Bestandsnaam een waarde heeft (d.w.z. het betreft een digitaal bestand)
    # en uit de waarde van Bestandsnaam (cq. de bestandsextensie)
    # geen geldig bestandstype af te leiden is.
    # See: https://tools.ietf.org/html/rfc6838#section-4.2
    formaat = models.CharField(
        max_length=255, null=True,
        blank=True, help_text='De code voor de wijze waarop de inhoud van het ENKELVOUDIG '
                              'INFORMATIEOBJECT is vastgelegd in een computerbestand.'
    )
    taal = models.CharField(
        max_length=20, help_text='Een taal van de intellectuele inhoud van het ENKELVOUDIG INFORMATIEOBJECT')
    # String
    link = models.CharField(
        null=True, blank=True, help_text='De URL waarmee de inhoud van het INFORMATIEOBJECT op te vragen is.',
        max_length=200)
    bestandsnaam = models.ForeignKey('rgbz.Bestandsnaam', null=True, blank=True, on_delete=models.SET_NULL)

    # De attribuutsoort moet van een waarde zijn voorzien op het moment dat het enkelvoudig INFORMATIEOBJECT een
    # digitaal bestand betreft en gearchiveerd wordt d.w.z. wanneer de attribuutsoort Inhoud een waarde heeft en de
    # attribuutsoort INFORMATIEOBJECT Status de waarde 'Gearchiveerd' krijgt.
    bestandsomvang = models.IntegerField(
        null=True, blank=True, help_text='Ruimtebeslag op het digitale opslagmedium waarin '
                                         'het fysieke bestand met de inhoud van het INFORMATIEOBJECT is vastgelegd')
    integriteit = models.ForeignKey(
        'rgbz.Integriteit', null=True, blank=True, on_delete=models.SET_NULL)
    samengesteld_informatieobject = models.ForeignKey(
        'rgbz.SamengesteldInformatieObject', null=True, blank=True, on_delete=models.SET_NULL)

    _object_id = models.TextField(help_text='CMIS storage object id, internal use only', blank=True)

    objects = EnkelvoudigInformatieObjectManager()

    # TODO [DMS]: The content model deviates from the specification...
    CMIS_MAPPING = {
        'zsdms:documenttaal': 'taal',  # v
        'zsdms:documentLink': 'link',  # o

        'cmis:name': 'titel',  # v
        'zsdms:zaakidentificatie': 'zaakidentificatie',
        'zsdms:documentIdentificatie': 'informatieobjectidentificatie',  # v
        'zsdms:documentcreatiedatum': 'creatiedatum',  # v (kan verschillen van cmis:creationDate)
        'zsdms:documentontvangstdatum': 'ontvangstdatum',  # o
        'zsdms:documentbeschrijving': 'beschrijving',  # o
        'zsdms:documentverzenddatum': 'verzenddatum',  # o
        # TODO [TECH]: Change field to vertrouw*E*lijkaanduiding
        'zsdms:vertrouwelijkaanduiding': 'vertrouwlijkaanduiding',  # v
        'zsdms:documentauteur': 'auteur',  # v (kan verschillen van cmis:createdBy)
        'zsdms:documentversie': 'versie',  # o
        'zsdms:documentstatus': 'informatieobject_status',  # o

        'zsdms:dct.omschrijving': 'informatieobjecttype__informatieobjecttypeomschrijving',  # o
        # 'zsdms:dct.categorie': 'informatieobjecttype__informatieobjectcategorie',  # o

        # 'Content-stream': 'Documentinhoud', # v (is content-stream van EDC object)
    }

    class Meta:
        verbose_name_plural = 'Enkelvoudige informatie objecten'
        mnemonic = 'EDC'

    def is_specialisatie_van(self):
        return self.informatieobject_ptr

    def get_cmis_properties(self, **kwargs) -> dict:
        properties = super().get_cmis_properties(**kwargs)
        zaak = self.zaak

        properties['tmlo:externKenmerk'] = list(zaak.zaakkenmerk_set.values_list('kenmerk', flat=True)) or None

        # The following properties cannot be filled by the ZS:
        # tmlo:ondertekening
        # tmlo:verantwoordelijkeFunctionaris

        return properties

    def update_cmis_properties(self, new_cmis_properties, commit=False):
        if not self.pk:
            raise ValueError('Cannot update CMIS properties on unsaved instance.')

        updated_objects = set()

        for cmis_property, field_name in self.CMIS_MAPPING.items():
            if cmis_property not in new_cmis_properties:
                continue

            new_value = new_cmis_properties.get(cmis_property)
            if isinstance(new_value, datetime):
                new_value = stuf_datetime.stuf_date(new_value)

            obj = set_model_value(self, field_name, new_value)
            updated_objects.add(obj)

        if commit:
            for obj in updated_objects:
                obj.save()

        return updated_objects

    @property
    def volledige_bestandsnaam(self):
        if not self.bestandsnaam:
            return None
        return '{}.{}'.format(self.bestandsnaam.naam, self.bestandsnaam.extensie)

    @volledige_bestandsnaam.setter
    def volledige_bestandsnaam(self, value):
        """
        Update or create the related model `Bestandsnaam`. The filename is
        simply split on the right-most "." character to separate "naam" from
        "extensie".

        :param value: The full filename
        """
        from zaakmagazijn.rgbz.models import Bestandsnaam

        parts = value.rsplit('.', 1)
        naam = parts[0]
        if len(parts) == 2:
            extensie = parts[1]
        else:
            extensie = None

        if not self.bestandsnaam:
            self.bestandsnaam = Bestandsnaam.objects.create(naam=naam, extensie=extensie)
        else:
            self.bestandsnaam.naam = naam
            self.bestandsnaam.extensie = extensie
            self.bestandsnaam.save()

    @property
    def zaak(self):
        return self.zaakinformatieobject_set.get().zaak

    @property
    def zaakidentificatie(self):
        return self.zaak.zaakidentificatie


class InformatieObjectTypeOmschrijvingGeneriek(models.Model):
    """
    Algemeen binnen de overheid gehanteerde omschrijvingen van de typen informatieobjecten
    http://www.gemmaonline.nl/index.php/Imztc_2.1/doc/referentielijst/informatieobjecttype-omschrijving_generiek
    """
    informatieobjecttypeomschrijving_generiek = models.CharField(
        max_length=80, help_text='Algemeen gehanteerde omschrijving van het type informatieobject.')
    definitie_informatieobjecttypeomschrijving_generiek = models.TextField(
        max_length=255, help_text='Nauwkeurige beschrijving van het generieke type informatieobject')
    herkomst_informatieobjecttypeomschrijving_generiek = models.CharField(
        max_length=12, help_text='De naam van de waardenverzameling, of van de beherende organisatie '
                                 'daarvan, waaruit de waarde is overgenomen.')
    hierarchie_informatieobjecttypeomschrijving_generiek = models.CharField(
        max_length=80, help_text='De plaats in de rangorde van het informatieobjecttype.')
    opmerking_informatieobjecttypeomschrijving_generiek = models.TextField(
        max_length=255, null=True, blank=True, help_text='Zinvolle toelichting bij het informatieobjecttype')
    begin_geldigheid_informatieobjecttypeomschrijving_generiek = StUFDateField(
        help_text='De datum waarop de generieke omschrijving van toepassing is geworden.'
    )
    einde_geldigheid_informatieobjecttypeomschrijving_generiek = StUFDateField(
        null=True, blank=True, help_text='De datum waarop de generieke omschrijving niet meer van toepassing is.')


class InformatieObjectType(models.Model):
    """
    De aan de ZTC ontleende gegevens van een INFORMATIEOBJECTTYPE zoals die in het RGBZ
    gebruikt worden. Zie voor de specificaties van deze gegevens het ZTC.
    """

    informatieobjecttypeomschrijving = models.CharField(max_length=80, unique=True)
    domein = models.CharField(
        max_length=5, help_text='Een afkorting waarmee wordt aangegeven voor welk domein in de CATALOGUS'
                                ' ZAAKTYPEn zijn uitgewerkt.')
    rsin = models.PositiveIntegerField(
        help_text='Het door een kamer toegekend uniek nummer voor de INGESCHREVEN NIET-NATUURLIJK PERSOON'
    )
    informatieobjecttypeomschrijving_generiek = models.ForeignKey(
        'rgbz.InformatieObjectTypeOmschrijvingGeneriek', null=True, blank=True)
    informatieobjectcategorie = models.CharField(max_length=80)
    informatieobjecttypetrefwoord = ArrayField(
        models.CharField(max_length=30),
        help_text='Een verzameling van trefwoorden waarmee ZAAKen '
                  'van het ZAAKTYPE kunnen worden gekarakteriseerd.', null=True, blank=True
    )  # Multivalue field
    datum_begin_geldigheid_informatieobjecttype = StUFDateField(default=stuf_datetime.today)
    datum_einde_geldigheid_informatieobjecttype = StUFDateField(null=True, blank=True)
