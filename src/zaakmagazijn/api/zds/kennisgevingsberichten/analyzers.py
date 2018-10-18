from django.db import transaction

from ...stuf.choices import ServerFoutChoices
from ...stuf.faults import StUFFault
from ...stuf.protocols import Nil
from .choices import EntiteitType, MutatiesoortChoices, VerwerkingssoortChoices
from .operations import GroupAttributeOperation, get_operation


def iter_relations(obj1, obj2, field_name):
    relation_list1 = getattr(obj1, field_name, None)
    relation_list2 = getattr(obj2, field_name, None)

    # Depending on how 'maxOccurs' is set, spyne creates a list, or
    # or a Model. Always convert to a list to ease iteration.
    if relation_list1:
        relation_list1 = [relation_list1, ] if not isinstance(relation_list1, list) else relation_list1
        relations_length = len(relation_list1)
    if relation_list2:
        relation_list2 = [relation_list2, ] if not isinstance(relation_list2, list) else relation_list2
        relations_length = len(relation_list2)

    if not relation_list1 and not relation_list2:
        raise StopIteration()

    if relation_list1 and relation_list2 and len(relation_list1) != len(relation_list2):
        stuf_details = 'Het aantal {}-elementen komt niet overeen in de oude en de huidige situatie.'.format(field_name)
        raise StUFFault(ServerFoutChoices.stuf031, stuf_details=stuf_details)

    for i in range(relations_length):
        obj1 = relation_list1[i] if relation_list1 else None
        obj2 = relation_list2[i] if relation_list2 else None

        yield (obj1, obj2)


