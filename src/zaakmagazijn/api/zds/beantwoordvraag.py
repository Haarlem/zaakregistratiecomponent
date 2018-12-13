import logging

from django.conf import settings

from spyne import Unicode, XmlAttribute
from spyne.model.complex import TypeInfo

from zaakmagazijn.api.stuf.faults import StUFFault
from zaakmagazijn.api.utils import create_unique_id
from zaakmagazijn.utils import stuf_datetime

from ..stuf import (
    ForeignKeyRelation, OneToManyRelation, attributes, simple_types
)
from ..stuf.base import ComplexModelBuilder
from ..stuf.choices import (
    BerichtcodeChoices, ClientFoutChoices, ServerFoutChoices
)
from ..stuf.constants import STUF_XML_NS, ZKN_XML_NS
from ..stuf.exceptions import EmptyResultError
from ..stuf.models import (
    BinaireInhoud, ScopeAttribute, StufParameters, Systeem, Tijdstip_e,
    TijdvakGeldigheid, TijdvakRelatie
)
from ..stuf.protocols import IgnoreAttribute, Nil
from ..stuf.utils import (
    create_query_args, django_field_to_spyne_model, get_model_value,
    get_ontvanger, get_spyne_field, get_systeem_zender, reorder_type_info,
    to_spyne_value
)

logger = logging.getLogger(__name__)


