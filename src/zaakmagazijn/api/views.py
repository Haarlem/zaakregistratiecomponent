
import os.path

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from spyne.server.django import DjangoApplication as _DjangoApplication

from .applications import (
    beantwoordvraag_app, ontvangasynchroon_app,
    verwerksynchroonvrijbericht_app
)
from .rewrite_engine import RewriteEngine
from .utils import rewrite_wsdl


class DjangoApplication(_DjangoApplication):
    def __init__(self, *args, **kwargs):
        self.wsdl_filename = kwargs.pop('wsdl_filename')
        kwargs['max_content_length'] = settings.ZAAKMAGAZIJN_MAX_CONTENT_LENGTH
        super().__init__(*args, **kwargs)

    def __call__(self, request):
        environ = request.META.copy()

        if self.is_wsdl_request(environ):
            if settings.ZAAKMAGAZIJN_REFERENCE_WSDL:
                wsdl_path = os.path.join(settings.ZAAKMAGAZIJN_ZDS_PATH, self.wsdl_filename)
                with open(wsdl_path, 'rb') as wsdl:
                    content = rewrite_wsdl(wsdl.read(), settings.ZAAKMAGAZIJN_ZDS_URL, settings.ZAAKMAGAZIJN_URL)
                return HttpResponse(content, content_type='text/xml; charset=utf-8')
        return super().__call__(request)


beantwoordvraag_view = csrf_exempt(RewriteEngine.rewrite(DjangoApplication(beantwoordvraag_app, wsdl_filename='zds0120_beantwoordVraag_zs-dms.wsdl')))
verwerksynchroonvrijbericht_view = csrf_exempt(RewriteEngine.rewrite(DjangoApplication(verwerksynchroonvrijbericht_app, wsdl_filename='zds0120_vrijeBerichten_zs-dms.wsdl')))
ontvangasynchroon_view = csrf_exempt(RewriteEngine.rewrite(DjangoApplication(ontvangasynchroon_app, wsdl_filename='zds0120_ontvangAsynchroon_mutatie_zs-dms.wsdl')))
