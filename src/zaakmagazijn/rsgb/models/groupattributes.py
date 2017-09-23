from django.core.validators import MaxValueValidator
from django.db import models

from ...rsgb.models.basemodels import (
    AdresBaseClass, KadastraleAanduidingBaseClass
)
from ..choices import PostadresType


class AdresMetPostcode(AdresBaseClass):
    """
    AdresBaseClass Specialisatie voor GroepsAttribuutSoorten met een Postcode
    """
    postcode = models.CharField(max_length=7, null=True, blank=True)


class Correspondentieadres(AdresMetPostcode):
    straatnaam = models.CharField(
        max_length=24, help_text='De officiële straatnaam zoals door het bevoegd gemeentelijk orgaan is vastgesteld, '
                                 'zo nodig ingekort conform de specificaties van de NEN 5825.'
    )


class Bezoekadres(Correspondentieadres):
    pass


class Locatieadres(Correspondentieadres):
    pass


class Adres(AdresBaseClass):
    """

    """
    identificatie = models.CharField(max_length=4)
    # authentiek =


class BasisAdres(AdresBaseClass):

    class Meta:
        abstract = False


class VerblijfAdres(AdresBaseClass):
    """
    AdresMetPostcode specialisatie voor GroepsAttribuutSoorten met een locatie_beschrijving
    """
    straatnaam = models.CharField(
        max_length=24, help_text='De officiële straatnaam zoals door het bevoegd gemeentelijk orgaan is vastgesteld, '
                                 'zo nodig ingekort conform de specificaties van de NEN 5825.'
    )
    postcode = models.CharField(max_length=7, null=True, blank=True)
    locatie_beschrijving = models.CharField(
        max_length=35, null=True, blank=True,
        help_text='Een geheel of gedeeltelijke omschrijving van de ligging van een object.')


class PostAdres(models.Model):
    """
    Datamodel afwijking; Dit is een representatie van het GroepsAttribuutSoort 'PostAdres'
    """
    postadres_postcode = models.CharField(
        max_length=7)
    postadrestype = models.CharField(
        max_length=1, choices=PostadresType.choices)
    postbus_of_antwoordnummer = models.CharField(
        max_length=5)
    woonplaatsnaam = models.CharField(
        max_length=80
    )


class VerblijfBuitenland(models.Model):
    """
        Datamodel afwijking, model representatie van de Groepattribuutsoort 'Verblijf buitenland'
    """
    adres_buitenland_1 = models.CharField(
        max_length=35, null=True, blank=True
    )
    adres_buitenland_2 = models.CharField(
        max_length=35, null=True, blank=True
    )
    adres_buitenland_3 = models.CharField(
        max_length=35, null=True, blank=True
    )
    land = models.ForeignKey('rsgb.LandGebied', on_delete=models.CASCADE)


class KadastraleAanduiding(KadastraleAanduidingBaseClass):
    """
    De typering van de kadastrale aanduiding van een onroerende zaak
    conform Kadaster.
    """
    appartementsrechtvolgnummer = models.PositiveSmallIntegerField(validators=[MaxValueValidator(9999)])


class KadastraleAanduidingAppartementsRecht(KadastraleAanduidingBaseClass):
    # TODO: [KING] Schatting, waarde stond niet gedefineerd in RSGB 3.0
    appartementsrecht = models.PositiveIntegerField()


class KadastraleAanduidingKadastraalPerceel(KadastraleAanduidingBaseClass):
    # TODO: [KING] Schatting, waarde stond niet gedefineerd in RSGB 3.0
    deelperceelnummer = models.PositiveIntegerField()


class NaamAanschrijving(models.Model):
    """
    Informatiemodel afwijking; Model representatie van het GroepAttribuutsoort 'Naam Aanschrijving'
    """
    voorletters_aanschrijving = models.CharField(
        max_length=20, null=True, blank=True,
        help_text='De voorletters waarmee een persoon aangeschreven wil worden.')
    voornamen_aanschrijving = models.CharField(
        max_length=200, null=True, blank=True,
        help_text='Voornamen bij de naam die de persoon wenst te voeren.'
    )
    geslachtsnaam_aanschrijving = models.CharField(
        max_length=200, help_text='Geslachtsnaam die de persoon wenst te voeren'
    )
    aanhef_aanschrijving = models.CharField(
        max_length=50, help_text='De aanhef waarmee de persoon aangeschreven wil worden.'
    )
