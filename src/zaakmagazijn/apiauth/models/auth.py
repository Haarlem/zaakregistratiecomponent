# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _

from ..choices import EndpointTypeChoices


class ServiceOperation(models.Model):
    name = models.CharField(_('naam'), max_length=150)
    namespace = models.CharField(_('namespace'), max_length=250)
    operation_name = models.CharField(_('functienaam'), max_length=150, unique=True)

    class Meta:
        verbose_name = _('service functie')
        verbose_name_plural = _('service functies')
        ordering = ('name', )

    def __str__(self):
        return self.name


class ApplicationGroup(models.Model):
    name = models.CharField(_('naam'), max_length=150, unique=True)
    service_operations = models.ManyToManyField('apiauth.ServiceOperation', verbose_name=_('service functies'))

    class Meta:
        verbose_name = _('applicatie groep')
        verbose_name_plural = _('applicatie groepen')
        ordering = ('name', )

    def __str__(self):
        return self.name


class ApplicationManager(models.Manager):
    def can_access(self, application, operation_name):
        user = self.model.objects.get(name=application)
        if user and user.can_access(operation_name):
            return True

        return False


class Organisation(models.Model):
    name = models.CharField(_('naam'), max_length=200, unique=True)
    description = models.CharField(_('omschrijving'), max_length=250, blank=True)

    class Meta:
        verbose_name = _('organisatie')
        verbose_name_plural = _('organisaties')
        ordering = ('name', )

    def __str__(self):
        return self.name


class Application(models.Model):
    name = models.CharField(_('naam'), max_length=50, unique=True)
    description = models.CharField(_('omschrijving'), max_length=250, blank=True)

    organisation = models.ForeignKey('apiauth.Organisation', null=True, blank=True, verbose_name=_('organisatie'))
    groups = models.ManyToManyField('apiauth.ApplicationGroup', verbose_name=_('groepen'), blank=True)

    objects = ApplicationManager()

    class Meta:
        verbose_name = _('applicatie')
        verbose_name_plural = _('applicaties')
        ordering = ('name', )

    def zender_as_dict(self):
        return {
            'organisatie': self.organisation.name if self.organisation else '',
            'applicatie': self.name,
            'administratie': '',
            'gebruiker': '',
        }

    def __str__(self):
        return self.name

    def can_access(self, operation_name):
        return self.groups.filter(service_operations__operation_name=operation_name).exists()


class Endpoint(models.Model):
    application = models.ForeignKey('apiauth.Application')
    type = models.CharField(_('type'), max_length=50, choices=EndpointTypeChoices.choices)
    url = models.CharField(_('url'), max_length=250)

    def __str__(self):
        return self.type

    class Meta:
        verbose_name = _('endpoint')
        verbose_name_plural = _('endpoints')
