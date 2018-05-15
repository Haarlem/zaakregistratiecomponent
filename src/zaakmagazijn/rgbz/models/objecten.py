from django.core.validators import (
    MaxLengthValidator, MinLengthValidator
)
from django.db import models

from zaakmagazijn.utils import stuf_datetime
from zaakmagazijn.utils.fields import StUFDateField

from ...rsgb.choices import TyperingOpenbareRuimte
from ...rsgb.models.basemodels import AdresBaseClass
from ..choices import (
    Huishoudensoort, JaNee, SoortRechtsvorm, TyperingInrichtingselement,
    TyperingKunstwerk, TyperingWater, TypeSpoorbaan
)
from ..validators import validate_nen360id, validate_non_negative_string
from .basemodels import (
    IngezeteneBaseClass, NietNatuurlijkPersoonBaseClass, Object, ObjectMixin
)
from .mixins import ExtraValidatorsMixin, GeslachtsAanduidingMixin


class AnderBuitenlandsNietNatuurlijkPersoonObject(NietNatuurlijkPersoonBaseClass, ObjectMixin, Object):
    """
    De aan het RSGB ontleende gegevens van een ANDER BUITENLANDS NIET-NATUURLIJK
    PERSOON die in het RGBZ gebruikt worden bij deze specialisatie van OBJECT. Zie voor de
    specificaties van deze gegevens het RSGB.
    """
    rsin = None
    nummer_ander_buitenlands_nietnatuurlijk_persoon = models.CharField(
        max_length=17, help_text='Het door de gemeente uitgegeven uniekenummer voor een ANDER NIET-NATUURLIJK PERSOON')
    verkorte_naam = models.CharField(
        max_length=45, null=True, blank=True,
        help_text='De administratieve naam in het handelsregister'
                  ' indien de (statutaire) naam langer is dan 45 karakters'
    )

    class Meta:
        mnemonic = 'ANN'


class AnderNatuurlijkPersoonObject(GeslachtsAanduidingMixin, ObjectMixin, Object):
    """
    Het betreft hier de natuurlijke personen die niet ingeschreven zijn in de BRP (GBA en het RNI)
    maar wel van belang zijn voor de gemeentelijke taakuitoefening. Het kan gaan om zowel in
    Nederland woonachtige personen als in het buitenlandse verblijvende personen. Een ANDER
    NATUURLIJK PERSOON is een specialisatie van NATUURLIJK PERSOON. In de BRP worden deze
    personen niet-ingeschrevenen genoemd en kunnen meerdere keren voorkomen in de centrale
    voorzieningen. In de BRP worden niet-ingeschrevenen gevonden door te zoeken op de
    combinatie van Samengestelde naam, Geboorte en Geslachtsaanduiding.
    """
    nummer_ander_natuurlijk_persoon = models.CharField(
        max_length=17, help_text='Het door de gemeente uitgegeven unieke nummer voor een ANDER NATUURLIJK PERSOON'
    )
    geboortedatum = StUFDateField(
        help_text='De datum waarop de ander natuurlijk persoon is geboren.', null=True, blank=True
    )
    overlijdensdatum = StUFDateField(
        help_text='De datum van overlijden van een ANDER NATUURLIJK PERSOON', null=True, blank=True
    )
    # Help texten
    naamaanschrijving = models.ForeignKey(
        'rsgb.NaamAanschrijving', on_delete=models.CASCADE
    )
    correspondentieadres = models.ForeignKey(
        'rsgb.Correspondentieadres', on_delete=models.CASCADE)
    verblijf_buitenland = models.ForeignKey(
        'rsgb.VerblijfBuitenland', null=True, blank=True)

    class Meta:
        mnemonic = 'ANP'


class AppartementsRechtObject(ObjectMixin, Object):
    """
    De aan het RSGB ontleende gegevens van een APPARTEMENTSRECHT die in het RGBZ gebruikt
    worden bij deze specialisatie van OBJECT. Zie voor de specificaties van deze gegevens het
    RSGB.
    """
    kadastrale_identificatie = models.ForeignKey(
        'rsgb.CompositeID', help_text='De unieke aanduiding van een onroerende zaak, die door het kadaster wordt vastgesteld.')
    datum_begin_geldigheid_kadastrale_onroerende_zaak = StUFDateField(
        default=stuf_datetime.today,
    )
    datum_einde_geldigheid_kadastrale_onroerende_zaak = StUFDateField(null=True, blank=True)

    @property
    def kadastrale_aanduiding_appartementsrecht(self):
        return self.object_ptr.kadastrale_aanduiding

    class Meta:
        mnemonic = 'APR'


class BuurtObject(ObjectMixin, Object):
    """
    De aan het RSGB ontleende gegevens van een BUURT die in het RGBZ gebruikt worden bij deze
    specialisatie van OBJECT.
    Zie voor de specificaties van deze gegevens het RSGB.

    Unieke aanduiding Combinatie van Buurtcode en WIJK
    """
    buurtcode = models.CharField(
        max_length=2, help_text='De code behorende bij de naam van de buurt')

    buurtnaam = models.CharField(
        max_length=40, help_text='De naam van de buurt, zoals die door het CBS wordt gebruikt.')

    datum_begin_geldigheid_buurt = StUFDateField(
        default=stuf_datetime.today,
        help_text='De datum waarop de buurt is gecreëerd.'
    )
    datum_einde_geldigheid_buurt = StUFDateField(
        help_text='De datum waarop een buurt is komen te vervallen.'
    )
    wijkcode = models.CharField(
        max_length=2, help_text='De code behorende bij de naam van de wijk')
    gemeentecode = models.CharField(
        max_length=4, help_text='Een numerieke aanduiding waarmee een Nederlandse gemeente uniek wordt aangeduid')

    class Meta:
        unique_together = ('buurtcode', 'wijkcode')
        mnemonic = 'BRT'

    @property
    def buurtgeometrie(self):
        """
        :return: De tweedimensionale geometrische representatie van de omtrekken van de buurt.
        """
        return self.object_ptr.geometrie

    def create_identificatie(self):
        return '{}{}'.format(self.buurtcode, self.wijkcode)


