from django.conf.urls import url
from django.urls import reverse_lazy
from django.views.generic import RedirectView

from .views import (
    beantwoordvraag_view, ontvangasynchroon_view,
    verwerksynchroonvrijbericht_view
)

urlpatterns = [
    url(r'Beantwoordvraag', RedirectView.as_view(
        url=reverse_lazy('beantwoordvraag'), permanent=True), name='beantwoordvraag-deprecated'),
    url(r'BeantwoordVraag', beantwoordvraag_view, name='beantwoordvraag'),
    url(r'VerwerkSynchroonVrijBericht', verwerksynchroonvrijbericht_view, name='verwerksynchroonvrijbericht'),
    url(r'OntvangAsynchroon', ontvangasynchroon_view, name='ontvangasynchroon'),
]
