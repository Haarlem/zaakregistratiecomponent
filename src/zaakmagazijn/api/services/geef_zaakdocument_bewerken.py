from spyne import AnyXml, ServiceBase, Unicode, rpc

from ...cmis.client import default_client as dms_client
from ..stuf import simple_types
from ..stuf.attributes import entiteittype, functie
from ..stuf.base import ComplexModelBuilder, complex_model_factory
from ..stuf.choices import BerichtcodeChoices
from ..stuf.constants import STUF_XML_NS, ZDS_XML_NS, ZKN_XML_NS
from ..stuf.models import ParametersVraag_gzdb, Systeem
from ..stuf.utils import get_model_value, get_spyne_field, to_spyne_value
from ..utils import get_enkelvoudig_informatie_object_or_fault
from ..zds import La01Builder
from .geef_zaakdocument_lezen import EnkelvoudigInformatieObjectEntiteit

output_builder_edc_la01 = La01Builder(EnkelvoudigInformatieObjectEntiteit, 'geefZaakdocumentBewerken')


# TODO: [TECH] Move to/merge in vrijeberichten?
# Vrij bericht met als namespace ZDS ipv ZKN
class GeefZaakdocumentBewerkenInputBuilder(ComplexModelBuilder):
    berichtcode = BerichtcodeChoices.di02

    def __init__(self, name, shortname, object_element_name, entiteittype):
        self.name = name
        self.shortname = shortname

        self.object_element_name = object_element_name
        self.entiteittype = entiteittype

    def create_stuurgegevens_model(self):
        type_info = (
            ('berichtcode', Unicode.customize(type_name='BerichtcodeDi02', sub_ns=STUF_XML_NS, pattern=self.berichtcode)),
            ('zender', Systeem),
            ('ontvanger', Systeem),
            ('referentienummer', simple_types.Refnummer.customize(min_occurs=0)),
            ('tijdstipBericht', simple_types.Tijdstip.customize(min_occurs=0)),
            ('functie', simple_types.Functie),
        )
        stuurgegevens_model = complex_model_factory('{}_Stuurgegevens_{}'.format(
            self.berichtcode, self.shortname), STUF_XML_NS, type_info)
        return stuurgegevens_model

    def create_gelijk_model(self):
        type_info = (
            ('identificatie', simple_types.ZaakIdentificatie_r),
            ('entiteittype', entiteittype),
        )
        gelijk_model = complex_model_factory('{}_vraagSelectie_{}'.format(
            self.entiteittype, self.shortname), ZKN_XML_NS, type_info)
        return gelijk_model

    def create_edc_lv01_model(self):
        type_info = (
            ('parameters', ParametersVraag_gzdb),
            ('gelijk', self.create_gelijk_model()),
            # Not entirely correct. Scope is an anonymous type, with object being the vraagScope type.
            ('scope', AnyXml.customize(type_name='{}-vraagScope-{}'.format(
                self.entiteittype, self.shortname))),
            ('functie', functie),
            ('entiteittype', entiteittype),
        )
        model = complex_model_factory('Vraag-{}'.format(
            self.entiteittype), ZKN_XML_NS, type_info)
        return model

    def create_model(self):
        type_name = '{}_{}'.format(self.name, self.berichtcode)
        type_info = (
            ('stuurgegevens', self.create_stuurgegevens_model()),
            (self.object_element_name, self.create_edc_lv01_model()),
        )
        body_model = complex_model_factory(type_name, ZDS_XML_NS, type_info)
        return body_model


