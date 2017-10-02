from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from spyne.server.django import DjangoApplication as _DjangoApplication

from .applications import (
    beantwoordvraag_app, ontvangasynchroon_app,
    verwerksynchroonvrijbericht_app
)


class DjangoApplication(_DjangoApplication):
    def __init__(self, *args, **kwargs):
        kwargs['max_content_length'] = settings.ZAAKMAGAZIJN_MAX_CONTENT_LENGTH
        super().__init__(*args, **kwargs)


beantwoordvraag_view = csrf_exempt(DjangoApplication(beantwoordvraag_app))
verwerksynchroonvrijbericht_view = csrf_exempt(DjangoApplication(verwerksynchroonvrijbericht_app))
ontvangasynchroon_view = csrf_exempt(DjangoApplication(ontvangasynchroon_app))
