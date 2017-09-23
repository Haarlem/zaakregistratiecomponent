from django.db import models


class BereikenMixin(models.Model):
    """
    Een mixin voor alle klasses welke Contact informatie gebruiken, wat bijna altijd tenminste een telefoonnummer,
    emaildres & faxnummer inhoudt.
    """
    telefoonnummer = models.CharField(
        max_length=20, null=True, blank=True, help_text='Telefoonnummer waaronder de MEDEWERKER in de regel bereikbaar is.')
    emailadres = models.EmailField(
        null=True, blank=True, max_length=254, help_text='Elektronisch postadres waaronder het subject in de regel bereikbaar is.')
    faxnummer = models.CharField(
        max_length=20, null=True, blank=True, help_text='Faxnummer waaronder het subject in de regel bereikbaar is.')

    class Meta:
        abstract = True