class GemeenteObject(ObjectMixin, Object):
    """
    De aan het RSGB ontleende gegevens van een GEMEENTE die in het RGBZ gebruikt worden bij
    deze specialisatie van OBJECT. Zie voor de specificaties van deze gegevens het RSGB.

    Unieke aanduiding Gemeentecode
    """
    gemeentenaam = models.CharField(
        max_length=80, help_text='De officiële door de gemeente vastgestelde gemeentenaam.')
    datum_begin_geldigheid_gemeente = StUFDateField(
        default=stuf_datetime.today,
        help_text='De datum waarop de gemeente is ontstaan')
    datum_einde_geldigheid_gemeente = StUFDateField(
        null=True, blank=True, help_text='De datum waarop de gemeente is opgeheven.')

    @property
    def gemeentecode(self):
        # gemeentecode = models.CharField(
        #     max_length=4, help_text='Een numerieke aanduiding waarmee een Nederlandse gemeente uniek wordt aangeduid')
        return self.object_ptr.identificatie

    @property
    def gemeentegeometrie(self):
        """
        :return: De tweedimensionale geometrische representatie van de omtrekken van het grondgebied van een gemeente.
        """
        return self.object_ptr.geometrie

    class Meta:
        mnemonic = 'GEM'


class GemeentelijkeOpenbareRuimteObject(ExtraValidatorsMixin, ObjectMixin, Object):
    """
    De aan het RSGB ontleende gegevens van een GEMEENTELIJKE OPENBARE RUIMTE die in het
    RGBZ gebruikt worden bij deze specialisatie van OBJECT. Zie voor de specificaties van deze
    gegevens het RSGB.
    """
    gemeentecode = models.CharField(
        max_length=4, help_text='Een numerieke aanduiding waarmee een Nederlandse gemeente uniek wordt aangeduid')
    # identificatiecode_gemeentelijke_openbare_ruimte = models.ForeignKey(
    #   'rsgb.BAGObjectnummering', on_delete=models.CASCADE)
    naam_openbare_ruimte = models.CharField(
        max_length=80, help_text='Een door het bevoegde gemeentelijke orgaan aan een '
                                 'OPENBARE RUIMTE toegekende benaming')
    # TODO [KING]: Volgens RSGB 3.0 is GemeentelijkeOpenbareRuimte.type_openbare_ruimte verplicht. Volgens ZDS echter niet en kan het zelfs niet worden meegegeven.
    type_openbare_ruimte = models.CharField(blank=True, null=True,
        max_length=36, choices=TyperingOpenbareRuimte.choices,
        help_text='De aard van de als zodanig benoemde OPENBARERUIMTE.'
    )
    datum_begin_geldigheid_gemeentelijke_openbare_ruimte = StUFDateField(
        default=stuf_datetime.today,
        help_text='De datum waarop de OPENBARE RUIMTE formeel is benoemd.'
    )
    datum_einde_geldigheid_gemeentelijke_openbare_ruimte = StUFDateField(
        null=True, blank=True,
        help_text='De datum waarop formeel is besloten de OPENBARE RUIMTE niet langer te laten')

    EXTRA_VALIDATORS = {
        'identificatie': [MaxLengthValidator(16), MinLengthValidator(16)]
    }

    @property
    def geometrie_gemeentelijke_openbare_ruimte(self):
        """
        De tweedimensionale geometrische representatie van de omtrekken van de openbare ruimte.
        :return:
        """
        return self.object_ptr.geometrie

    class Meta:
        mnemonic = 'OPR'


class HuishoudenObject(AdresBaseClass, ObjectMixin, Object):
    huishoudennummer = models.CharField(
        max_length=12, help_text='Uniek identificerend administratienummer van een huishouden '
                                 'zoals toegekend door de gemeente waarin het huishouden woonachtig is.')
    # TODO [KING] Verplicht in RSGB, optioneel in XSD.
    huishoudensoort = models.CharField(blank=True, null=True,
        max_length=2, choices=Huishoudensoort.choices, help_text='Typering van het huishouden naar grootte en verbondenheid.')
    datum_begin_geldigheid_huishouden = StUFDateField(
        default=stuf_datetime.today,
        help_text='De datum waarop het HUISHOUDEN is ontstaan.')
    datum_einde_geldigheid_huishouden = StUFDateField(
        null=True, blank=True,
        help_text='De datum waarop het HUISHOUDEN is komen te vervallen.')

    class Meta:
        mnemonic = 'HHD'

    def create_identificatie(self):
        return '{}'.format(self.huishoudennummer)


class IngeschrevenNietNatuurlijkPersoonObject(NietNatuurlijkPersoonBaseClass, ObjectMixin, Object):
    """
    De aan het RSGB ontleende gegevens van een INGESCHREVEN NIET-NATUURLIJK PERSOON die
    in het RGBZ gebruikt worden bij deze specialisatie van OBJECT.
    Zie voor de specificaties van deze gegevens het RSGB.
    """
    rechtsvorm = models.CharField(
        max_length=30, choices=SoortRechtsvorm.choices, null=True, blank=True,
        help_text='De juridische vorm van de INGESCHREVEN NIET-NATUURLIJK PERSOON.')
    bezoekadres = models.ForeignKey(
        'rsgb.Bezoekadres', on_delete=models.SET_NULL, null=True, blank=True, related_name='bezoekadres')
    correspondentieadres = models.ForeignKey(
        'rsgb.Correspondentieadres', on_delete=models.SET_NULL, null=True, blank=True
    )
    postadres = models.ForeignKey(
        'rsgb.PostAdres', on_delete=models.SET_NULL, null=True, blank=True, related_name='postadres')

    class Meta:
        mnemonic = 'INN'


class IngezeteneObject(IngezeteneBaseClass):
    pass


class InrichtingsElementObject(ExtraValidatorsMixin, ObjectMixin, Object):
    """
    De aan het RSGB ontleende gegevens van een INRICHTINGSELEMENT die in het RGBZ gebruikt
    worden bij deze specialisatie van OBJECT. Zie voor de specificaties van deze gegevens het RSGB.
    """
    inrichtingselementtype = models.CharField(
        max_length=30, choices=TyperingInrichtingselement.choices,
        help_text='Specificatie van de aard van het inrichtingselement.')

    datum_begin_geldigheid_inrichtingselement = StUFDateField(
        default=stuf_datetime.today,
        help_text='De datum waarop het inrichtingselement is ontstaan.')
    datum_einde_geldigheid_inrichtingselement = StUFDateField(
        null=True, blank=True, help_text='De datum waarop het inrichtingselement ongeldig is geworden.')

    EXTRA_VALIDATORS = {
        'identificatie': [validate_nen360id, ]
    }

    @property
    def geometrie_inrichtingselement(self):
        """
        :return: De geometrische representatie van een inrichtingselement.
        """
        return self.object_ptr.geometrie

    def naam_inrichtingselement(self):
        return self.object_ptr.naam

    class Meta:
        mnemonic = 'INR'