class Lv01Builder(ComplexModelBuilder):
    berichtcode = BerichtcodeChoices.lv01

    def __init__(self, stuf_entiteit, name):
        assert stuf_entiteit.is_entiteit(), 'Only a StUFEntiteit can be used as topfundamenteel'

        self.stuf_entiteit = stuf_entiteit
        self.name = name

    def create_scope_name(self, stuf_entiteit=None, field_name=None):
        """
        Create name which uniquely identifies the scope type in de XSD.
        """
        if stuf_entiteit and not stuf_entiteit.is_entiteit():
            return stuf_entiteit.get_model().__name__ + 'Grp_scope'

        prefix = 'vraagScope'
        if stuf_entiteit and stuf_entiteit.heeft_kerngegevens():
            prefix = 'vraagScopeKerngegevens'
        if stuf_entiteit and field_name:
            return '{}_{}_{}_{}'.format(self.name, stuf_entiteit.get_mnemonic(), field_name, prefix)
        elif stuf_entiteit:
            return '{}_{}_{}'.format(self.name, stuf_entiteit.get_mnemonic(), prefix)
        else:
            return '{}_{}'.format(self.name, prefix)

    def create_gelijk_name(self, stuf_entiteit=None, field_name=None):
        """
        Create name which uniquely identifies the gelijk type in de XSD.
        """
        prefix = 'vraagSelectie'
        if stuf_entiteit and stuf_entiteit.heeft_kerngegevens():
            prefix = 'vraagSelectieKerngegevens'
        if stuf_entiteit and field_name:
            return '{}_{}_{}_{}'.format(self.name, stuf_entiteit.get_mnemonic(), field_name, prefix)
        elif stuf_entiteit:
            return '{}_{}_{}'.format(self.name, stuf_entiteit.get_mnemonic(), prefix)

    def create_stuurgegevens_name(self):
        """
        Create name which uniquely identifies the stuurgegevens type in de XSD.
        """
        return '{}_Stuurgegevens{}{}'.format(self.stuf_entiteit.get_mnemonic(), self.name, self.berichtcode)

    def create_model(self):
        name = self.name
        root_type_info = [
            ('stuurgegevens', self.create_stuurgegevens_model()),
            ('parameters', self.get_input_parameters_model()),
        ]
        try:
            root_type_info.append(('gelijk', self.create_gelijk_model()))
        except EmptyResultError:
            pass
        scope_model = self.create_scope_model()
        scope_model._type_info['scope'] = XmlAttribute(attributes.Scope__Anonymous, ref='scope', ns=STUF_XML_NS)
        object_type_info = [
            ('object', scope_model),
        ]
        object_model = self.create_reusable_model(self.create_scope_name(), ZKN_XML_NS, object_type_info)
        root_type_info.append(('scope', object_model))
        root_model = self.create_reusable_model('{}_Lv01'.format(name), ZKN_XML_NS, root_type_info)
        root_model.stuf_entiteit = self.stuf_entiteit
        return root_model

    def create_stuurgegevens_model(self):
        type_info = (
            ('berichtcode', Unicode.customize(type_name='BerichtcodeLv01', fixed=BerichtcodeChoices.lv01, min_occurs=1, nillable=False)),
            ('zender', Systeem.customize(min_occurs=0, nillable=False)),
            ('ontvanger', Systeem.customize(min_occurs=0, nillable=False)),
            ('referentienummer', simple_types.Refnummer.customize(min_occurs=0, nillable=False)),
            ('tijdstipBericht', simple_types.Tijdstip.customize(min_occurs=0, nillable=False)),
            # Technically: EntiteittypeBSL, EntiteittypeZAK, EntiteittypeEDC
            ('entiteittype', simple_types.Entiteittype.customize(fixed=self.stuf_entiteit.get_mnemonic(), min_occurs=1, nillable=False)),
        )
        stuurgegevens_model = self.create_reusable_model(self.create_stuurgegevens_name(), STUF_XML_NS, type_info).customize(min_occurs=1, nillable=False)
        return stuurgegevens_model

    def create_gelijk_model(self, stuf_entiteit=None):
        # TODO [TECH]: The gelijk model is required, and should always be set.
        stuf_entiteit = stuf_entiteit or self.stuf_entiteit
        type_info = TypeInfo()
        for related_field in stuf_entiteit.get_related_fields():
            try:
                # This is not consistent with the prototype-XSD. See Taiga issue #88
                type_info[related_field.field_name] = self.create_gelijk_model(related_field.stuf_entiteit)
            except EmptyResultError:
                pass

        # Create spyne model for 'gerelateerde'
        # TODO [TECH]: In the WSDL this should be minOccurs and maxOccurs of 1.
        gerelateerde = stuf_entiteit.get_gerelateerde()
        if gerelateerde:
            _, gerelateerde_data = gerelateerde
            if isinstance(gerelateerde_data, tuple) or isinstance(gerelateerde_data, list):
                for relation_name, related_cls in gerelateerde_data:
                    try:
                        sub_type_info = []
                        for relation_name, related_cls in gerelateerde_data:
                            sub_type_info.append((relation_name, self.create_gelijk_model(related_cls).customize(xml_choice_group='gerelateerde')))
                        sub_model = self.create_reusable_model(self.create_gelijk_name(stuf_entiteit, 'gerelateerde'), stuf_entiteit.get_namespace(), sub_type_info)
                        type_info['gerelateerde'] = sub_model
                    except EmptyResultError:
                        pass
            else:
                related_cls = gerelateerde_data
                try:
                    type_info.append(('gerelateerde', self.create_gelijk_model(related_cls)))
                except EmptyResultError:
                    pass

        field_mapping = stuf_entiteit.get_django_field_mapping(filter_fields=True)
        if not field_mapping and not type_info:
            raise EmptyResultError()

        # Build the Spyne model
        for field_name, django_field_name, django_field in field_mapping:
            type_info[field_name] = django_field_to_spyne_model(django_field)
        complex_model = self.create_reusable_model(
            self.create_gelijk_name(stuf_entiteit), stuf_entiteit.get_namespace(), type_info)

        if stuf_entiteit.is_entiteit():
            complex_model._type_info['entiteittype'] = XmlAttribute(simple_types.Entiteittype, ref='entiteittype', ns=STUF_XML_NS)
        complex_model._type_info.update(type_info)
        complex_model.stuf_entiteit = stuf_entiteit

        complex_model._type_info = reorder_type_info(stuf_entiteit.get_fields(), complex_model._type_info, allow_partial=True)

        return complex_model

    def create_scope_model(self, stuf_entiteit=None):
        stuf_entiteit = stuf_entiteit or self.stuf_entiteit

        field_names = [field_name for field_name, _unused in stuf_entiteit.get_field_mapping()]
        type_info = [(field_name, ScopeAttribute) for field_name in field_names]
        # type_info = []
        #
        # file_fields = stuf_entiteit.get_file_fields()
        # field_mapping = stuf_entiteit.get_django_field_mapping()
        # for field_name, django_field_name, django_field in field_mapping:
        #     if field_name in file_fields:
        #         type_info.append((field_name, Unicode))  # TODO
        #     else:
        #         type_info.append((field_name, django_field_to_spyne_model(django_field)))

        for related_field in stuf_entiteit.get_related_fields():
            type_info.append((related_field.field_name, self.create_scope_model(related_field.stuf_entiteit)))

        # Create spyne model for 'gerelateerde'
        # TODO [TECH]: In the WSDL this should be minOccurs and maxOccurs of 1.
        gerelateerde = stuf_entiteit.get_gerelateerde()
        if gerelateerde:
            _, gerelateerde_data = gerelateerde
            if isinstance(gerelateerde_data, tuple) or isinstance(gerelateerde_data, list):
                sub_type_info = []
                for relation_name, related_cls in gerelateerde_data:
                    sub_type_info.append((relation_name, self.create_scope_model(related_cls).customize(xml_choice_group='gerelateerde')))
                sub_model = self.create_reusable_model(self.create_scope_name(stuf_entiteit, 'gerelateerde'), stuf_entiteit.get_namespace(), sub_type_info)
                sub_model.stuf_entiteit = stuf_entiteit
                type_info.append(('gerelateerde', sub_model))
            else:
                related_cls = gerelateerde_data
                type_info.append(('gerelateerde', self.create_scope_model(related_cls)))

        if stuf_entiteit.is_entiteit():
            type_info.append(('entiteittype', XmlAttribute(simple_types.Entiteittype, ref='entiteittype', ns=STUF_XML_NS)))

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

        scope_model = self.create_reusable_model(self.create_scope_name(stuf_entiteit), stuf_entiteit.get_namespace(), type_info)
        scope_model.stuf_entiteit = stuf_entiteit

        scope_model._type_info = reorder_type_info(stuf_entiteit.get_fields(), scope_model._type_info, allow_partial=True)

        return scope_model

    def get_input_parameters_model(self):
        if hasattr(self.stuf_entiteit, 'input_parameters'):
            return self.stuf_entiteit.input_parameters
        return StufParameters


