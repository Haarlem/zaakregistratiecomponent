from spyne import ServiceBase, Unicode, rpc

from zaakmagazijn.cmis.client import default_client as dms_client

from ..stuf import simple_types
from ..stuf.attributes import entiteittype, functie, verwerkingssoort
from ..stuf.base import ComplexModelBuilder, complex_model_factory
from ..stuf.choices import BerichtcodeChoices
from ..stuf.constants import STUF_XML_NS, ZDS_XML_NS, ZKN_XML_NS
from ..stuf.models import Systeem
from ..utils import get_enkelvoudig_informatie_object_or_fault


class CancelCheckoutOutputBuilder(ComplexModelBuilder):
    berichtcode = BerichtcodeChoices.bv02

    def __init__(self, name, shortname, object_element_name, entiteittype):
        self.name = name
        self.shortname = shortname

        self.object_element_name = object_element_name
        self.entiteittype = entiteittype

    def create_stuurgegevens_model(self):
        type_info = (
            ('berichtcode', Unicode.customize(sub_ns=STUF_XML_NS, pattern=self.berichtcode)),
        )
        stuurgegevens_model = complex_model_factory('{}_Stuurgegevens_{}'.format(
            self.berichtcode, self.shortname), STUF_XML_NS, type_info)
        return stuurgegevens_model

    def create_model(self):
        type_name = '{}_{}'.format(self.name, self.berichtcode)
        type_info = (
            ('stuurgegevens', self.create_stuurgegevens_model()),
        )
        body_model = complex_model_factory(type_name, STUF_XML_NS, type_info)
        return body_model

    def create_data(self):
        return {
            'stuurgegevens': {
                'berichtcode': self.berichtcode,
            },
        }


class CancelCheckoutInputBuilder(ComplexModelBuilder):
    berichtcode = BerichtcodeChoices.di02

    def __init__(self, name, shortname):
        self.name = name
        self.shortname = shortname

    def create_stuurgegevens_model(self):
        type_info = (
            ('berichtcode', Unicode.customize(
                type_name='BerichtcodeDi02', sub_ns=STUF_XML_NS,
                pattern=self.berichtcode
            )),
            ('zender', Systeem),
            ('ontvanger', Systeem),
            ('referentienummer', simple_types.Refnummer.customize(min_occurs=0)),
            ('tijdstipBericht', simple_types.Tijdstip.customize(min_occurs=0)),
            ('functie', simple_types.Functie),
        )
        stuurgegevens_model = complex_model_factory('{}_Stuurgegevens_{}'.format(
            self.berichtcode, self.shortname), STUF_XML_NS, type_info)
        return stuurgegevens_model

    def create_parameters_model(self):
        type_info = (
            ('checkedOutId', Unicode.customize(type_name='checkedOutId')),
            # ('versioningState', Unicode.customize(type_name='versioningState', min_occurs=0))
        )
        parameters_model = complex_model_factory('{}_Parameters_{}'.format(
            self.berichtcode, self.shortname), ZDS_XML_NS, type_info)
        return parameters_model

    def create_document_model(self):
        type_info = (
            ('identificatie', Unicode.customize(min_occurs=1, max_occurs=1, nillable=False)),
            ('functie', functie),
            ('entiteittype', entiteittype),
            ('verwerkingssoort', verwerkingssoort)
        )
        document_model = complex_model_factory('EDC_cc_e', ZKN_XML_NS, type_info)
        return document_model

    def create_model(self):
        type_name = '{}_{}'.format(self.name, self.berichtcode)
        type_info = (
            ('stuurgegevens', self.create_stuurgegevens_model()),
            ('parameters', self.create_parameters_model()),
            ('document', self.create_document_model()),
        )
        body_model = complex_model_factory(type_name, ZDS_XML_NS, type_info)
        return body_model


input_builder = CancelCheckoutInputBuilder('cancelCheckout', 'cc')
output_builder = CancelCheckoutOutputBuilder('cancelCheckout', 'cc', 'informatieobject', 'EDC')


class CancelCheckout(ServiceBase):
    """
    De "cancelCheckout"-service biedt DSC's de mogelijkheid om aan te geven dat
    er geen bijgewerkte versie komt van een document dat in een eerder stadium
    is opgevraagd voor bewerking via de "geefZaakdocumentbewerken"-service.
    """
    input_model = input_builder.create_model()
    output_model = output_builder.create_model()

    @rpc(input_model, _body_style="bare", _out_message_name="Bv02Bericht", _returns=output_model)
    def cancelCheckout_Di02(ctx, data):

        # Eisen aan ZS
        #
        # Er zijn geen aanvullende eisen aan het ZS.

        document_identificatie = data.document.identificatie
        checked_out_id = data.parameters.checkedOutId
        output = output_builder.create_data()

        document = get_enkelvoudig_informatie_object_or_fault(document_identificatie)
        dms_client.cancel_checkout(document, checked_out_id)

        return output