class KadastraalPerceelObject(ExtraValidatorsMixin, ObjectMixin, Object):
    """
    De aan het RSGB ontleende gegevens van een KADASTRAAL PERCEEL die in het RGBZ gebruikt
    worden bij deze specialisatie van OBJECT. Zie voor de specificaties van deze gegevens het
    RSGB.
    """
    begrenzing_perceel = models.TextField(
        null=True, blank=True,
        help_text='Het geheel van lijnketens waarmee de vlakomtrek van een perceel wordt gevormd.')
    datum_begin_geldigheid_kadastrale_onroerende_zaak = StUFDateField(
        default=stuf_datetime.today,
        help_text='De datum waarop de gegevens van de kadastrale onroerende zaak voor het eerst geldig zijn geworden.')
    datum_einde_geldigheid_kadastrale_onroerende_zaak = StUFDateField(
        null=True, blank=True, help_text='De datum waarop de gegevens van de kadastrale '
                                         'onroerende zaak voor het laatstgeldig zijn geweest.')

    EXTRA_VALIDATORS = {
        'identificatie': [validate_non_negative_string, MaxLengthValidator(15)]
    }

    class Meta:
        mnemonic = 'KDP'


class KunstwerkDeelObject(ExtraValidatorsMixin, ObjectMixin, Object):
    """
    De aan het RSGB ontleende gegevens van een KUNSTWERKDEEL die in het RGBZ gebruikt
    worden bij deze spFecialisatie van OBJECT. Zie voor de specificaties van deze gegevens het
    RSGB.

    Unieke aanduiding Identificatie kunstwerkdeel
    """
    type_kunstwerk = models.CharField(
        max_length=40, choices=TyperingKunstwerk.choices,
        help_text='Specificatie van het soort Kunstwerk waartoe het kunstwerkdeel behoort.')
    # TODO [KING]: Attribuut "naam kunstwerkdeel" van Objecttype KunstwerkDeel staat niet in het RGBZ of het RSGB
    naam_kunstwerkdeel = models.CharField(max_length=80)
    datum_begin_geldigheid_kunstwerkdeel = StUFDateField(
        default=stuf_datetime.today,
        help_text='De datum waarop het kunstwerkdeel is ontstaan.')
    datum_einde_geldigheid_kunstwerkdeel = StUFDateField(
        null=True, blank=True, help_text='De datum waarop het kunstwerkdeel ongeldig is geworden.')

    EXTRA_VALIDATORS = {
        'identificatie': [validate_nen360id, ]
    }

    @property
    def identificatie_kunstwerkdeel(self):
        return self.object_ptr.identificatie

    @property
    def geometrie_kunstwerkdeel(self):
        """
        :return: De minimaal tweedimensionale geometrische representatie van de omtrekken van een kunstwerkdeel
        """
        return self.object_ptr.geometrie

    class Meta:
        mnemonic = 'KWD'


class LigplaatsObject(ObjectMixin, Object):
    """
    De aan het RSGB ontleende gegevens van een LIGPLAATS die in het RGBZ gebruikt worden bij
    deze specialisatie van OBJECT. Zie voor de specificaties van deze gegevens het RSGB.
    """
    # TODO [KING]: volgens rsgb 2.0 model, Zie BAG voor de specificatie, alleen, waar is de BAG documentatie..
    # http://www.gemmaonline.nl/index.php/INRICHTINGSELEMENT_(RGBView-RSGB_-in_gebruik-02.01)_-_EAID_82C50ACC_AFFB_486f_BA82_CE8462CBDD44
    # benoemd_terrein_identificatie =

    datum_begin_geldigheid_benoemd_terrein = StUFDateField(
        default=stuf_datetime.today,
        help_text='De datum waarop van gemeentewege het benoemd terrein formeel is aangewezen.'
    )
    datum_einde_geldigheid_benoemd_terrein = StUFDateField(
        null=True, blank=True,
        help_text='De datum waarop van gemeentewege het benoemd terrein formeel is ingetrokken.')
    hoofdadres = models.ForeignKey('rsgb.AdresMetPostcode', on_delete=models.CASCADE)

    class Meta:
        mnemonic = 'LPL'


class MaatschappelijkeActiviteitObject(ObjectMixin, Object):
    """
    De aan het RSGB ontleende gegevens van een MAATSCHAPPELIJKE ACTIVITEIT die in het RGBZ gebruikt worden bij
    deze specialisatie van OBJECT. Zie voor de specificaties van deze gegevens het RSGB.

    Unieke aanduiding KvK-nummer
    """
    kvknummer = models.CharField(
        max_length=8, help_text='Landelijk uniek identificerend administratienummer van een '
                                'MAATSCHAPPELIJKE ACTIVITEIT zoals toegewezen door de Kamer van Koophandel (KvK).')

    datum_aanvang = StUFDateField(
        help_text='De datum van aanvang van de MAATSCHAPPELIJKE ACTIVITEIT'
    )
    datum_beeindiging = StUFDateField(
        null=True, blank=True, help_text='De datum van beëindiging van de MAATSCHAPPELIJKE ACTIVITEIT')

    # In RGBZ/RSGB genaamd: "1e Handelsnaam"
    eerste_handelsnaam = models.CharField(
        max_length=200, help_text='De naam waaronder de onderneming handelt.')

    def identificatie_eigenaar(self):
        return self.identificatie

    class Meta:
        mnemonic = 'MAC'


class NietIngezeteneObject(IngezeteneBaseClass):
    """
    De aan het RSGB ontleende gegevens van een NIET-INGEZETENE die in het RGBZ gebruikt
    worden bij deze specialisatie van OBJECT. Zie voor de specificaties van deze gegevens het RSGB.
    """
    pass


