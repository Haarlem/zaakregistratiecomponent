from django.apps import AppConfig


class UtilsConfig(AppConfig):
    name = 'zaakmagazijn.utils'

    def ready(self):
        from . import checks  # noqa
