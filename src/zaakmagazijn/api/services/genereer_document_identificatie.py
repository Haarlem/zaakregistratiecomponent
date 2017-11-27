from spyne import ComplexModel, ServiceBase, rpc

from ...rgbz.models import EnkelvoudigInformatieObject
from ..stuf.constants import STUF_XML_NS
from ..stuf.models import ExtraElementen
from ..utils import create_unique_id
from ..zds.vrijeberichten import (
    GenereerIdentificatieInputBuilder, GenereerIdentificatieOutputBuilder
)

input_builder = GenereerIdentificatieInputBuilder('genereerDocumentidentificatie', 'gdi')
output_builder = GenereerIdentificatieOutputBuilder('genereerDocumentidentificatie', 'gdi', 'document', 'EDC')


class Parameters(ComplexModel):
    __namespace__ = STUF_XML_NS
    __type_name__ = 'ParametersVraag_gdi'
    _type_info = (
        ('extraElementen', ExtraElementen.customize(ref='extraElementen')),
    )


class GenereerDocumentIdentificatie(ServiceBase):
    """
    De "genereer Documentidentificatie"-service biedt DSC's de mogelijkheid om
    een uniek en geldige Documentidentificatie op te halen. De DSC stuurt
    hiervoor een vrij bericht naar het ZS en ontvangt synchroon als reactie een
    geldige Documentidentificatie.

    Zie: ZDS 1.2, paragraaf 4.3.7
    """
    input_model = input_builder.create_model(parameters=Parameters.customize(min_occurs=0))
    output_model = output_builder.create_model()

    @rpc(input_model, _body_style="bare", _out_message_name="genereerDocumentIdentificatie_Du02", _returns=output_model)
    def genereerDocumentIdentificatie_Di02(ctx, data):

        # Eisen aan ZS:
        #
        # * De uitgegeven Documentidentificatie wordt gereserveerd en wordt
        #   eenmalig uitgegeven;
        # * De uitgegeven Documentidentificatie is uniek binnen de gemeente;
        # * Er wordt direct (synchroon) een Documentidentificatie
        #   teruggestuurd.

        # Interactie tussen DSC en ZS:
        #
        # De interactie tussen DSC en ZS is gebaseerd op vrije berichten. Het
        # inkomende bericht (genereerDocumentIdentificatie_Di02) heeft naast de
        # stuurgegevens geen verplichte elementen. Wel dient het stuurgegeven
        # "functie" de waarde "genereerDocumentidentificatie" te hebben.
        #
        # In het genereerDocumentIdentificatie_Di02 mogen extra gegevens
        # meegestuurd worden middels extraElementen in de parameters.
        #
        # De serviceprovider dient als reactie op het inkomende bericht met
        # functie "genereerDocumentidentificatie" te antwoorden met een vrij
        # bericht (Du02). Ook in dit bericht is het stuurgegeven "functie"
        # gevuld met de waarde "genereerDocumentidentificatie". Na de
        # stuurgegevens volgt een element document met attribuut
        # StUF:entiteittype="EDC". Binnen document is één verplicht element
        # opgenomen namelijk de Documentidentificatie.

        # Find an unused uuid. Hopefully this does never go trough more than 1 iteration.
        while True:
            informatieobjectidentificatie = create_unique_id()
            if not EnkelvoudigInformatieObject.objects.filter(informatieobjectidentificatie=informatieobjectidentificatie).exists():
                break

        return output_builder.create_data(data, informatieobjectidentificatie)
