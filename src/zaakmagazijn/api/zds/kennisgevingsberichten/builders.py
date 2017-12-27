from spyne import Unicode
from spyne.model.complex import TypeInfo

from ...stuf import simple_types
from ...stuf.attributes import entiteittype, verwerkingssoort
from ...stuf.base import ComplexModelBuilder
from ...stuf.choices import BerichtcodeChoices
from ...stuf.constants import STUF_XML_NS, ZKN_XML_NS
from ...stuf.models import (
    BinaireInhoud, Systeem, Tijdstip_e, TijdvakGeldigheid, TijdvakRelatie
)
from ...stuf.simple_types import IndicatorOvername
from ...stuf.utils import django_field_to_spyne_model, reorder_type_info


class Lk01Builder(ComplexModelBuilder):
    berichtcode = BerichtcodeChoices.lk01

    def __init__(self, stuf_entiteit, name, update=False):
        self.name = name
        self.stuf_entiteit = stuf_entiteit
        self.update = update

    def create_stuurgegevens_name(self):
        """
        Create name which uniquely identifies the stuurgegevens type in de XSD.
        """
        return '{}_Stuurgegevens{}{}'.format(self.stuf_entiteit.get_mnemonic(), self.name, self.berichtcode)

    def create_parameters_name(self):
        """
        Create name which uniquely identifies the stuurgegevens type in de XSD.
        """
        return '{}_Parameters{}{}'.format(self.stuf_entiteit.get_mnemonic(), self.name, self.berichtcode)

    def create_object_name(self, stuf_entiteit, field_name=None):
        if stuf_entiteit and field_name:
            if stuf_entiteit.heeft_kerngegevens():
                postfix = 'AntwoordKerngegevens'
            else:
                postfix = 'Antwoord'
            return '{}_{}_{}_{}'.format(self.name, stuf_entiteit.get_mnemonic(), field_name, postfix)
        if stuf_entiteit:
            if stuf_entiteit.heeft_kerngegevens():
                postfix = '_AntwoordKerngegevens'
            else:
                postfix = ''
            return '{}_{}{}'.format(stuf_entiteit.get_mnemonic(), self.name, postfix)

    def create_stuurgegevens_model(self):
        BerichtCode = Unicode.customize(type_name='BerichtcodeLk01', sub_ns=STUF_XML_NS, fixed=self.berichtcode, min_occurs=1, max_occurs=1, nillable=False)
        type_info = (
            ('berichtcode', BerichtCode.customize(min_occurs=1, max_occurs=1, nillable=False)),
            ('zender', Systeem.customize(min_occurs=1, max_occurs=1, nillable=False)),
            ('ontvanger', Systeem.customize(min_occurs=1, max_occurs=1, nillable=False)),
            ('referentienummer', simple_types.Refnummer),
            ('tijdstipBericht', simple_types.Tijdstip),
            ('entiteittype', simple_types.Entiteittype.customize(fixed=self.stuf_entiteit.get_mnemonic(), nillable=False, min_occurs=1, max_occurs=1)),
        )
        name = self.create_stuurgegevens_name()
        return self.create_reusable_model(name, STUF_XML_NS, type_info)

    def create_parameters_model(self):
        # See StUF 3.01 Tabel 5.2
        mutatiesoort = 'W' if self.update else 'T'
        type_info = (
            ('mutatiesoort', Unicode.customize(sub_ns=STUF_XML_NS, fixed=mutatiesoort, min_occurs=1, max_occurs=1, nillable=False)),
            ('indicatorOvername', IndicatorOvername.customize(min_occurs=1, max_occurs=1, nillable=False)),
        )
        parameters_model = self.create_reusable_model(self.create_parameters_name(), STUF_XML_NS, type_info)
        return parameters_model

    def reorder_type_info(self, fields, type_info):
        """
        re-order the given type_info into the order given with fields. Anything
        not mentioned in fields, will be appended last.
        """

        copy = TypeInfo(type_info.items())
        new = TypeInfo()
        for field in fields:
            value = copy[field]
            del copy[field]
            new[field] = value

        # Add the fields not specified in fields last.
        for field, value in copy.items():
            new[field] = value
        return new

    def create_related_model(self, stuf_entiteit, field_name, data):
        """
        Create a model for a 'gerelateerde'
        """
        if isinstance(data, tuple) or isinstance(data, list):
            sub_type_info = []
            for relation_name, related_cls in data:
                relation_model = self.create_object_model(related_cls).customize(xml_choice_group=field_name)
                sub_type_info.append((relation_name, relation_model))

            # See Stuf 03.01 - 3.2.2 De structuur van een object, as to why this
            # model does not have a 'entiteittype' attribute.
            #
            # Het element <gerelateerde> mag ook als kind een <choice> bevatten met twee of meer elementen
            # met een attribute StUF:entiteittype en daarbinnen de elementen voor dat entiteittype. Het element
            # <gerelateerde> heeft dan geen attributes.
            #
            sub_model_name = self.create_object_name(stuf_entiteit, field_name)
            sub_model = self.create_reusable_model(sub_model_name, stuf_entiteit.get_namespace(), sub_type_info)
        else:
            related_cls = data
            sub_model = self.create_object_model(related_cls)

        return sub_model

    def create_object_model(self, stuf_entiteit=None, topfundamenteel=False):
        """
        From a StUFEntiteit create a hierarchy of ComplexModels for everything under the object element.
        """
        stuf_entiteit = stuf_entiteit or self.stuf_entiteit

        type_info = TypeInfo()
        if stuf_entiteit.is_entiteit():
            type_info['entiteittype'] = entiteittype.customize(fixed=stuf_entiteit.get_mnemonic())
            type_info['verwerkingssoort'] = verwerkingssoort

        for related_field in stuf_entiteit.get_related_fields():
            # In the case of an update the element can be optional (since it isn't modified)
            model_kwargs = {
                'min_occurs': 0,
                'max_occurs': related_field.max_occurs or 'unbounded'
            }
            # On create, the min_occurs _is_ required.
            if not self.update:  # Create
                model_kwargs['min_occurs'] = related_field.min_occurs

            type_info[related_field.field_name] = self.create_object_model(
                related_field.stuf_entiteit).customize(**model_kwargs)

        # TODO [TECH]: In the WSDL this should be minOccurs and maxOccurs of 1.
        gerelateerde = stuf_entiteit.get_gerelateerde()
        if gerelateerde:
            _, gerelateerde_data = gerelateerde
            type_info['gerelateerde'] = self.create_related_model(stuf_entiteit, 'gerelateerde', gerelateerde_data)

        # Build up spyne model
        field_mapping = stuf_entiteit.get_django_field_mapping()
        file_fields = stuf_entiteit.get_file_fields()
        for field_name, django_field_name, django_field in field_mapping:
            #
            # These field requirement rules are not exactly as the KING XSD defines them,
            # but they're close enough (TM). On the highest level (topfundamenteel)
            # and on a 'creeer' service only a 'T' (create) can be done, so all django
            # required fields, are required for that, on the lower levels a 'I' might
            # be done, so not all fields are required.
            #
            if topfundamenteel and not self.update:  # create topfundamenteel -> read the Django field definitions
                customize_kwargs = {}
            else:
                required = False
                customize_kwargs = dict(
                    nullable=not required,
                    min_occurs=1 if required else 0
                )

            # TODO [TECH]: figure out if we can put this in the DJANGO -> SPYNE mapping
            if field_name in file_fields:
                spyne_model = BinaireInhoud.customize(**customize_kwargs)
            else:
                spyne_model = django_field_to_spyne_model(django_field, **customize_kwargs)

            type_info[field_name] = spyne_model

        for field_name, spyne_model, _ in stuf_entiteit.get_custom_fields():
            type_info[field_name] = spyne_model

        tijdvak_geldigheid = stuf_entiteit.get_tijdvak_geldigheid()
        if tijdvak_geldigheid:
            type_info.append(
                ('tijdvakGeldigheid', TijdvakGeldigheid.customize(ref='tijdvakGeldigheid')),
            )

        tijdvak_relatie = stuf_entiteit.get_tijdvak_relatie()
        if tijdvak_relatie:
            type_info.append(
                ('tijdvakRelatie', TijdvakRelatie.customize(ref='tijdvakRelatie')),
            )

        tijdstip_registratie = stuf_entiteit.get_tijdstip_registratie()
        if tijdstip_registratie:
            type_info.append(
                ('tijdstipRegistratie', Tijdstip_e.customize(ref='tijdstipRegistratie')),
            )

        complex_model = self.create_reusable_model(
            self.create_object_name(stuf_entiteit),
            stuf_entiteit.get_namespace(),
            type_info
        )

        complex_model._type_info = reorder_type_info(stuf_entiteit.get_fields(), complex_model._type_info)

        return complex_model

    def create_model(self):
        type_name = "{}_{}".format(self.name, self.berichtcode)
        occurs = 2 if self.update else 1
        type_info = (
            ('stuurgegevens', self.create_stuurgegevens_model()),
            ('parameters', self.create_parameters_model()),
            ('object', self.create_object_model(topfundamenteel=True).customize(min_occurs=occurs, max_occurs=occurs)),
        )
        body_model = self.create_reusable_model(type_name, ZKN_XML_NS, type_info)
        return body_model


class Lk02Builder(Lk01Builder):
    berichtcode = BerichtcodeChoices.lk02

    def create_parameters_model(self):
        # See StUF 3.01 Tabel 5.2, only mutatiesoort should be part of the parameters.
        mutatiesoort = 'W' if self.update else 'T'
        type_info = (
            ('mutatiesoort', Unicode.customize(sub_ns=STUF_XML_NS, fixed=mutatiesoort, min_occurs=1, max_occurs=1, nillable=False)),
        )
        parameters_model = self.create_reusable_model(self.create_parameters_name(), STUF_XML_NS, type_info)
        return parameters_model

    def create_model(self):
        type_name = "{}_{}".format(self.name, self.berichtcode)
        occurs = 2 if self.update else 1
        type_info = (
            ('parameters', self.create_parameters_model()),
            ('object', self.create_object_model(topfundamenteel=True).customize(min_occurs=occurs, max_occurs=occurs)),
        )
        body_model = self.create_reusable_model(type_name, ZKN_XML_NS, type_info)
        return body_model
