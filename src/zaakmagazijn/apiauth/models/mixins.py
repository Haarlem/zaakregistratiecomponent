from django.db import models


class StufObjectHistorieMixin(models.Model):
    tijdstip_registratie = models.DateTimeField(auto_now=True)
    tijdvak_geldigheid_begin_van_geldigheid = models.DateTimeField(null=True)
    tijdvak_geldigheid_eind_van_geldigheid = models.DateTimeField(null=True)

    class Meta:
        abstract = True

    def get_entitity(self):
        return


class StufRelatieHistorieMixin(models.Model):
    tijdvak_relatie_begin_relatie = models.DateTimeField(null=True)
    tijdvak_relatie_eind_relatie = models.DateTimeField(null=True)

    class Meta:
        abstract = True

    def get_entitity(self):
        return


class ZenderMixin(models.Model):
    zender_organisatie = models.CharField(max_length=50, blank=True)
    zender_applicatie = models.CharField(max_length=50)
    zender_administratie = models.CharField(max_length=200, blank=True)
    zender_gebruiker = models.CharField(max_length=100, blank=True)

    class Meta:
        abstract = True

    def zender_as_dict(self):
        return {
            'organisatie': self.zender_organisatie,
            'applicatie': self.zender_applicatie,
            'administratie': self.zender_administratie,
            'gebruiker': self.zender_gebruiker,
        }