class Mutation:
    def __init__(self, stuf_entiteit, data, mutatiesoort):
        """
        :param data ComplexType data as received from Spyne.
        :param mutatiesoort str
        :param verwerkingssoort str Verwerkingssoort of the object in the topfundamenteel.
        """
        self.stuf_entiteit = stuf_entiteit
        self.data = data
        self.mutatiesoort = mutatiesoort

    def process(self):
        self.operation.process_fundamenteel()

    def verify_entity_type(self, stuf_entiteit, obj):
        # Verify if the given entity type (entiteittype) matches.
        if obj and stuf_entiteit.get_mnemonic() != obj.entiteittype:
            stuf_details = 'Het entiteittype \'{}\' komt niet overeen met het verwachtte entiteittype \'{}\''.format(
                obj.entiteittype, stuf_entiteit.get_mnemonic()
            )
            raise StUFFault(ServerFoutChoices.stuf031, stuf_details=stuf_details)

    def create_operation(self, stuf_entiteit, entiteit_type, obj1, obj2, parent_operation):
        """
        From the data retrieved from the service build up a list of operations that
        need to be executed for the update. This merges together the two element
        trees: object[0] and object[1] in a StUF-update and creates a new tree with
        these two trees combined.
        """
        # Determine the kind of operation this is.
        operation = get_operation(stuf_entiteit, entiteit_type, self.mutatiesoort, obj1, obj2, parent_operation)
        if operation is None:
            raise StUFFault(
                ServerFoutChoices.stuf058,
                stuf_details='Kan dit bericht niet verwerken met een verwerkingssoort \'{}\' voor het oude voorkomen '
                             'en \'{}\' voor het huidige voorkomen.'.format(
                    getattr(obj1, 'verwerkingssoort', '?'), getattr(obj2, 'verwerkingssoort', '?')
                ))

        self.verify_entity_type(stuf_entiteit, obj1)
        self.verify_entity_type(stuf_entiteit, obj2)

        def get_field(obj, field_name):
            if obj is None:
                return None
            return getattr(obj, field_name, None)

        for related_field in stuf_entiteit.get_related_fields(gegevensgroepen=False):
            for child_obj1, child_obj2 in iter_relations(obj1, obj2, related_field.field_name):
                child_operation = self.create_operation(
                    related_field.stuf_entiteit, EntiteitType.relatie_entiteit, child_obj1, child_obj2, parent_operation=operation)
                operation.add_relation(related_field, child_operation)

        #
        # TODO [KING]: For attributes/gegevensgroepen that can occur more than 1 times, It is unclear how these should be processed.
        # See the discussion below, and the excerpt from the StUF standard.
        #
        # See https://discussie.kinggemeenten.nl/discussie/gemma/stuf-zkn-310/verwerken-van-kenmerk-een-update-van-een-zaak-zaklk01#comment-5308
        #
        # See 5.2.4 Het vullen van de <object> elementen
        #
        # Indien in een kennisgevingbericht een element voor een attribuutwaarde meer dan één keer mag voorkomen, dan
        # worden bij het toevoegen, wijzigen of verwijderen van de waarde van dat element alle waarden voor dat element
        # in het bericht opgenomen. Bij het toevoegen van een tweede telefoonnummer wordt het huidige telefoonnummer
        # dus zowel in het ‘oude’ als het ‘huidige’ voorkomen opgenomen.
        #

        # Process groepattributen separately, they are unique little snowflakes.
        if obj1 and (obj1.verwerkingssoort == 'T' or obj1.verwerkingssoort == 'W') \
                or obj2 and (obj2.verwerkingssoort == 'T' or obj2.verwerkingssoort == 'W'):
            for gegevensgroep in stuf_entiteit.get_gegevensgroepen():
                groepattributen_old = [child_obj1 for child_obj1, child_obj1 in iter_relations(obj1, obj2, gegevensgroep.field_name)]
                groepattributen_current = [child_obj2 for child_obj1, child_obj2 in iter_relations(obj1, obj2, gegevensgroep.field_name)]
                # Taiga #416 -- Negeer bij updateZaak een groepattribuut als deze niet expliciet wordt meegegeven
                if obj1 and obj2 and obj1.verwerkingssoort == 'W' and obj2.verwerkingssoort == 'W' and \
                   (groepattributen_old == [] and groepattributen_current == []):
                    continue
                operation.add_relation(
                    gegevensgroep, GroupAttributeOperation(gegevensgroep.stuf_entiteit, groepattributen_old, groepattributen_current))

        #
        # Either the old or new situation can be Nil, in that case there is no 'gerelateerde'.
        #
        gerelateerde = stuf_entiteit.get_gerelateerde()
        obj1_gerelateerde = get_field(obj1, 'gerelateerde')
        obj2_gerelateerde = get_field(obj2, 'gerelateerde')
        if gerelateerde and (obj1_gerelateerde or obj2_gerelateerde):
            fk_name, data = gerelateerde

            if isinstance(data, tuple) or isinstance(data, list):
                relation1 = relation2 = None
                stuf_entiteit1 = stuf_entiteit2 = None
                if obj1_gerelateerde:
                    for relation_name, related_cls in data:
                        stuf_entiteit1 = related_cls
                        relation1 = getattr(obj1_gerelateerde, relation_name)
                        if relation1:
                            break
                if obj2_gerelateerde:
                    for relation_name, related_cls in data:
                        stuf_entiteit2 = related_cls
                        relation2 = getattr(obj2_gerelateerde, relation_name)
                        if relation2:
                            break

                # if stuf_entiteit1 is None and stuf_entiteit2 is None:
                assert not (stuf_entiteit1 is None and stuf_entiteit2 is None)

                if (stuf_entiteit1 is None or stuf_entiteit2 is None) or stuf_entiteit1 == stuf_entiteit2:
                    stuf_entiteit = stuf_entiteit1 or stuf_entiteit2
                    operation.add_related(fk_name, self.create_operation(stuf_entiteit, EntiteitType.gerelateerde, relation1, relation2, operation))
                else:
                    operation.add_related(fk_name, self.create_operation(stuf_entiteit1, EntiteitType.gerelateerde, relation1, None, operation))
                    operation.add_related(fk_name, self.create_operation(stuf_entiteit2, EntiteitType.gerelateerde, None, relation2, operation))
            else:
                related_cls = data
                stuf_entiteit1 = stuf_entiteit2 = related_cls
                relation1 = obj1_gerelateerde
                relation2 = obj2_gerelateerde

                operation.add_related(fk_name, self.create_operation(stuf_entiteit1, EntiteitType.gerelateerde, relation1, relation2, operation))

        return operation


