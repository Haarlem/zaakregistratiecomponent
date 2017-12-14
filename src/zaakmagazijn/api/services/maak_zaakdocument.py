from django.db import transaction

from spyne import ServiceBase, rpc

from ...cmis.client import default_client as dms_client
from ...rgbz.models import EnkelvoudigInformatieObject, Zaak
from ..stuf.models import BinaireInhoud, Bv03Bericht  # , TijdvakGeldigheid
from ..stuf.utils import get_bv03_stuurgegevens
from ..zds import Lk01Builder
from ..zds.kennisgevingsberichten import process_create
from .voeg_zaakdocument_toe import EnkelvoudigDocumentEntiteit

input_builder = Lk01Builder(EnkelvoudigDocumentEntiteit, 'MaakZaakdocument')


class MaakZaakdocument(ServiceBase):
    """
    De "maak Zaakdocument"-service biedt DSC's de mogelijkheid om een container
    (of placeholder) aan te maken voor een nieuw DOCUMENT. Het ZS maakt gebruik
    van de CMIS-documentservices het DMS te synchroniseren.
    """
    input_model = input_builder.create_model()

    @rpc(input_model, _body_style="bare", _out_message_name="{http://www.egem.nl/StUF/StUF0301}Bv03Bericht", _returns=Bv03Bericht)
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
            process_create(EnkelvoudigDocumentEntiteit, data)

            # determineer de afzender
            zender = data.stuurgegevens.zender
            created_by = zender.gebruiker or zender.administratie or zender.applicatie or zender.organisatie or None

            # maak leeg document aan
            document = EnkelvoudigInformatieObject.objects.get(informatieobjectidentificatie=data.object.identificatie)

            inhoud = data.object.inhoud

            dms_client.maak_zaakdocument(
                document,
                filename=inhoud.bestandsnaam if inhoud else None,
                sender=created_by,
            )

            # relateer document aan juiste zaak folder
            zaak = Zaak.objects.get(zaakidentificatie=data.object.isRelevantVoor[0].gerelateerde.identificatie)
            dms_client.relateer_aan_zaak(document, zaak)

        return {
            'stuurgegevens': get_bv03_stuurgegevens(data),
        }