class NummerAanduidingObject(AdresBaseClass, ObjectMixin, Object): # add bezoekadres?
    """
    De aan het RSGB ontleende gegevens van een NUMMERAANDUIDING die in het RGBZ gebruikt
    worden bij deze specialisatie van OBJECT. Zie voor de specificaties van deze gegevens het
    RSGB.
    """
    indicatie_hoofdadres = models.CharField(max_length=1, choices=JaNee.choices,
                                            help_text='Indicatie of de NUMMERAANDUIDING een hoofdadres is van het gerelateerde VERBLIJFSOBJECT, '
                                            'STANDPLAATS of LIGPLAATS'
                                            )
    identificatiecode_adresseerbaar_object_aanduiding = models.ForeignKey(
        'rsgb.BAGObjectnummering', on_delete=models.CASCADE,
        help_text='De unieke aanduiding van een ADRESSEERBAAR OBJECT AANDUIDING')
    datum_begin_geldigheid_adresseerbaar_object_aanduiding = StUFDateField(
        default=stuf_datetime.today,
        help_text='De datum waarop de ADRESSEERBAAR OBJECT AANDUIDING formeel is vastgesteld.'
    )
    datum_einde_geldigheid_adresseerbaar_object_aanduiding = StUFDateField(
        null=True, blank=True, help_text='De datum waarop de ADRESSEERBAAR OBJECT AANDUIDING formeel is ingetrokken.')

    class Meta:
        mnemonic = 'NRA'


class OpenbareRuimteObject(ExtraValidatorsMixin, ObjectMixin, Object):
    """
    De aan het RSGB ontleende gegevens van een OPENBARE RUIMTE die in het RGBZ gebruikt
    worden bij deze specialisatie van OBJECT. Zie voor de specificaties van deze gegevens het
    RSGB.

    Unieke aanduiding Identificatiecode openbare ruimte
    """
    # identificatiecode_openbare_ruimte = models.ForeignKey(
    #     'rsgb.BAGObjectnummering', on_delete=models.CASCADE, related_name='identificatiecode',
    #     help_text='De unieke aanduiding van een OPENBARE RUIMTE.')

    naam_openbare_ruimte = models.CharField(
        max_length=80, help_text='Een door het bevoegde gemeentelijke orgaan aan een '
                                 'OPENBARE RUIMTE toegekende benaming')
    # TODO [KING]: Volgens RSGB 3.0 is GemeentelijkeOpenbareRuimte.type_openbare_ruimte verplicht. Volgens ZDS echter niet en kan het zelfs niet worden meegegeven.
    type_openbare_ruimte = models.CharField(blank=True, null=True,
        max_length=36, choices=TyperingOpenbareRuimte.choices,
        help_text='De aard van de als zodanig benoemde OPENBARERUIMTE.'
    )
    datum_begin_geldigheid_openbare_ruimte = StUFDateField(
        default=stuf_datetime.today,
        help_text='De datum waarop de OPENBARE RUIMTE formeel is benoemd.'
    )
    datum_einde_geldigheid_openbare_ruimte = StUFDateField(
        null=True, blank=True, help_text='De datum waarop formeel is besloten de '
        'OPENBARE RUIMTE niet langer te laten bestaan.')
    woonplaatsnaam = models.CharField(max_length=80)

    EXTRA_VALIDATORS = {
        'identificatie': [MaxLengthValidator(16), ]
    }

    class Meta:
        mnemonic = 'OPR'


class OverigGebouwdObject(ObjectMixin, Object):
    """
    De aan het RSGB ontleende gegevens van een OVERIG GEBOUWD OBJECT die in het RGBZ
    gebruikt worden bij deze specialisatie van OBJECT. Zie voor de specificaties van deze gegevens
    het RSGB
    """
    # TODO [KING]: Atribuut "overig_gebouwd_object_locatieaanduiding" in Objecttype OverigGebouwdObject staat niet in RGBZ of RSGB
    # gebouwd_object_identificatie = models.ForeignKey(
    #     'rsgb.BAGObjectnummering')

    datum_begin_geldigheid = StUFDateField(
        default=stuf_datetime.today,
        help_text='De datum waarop vangeldigheid gebouwd gemeentewege is vastgesteld dat de bouwwerkzaamheden '
                  'betreffende de oprichting van een GEBOUWD OBJECT conform de vergunning, '
                  'de melding of de aanschrijving zijn uitgevoerd.'
    )
    datum_einde_geldigheid = StUFDateField(
        null=True, blank=True,
        help_text='De datum waarop het gebouwd object is gesloopt volgens de sloopgereedmelding.')
    locatieadres = models.ForeignKey('rsgb.AdresMetPostcode')

    @property
    def gebouwd_object_puntgeometrie(self):
        """
        :return: De minimaal tweedimensionale geometrische representatie van een GEBOUWD OBJECT
        """
        return self.object_ptr.geometrie

    EXTRA_VALIDATORS = {
        'identificatie': [MaxLengthValidator(16), ]
    }

    class Meta:
        mnemonic = 'OGO'


class OverigTerreinObject(ObjectMixin, Object):
    """
    De aan het RSGB ontleende gegevens van een OVERIG TERREIN die in het RGBZ gebruikt
    worden bij deze specialisatie van OBJECT. Zie voor de specificaties van deze gegevens het
    RSGB.
    """
    benoemd_terrein_identificatie = models.ForeignKey(
        'rsgb.BAGObjectnummering', help_text='De unieke aanduiding van een OVERIG BENOEMD TERREIN.')
    # TODO [KING]: Dubbel gedefinieerd in RGBZ 2.0?
    # geometrie = models.TextField(
    #     help_text='De tweedimensionale geometrische representatie van de omtrekken van een BENOEMD TERREIN.')
    datum_begin_geldigheid = StUFDateField(
        default=stuf_datetime.today,
        help_text='De datum waarop van gemeentewege het benoemd terrein formeel is aangewezen.'
    )
    datum_einde_geldigheid = StUFDateField(
        null=True, blank=True, help_text='De datum waarop van gemeentewege het benoemd terrein formeel is ingetrokken.')
    officieel_adres = models.ForeignKey('rsgb.AdresMetPostcode')

    class Meta:
        mnemonic = 'BTR'


class OverigeAdresseerbaarObjectAanduidingObject(ObjectMixin, Object, AdresBaseClass):
    """
    De aan het RSGB ontleende gegevens van een OVERIGE ADRESSEERBAAR OBJECT AANDUIDING
    die in het RGBZ gebruikt worden bij deze specialisatie van OBJECT. Zie voor de specificaties van
    deze gegevens het RSGB.
    """
    # This used to be set, but checking the RGBZ, this seems to be a mistake.
    # woonplaatsnaam = None
    datum_begin_geldigheid_adresseerbaar_object_aanduiding = StUFDateField(
        default=stuf_datetime.today,
        help_text='De datum waarop de ADRESSEERBAAR OBJECT AANDUIDING formeel is vastgesteld.'
    )
    datum_einde_geldigheid_adresseerbaar_object_aanduiding = StUFDateField(
        null=True, blank=True, help_text='De datum waarop de ADRESSEERBAAR OBJECT AANDUIDING formeel is ingetrokken.')

    class Meta:
        mnemonic = 'OAO'


