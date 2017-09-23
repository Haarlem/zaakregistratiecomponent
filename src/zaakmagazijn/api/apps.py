from django.apps import AppConfig
from django.conf import settings
from django.core.checks import Error, Tags, register

from zaakmagazijn.rgbz.choices import Rolomschrijving, RolomschrijvingGeneriek


class ApiConfig(AppConfig):
    name = 'zaakmagazijn.api'
    verbose_name = "API"

    def ready(self):
        register(check_gemeente_code, Tags.compatibility)
        register(check_rolomschrijvingen, Tags.compatibility)


def check_gemeente_code(app_configs, **kwargs):
    errors = []

    from django.conf import settings
    gemeente_code = getattr(settings, 'ZAAKMAGAZIJN_GEMEENTE_CODE', None)
    if gemeente_code is None:
        errors.append(
            Error(
                'Setting ZAAKMAGAZIJN_GEMEENTE_CODE should be set.',
                obj=settings
            )
        )
    elif len(gemeente_code) != 4:
        errors.append(
            Error(
                'Setting ZAAKMAGAZIJN_GEMEENTE_CODE ("{}") should be 4 characters.'.format(gemeente_code),
                obj=settings
            )
        )

    return errors


def check_rolomschrijvingen(app_configs, **kwargs):
    errors = []
    missing = set(Rolomschrijving.values.keys()) - set(settings.ZAAKMAGAZIJN_ROLOMSCHRIJVINGEN.keys())
    errors += [
        Error(
            'An entry for rol: {} is missing from setting \'ZAAKMAGAZIJN_ROLOMSCHRIJVINGEN\''.format(m),
            obj=settings
        ) for m in missing]
    extra = set(settings.ZAAKMAGAZIJN_ROLOMSCHRIJVINGEN.keys()) - set(Rolomschrijving.values.keys())
    errors += [
        Error(
            'An entry for rol: {} is set in the setting \'ZAAKMAGAZIJN_ROLOMSCHRIJVINGEN\' while it is not a valid rol from Rolomschrijving'.format(e),
            obj=settings
        ) for e in extra]

    errors = []
    for rol_setting in settings.ZAAKMAGAZIJN_ROLOMSCHRIJVINGEN.values():
        if set(rol_setting.keys()) != {'generiek', 'toelichting'} or \
                rol_setting.get('generiek') not in RolomschrijvingGeneriek.values.keys() or \
                not isinstance(rol_setting.get('toelichting'), str):
            errors.append(Error('The following syntax should be used in ZAAKMAGAZIJN_ROLOMSCHRIJVINGEN: {Rolomschrijving.adviseur: {\'generiek\': RolomschrijvingGeneriek.initiator, \'toelichting\': \'Aanleiding geven tot de start van een zaak\'}, ... etc},'))

    return errors
