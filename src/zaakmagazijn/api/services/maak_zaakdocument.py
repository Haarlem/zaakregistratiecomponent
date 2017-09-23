from django.conf import settings
from django.db import transaction

from spyne import ServiceBase, rpc

from ...cmis.client import default_client as dms_client
from ...rgbz.models import EnkelvoudigInformatieObject, Zaak
from ...utils import stuf_datetime
from ..stuf.choices import BerichtcodeChoices
from ..stuf.models import BinaireInhoud, Bv03Bericht  # , TijdvakGeldigheid
from ..utils import create_unique_id
from ..zds import Lk01Builder
from ..zds.kennisgevingsberichten import process_create
from .voeg_zaakdocument_toe import InformatieObjectEntiteit

input_builder = Lk01Builder(InformatieObjectEntiteit, 'MaakZaakdocument')


class MaakZaakdocument(ServiceBase):
    """
    De "maak Zaakdocument"-service biedt DSC's de mogelijkheid om een container
    (of placeholder) aan te maken voor een nieuw DOCUMENT. Het ZS maakt gebruik
    van de CMIS-documentservices het DMS te synchroniseren.
    """
    input_model = input_builder.create_model()

    @rpc(input_model, _body_style="bare", _out_message_name="Bv03Bericht", _returns=Bv03Bericht)
    def maakZaakdocument_EdcLk01(ctx, data):
        """
        Er wordt gestart met het aanmaken van een document dat relevant is
        voor een lopende zaak.
        """

        # Eisen aan ZS
        #
        # * Het ZS verwerkt alle berichten asynchroon en direct
        #   ("near realtime");
        # * Het ZS controleert of de aangeleverde documentidentificatie uniek
        #   en geldig is (volgens RGBZ);

        # Interactie tussen ZS en DMS
        #
        # Het ZS zorgt ervoor dat in het DMS een EDC-object wordt aangemaakt
        # zonder binaire inhoud. Hiervoor maakt het ZS gebruik van de
        # CMIS-services die aangeboden worden door het DMS. Hierbij gelden de
        # volgende eisen:
        #
        # * Er wordt een object aangemaakt van het objecttype EDC (Zie 5.1);
        # * Het EDC-object wordt gerelateerd aan de juiste Zaakfolder
        #   (Zie 5.1);
        # * Tenminste de minimaal vereiste metadata voor een EDC wordt
        #   vastgelegd in de daarvoor gedefinieerde objectproperties. In
        #   Tabel 3 is een mapping aangegeven tussen de StUF-ZKN-elementen en
        #   CMIS-objectproperties.

        with transaction.atomic():
            if data.object.inhoud is None:  # trigger ZS-DMS interaction
                data.object.inhoud = BinaireInhoud()

            # geen binaire inhoud toegelaten -> maak leeg indien wel meegestuurd
            data.object.inhoud.data = None

            process_create(InformatieObjectEntiteit, data)

            # relateer document aan juiste zaak folder
            document = EnkelvoudigInformatieObject.objects.get(informatieobjectidentificatie=data.object.identificatie)
            zaak = Zaak.objects.get(zaakidentificatie=data.object.isRelevantVoor[0].gerelateerde.identificatie)
            dms_client.relateer_aan_zaak(document, zaak)

        return {
            'stuurgegevens': {
                'berichtcode': BerichtcodeChoices.bv03,
                'zender': settings.ZAAKMAGAZIJN_SYSTEEM,
                'ontvanger': data.stuurgegevens.zender,
                'referentienummer': create_unique_id(),
                'tijdstipBericht': stuf_datetime.now()
            },
        }