class PandObject(ObjectMixin, Object):
    """
    De aan het RSGB ontleende gegevens van een PAND die in het RGBZ gebruikt worden bij deze
    specialisatie van OBJECT. Zie voor de specificaties van deze gegevens het RSGB.

    Unieke aanduiding Pandidentificatie
    """
    # pandidentificatie = models.ForeignKey(
    # 'rsgb.BAGObjectnummering', help_text='De unieke aanduiding van een PAND')

    datum_begin_geldigheid_pand = StUFDateField(
        default=stuf_datetime.today,
        help_text='De datum waarop van gemeentewege is vastgesteld dat de bouwwerkzaamheden betreffende de oprichting '
                  'van een PAND conform de vergunning, de melding of de aanschrijving zijn uitgevoerd.')
    datum_einde_geldigheid_pand = StUFDateField(null=True, blank=True,
                                                help_text='De datum waarop het pand is gesloopt volgens de sloopgereedmelding.')

    @property
    def padgeometrie_bovenaanzicht(self):
        """
        :return: De minimaal tweedimensionale geometrische representatie van het bovenaanzicht van de omtrekken van een PAND
        """
        return self.object_ptr.geometrie

    EXTRA_VALIDATORS = {
        # ObjectNummering
        'identificatie': [MaxLengthValidator(16), ]
    }

    class Meta:
        mnemonic = 'PND'


class SpoorbaanDeelObject(ObjectMixin, Object):
    """
    De aan het RSGB ontleende gegevens van een SPOORBAANDEEL die in het RGBZ gebruikt
    worden bij deze specialisatie van OBJECT. Zie voor de specificaties van deze gegevens het RSGB.
    """
    type_spoorbaan = models.CharField(
        max_length=40, choices=TypeSpoorbaan.choices, help_text='Specificatie van het soort Spoorbaan')

    datum_begin_geldigheid_spoorbaandeel = StUFDateField(
        default=stuf_datetime.today,
        help_text='De datum waarop het spoorbaandeel is ontstaan.')
    datum_einde_geldigheid_spoorbaandeel = StUFDateField(
        null=True, blank=True, help_text='De datum waarop het spoorbaandeel ongeldig is geworden.')

    EXTRA_VALIDATORS = {
        'identificatie': [validate_nen360id, ]
    }

    class Meta:
        mnemonic = 'SBD'


class StandPlaatsObject(ObjectMixin, Object):
    """
    De aan het RSGB ontleende gegevens van een STANDPLAATS die in het RGBZ gebruikt worden
    bij deze specialisatie van OBJECT. Zie voor de specificaties van deze gegevens het RSGB.
    """
    # FIXME Benoemd terrein identificatie staat niet in RSGB
    # benoemd_terrein_identificatie = ?

    # Dubbel gedefinieerd in RGBZ 2.0?
    # geometrie = models.TextField(
    #     help_text='De tweedimensionale geometrische representatie van de omtrekken van een BENOEMD TERREIN.')
    datum_begin_geldigheid_benoemd_terrein = StUFDateField(
        default=stuf_datetime.today,
        help_text='De datum waarop van gemeentewege het benoemd terrein formeel is aangewezen.')
    datum_eind_geldigheid_benoemd_terrein = StUFDateField(
        null=True, blank=True,
        help_text='De datum waarop van gemeentewege het benoemd terrein formeel is ingetrokken.')
    hoofdadres = models.ForeignKey('rsgb.AdresMetPostcode')

    class Meta:
        mnemonic = 'SPL'


class TerreinDeelObject(ExtraValidatorsMixin, ObjectMixin, Object):
    """
    De aan het RSGB ontleende gegevens van een TERREINDEEL die in het RGBZ gebruikt worden
    bij deze specialisatie van OBJECT. Zie voor de specificaties van deze gegevens het RSGB.
    """
    # TODO [KING]: Issue #268 Terreindeel komt niet voor in RSGB
    type_terrein = models.CharField(max_length=40)

    datum_begin_geldigheid_terreindeel = StUFDateField(
        default=stuf_datetime.today,
        help_text='De datum waarop het terreindeel is ontstaan.')
    datum_einde_geldigheid_terreindeel = StUFDateField(
        null=True, blank=True,
        help_text='De datum waarop het terreindeel ongeldig is geworden.')

    EXTRA_VALIDATORS = {
        'identificatie': [validate_nen360id, ]
    }

    class Meta:
        mnemonic = 'TDL'


class VerblijfsObject(ObjectMixin, Object):
    """
    De aan het RSGB ontleende gegevens van een VERBLIJFSOBJECT die in het RGBZ gebruikt
    worden bij deze specialisatie van OBJECT. Zie voor de specificaties van deze gegevens het RSGB.
    """
    genoemd_object_identificatie = models.ForeignKey('rsgb.BAGObjectnummering')

    datum_begin_geldigheid_gebouwd_object = StUFDateField(
        default=stuf_datetime.today,
        help_text='gemeentewege is vastgesteld dat de bouwwerkzaamheden betreffende de '
                  'oprichting van een GEBOUWD OBJECT conform de vergunning, de melding '
                  'of de aanschrijving zijn uitgevoerd.'
    )
    datum_eind_geldigheid_gebouwd_object = StUFDateField(
        null=True, blank=True,
        help_text='De datum waarop het gebouwd geldigheid is gesloopt volgens de object sloopgereedmelding.'
    )
    hoofdadres = models.ForeignKey('rsgb.AdresMetPostcode')

    class Meta:
        mnemonic = 'VBO'

    @property
    def gebouwd_object_puntgeometrie(self):
        """
        :return: De tweedimensionale geometrische representatie van de omtrekken van een GEBOUWD OBJECT
        """
        return self.object_ptr.geometrie


