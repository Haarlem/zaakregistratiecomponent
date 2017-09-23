from django.views.decorators.csrf import csrf_exempt

from spyne.server.django import DjangoApplication

from .applications import (
    beantwoordvraag_app, ontvangasynchroon_app,
    verwerksynchroonvrijbericht_app
)

beantwoordvraag_view = csrf_exempt(DjangoApplication(beantwoordvraag_app))
verwerksynchroonvrijbericht_view = csrf_exempt(DjangoApplication(verwerksynchroonvrijbericht_app))
ontvangasynchroon_view = csrf_exempt(DjangoApplication(ontvangasynchroon_app))
