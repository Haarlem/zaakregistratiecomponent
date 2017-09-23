from django.conf import settings

from spyne import ComplexModel, ServiceBase, Unicode, rpc

from zaakmagazijn.cmis.client import default_client as dms_client
from zaakmagazijn.cmis.exceptions import DocumentConflictException
from zaakmagazijn.rgbz.models import EnkelvoudigInformatieObject

from ...utils import stuf_datetime
from ..stuf import attributes, simple_types
from ..stuf.base import ComplexModelBuilder, complex_model_factory
from ..stuf.choices import BerichtcodeChoices, ServerFoutChoices
from ..stuf.constants import STUF_XML_NS, ZDS_XML_NS
from ..stuf.faults import StUFFault
from ..stuf.models import Bv02Bericht, Systeem
from ..utils import create_unique_id
from ..zds import Lk02Builder
from ..zds.kennisgevingsberichten import process_update
from .voeg_zaakdocument_toe import InformatieObjectEntiteit

input_builder_edc_lk02 = Lk02Builder(InformatieObjectEntiteit, 'updateZaakdocument', update=True)


class Di02_Stuurgegevens_uzd(ComplexModel):
    __namespace__ = STUF_XML_NS
    __type_name__ = 'Di02_Stuurgegevens_uzd'
    _type_info = (
        ('berichtcode', simple_types.Berichtcode.customize(fixed=BerichtcodeChoices.di02)),
        ('zender', Systeem),
        ('ontvanger', Systeem),
        ('referentienummer', simple_types.Refnummer),
        ('tijdstipBericht', simple_types.Tijdstip),
        ('functie', simple_types.Functie),
    )


# Vrij bericht met ZDS namespace ipv ZKN
class UpdateZaakdocumentInputBuilder(ComplexModelBuilder):
    berichtcode = BerichtcodeChoices.di02

    def __init__(self, name: str, shortname: str):
        self.name = name
        self.shortname = shortname

    def create_parameters_model(self):
        name = '{}_Parameters_{}'.format(self.berichtcode, self.shortname)
        type_info = (
            ('checkedOutId', Unicode),
            ('versioningState', Unicode),
        )
        return self.create_reusable_model(name, ZDS_XML_NS, type_info)

    def create_model(self):
        edc_lk02 = input_builder_edc_lk02.create_model()
        edc_lk02._type_info['entiteittype'] = attributes.entiteittype
        edc_lk02._type_info['functie'] = attributes.functie
        type_info = (
            ('stuurgegevens', Di02_Stuurgegevens_uzd),
            ('parameters', self.create_parameters_model()),
            ('edcLk02', edc_lk02),
        )
        type_name = '{}_{}'.format(self.name, self.berichtcode)
        return complex_model_factory(type_name, ZDS_XML_NS, type_info)


input_builder = UpdateZaakdocumentInputBuilder('updateZaakdocument', 'uzd')


class UpdateZaakdocument(ServiceBase):
    """
    De "Update Zaakdocument"-service biedt DSC's de mogelijkheid om de fysieke
    inhoud aan een container toe te voegen (zie ook #10). Daarnaast kunnen ook
    attributen van een DOCUMENT worden gemuteerd of toegevoegd. Het ZS maakt
    gebruik van de CMIS-documentservices om de wijzigingen in het DMS te
    synchroniseren.

    Zie: ZDS 1.2, paragraaf 4.3.6
    """
    input_model = input_builder.create_model()

    @rpc(input_model, _body_style="bare", _out_message_name="updateZaakdocument_Du02", _returns=Bv02Bericht)
    def updateZaakdocument_Di02(ctx, data):
        """
        Een document dat relevant is voor een lopende zaak is gewijzigd.
        """

        # Eisen aan ZS
        #
        # Er zijn geen aanvullende aan het ZS

        # Interactie tussen DSC en ZS
        #
        # Het updateZaakdocument_Di02 bericht is een vrij bericht. Het in het
        # bericht aanwezige object dient volgens de StUF regels zowel de oude
        # als de nieuwe situatie te bevatten.

        # Interactie tussen ZS en DMS
        #
        # Het ZS zorgt ervoor dat in het DMS het EDC-object wordt bijgewerkt
        # met de door de documentserviceconsumser aangeleverde
        # documentidentificatie. Hiervoor maakt het ZS gebruik van de
        # CMIS-services die aangeboden worden door het DMS. De volgende eisen
        # gelden:
        #
        # * Alle door de serviceconsumer aangeleverde attributen worden
        #   gemuteerd bij het object met juiste documentidentificatie;
        # * Er wordt rekening gehouden met de regels voor minimaal vereiste
        #   metadata bij een EDC.
        process_update(InformatieObjectEntiteit, data.edcLk02)
        identificatie = data.edcLk02.object[0].identificatie
        inhoud = data.edcLk02.object[0].inhoud

        document = EnkelvoudigInformatieObject.objects.get(informatieobjectidentificatie=identificatie)
        try:
            dms_client.update_zaakdocument(document, data.parameters.checkedOutId, inhoud)
        except DocumentConflictException as exc:
            raise StUFFault(
                ServerFoutChoices.stuf058,
                "Missende of foutieve checkout ID"
            ) from exc

        return {
            'stuurgegevens': {
                'berichtcode': BerichtcodeChoices.bv02,
                'zender': settings.ZAAKMAGAZIJN_SYSTEEM,
                'ontvanger': data.stuurgegevens.zender,
                'referentienummer': create_unique_id(),
                'tijdstipBericht': stuf_datetime.now()
            },
        }