class CreateMutation(Mutation):
    @classmethod
    def from_data(cls, stuf_entiteit, data):
        assert data.parameters.mutatiesoort == 'T', 'Updates should always have mutatiesoort "T"'

        mutation = cls(stuf_entiteit, data, data.parameters.mutatiesoort)
        mutation.operation = mutation.create_operation(stuf_entiteit, EntiteitType.topfundamenteel, None, data.object, None)
        # mutation.operation.print_tree()
        return mutation


class UpdateMutation(Mutation):
    @classmethod
    def from_data(cls, stuf_entiteit, data):
        """
        Make sure that only situatie 'Wijziging' (W) from StUF - Tabel 5.3 is allowed.
        """
        assert len(data.object) == 2, 'Updates should always have two objects'
        obj1, obj2 = data.object[0], data.object[1]

        if data.parameters.mutatiesoort != MutatiesoortChoices.wijziging:
            error_msg = 'Alleen de mutatiesoort \'{}\' is toegestaan'.format(MutatiesoortChoices.wijziging)
            # StUF058: Proces voor afhandelen bericht geeft fout
            raise StUFFault(ServerFoutChoices.stuf058, stuf_details=error_msg)

        # TODO [KING]: 'I' is technically also allowed See StUF 3.01 - Tabel 5.3
        if (isinstance(obj1, Nil) or obj2 is None) or (isinstance(obj2, Nil) or obj2 is None):
            error_msg = 'Zowel oud als huidig moeten worden gevuld voor een (W)ijziging.'.format(VerwerkingssoortChoices.wijziging)
            # StUF058: Proces voor afhandelen bericht geeft fout
            raise StUFFault(ServerFoutChoices.stuf058, stuf_details=error_msg)

        if obj1.verwerkingssoort != VerwerkingssoortChoices.wijziging or obj2.verwerkingssoort != VerwerkingssoortChoices.wijziging:
            error_msg = 'Alleen de verwerkingssoort \'{}\' is toegestaan in het topfundamenteel.'.format(VerwerkingssoortChoices.wijziging)
            # StUF058: Proces voor afhandelen bericht geeft fout
            raise StUFFault(ServerFoutChoices.stuf058, stuf_details=error_msg)

        mutation = cls(stuf_entiteit, data, data.parameters.mutatiesoort)
        mutation.operation = mutation.create_operation(stuf_entiteit, EntiteitType.topfundamenteel, obj1, obj2, None)
        # mutation.operation.print_tree()

        return mutation


@transaction.atomic()
def process_update(stuf_entiteit, data):
    """
    Process a StUF 3.01 kennisgevingsbericht with mutatiesoort 'W' (update)

    :param stuf_entiteit StUFEntiteit The stuf entiteit that is used in the topfundamenteel of the update request.
    :param data ComplexModel a spyne complex model which contains the StUF update request.
    """
    mutation = UpdateMutation.from_data(stuf_entiteit, data)
    mutation.process()


@transaction.atomic()
def process_create(stuf_entiteit, data):
    """
    Process a StUF 3.01 kennisgevingsbericht with mutatiesoort 'T' (create)

    :param stuf_entiteit StUFEntiteit The stuf entiteit that is used in the topfundamenteel of the create request.
    :param data ComplexModel a spyne complex model which contains the StUF create request.
    """
    mutation = CreateMutation.from_data(stuf_entiteit, data)
    mutation.process()