class WaterdeelObject(ExtraValidatorsMixin, ObjectMixin, Object):
    """
    De aan het RSGB ontleende gegevens van een WATERDEEL die in het RGBZ gebruikt worden bij
    deze specialisatie van OBJECT. Zie voor de specificaties van deze gegevens het RSGB.

    Unieke aanduiding Identificatie waterdeel
    """
    type_waterdeel = models.CharField(
        max_length=50, choices=TyperingWater.choices,
        help_text='Specificatie van het soort water')

    # TODO [KING]: Atribuut "naam waterdeel" in Objecttype WaterdeelObject staat niet in RGBZ of RSGB
    datum_begin_geldigheid_waterdeel = StUFDateField(
        default=stuf_datetime.today,
        help_text='De datum waarop het waterdeel is ontstaan.')
    datum_einde_geldigheid_waterdeel = StUFDateField(
        null=True, blank=True, help_text='De datum waarop het waterdeel ongeldig is geworden.')

    EXTRA_VALIDATORS = {
        'identificatie': [validate_nen360id, ]
    }

    @property
    def geometrie_waterdeel(self):
        """
        :return: De minimaal tweedimensionale geometrische representatie van de omtrekken van een waterdeel.
        """
        return self.object_ptr.geometrie

    class Meta:
        mnemonic = 'WTD'


class WegdeelObject(ExtraValidatorsMixin, ObjectMixin, Object):
    """
    De aan het RSGB ontleende gegevens van een WEGDEEL die in het RGBZ gebruikt worden bij
    deze specialisatie van OBJECT. Zie voor de specificaties van deze gegevens het RSGB.

    Unieke aanduiding Identificatie wegdeel
    """
    # TODO [KING]: Atribuut "type weg" in Objecttype WegdeelObject staat niet in RGBZ of RSGB

    # TODO [KING]: Atribuut "naam wegdeel" in Objecttype WegdeelObject staat niet in RGBZ of RSGB
    datum_begin_geldigheid_wegdeel = StUFDateField(
        default=stuf_datetime.today,
        help_text='De datum waarop het wegdeel is ontstaan')
    datum_einde_geldigheid_wegdeel = StUFDateField(
        null=True, blank=True, help_text='De datum waarop het wegdeel ongeldig is geworden.')

    EXTRA_VALIDATORS = {
        'identificatie': [validate_nen360id, ]
    }

    @property
    def geometrie_wegdeel(self):
        """
        :return: De minimaal tweedimensionale geometrische representatie van de omtrekken van een wegdeel.
        """
        return self.object_ptr.geometrie

    class Meta:
        mnemonic = 'WGD'


class WijkObject(ObjectMixin, Object):
    """
    De aan het RSGB ontleende gegevens van een WIJK die in het RGBZ gebruikt worden bij deze
    specialisatie van OBJECT. Zie voor de specificaties van deze gegevens het RSGB.

    Unieke aanduiding Combinatie van Wijkcode en GEMEENTE
    """
    wijkcode = models.CharField(
        max_length=2, help_text='De code behorende bij de naam van de wijk.')
    wijknaam = models.CharField(
        max_length=40, help_text='De naam van de wijk, zoals die door het CBS wordt gebruikt.')
    datum_begin_geldigheid_wijk = StUFDateField(
        default=stuf_datetime.today,
        help_text='De datum waarop de wijk is gecreëerd.'
    )
    datum_eind_geldigheid_wijk = StUFDateField(
        null=True, blank=True, help_text='De datum waarop een wijk is komen te vervallen.')
    gemeentecode = models.CharField(
        max_length=4, help_text='Een numerieke aanduiding waarmee een Nederlandse gemeente uniek wordt aangeduid')

    # TODO [TECH]: geometrie is verwijderd op Object
    # def wijkgeometrie(self):
    #     """
    #     :return: De tweedimensionale geometrische representatie van de omtrekken van de wijk.
    #     """
    #     return self.object_ptr.geometrie

    class Meta:
        unique_together = ('wijkcode', 'gemeentecode')
        mnemonic = 'WYK'

    def create_identificatie(self):
        return '{}{}'.format(self.wijkcode, self.gemeentecode)


class WoonplaatsObject(ObjectMixin, Object):
    """
    De aan het RSGB ontleende gegevens van een WOONPLAATS die in het RGBZ gebruikt worden
    bij deze specialisatie van OBJECT. Zie voor de specificaties van deze gegevens het RSGB.

    Unieke aanduiding Woonplaatsidentificatie
    """
    woonplaatsnaam = models.CharField(
        max_length=80, help_text='De door het bevoegde gemeentelijke orgaan aan een WOONPLAATS toegekende benaming.')
    datum_begin_geldigheid_woonplaats = StUFDateField(
        default=stuf_datetime.today,
        help_text='De datum waarop de woonplaats is ontstaan'
    )
    datum_einde_geldigheid_woonplaats = StUFDateField(
        null=True, blank=True, help_text='De datum waarop de woonplaats is komen te vervallen')

    def woonplaatsgeometrie(self):
        """
        :return: De tweedimensionale geometrische representatie van het vlak dat wordt gevormd door '
                  'de omtrekken van een woonplaats.
        """
        return self.object_ptr.geometrie

    class Meta:
        mnemonic = 'WPL'

    EXTRA_VALIDATORS = {
        # WoonplaatsCodering
        'identificatie': [validate_non_negative_string, MaxLengthValidator(4)]
    }

    @property
    def woonplaatsidentificatie(self):
        # woonplaatsidentificatie = models.CharField(
        #     max_length=4, help_text='De unieke aanduiding van een WOONPLAATS, zoals opgenomen in de landelijke woonplaatsentabel.')
        return self.object_ptr.identificatie


class WozdeelObject(ObjectMixin, Object):
    """
    Unieke aanduiding Combinatie van Nummer WOZ-deelobject en WOZ-OBJECT
    """
    nummer_wozdeelobject = models.CharField(
        max_length=6, help_text='Uniek identificatienummer voor het deelobject binnen een WOZ-object.')
    code_wozdeelobject = models.ForeignKey('rsgb.Deelobjectcode', models.CASCADE)
    datum_begin_geldigheid_deelobject = StUFDateField(
        default=stuf_datetime.today,
        help_text='Een aanduiding op welk tijdstip een deelobject is ontstaan.')
    datum_einde_geldigheid_deelobject = StUFDateField(
        null=True, blank=True, help_text='Een aanduiding op welk tijdstip een deelobject is beëindigd.')
    # TODO [KING] Verplicht in RSGB, optioneel in XSD.
    woz_objectnummer = models.CharField(null=True, blank=True,
        max_length=12, help_text='De unieke aanduiding van een WOZ-OBJECT.')

    class Meta:
        unique_together = ('nummer_wozdeelobject', 'woz_objectnummer')
        mnemonic = 'WDO'

    def create_identificatie(self):
        return '{}{}'.format(self.nummer_wozdeelobject, self.woz_objectnummer)


