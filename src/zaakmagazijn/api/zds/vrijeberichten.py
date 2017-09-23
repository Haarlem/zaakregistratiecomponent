from django.conf import settings

from spyne import Unicode, XmlAttribute

from ...utils import stuf_datetime
from ..stuf import simple_types
from ..stuf.base import ComplexModelBuilder, complex_model_factory
from ..stuf.choices import BerichtcodeChoices
from ..stuf.models import Systeem
from ..utils import create_unique_id


class GenereerIdentificatieOutputBuilder(ComplexModelBuilder):
    stuf_ns = 'http://www.egem.nl/StUF/StUF0301'
    stuf_zkn_ns = "http://www.egem.nl/StUF/sector/zkn/0310"
    stuf_zds_ns = "http://www.stufstandaarden.nl/koppelvlak/zds0120"
    berichtcode = BerichtcodeChoices.du02

    def __init__(self, name, shortname, object_element_name, entiteittype):
        self.name = name
        self.shortname = shortname

        self.object_element_name = object_element_name
        self.entiteittype = entiteittype

    def create_stuurgegevens_model(self):
        type_info = (
            ('berichtcode', Unicode.customize(sub_ns=self.stuf_ns, pattern=self.berichtcode)),  # sub_ns=self.stuf_ns
            ('zender', Systeem.customize(min_occurs=0)),
            ('ontvanger', Systeem.customize(min_occurs=0)),
            ('referentienummer', simple_types.Refnummer.customize(min_occurs=0)),
            ('tijdstipBericht', simple_types.Tijdstip.customize(min_occurs=0)),
            ('crossRefnummer', simple_types.Refnummer.customize(min_occurs=0)),
            ('functie', simple_types.Functie),
        )
        stuurgegevens_model = complex_model_factory('{}_Stuurgegevens_{}'.format(
            self.berichtcode, self.shortname), self.stuf_ns, type_info)
        return stuurgegevens_model

    def create_object_model(self):
        type_info = (
            ('identificatie', Unicode.customize(sub_ns=self.stuf_zkn_ns)),
            ('functie', XmlAttribute(Unicode.customize(sub_ns=self.stuf_ns), ns='http://www.egem.nl/StUF/StUF0301')),
            ('entiteittype', XmlAttribute(Unicode.customize(sub_ns=self.stuf_ns, ns='http://www.egem.nl/StUF/StUF0301'))),
        )
        object_model = complex_model_factory(
            '{}_{}'.format(self.entiteittype, self.shortname), self.stuf_zkn_ns, type_info)
        return object_model

    def create_model(self):
        type_name = '{}_{}'.format(self.name, self.berichtcode)
        type_info = (
            ('stuurgegevens', self.create_stuurgegevens_model()),
            (self.object_element_name, self.create_object_model()),
        )
        body_model = complex_model_factory(type_name, self.stuf_zds_ns, type_info)
        return body_model

    def create_data(self, request_obj, identificatie):
        # TODO: [TECH] Maybe we should move the whole stuurgegevens (or at least zender/ontvanger) to the application level?
        # TODO: [TECH] Reference etc. should also be logged.
        ontvanger = request_obj.stuurgegevens.zender
        cross_refnummer = request_obj.stuurgegevens.referentienummer

        return {
            'stuurgegevens': {
                'berichtcode': self.berichtcode,
                'zender': settings.ZAAKMAGAZIJN_SYSTEEM,
                'ontvanger': ontvanger,
                'referentienummer': create_unique_id(),
                'tijdstipBericht': stuf_datetime.now(),
                'crossRefnummer': cross_refnummer,
                'functie': self.name,
            },
            self.object_element_name: {
                'identificatie': identificatie,
                'functie': 'entiteit',
                'entiteittype': self.entiteittype,
            }
        }


class GenereerIdentificatieInputBuilder(ComplexModelBuilder):
    stuf_ns = 'http://www.egem.nl/StUF/StUF0301'
    stuf_zkn_ns = "http://www.egem.nl/StUF/sector/zkn/0310"
    stuf_zds_ns = "http://www.stufstandaarden.nl/koppelvlak/zds0120"
    berichtcode = BerichtcodeChoices.di02

    def __init__(self, name, shortname):
        self.name = name
        self.shortname = shortname

    def create_stuurgegevens_model(self):
        type_info = (
            ('berichtcode', Unicode.customize(type_name='BerichtcodeDi02', sub_ns=self.stuf_ns, pattern=self.berichtcode)),  # sub_ns=self.stuf_ns
            ('zender', Systeem),
            ('ontvanger', Systeem),
            ('referentienummer', simple_types.Refnummer.customize(min_occurs=0)),
            ('tijdstipBericht', simple_types.Tijdstip.customize(min_occurs=0)),
            ('functie', simple_types.Functie),
        )
        stuurgegevens_model = complex_model_factory('{}_Stuurgegevens_{}'.format(
            self.berichtcode, self.shortname), self.stuf_ns, type_info)
        return stuurgegevens_model

    def create_model(self, parameters=None):
        type_name = '{}_{}'.format(self.name, self.berichtcode)
        type_info = (
            ('stuurgegevens', self.create_stuurgegevens_model()),
        )
        # Added for genereerDocumentIdentificatie_Di02.
        if parameters is not None:
            type_info += (
                ('parameters', parameters),
            )

        body_model = complex_model_factory(type_name, self.stuf_zds_ns, type_info)
        return body_model
