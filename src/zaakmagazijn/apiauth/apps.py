# -*- coding: utf-8 -*-
from django.apps import AppConfig
from django.db.models.signals import post_migrate

from .signals import update_service_operations


class ApiAuthConfig(AppConfig):
    name = 'zaakmagazijn.apiauth'
    verbose_name = "Authentication"

    def ready(self):
        post_migrate.connect(update_service_operations, sender=self)
