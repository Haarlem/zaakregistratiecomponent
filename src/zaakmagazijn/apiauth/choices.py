from django.utils.translation import ugettext_lazy as _

from djchoices import ChoiceItem, DjangoChoices


class EndpointTypeChoices(DjangoChoices):
    beantwoord_vraag = ChoiceItem('beantwoordVraag', _('beantwoordVraag'))
    ontvang_asynchroon = ChoiceItem('OntvangAsynchroon', _('OntvangAsynchroon'))
    verwerk_synchroon_vrij_bericht = ChoiceItem('VerwerkSynchroonVrijBericht', _('VerwerkSynchroonVrijBericht'))