class WozObject(ObjectMixin, Object):
    """
    De aan het RSGB ontleende gegevens van een WOZ-OBJECT die in het RGBZ gebruikt worden
    bij deze specialisatie van OBJECT. Zie voor de specificaties van deze gegevens het RSGB.

    Unieke aanduiding WOZ-objectnummer
    """
    # TODO [KING]: Atribuut "locatieomschrijving" in Objecttype WozObject staat niet in RGBZ of RSGB

    # TODO [KING] Verplicht in RSGB, optioneel in XSD.
    soortobjectcode = models.ForeignKey('rsgb.SoortWOZObject', null=True,
        help_text='Aanduiding van het soort object ten behoeve van een correcte bepaling van de waarde.')
    datum_begin_geldigheid_wozobject = StUFDateField(
        default=stuf_datetime.today,
        help_text='Een aanduiding op welk tijdstip een object is ontstaan.'
    )
    datum_einde_geldigheid_wozobject = StUFDateField(
        null=True, blank=True, help_text='Een aanduiding op welk tijdstip een object is beëindigd.')
    adresaanduiding = models.ForeignKey('rsgb.AdresMetPostcode')

    @property
    def wozobjectnummer(self):
        # wozobjectnummer = models.CharField(
        #     max_length=12, help_text='De unieke aanduiding van een WOZ-OBJECT.')
        return self.object_ptr.identificatie

    @property
    def geometrie_wozobject(self):
        """
        :return: De minimaal tweedimensionale geometrische representatie van de omtrekken van een WOZ-OBJECT.
        """
        return self.object_ptr.geometrie

    class Meta:
        mnemonic = 'WOZ'


class WozWaardeObject(ObjectMixin, Object):
    """
    De aan het RSGB ontleende gegevens van een WOZ-WAARDE die in het RGBZ gebruikt worden
    bij deze specialisatie van OBJECT. Zie voor de specificaties van deze gegevens het RSGB.

    Unieke aanduiding Combinatie van Waardepeildatum en WOZ-OBJECT
    """
    # TODO [KING]: hier mist waarschijnlijk de relatie met het Woz-Object

    # TODO [KING] Verplicht in RSGB, optioneel in XSD.
    vastgestelde_waarde = models.CharField(null=True, blank=True,
        max_length=11, help_text='Waarde van het WOZ-object zoals deze in het kader van de Wet WOZ is vastgesteld.')
    waardepeildatum = StUFDateField(
        help_text='De datum waarnaar de waarde van het WOZ-object wordt bepaald.'
    )

    class Meta:
        mnemonic = 'WRD'


class ZakelijkRechtObject(ObjectMixin, Object):
    """
    De aan het RSGB ontleende gegevens van een ZAKELIJK RECHT die in het RGBZ gebruikt
    worden bij deze specialisatie van OBJECT. Zie voor de specificaties van deze gegevens het RSGB.

    Unieke aanduiding Identificatie zakelijk recht
    """
    # TODO [KING]: identificatie moet nog worden ingevuld, de unieke waarde is de FK..
    # name in rsgb3.0 does not have the prefix 'kadaster_'
    # kadaster_identificatie_zakelijk_recht = models.ForeignKey(
    # 'rsgb.CompositeID', help_text='Een door het Kadaster toegekende landelijk uniek nummer aan een recht.',
    # related_name='kadaster_identificatie', on_delete=models.CASCADE)
    ingangsdatum_recht = StUFDateField(
        null=True, blank=True, help_text='De datum waarop de notariële akte is ingeschreven of anderszins een '
                                         'brondocument waar het zakelijk recht op berust is ingeschreven.')
    einddatum_recht = StUFDateField(
        null=True, blank=True, help_text='De laatste dag waarop het recht volgens het brondocument, op grond '
                                         'waarvan het recht is opgevoerd, nog van toepassing zal zijn.'
    )
    aanduiding_aard_verkregen_recht = models.ForeignKey(
        'rsgb.AardZakelijkRecht', on_delete=models.CASCADE,
        help_text='Een aanduiding voor de aard van het recht.'
    )
    kadastrale_identificatie = models.ForeignKey(
        'rsgb.CompositeID', related_name='kadastrale_identificatie')
    # TODO [KING]: Staan niet in RSGB 3.0
    kadastrale_aanduiding_kadastraal_perceel = models.ForeignKey(
        'rsgb.KadastraleAanduidingKadastraalPerceel', related_name='kadastrale_aanduiding_kadastraal_perceel',
        null=True, blank=True
    )
    kadastrale_aanduiding_appartementsrecht = models.ForeignKey(
        'rsgb.KadastraleAanduidingAppartementsRecht',
        null=True, blank=True
    )
    # identificatie_zaakgerechtigde

    class Meta:
        mnemonic = 'ZKR'


