from django.conf.urls import url

from .views import (
    beantwoordvraag_view, ontvangasynchroon_view,
    verwerksynchroonvrijbericht_view
)

urlpatterns = [
    url(r'Beantwoordvraag', beantwoordvraag_view, name='beantwoordvraag'),
    url(r'VerwerkSynchroonVrijBericht', verwerksynchroonvrijbericht_view, name='verwerksynchroonvrijbericht'),
    url(r'OntvangAsynchroon', ontvangasynchroon_view, name='ontvangasynchroon'),
]