class GeefZaakdocumentBewerkenOutputBuilder(ComplexModelBuilder):
    berichtcode = BerichtcodeChoices.du02

    def __init__(self, name, shortname, object_element_name, entiteittype):
        self.name = name
        self.shortname = shortname

        self.object_element_name = object_element_name
        self.entiteittype = entiteittype
        self.output_builder_edc_la01_model = output_builder_edc_la01.create_model()

    def create_stuurgegevens_model(self):
        type_info = (
            ('berichtcode', Unicode.customize(sub_ns=STUF_XML_NS, pattern=self.berichtcode)),
            ('zender', Systeem.customize(min_occurs=0)),
            ('ontvanger', Systeem.customize(min_occurs=0)),
            ('referentienummer', simple_types.Refnummer.customize(min_occurs=0)),
            ('tijdstipBericht', simple_types.Tijdstip.customize(min_occurs=0)),
            ('crossRefnummer', simple_types.Refnummer.customize(min_occurs=0)),
            ('functie', simple_types.Functie),
        )
        stuurgegevens_model = complex_model_factory('{}_Stuurgegevens_{}'.format(
            self.berichtcode, self.shortname), STUF_XML_NS, type_info)
        return stuurgegevens_model

    def create_parameters_model(self):
        type_info = (
            ('checkedOutId', Unicode.customize()),
            ('checkedOutBy', Unicode.customize(min_occurs=0)),
        )
        parameters_model = complex_model_factory('Parameters-zs-dms-r', ZDS_XML_NS, type_info)
        return parameters_model

    def create_model(self):

        type_name = '{}_{}'.format(self.name, self.berichtcode)
        stuurgegevens_model = self.create_stuurgegevens_model()

        type_info = (
            ('stuurgegevens', stuurgegevens_model),
            # TODO: [KING] Taiga #235 geefZaakdocumentbewerken antwoord bericht kent geen parameters in ZDS 1.2 maar dit lijkt ons de enige reden van dit bericht.
            ('parameters', self.create_parameters_model()),
            (self.object_element_name, self.output_builder_edc_la01_model),
        )
        body_model = complex_model_factory(type_name, ZDS_XML_NS, type_info)
        return body_model

    def create_data(self, data, obj):
        # Using sections of beantwoordvraag.py to build a valid antwoord/object dictionary, so it can map the given
        # InformatieObject to the output model

        model_answer = {}
        # Actual name is: Kennisgeving-EDC
        output_model = self.output_builder_edc_la01_model
        spyne_model = get_spyne_field(output_model, 'antwoord/object')

        field_mapping = EnkelvoudigInformatieObjectEntiteit.get_django_field_mapping()
        for field_name, django_field_name, django_field in field_mapping:

            model_answer[field_name] = to_spyne_value(
                get_model_value(obj, django_field_name), django_field,
                get_spyne_field(spyne_model, field_name)
            )
        return {
            'stuurgegevens': {
                'berichtcode': self.berichtcode,
                'functie': self.name,
            },
            self.object_element_name: {
                'antwoord': {
                    'object': [model_answer]
                }
            }
        }


input_builder = GeefZaakdocumentBewerkenInputBuilder('geefZaakdocumentBewerken', 'gzdb', 'edcLv01', 'EDC')
output_builder = GeefZaakdocumentBewerkenOutputBuilder('geefZaakdocumentBewerken', 'gzdb', 'edcLa01', 'EDC')


class GeefZaakdocumentBewerken(ServiceBase):
    """
    De "geef Zaakdocument bewerken"-service biedt dezelfde functionaliteit als
    de "geefZaakdocumentLezen"-service (zie paragraaf 4.3.2 service #8) met het
    verschil dat het document nu bewerkt mag worden door de DSC. Het document
    wordt daarbij "gelockt" (vergrendeld), zodat het niet gewijzigd kan worden
    door derden tot de DSC via de "updateZaakdocument"-service (zie paragraaf
    4.3.6 service #12) wijzigingen heeft doorgevoerd. Er wordt gebruik gemaakt
    van StUF-Dienstberichten om extra gegevens met betrekking tot locking mee
    te kunnen geven.

    De DSC dient gebruik te maken van de Update Zaakdocument service of de
    cancelCheckOut service om ervoor te zorgen dat het document weer
    beschikbaar komt voor anderen om te muteren ("unlock").

    Zie: ZDS 1.2, paragraaf 4.3.3
    """
    input_model = input_builder.create_model()
    output_model = output_builder.create_model()

    @rpc(input_model, _body_style="bare", _out_message_name="geefZaakdocumentBewerken_Du02", _returns=output_model)
    def geefZaakdocumentBewerken_Di02(ctx, data):
        """
        Een document wat behoort tot een lopende zaak wordt opgevraagd om te bewerken.
        """

        # Eisen aan ZS:
        #
        # Er gelden geen aanvullende eisen.

        # Interactie tussen ZSC en ZS:
        #
        # Tussen DSC en ZS is een vraag-/antwoord interactie met vrije
        # berichten.

        # Interactie tussen ZS en DMS:
        #
        # Het Di02-bericht wordt vertaald naar CMIS-operatie(s) zodanig dat het
        # ZS het Du02-antwoordbericht voor de ZSC kan genereren met de
        # gevraagde elementen. In Tabel 3 is een mapping aangegeven tussen de
        # StUF-ZKN-elementen en CMIS-properties om de vertaling uit te voeren.
        #
        # Het DMS zet een lock op het EDC-object, zodat er geen mutaties kunnen
        # plaatsvinden totdat er een mutatie komt van (eind)gebruiker, die het
        # document heeft gelockt.

        identificatie = data.edcLv01.gelijk.identificatie
        eio = get_enkelvoudig_informatie_object_or_fault(identificatie)

        checked_out_id, checked_out_by = dms_client.checkout(eio)

        data = output_builder.create_data(data, eio)
        data['parameters'] = {
            'checkedOutId': checked_out_id,
            'checkedOutBy': checked_out_by
        }
        return data
