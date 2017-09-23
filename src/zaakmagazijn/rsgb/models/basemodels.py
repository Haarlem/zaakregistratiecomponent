from django.core.validators import MaxValueValidator
from django.db import models


class KadastraleAanduidingBaseClass(models.Model):
    kadastralegemeentecode = models.CharField(max_length=5)  # AKR, Drie letters en twee cijfers
    perceelnummer = models.PositiveIntegerField(validators=[MaxValueValidator(99999)])
    sectie = models.CharField(max_length=2)

    class Meta:
        abstract = True


class AdresBaseClass(models.Model):
    """
    (bijna) altijd voorkomende velden in Adres specialisaties
    Dit dient gebruikt te worden als basis voor Adres gerelateerde GroepsAttribuutSoorten indien deze velden hiervoor
    relevant zijn
    """
    woonplaatsnaam = models.CharField(max_length=80)
    naam_openbare_ruimte = models.CharField(
        max_length=80, help_text='Een door het bevoegde gemeentelijke orgaan aan een '
                                 'OPENBARE RUIMTE toegekende benaming')
    huisletter = models.CharField(max_length=1, null=True, blank=True)
    huisnummer = models.PositiveIntegerField(validators=[MaxValueValidator(99999)])
    huisnummertoevoeging = models.CharField(max_length=4, null=True, blank=True)

    class Meta:
        abstract = True