# onderstaande 7 models zijn ongedaan gemaakt
# volgens Acceptatie Zaakmagazijn - Sprint 1 -- issue 3
#
# class BesluitObject(Object):
#     """
#     De aan het RGBZ ontleende gegevens van een BESLUIT die in het RGBZ gebruikt worden bij
#     deze specialisatie van OBJECT. Zie voor de specificaties van deze gegevens het RGBZ.
#     """
#     besluitidentificatie = models.CharField(
#         help_text='Identificatie van het besluit.',
#         max_length=50, validators=[AlphanumericExcludingDiacritic(start=5)])
#     besluitdatum = StUFDateField(
#         help_text='De beslisdatum (AWB) van het besluit'
#     )
#     ingangsdatum = StUFDateField(
#         help_text='Ingangsdatum van de werkingsperiode van het besluit.')
#     vervaldatum = StUFDateField(
#         null=True, blank=True,
#         help_text='Datum waarop de werkingsperiode van het besluit eindigt.')
#     besluittypeomschrijving = models.CharField(
#         max_length=80, null=True, blank=True, help_text='Omschrijving van de aard van BESLUITen van het BESLUITTYPE.')
#     besluittypeomschrijving_generiek = models.CharField(
#         max_length=80, null=True, blank=True, help_text='Algemeen gehanteerde omschrijving van de aard van '
#                                              'BESLUITen van het BESLUITTYPE')
#
#     class Meta:
#         mnemonic = 'BSL'
#
#
# class EnkelvoudigInformatieobjectObject(Object):
#     """
#     De aan het RGBZ ontleende gegevens van een ENKELVOUDIG INFORMATIEOBJECT die in het
#     RGBZ gebruikt worden bij deze specialisatie van OBJECT. Zie voor de specificaties van deze
#     gegevens het RGBZ.
#     """
#     informatieobjectidentificatie = models.CharField(
#         max_length=40,
#         help_text='Een binnen een gegeven context ondubbelzinnige referentie naar het INFORMATIEOBJECT.')
#     informatieobjectcreatiedatum = StUFDateField(
#         help_text='Een datum of een gebeurtenis in de levenscyclus van het INFORMATIEOBJECT.')
#
#     # Verplicht te registreren voor INFORMATIEOBJECTen die van buiten de zaakbehandelende organisatie(s) ontvangen zijn
#     informatieobjectontvangstdatum = StUFDateField(
#         null=True, blank=True, help_text='De datum waarop het INFORMATIEOBJECT ontvangen is.')
#     informatieobjecttitel = models.CharField(
#         max_length=200, null=True, blank=True,
#         help_text='De naam waaronder het INFORMATIEOBJECT formeel bekend is.')
#
#     class Meta:
#         mnemonic = 'EDC'
#
#
# class MedewerkerObject(MedewerkerMixin, Object):
#     """
#     De aan het RGBZ ontleende gegevens van een MEDEWERKER die in het RGBZ gebruikt worden
#     bij deze specialisatie van OBJECT. Zie voor de specificaties van deze gegevens het RGBZ
#     """
#     pass
#
#
# class OrganisatorischeEenheidObject(OrganisatorischeEenheidBaseClass, Object):
#     """
#     De aan het RGBZ ontleende gegevens van een ORGANISATORISCHE EENHEID die in het RGBZ
#     gebruikt worden bij deze specialisatie van OBJECT. Zie voor de specificaties van deze gegevens
#     het RGBZ.
#     """
#     naam = OrganisatorischeEenheidBaseClass.naam
#
#     class Meta:
#         mnemonic = 'OEH'
#
#
# class SamengesteldInformatieobjectObject(Object):
#     """
#     De aan het RGBZ ontleende gegevens van een SAMENGESTELD INFORMATIEOBJECT die in het
#     RGBZ gebruikt worden bij deze specialisatie van OBJECT. Zie voor de specificaties van deze
#     gegevens het RGBZ.
#     """
#     # TODO: staat wel in rgbz, maar we hebben al 'identificatie'
#     # informatieobjectidentificatie = models.CharField(
#     #     max_length=40, help_text='Een binnen een gegeven context ondubbelzinnige referentie naar het INFORMATIEOBJECT.')
#     informatieobjectcreatiedatum = StUFDateField(
#         help_text='Een datum of een gebeurtenis in de levenscyclus van het INFORMATIEOBJECT.')
#
#     # Verplicht te registreren voor INFORMATIEOBJECTen die van buiten de zaakbehandelende organisatie(s) ontvangen zijn
#     informatieobjectontvangstdatum = StUFDateField(
#         null=True, blank=True, help_text='De datum waarop het INFORMATIEOBJECT ontvangen is.')
#
#     informatieobjecttitel = models.CharField(
#         max_length=200, null=True, blank=True, help_text='De naam waaronder het INFORMATIEOBJECT formeel bekend is.')
#     informatieobjecttypeomschrijving = models.CharField(max_length=80)
#     informatieobjecttypeomschrijving_generiek = models.ForeignKey(
#         'rgbz.InformatieObjectTypeOmschrijvingGeneriek', null=True, blank=True)
#
#     class Meta:
#         mnemonic = 'SDC'
#
#     @property
#     def informatieobjectidentificatie(self):
#         return self.identificatie
#
#
# class StatusObject(Object):
#     """
#     De aan het RGBZ ontleende gegevens van een STATUS die in het RGBZ gebruikt worden bij
#     deze specialisatie van OBJECT. Zie voor de specificaties van deze gegevens het RGBZ.
#     """
#     datum_status_gezet = StUFDateTimeField(
#         help_text='De datum waarop de ZAAK de status heeft verkregen.'
#     )
#     zaakidentificatie = models.CharField(max_length=40, unique=True,
#                                          help_text='De unieke identificatie van de ZAAK binnen de organisatie die '
#                                                    'verantwoordelijk is voor de behandeling van de ZAAK.')
#     statustypeomschrijving = models.CharField(
#         max_length=80, help_text='Een korte, voor de initiator van de zaak relevante, '
#                                  'omschrijving van de aard van de STATUS van zaken van een ZAAKTYPE.')
#     statustypevolgnummer = models.PositiveSmallIntegerField(
#         help_text='Een volgnummer voor statussen van het STATUSTYPE binnen een zaak.',
#         validators=[MaxValueValidator(9999)]
#     )
#
#     class Meta:
#         mnemonic = 'STA'
#
#
# class VestigingObject(Object):
#     """
#     De aan het RSGB ontleende gegevens van een VESTIGING die in het RGBZ gebruikt worden bij
#     deze specialisatie van OBJECT. Zie voor de specificaties van deze gegevens het RSGB.
#     """
#     vestigingsnummer = models.CharField(
#         max_length=12, help_text='Landelijk uniek identificerend administratienummer van een VESTIGING zoals toegewezen'
#                                  'door de Kamer van Koophandel (KvK).')
#     handelsnaam = models.TextField(
#         max_length=625, help_text='De naam van de vestiging waaronder gehandeld wordt.')
#     datum_aanvang = StUFDateField(
#         help_text='De datum van aanvang van de vestiging.'
#     )
#     datum_beeindiging = StUFDateField(
#         null=True, blank=True, help_text='De datum van beëindiging van de vestiging')
#     verblijf_buitenland = models.ForeignKey('rsgb.VerblijfBuitenland', null=True, blank=True, related_name='verblijfbuitenland')
#     correspondentieadres = models.ForeignKey('rsgb.BasisAdres', on_delete=models.SET_NULL, null=True, blank=True,
#                                              related_name='correspondentieadres')
#
#     class Meta:
#         mnemonic = 'VES'