class La01Builder(ComplexModelBuilder):
    berichtcode = BerichtcodeChoices.la01

    def __init__(self, stuf_entiteit, name):
        self.stuf_entiteit = stuf_entiteit
        self.name = name
        self.total_objs = 0

    def create_stuurgegevens_name(self):
        return '{}_Stuurgegevens{}{}'.format(self.stuf_entiteit.get_mnemonic(), self.name, self.berichtcode)

    def create_object_name(self, stuf_entiteit, field_name=None):

        if stuf_entiteit and not stuf_entiteit.is_entiteit():
            return stuf_entiteit.get_model().__name__ + 'Grp'

        if stuf_entiteit and field_name:
            if stuf_entiteit.heeft_kerngegevens():
                postfix = 'AntwoordKerngegevens'
            else:
                postfix = 'Antwoord'
            return '{}_{}_{}_{}'.format(self.name, stuf_entiteit.get_mnemonic(), field_name, postfix)
        if stuf_entiteit:
            if stuf_entiteit.heeft_kerngegevens():
                postfix = 'AntwoordKerngegevens'
            else:
                postfix = ''
            return '{}_{}_{}'.format(stuf_entiteit.get_mnemonic(), self.name, postfix)

    def create_object_model(self, stuf_entiteit=None):
        """
        From a StUFEntiteit create a hierarchy of ComplexModels for everything under the object element.
        """
        stuf_entiteit = stuf_entiteit or self.stuf_entiteit

        type_info = []
        if stuf_entiteit.is_entiteit():
            type_info.append(
                ('entiteittype', XmlAttribute(simple_types.Entiteittype, ref='entiteittype', ns=STUF_XML_NS))
            )

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

        if getattr(stuf_entiteit, 'append_object_model', False):
            for key, append_complex_model in stuf_entiteit.append_object_model:
                # assert False, append_complex_model.__dict__
                type_info.append((key, append_complex_model))

        for related_field in stuf_entiteit.get_related_fields():
            type_info.append(
                (related_field.field_name, self.create_object_model(related_field.stuf_entiteit).customize(max_occurs='unbounded'))
            )

        # Create spyne model for 'gerelateerde'
        # TODO [TECH]: In the WSDL this should be minOccurs and maxOccurs of 1.
        gerelateerde = stuf_entiteit.get_gerelateerde()
        if gerelateerde:
            _, gerelateerde_data = gerelateerde
            if isinstance(gerelateerde_data, tuple) or isinstance(gerelateerde_data, list):
                sub_type_info = []
                for relation_name, related_cls in gerelateerde_data:
                    _object_model = self.create_object_model(related_cls).customize(xml_choice_group='gerelateerde')
                    sub_type_info.append((relation_name, _object_model))

                # See Stuf 03.01 - 3.2.2 De structuur van een object, why this model does not have a 'entiteittype'
                # attribute.
                #
                # Het element <gerelateerde> mag ook als kind een <choice> bevatten met twee of meer elementen
                # met een attribute StUF:entiteittype en daarbinnen de elementen voor dat entiteittype. Het element
                # <gerelateerde> heeft dan geen attributes.
                #
                sub_model = self.create_reusable_model(
                    self.create_object_name(stuf_entiteit, 'gerelateerde'),
                    stuf_entiteit.get_namespace(), sub_type_info
                ).customize(min_occurs=1, max_occurs=1)  # TODO [TECH]: min/max_occurs does not show up in the WSDL for some reason.
                type_info.append(('gerelateerde', sub_model))
            else:
                related_cls = gerelateerde_data
                # TODO [TECH]: min/max_occurs does not show up in the WSDL for some reason.
                type_info.append(('gerelateerde', self.create_object_model(related_cls).customize(min_occurs=1, max_occurs=1)))

        # Build up spyne model
        field_mapping = stuf_entiteit.get_django_field_mapping()
        new_type_info = TypeInfo()
        file_fields = stuf_entiteit.get_file_fields()
        required_fields = stuf_entiteit.get_required_fields()
        for field_name, _, django_field in field_mapping:
            if field_name in file_fields:
                new_type_info[field_name] = BinaireInhoud
            else:
                min_occurs = 1 if field_name in required_fields else 0
                new_type_info[field_name] = django_field_to_spyne_model(django_field, min_occurs=min_occurs)

        complex_model = self.create_reusable_model(
            self.create_object_name(stuf_entiteit),
            stuf_entiteit.get_namespace(), new_type_info
        )
        complex_model.stuf_entiteit = stuf_entiteit

        for k, v in type_info:
            complex_model._type_info[k] = v

        for field_name, spyne_model, _ in stuf_entiteit.get_custom_fields():
            complex_model._type_info[field_name] = spyne_model

        complex_model._type_info = reorder_type_info(stuf_entiteit.get_fields(), complex_model._type_info)

        return complex_model

    def create_stuurgegevens_model(self):
        type_info = [
            ('berichtcode', Unicode.customize(type_name='BerichtcodeLa01')),
            ('zender', Systeem.customize(min_occurs=0)),
            ('ontvanger', Systeem.customize(min_occurs=0)),
            ('referentienummer', simple_types.Refnummer.customize(min_occurs=0)),
            ('tijdstipBericht', simple_types.Tijdstip.customize(min_occurs=0)),
            ('crossRefnummer', simple_types.Refnummer.customize(min_occurs=0)),
            # Technically: EntiteittypeBSL, EntiteittypeZAK, EntiteittypeEDC
            ('entiteittype', simple_types.Entiteittype),
        ]
        stuurgegevens_model = self.create_reusable_model(self.create_stuurgegevens_name(), STUF_XML_NS, type_info)
        return stuurgegevens_model

    def create_model(self):
        """
        Create the basic hierarchy of complex models for stuf, i.e. <antwoord><object></object></antwoord>
        """
        stuurgegevens_model = self.create_stuurgegevens_model()
        parameters_model = self.get_output_parameters_model()
        answer_model = self.create_object_model()
        namespace = ZKN_XML_NS
        antwoord_model = self.create_reusable_model(
            '{}_antwoord'.format(self.name), namespace, (('object', answer_model.customize(max_occurs='unbounded')), ))
        root_model = self.create_reusable_model(
            '{}_La01'.format(self.name), namespace, (
                ('stuurgegevens', stuurgegevens_model),
                ('parameters', parameters_model),
                ('antwoord', antwoord_model), ))
        return root_model

    def get_queryset(self, obj):
        """
        From a ComplexModel instance create a query.

        :param obj Instance of a ComplexModel
        :return queryset
        """
        django_model = self.stuf_entiteit.get_model()
        queryset = django_model.objects.all()
        return queryset.all()

    def create_output_parameters_data(self, input_parameters_obj):
        params = {'indicatorVervolgvraag': False}
        if not input_parameters_obj:
            return params
        if input_parameters_obj.indicatorVervolgvraag is True:
            params['indicatorVervolgvraag'] = True
        if hasattr(input_parameters_obj, 'indicatorAfnemerIndicatie'):
            params['indicatorAfnemerIndicatie'] = input_parameters_obj.indicatorAfnemerIndicatie
        if hasattr(input_parameters_obj, 'indicatorAantal'):
            params['aantalVoorkomens'] = self.total_objs
        return params

    def create_data(self, request_obj, output_model):
        gelijk_obj = request_obj.gelijk
        scope_obj = request_obj.scope.object if request_obj.scope else None
        input_parameters_obj = request_obj.parameters if request_obj.parameters else None
        objects = self.create_object_data(gelijk_obj, scope_obj, input_parameters_obj,
                                          self.get_queryset(request_obj), output_model)

        # TODO [TECH]: Maybe we should move the whole stuurgegevens (or at least zender/ontvanger) to the application level?
        # TODO [TECH]: Reference etc. should also be logged.
        return {
            'stuurgegevens': {
                'berichtcode': self.berichtcode,
                'zender': get_systeem_zender(request_obj.stuurgegevens.ontvanger),
                'ontvanger': get_ontvanger(request_obj.stuurgegevens.zender),
                # TODO [TECH]: Generate reference
                'referentienummer': create_unique_id(),
                'tijdstipBericht': stuf_datetime.now(),
                'crossRefnummer': request_obj.stuurgegevens.referentienummer or IgnoreAttribute(),
                'entiteittype': self.stuf_entiteit.get_mnemonic()
            },
            'parameters': self.create_output_parameters_data(input_parameters_obj),
            'antwoord': {
                'object': objects
            }
        }

    def get_fields_in_scope(self, stuf_entiteit, scope_obj, scope=None):
        """
        Returns a list of fields that should be in the response for this entity.
        """

        field_names = [field_name for field_name, _unused in stuf_entiteit.get_field_mapping()]

        # TODO [TECH]: raise ClientFoutChoices.stuf097 als zowel scope attribute als elementen zijn gebruikt.
        # TODO [TECH]: Implement other scope attribute choices, although it's
        # unclear why anyone would request anything else.
        if scope:  # in [ScopeChoices.alles, ScopeChoices....]
            return field_names

        if scope_obj:
            return [field_name for field_name in field_names if isinstance(getattr(scope_obj, field_name), Nil)]

        # No scope attribute nor a scope object is set for this entity.
        return []

    def create_order_args(self, stuf_entiteit, parameters_obj):
        """
        Based on the 'sortering' variable in the parameters element return a list of model fields for ordering.

        Returns an empty list if 'sortering' is missing, and raises an error if an invalid sortering variable
        is provided.
        """
        if not parameters_obj or not getattr(parameters_obj, 'sortering', None):
            return []
        para_model = self.get_input_parameters_model()()
        if not getattr(para_model, 'ordering', None):
            return []
        order_args = []
        if parameters_obj.sortering not in para_model.ordering.keys():
            raise StUFFault(ServerFoutChoices.stuf133)
        # Map sorting number versus the Entity-specific type of ordering
        ordering_fields = para_model.ordering[parameters_obj.sortering]
        for field in ordering_fields:
            order_args += [field]
        return order_args

    def create_limit_arg(self, stuf_entiteit, parameters_obj):
        """
        Based on the 'maximumAantal' variable in the parameters element return the number of objects to be returned

        Returns 0 if 'maximumAantal' is missing, and raises an error if a non-positive integer is used is provided.
        """
        if not parameters_obj or not getattr(parameters_obj, 'maximumAantal', None):
            return 0
        para_model = self.get_input_parameters_model()()
        if not getattr(para_model, 'maximumAantal', None):
            return 0
        limit = settings.ZAAKMAGAZIJN_DEFAULT_MAX_NR_RESULTS
        try:
            limit = int(parameters_obj.maximumAantal)
        except ValueError:
            raise StUFFault(ClientFoutChoices.stuf055)
        if limit < 0:
            raise EmptyResultError()
        return limit

    def get_model_data(self, stuf_entiteit, obj, filter_obj, scope_obj, parameters_obj, root_scope_obj, spyne_model):
        """
        See StUF 03.01 - 3.4.1 Het opnemen van elementen in een entiteit

        Return the data expected by the spyne model created by this factor for a given django model instance.
        """
        # TODO [KING]: What should happen when an relation is specified in the scope, but does not
        # not actually exist in the database (i.e. the foreign key is None), should all
        # the attributes of the relation be returned? For now, we return it with None.
        if obj is None and scope_obj:
            return None
        elif obj is None and scope_obj is None:
            raise EmptyResultError()

        scope = root_scope_obj.scope if hasattr(root_scope_obj, 'scope') else None

        model_answer = {}
        has_result = False
        fields_in_scope = self.get_fields_in_scope(stuf_entiteit, scope_obj, scope=scope)

        for field_name, _, value in stuf_entiteit.get_custom_fields():
            model_answer[field_name] = value

        for field_name, django_field_name, django_field in stuf_entiteit.get_django_field_mapping():
            spyne_field = get_spyne_field(spyne_model, field_name)
            if field_name not in fields_in_scope and spyne_field.Attributes.min_occurs == 0:
                model_answer[field_name] = IgnoreAttribute()
                continue

            model_answer[field_name] = to_spyne_value(
                get_model_value(obj, django_field_name), django_field, spyne_field
            )
            has_result = True

        if not has_result:
            raise EmptyResultError()

        return model_answer

    def _create_fundamenteel(self, stuf_entiteit, obj, filter_obj, scope_obj, parameters_obj, root_scope_obj, object_model):
        obj_answer = {}
        has_result = False
        try:
            obj_answer.update(self.get_model_data(
                stuf_entiteit=stuf_entiteit,
                obj=obj,
                filter_obj=filter_obj,
                scope_obj=scope_obj,
                parameters_obj=parameters_obj,
                root_scope_obj=root_scope_obj,
                spyne_model=object_model))
            has_result = True
        except EmptyResultError:
            pass

        #
        # Deal with 'related' foreign keys, (foreign keys which point to this model)
        #
        for related_field in stuf_entiteit.get_related_fields():
            child_filter_obj = getattr(filter_obj, related_field.field_name, None) if filter_obj else None
            child_scope_obj = getattr(scope_obj, related_field.field_name, None) if scope_obj else None
            child_parameters_obj = None  # TODO [TECH]: Taiga issue #208 ordering should be done on lower levels as well.

            # If the attribute 'scope' in the root scope object, and there is no Nil, or ComplexType
            # set in the scope, do not include the entity in the result.
            scope = root_scope_obj.scope if hasattr(root_scope_obj, 'scope') else None
            if scope is None and child_scope_obj is None:
                obj_answer[related_field.field_name] = IgnoreAttribute()
                continue

            kwargs = {
                'stuf_entiteit': related_field.stuf_entiteit,
                'scope_obj': child_scope_obj,
                'filter_obj': child_filter_obj,
                'parameters_obj': child_parameters_obj,
                'root_scope_obj': root_scope_obj,
                'object_model': get_spyne_field(object_model, related_field.field_name)
            }
            try:
                if isinstance(related_field, ForeignKeyRelation):
                    if related_field.fk_name == 'self':
                        fk_obj = obj
                    else:
                        fk_obj = getattr(obj, related_field.fk_name, None)
                    obj_answer[related_field.field_name] = [self._create_fundamenteel(obj=fk_obj, **kwargs), ]
                elif isinstance(related_field, OneToManyRelation):
                    if related_field.related_name == 'self':
                        obj_answer[related_field.field_name] = [self._create_fundamenteel(obj=obj, **kwargs), ]
                    else:
                        obj_answer[related_field.field_name] = self._create_object_data(queryset=getattr(obj, related_field.related_name), **kwargs)
                else:
                    raise NotImplementedError

            except EmptyResultError:
                obj_answer[related_field.field_name] = IgnoreAttribute()
            else:
                has_result = True

        #
        # Process the 'gerelateerde'
        #
        gerelateerde = stuf_entiteit.get_gerelateerde()
        if gerelateerde:
            gerelateerde_fk_name, gerelateerde_data = gerelateerde
            child_scope_obj = getattr(scope_obj, 'gerelateerde', None) if scope_obj else None
            #
            # Deal with polymorphic foreign key relations.
            #
            if isinstance(gerelateerde_data, tuple) or isinstance(gerelateerde_data, list):
                fk_object = getattr(obj, gerelateerde_fk_name)
                # TODO [TECH]: This being a callable will only work for 'beantwoordvraag', for updates
                # another method is required.
                fk_object = fk_object() if callable(fk_object) else fk_object
                assert hasattr(fk_object, 'is_type'), "The foreign key class should have a 'is_type' method to determine the subclass"
                child_obj = fk_object.is_type()
                obj_answer['gerelateerde'] = {}
                for relation_name, related_cls in gerelateerde_data:
                    if related_cls.get_model() is child_obj.__class__:
                        relation_scope_obj = getattr(child_scope_obj, relation_name) if child_scope_obj else None
                        try:
                            obj_answer['gerelateerde'][relation_name] = self._create_fundamenteel(
                                stuf_entiteit=related_cls,
                                obj=child_obj,
                                filter_obj=None,
                                scope_obj=relation_scope_obj,
                                parameters_obj=None,
                                root_scope_obj=root_scope_obj,
                                object_model=get_spyne_field(object_model, 'gerelateerde', relation_name)
                            )
                        except EmptyResultError:
                            pass
                        else:
                            has_result = True
                    else:
                        # TODO [TECH]: only one choice should show up in a choices element
                        # however, since we need specific control to deal with which elements should show up in the response
                        # and which ones should not show up in the result, I flipped the way spyne deals with None
                        # values, values with 'IgnoreAttribute()' are not serialized, and None values are serialized.
                        #
                        # This is a side-effect of that, and now we need to specify 'IgnoreAttribute()' here
                        obj_answer['gerelateerde'][relation_name] = IgnoreAttribute()
            #
            # Deal with normal foreign key relations
            #
            else:
                related_cls = gerelateerde_data
                fk_value = obj if gerelateerde_fk_name == 'self' else getattr(obj, gerelateerde_fk_name, None)
                try:
                    obj_answer['gerelateerde'] = self._create_fundamenteel(
                        stuf_entiteit=related_cls,
                        obj=fk_value,
                        filter_obj=None,
                        scope_obj=child_scope_obj,
                        parameters_obj=None,
                        root_scope_obj=root_scope_obj,
                        object_model=get_spyne_field(object_model, 'gerelateerde'))
                    has_result = True
                except EmptyResultError:
                    obj_answer['gerelateerde'] = IgnoreAttribute()

        tijdvak_geldigheid = stuf_entiteit.get_tijdvak_geldigheid()
        if tijdvak_geldigheid:
            has_result = True
            begin_geldigheid = get_model_value(
                obj, tijdvak_geldigheid['begin_geldigheid']
            ) if tijdvak_geldigheid['begin_geldigheid'] else None
            eind_geldigheid = get_model_value(
                obj, tijdvak_geldigheid['eind_geldigheid']
            ) if tijdvak_geldigheid['eind_geldigheid'] else None

            spyne_begin_geldigheid = get_spyne_field(object_model, 'tijdvakGeldigheid/beginGeldigheid')
            spyne_eind_geldigheid = get_spyne_field(object_model, 'tijdvakGeldigheid/eindGeldigheid')

            obj_answer['tijdvakGeldigheid'] = {
                'beginGeldigheid': to_spyne_value(begin_geldigheid, None, spyne_begin_geldigheid),
                'eindGeldigheid': to_spyne_value(eind_geldigheid, None, spyne_eind_geldigheid),
            }

        tijdvak_relatie = stuf_entiteit.get_tijdvak_relatie()
        if tijdvak_relatie:
            has_result = True
            begin_relatie = get_model_value(
                obj, tijdvak_relatie['begin_relatie']
            ) if tijdvak_relatie['begin_relatie'] else None
            eind_relatie = get_model_value(
                obj, tijdvak_relatie['eind_relatie']
            ) if tijdvak_relatie['eind_relatie'] else None

            spyne_begin_relatie = get_spyne_field(object_model, 'tijdvakRelatie/beginRelatie')
            spyne_eind_relatie = get_spyne_field(object_model, 'tijdvakRelatie/eindRelatie')

            obj_answer['tijdvakRelatie'] = {
                'beginRelatie': to_spyne_value(begin_relatie, None, spyne_begin_relatie),
                'eindRelatie': to_spyne_value(eind_relatie, None, spyne_eind_relatie),
            }

        tijdstip_registratie = stuf_entiteit.get_tijdstip_registratie()
        if tijdstip_registratie:
            has_result = True
            value = get_model_value(obj, tijdstip_registratie) if tijdstip_registratie else None
            spyne_tijdstip_registratie = get_spyne_field(object_model, 'tijdstipRegistratie')

            obj_answer['tijdstipRegistratie'] = to_spyne_value(value, None, spyne_tijdstip_registratie)

        if not has_result:
            raise EmptyResultError()

        if stuf_entiteit.is_entiteit():
            obj_answer['entiteittype'] = stuf_entiteit.get_mnemonic()
        return obj_answer

    def _create_object_data(self, stuf_entiteit, queryset, scope_obj, filter_obj, parameters_obj, root_scope_obj, object_model):
        """
        See StUF 03.01 6.3.3 and 6.4.2
        """
        from django.db.models.manager import Manager
        from django.db.models.query import QuerySet

        if isinstance(queryset, Manager) or isinstance(queryset, QuerySet):
            queryset = queryset
        elif callable(queryset):
            related_manager, filter_args = queryset()
            queryset = related_manager.filter(**filter_args)

        answer = []
        has_result = False
        query_args = create_query_args(filter_obj)
        order_args = self.create_order_args(stuf_entiteit, parameters_obj)
        limit_arg = self.create_limit_arg(stuf_entiteit, parameters_obj)
        qs = queryset.filter(**query_args).order_by(*order_args)

        if getattr(parameters_obj, 'indicatorAantal', False) is True:
            self.total_objs = qs.count()
        if limit_arg > 0:
            qs = qs[:limit_arg]

        for obj in qs:
            try:
                obj_answer = self._create_fundamenteel(
                    stuf_entiteit=stuf_entiteit,
                    obj=obj,
                    filter_obj=filter_obj,
                    scope_obj=scope_obj,
                    parameters_obj=parameters_obj,
                    root_scope_obj=root_scope_obj,
                    object_model=object_model)
            except EmptyResultError:
                pass
            else:
                has_result = True
                answer.append(obj_answer)
        if not has_result:
            raise EmptyResultError()
        return answer

    def create_object_data(self, filter_obj, scope_obj, parameters_obj, queryset, output_model):
        #
        # Filter out all objects, on the highest level, which aren't needed based on the entire search query early.
        # I know, I know. early optimalization is the root of all evil.
        #

        # TODO [TECH]: Taiga task #376 Implement support for nested queries.
        # query_args = create_query_args(filter_obj, recurse=True)
        query_args = {}

        object_model = get_spyne_field(output_model, 'antwoord/object')
        try:
            data = self._create_object_data(stuf_entiteit=self.stuf_entiteit,
                                            queryset=queryset.filter(**query_args).distinct(),
                                            scope_obj=scope_obj,
                                            filter_obj=filter_obj,
                                            parameters_obj=parameters_obj,
                                            root_scope_obj=scope_obj,
                                            object_model=object_model)
        except EmptyResultError:
            data = []

        return data

    def get_input_parameters_model(self):
        if hasattr(self.stuf_entiteit, 'input_parameters'):
            return self.stuf_entiteit.input_parameters
        return StufParameters

    def get_output_parameters_model(self):
        if hasattr(self.stuf_entiteit, 'output_parameters'):
            return self.stuf_entiteit.output_parameters
        return StufParameters
