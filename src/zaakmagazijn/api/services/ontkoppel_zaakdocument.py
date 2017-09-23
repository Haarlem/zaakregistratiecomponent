from spyne import AnyXml, ComplexModel, ServiceBase, Unicode, rpc

from zaakmagazijn.cmis.client import default_client as dms_client

from ...rgbz.models import EnkelvoudigInformatieObject, ZaakInformatieObject
from ..stuf import simple_types
from ..stuf.attributes import entiteittype, functie, verwerkingssoort
from ..stuf.base import ComplexModelBuilder, complex_model_factory
from ..stuf.choices import BerichtcodeChoices, ServerFoutChoices
from ..stuf.constants import STUF_XML_NS, ZKN_XML_NS
from ..stuf.faults import StUFFault
from ..stuf.models import Systeem


class OntkoppelZaakdocumentOutputBuilder(ComplexModelBuilder):
    berichtcode = BerichtcodeChoices.bv02

    def __init__(self, name, shortname, object_element_name, entiteittype):
        self.name = name
        self.shortname = shortname

        self.object_element_name = object_element_name
        self.entiteittype = entiteittype

    def create_stuurgegevens_model(self):
        type_info = (
            ('berichtcode', Unicode.customize(sub_ns=STUF_XML_NS, pattern=self.berichtcode)),  # sub_ns=self.stuf_ns
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


class OntkoppelZaakdocument_gerelateerde(ComplexModel):
    __namespace__ = ZKN_XML_NS
    __type_name__ = 'OntkoppelZaakdocument_gerelateerde'
    _type_info = [
        ('identificatie', Unicode.customize(type_name='zaakIdentificatie')),
        ('omschrijving', Unicode.customize(type_name='zaakIdentificatie')),
        # TODO: [TECH] Taiga #216 Gaan we alle niet in ZDS 1.2 gedefinieerde
        # relaties/attributen toestaan middels dummy elementen (AnyXML)?
        # ('isVan', AnyXml.customize(type_name='ontkoppelZaakIsVan')),
        ('entiteittype', entiteittype),
        ('verwerkingssoort', verwerkingssoort)
    ]


class OntkoppelZaakdocument_isRelevantVoor(ComplexModel):
    __namespace__ = ZKN_XML_NS
    __type_name__ = 'OntkoppelZaakdocument_isRelevantVoor'
    _type_info = [
        ('gerelateerde', OntkoppelZaakdocument_gerelateerde),
        ('entiteittype', entiteittype),
        ('verwerkingssoort', verwerkingssoort)
    ]


class OntkoppelZaakdocument_object(ComplexModel):
    __namespace__ = ZKN_XML_NS
    __type_name__ = 'OntkoppelZaakdocument_object'
    _type_info = [
        ('identificatie', Unicode.customize(type_name='edcIdentificatie')),
        # ('dct.omschrijving', Unicode.customize(type_name='edcOmschrijving', min_occurs=0)),
        ('isRelevantVoor', OntkoppelZaakdocument_isRelevantVoor.customize(min_occurs=0)),
        ('entiteittype', entiteittype),
        ('verwerkingssoort', verwerkingssoort)
    ]


class OntkoppelZaakdocumentInputBuilder(ComplexModelBuilder):
    stuf_ns = 'http://www.egem.nl/StUF/StUF0301'
    stuf_zkn_ns = "http://www.egem.nl/StUF/sector/zkn/0310"
    stuf_zds_ns = "http://www.stufstandaarden.nl/koppelvlak/zds0120"
    berichtcode = BerichtcodeChoices.di02

    def __init__(self, name, shortname):
        self.name = name
        self.shortname = shortname

    def create_stuurgegevens_model(self):
        type_info = (
            ('berichtcode', Unicode.customize(
                type_name='BerichtcodeDi02', sub_ns=self.stuf_ns,
                pattern=self.berichtcode
            )),
            ('zender', Systeem),
            ('ontvanger', Systeem),
            ('referentienummer', simple_types.Refnummer.customize(min_occurs=0)),
            ('tijdstipBericht', simple_types.Tijdstip.customize(min_occurs=0)),
            ('functie', simple_types.Functie),
        )
        stuurgegevens_model = complex_model_factory('{}_Stuurgegevens_{}'.format(
            self.berichtcode, self.shortname), self.stuf_ns, type_info)
        return stuurgegevens_model

    def create_parameters_model(self):
        type_info = (
            ('checkedOutId', Unicode.customize(type_name='checkedOutId')),
            ('versioningState', Unicode.customize(type_name='versioningState', min_occurs=0))
        )
        parameters_model = complex_model_factory('{}_Parameters_{}'.format(
            self.berichtcode, self.shortname), self.stuf_zds_ns, type_info)
        return parameters_model

    def create_edc_parameters_model(self):
        type_info = (
            ('mutatiesoort', Unicode.customize(type_name='mutatiesoort', sub_ns=self.stuf_ns)),
        )
        model = complex_model_factory('{}_EdcParameters_{}'.format(
            self.berichtcode, self.shortname), self.stuf_ns, type_info)
        return model

    def create_edclk02_model(self):
        type_info = (
            # TODO: [KING/COMPAT] Taiga #217 Element parameters.mutatiesoort staat in ZDS 1.2,
            # volgens ons, onterrecht onder object ipv onder edcLk02 voor ontkoppelZaakdocument_Di02
            ('parameters', self.create_edc_parameters_model()),
            ('object', OntkoppelZaakdocument_object.customize(max_occurs=2, min_occurs=2)),
            ('functie', functie),
            ('entiteittype', entiteittype),
        )
        model = complex_model_factory('{}_EdcLk02_{}'.format(
            self.berichtcode, self.shortname), self.stuf_zkn_ns, type_info)
        return model

    def create_model(self):
        type_name = '{}_{}'.format(self.name, self.berichtcode)
        type_info = (
            ('stuurgegevens', self.create_stuurgegevens_model()),
            ('parameters', self.create_parameters_model()),
            ('edcLk02', self.create_edclk02_model()),
        )
        body_model = complex_model_factory(type_name, self.stuf_zds_ns, type_info)
        return body_model


input_builder = OntkoppelZaakdocumentInputBuilder('OntkoppelZaakdocument', 'ozd')
output_builder = OntkoppelZaakdocumentOutputBuilder('OntkoppelZaakdocument', 'ozd', 'informatieobject', 'EDC')


class OntkoppelZaakdocument(ServiceBase):
    """
    Een zaakgerelateerd document kan verwijderd worden bij een zaak door de
    relatie tussen ZAAK en DOCUMENT te verwijderen. Daarvoor kan het bericht
    ontkoppelZaakdocument gebruikt worden. Het ontkoppelZaakdocument bericht
    dient in dit geval te voldoen aan onderstaande tabel. Een Zaakdocument mag
    niet in bewerking zijn alvorens het losgekoppeld wordt. Ook is het niet
    toegestaan andere eigenschappen van het document te wijzigen, anders dan
    het verbreken van de relatie tussen zaak en document. Conform de
    StUF-specificaties wordt bij een verwijdering van een relatie in de oude
    situatie de betreffende relatie opgenomen met de (kerngegevens van) de
    gerelateerde en in de nieuwe situatie een lege relatie.
    """
    input_model = input_builder.create_model()
    output_model = output_builder.create_model()

    @rpc(input_model, _body_style="bare", _out_message_name="Bv02Bericht", _returns=output_model)
    def ontkoppelZaakdocument_Di02(ctx, data):
        """
        Een zaakgerelateerd document moet losgekoppeld worden van een zaak.
        """

        # Eisen aan ZS
        #
        # Er zijn geen aanvullende eisen aan het ZS

        # Interactie tussen DSC en ZS
        #
        # Tussen DSC en ZS wordt een vrij bericht uitgewisseld.

        informatieobject_id = data.edcLk02.object[0].identificatie
        zaak_id = data.edcLk02.object[0].isRelevantVoor.gerelateerde.identificatie
        zio_qs = ZaakInformatieObject.objects.filter(
            zaak__zaakidentificatie=zaak_id,
            informatieobject__informatieobjectidentificatie=informatieobject_id
        )
        if not zio_qs.exists():
            raise StUFFault(ServerFoutChoices.stuf064, stuf_details='Gerefereerde zaak/document combinatie is niet aanwezig')
        if data.edcLk02.parameters.mutatiesoort != 'W':
            raise StUFFault(ServerFoutChoices.stuf064, stuf_details='Parameters mutatiesoort is niet gelijk aan "W"')
        if data.edcLk02.object[0].isRelevantVoor.verwerkingssoort != 'V':
            raise StUFFault(ServerFoutChoices.stuf064, stuf_details='Parameters mutatiesoort is niet gelijk aan "W"')

        document = EnkelvoudigInformatieObject.objects.get(informatieobjectidentificatie=informatieobject_id)
        # check if it's being edited or not
        if dms_client.is_locked(document):
            raise StUFFault(ServerFoutChoices.stuf064, stuf_details='Document is in bewerking')

        # Jacked up and good to go!

        for zio in zio_qs:
            dms_client.ontkoppel_zaakdocument(document, zio.zaak)
            zio.delete()

        # TODO: [TECH] Taiga #238
        # # ontkoppeld van alle zaken
        # if not document.zaakinformatieobject_set.exists():
        #     dms_client.verwijder_document(document)

        output = output_builder.create_data()
        return output
