"""

StUF 3.01 - Tabel 5.3 (Regels voor de opbouw van een bericht)

|-----------------------------------|--------------|------------------|------------|-----------------|----------------|---------------------|--------------------------------------|
| Situatie                          | mutatiesoort | verwerkingssoort | Oud/Huidig | beginGeldigheid | eindGeldigheid | tijdstipRegistratie | Overige elementen                    |
|-----------------------------------|--------------|------------------|------------|-----------------|----------------|---------------------|--------------------------------------|
| Relevant geworden                 | T            | T                | Huidig     | N               | G              | N                   | Alle bekende elementen               |
|-----------------------------------|--------------|------------------|------------|-----------------|----------------|---------------------|--------------------------------------|
| Wijziging                         | W            | W                | Oud        | OW              | N              | -                   | K/Sleutel + te wijzigen elementen*   |
|                                   |              |                  | Huidig     | N               | G              | N                   | K/Sleutel + gewijzigde elementen*    |
|-----------------------------------|--------------|------------------|------------|-----------------|----------------|---------------------|--------------------------------------|
| Correctie zonder formele historie | C            | W                | Oud        | OC              | G              | -                   | K/Sleutel + te corrigeren elementen* |
|                                   |              |                  | Huidig     | N               | G              | N                   | K/Sleutel + gecorrigeerde elementen* |
|-----------------------------------|--------------|------------------|------------|-----------------|----------------|---------------------|--------------------------------------|
| Correctie met formele historie    | F            | W                | Oud        | OC              | G              | -                   | K/Sleutel + te corrigeren elementen* |
|                                   |              |                  | Huidig     | N               | G              | N                   | K/Sleutel + gecorrigeerde elementen* |
|-----------------------------------|--------------|------------------|------------|-----------------|----------------|---------------------|--------------------------------------|
| Sleutelwijziging                  | C            | S                | Oud        | -               | -              | -                   | K* en zo mogelijk sleutelOntvangend  |
|                                   |              |                  | Huidig     | -               | -              | N                   | K* en zo mogelijk sleutelOntvangend  |
|-----------------------------------|--------------|------------------|------------|-----------------|----------------|---------------------|--------------------------------------|
| Ontdubbeling                      | C            | O                | Oud        | -               | -              | -                   | K* en zo mogelijk sleutelOntvangend  |
|                                   |              |                  | Huidig     | -               | -              | N                   | K* en zo mogelijk sleutelOntvangend  |
|-----------------------------------|--------------|------------------|------------|-----------------|----------------|---------------------|--------------------------------------|
| Irrelevant geworden               | V            | V                | Huidig     | -               | -              | N                   | K/Sleutel*                           |
|-----------------------------------|--------------|------------------|------------|-----------------|----------------|---------------------|--------------------------------------|
| Identificatie                     | "W, F of C"  | I                | Oud        | -               | -              | -                   | K/Sleutel*                           |
|                                   |              |                  | Huidig     | -               | -              | -                   | K/Sleutel*                           |
|-----------------------------------|--------------|------------------|------------|-----------------|----------------|---------------------|--------------------------------------|


StUF 3.01 - Tabel 5.5 (Regels voor het vullen van de attributen en elementen binnen een relatie-entiteit)


|------------------------------------------|--------------|------------|------------------|------------------|----------------|---------------------|------------------|--------------|--------------|------------------------------|-----------------------------|-----------------------|-------------------|----------------|
|                                          |              |            |                  | Relatie-entiteit |                |                     |                  |              |              |                              |                             | Gerelateerde entiteit |                   |                |
|------------------------------------------|--------------|------------|------------------|------------------|----------------|---------------------|------------------|--------------|--------------|------------------------------|-----------------------------|-----------------------|-------------------|----------------|
| Soort kennisgeving                       | mutatiesoort | Oud/Huidig | Topfundamenteel  |                  |                |                     |                  |              |              |                              |                             |                       |                   |                |
|------------------------------------------|--------------|------------|------------------|------------------|----------------|---------------------|------------------|--------------|--------------|------------------------------|-----------------------------|-----------------------|-------------------|----------------|
|                                          |              |            | Verwerkingssoort | beginGeldigheid  | eindGeldigheid | tijdstipRegistratie | verwerkingssoort | beginRelatie | eindRelatie  | Rest inhoud                  | Sleutel-Verzendend          | Verwerkings-soort     | Element-inhoud    |
|------------------------------------------|--------------|------------|------------------|------------------|----------------|---------------------|------------------|--------------|--------------|------------------------------|-----------------------------|-----------------------|-------------------|----------------|
| Toevoegen relatie bij                    | T            | Huidig     | T                | B                | G              | N                   | T                | N            | G            | Alles                        | V                           |                       | I of T            | K/sleutel      |
| toevoegen object                         |              |            |                  |                  |                |                     |                  |              |              |                              |                             |                       |                   |                |
|------------------------------------------|--------------|------------|------------------|------------------|----------------|---------------------|------------------|--------------|--------------|------------------------------|-----------------------------|-----------------------|-------------------|----------------|
| Toevoegen relatie bij wijzigen object    | W            | Oud        | W/I              | -                | -              | -                   | T                | -            | -            | Leeg                         | -                           |                       | -                 | -              |
|                                          |              | Huidig     | W/I              | B                | G              | N                   | T                | N            | G            | Alles                        | V                           | I of T                | K/Sleutel         |
|------------------------------------------|--------------|------------|------------------|------------------|----------------|---------------------|------------------|--------------|--------------|------------------------------|-----------------------------|-----------------------|-------------------|----------------|
| Wijzigen relatie                         | W            | Oud        | W/I              | OW               | N              | -                   | W                | "K, O"       | "K, G"       | K/Sleutel + te wijzigen geg. | V                           |                       | I                 | K/Sleutel      |
|                                          |              | Huidig     | W/I              | N                | G              | N                   | W                | "K, O"       | "K, G"       | K/Sleutel + gewijzigde geg.  | V                           | I                     | K/Sleutel         |
|------------------------------------------|--------------|------------|------------------|------------------|----------------|---------------------|------------------|--------------|--------------|------------------------------|-----------------------------|-----------------------|-------------------|----------------|
| Corrigeren relatie zonder form. historie | C            | Oud        | W/I              | OC               | G              | -                   | W                | "K, O"       | "K, O"       | K/Sleutel + te corrig. geg.  | V                           |                       | I                 | K/Sleutel      |
|                                          |              | Huidig     | W/I              | N                | G              | N                   | W                | "K, O"       | "K, O"       | K/Sleutel + gecorrig. geg.   | V                           | I                     | K/Sleutel         |
|------------------------------------------|--------------|------------|------------------|------------------|----------------|---------------------|------------------|--------------|--------------|------------------------------|-----------------------------|-----------------------|-------------------|----------------|
| Corrigeren relatie met formele historie  | F            | Oud        | W/I              | OC               | G              | -                   | W                | "K, O"       | "K, O"       | K/Sleutel + te corrig. geg.  | V                           |                       | I                 | K/Sleutel      |
|                                          |              | Huidig     | W/I              | N                | G              | N                   | W                | "K, O"       | "K, O"       | K/Sleutel + gecorrig. geg.   | V                           | I                     | K/Sleutel         |
|------------------------------------------|--------------|------------|------------------|------------------|----------------|---------------------|------------------|--------------|--------------|------------------------------|-----------------------------|-----------------------|-------------------|----------------|
| Verwijderen relatie                      | W[3]         | Oud        | W/I              | -                | -              | -                   | V                | "K, O"       | "K, G"       | K/Sleutel                    | V                           |                       | I                 | K/Sleutel      |
|                                          |              | Huidig     | W/I              | -                | -              | -                   | V                | -            | -            |                              | Leeg                        | -                     | -                 | -              |
|------------------------------------------|--------------|------------|------------------|------------------|----------------|---------------------|------------------|--------------|--------------|------------------------------|-----------------------------|-----------------------|-------------------|----------------|
| Beëindigen relatie                       | W            | Oud        | W/I              | E                | G              | N                   | E                | O            | N            | K/Sleutel                    | V                           |                       | I                 | K/Sleutel      |
|                                          |              | Huidig     | W/I              | -                | -              | -                   | E                | -            | -            |                              | Leeg                        | -                     | -                 | -              |
|------------------------------------------|--------------|------------|------------------|------------------|----------------|---------------------|------------------|--------------|--------------|------------------------------|-----------------------------|-----------------------|-------------------|----------------|
| Vervangen relatie                        | "W, C, F"    | Oud        | W/I              | E                | G              | N                   | R                | O            | N            | K/Sleutel                    | V                           |                       | I                 | K/Sleutel      |
|                                          |              | Huidig     | W/I              | B                | G              | N                   | R                | N            | G            |                              | Alles                       | V                     | I of T            | K/Sleutel      |
|------------------------------------------|--------------|------------|------------------|------------------|----------------|---------------------|------------------|--------------|--------------|------------------------------|-----------------------------|-----------------------|-------------------|----------------|
| Correctie toevoeging van een relatie     | "C, F"       | Oud        | W/I              | B                | G              | N                   | V                | "K, O"       | "K, G"       | K/Sleutel                    | V                           |                       | I                 | K/Sleutel      |
|                                          |              | Huidig     | W/I              | -                | -              | -                   | V                | -            | -            |                              | Leeg                        | -                     | -                 | -              |
|------------------------------------------|--------------|------------|------------------|------------------|----------------|---------------------|------------------|--------------|--------------|------------------------------|-----------------------------|-----------------------|-------------------|----------------|
| Identificatie                            | "W, C, F"    | Oud        | W/I/V/S          | -                | -              | -                   | I                | "K, O"       | "K, G"       | K/Sleutel                    | V                           |                       | I                 | K/Sleutel      |
|                                          |              | Huidig     | W/I/V/S          | -                | -              | -                   | I                | "K, O"       | "K, G"       |                              | K/Sleutel                   | V                     | I                 | K/Sleutel      |
|------------------------------------------|--------------|------------|------------------|------------------|----------------|---------------------|------------------|--------------|--------------|------------------------------|-----------------------------|-----------------------|-------------------|----------------|
| Identificatie bij irrelevant worden      | V            | Huidig     | V                | -                | -              | -                   | I                | "K, O"       | "K, G"       | K/Sleutel                    | V                           |                       | I                 | K/Sleutel      |
|------------------------------------------|--------------|------------|------------------|------------------|----------------|---------------------|------------------|--------------|--------------|------------------------------|-----------------------------|-----------------------|-------------------|----------------|
| Sleutelwijziging/                        | "C, F"       | Oud        | I                | -                | -              | -                   | S/O              | "K, O"       | "K, G"       | K + sleutelVerzendend        | V                           |                       | I                 | K/Sleutel      |
| ontdubbeling                             |              |            |                  |                  |                |                     |                  |              |              |                              |                             |                       |                   |                |
|                                          |              | Huidig     | I                | -                | -              | N                   | S/O              | "K, O"       | "K, G"       |                              | K + sleutelVerzendend       | V                     | I                 | K/Sleutel      |
|------------------------------------------|--------------|------------|------------------|------------------|----------------|---------------------|------------------|--------------|--------------|------------------------------|-----------------------------|-----------------------|-------------------|----------------|


StUF 3.01 - Tabel 5.7 (Invullen attribute StUF:verwerkingssoort in de topfundamenteel, relaties en de gerelateerde)

|                                        |              |            |                  |                  |                       |
|----------------------------------------|--------------|------------|------------------|------------------|-----------------------|
| Soort kennisgeving                     |              |            | verwerkingssoort |                  |                       |
|----------------------------------------|--------------|------------|------------------|------------------|-----------------------|
|                                        | mutatiesoort | Oud/Huidig |                  |                  |                       |
|                                        |              |            | Topfundamenteel  | Relatie-entiteit | Gerelateerde entiteit |
|----------------------------------------|--------------|------------|------------------|------------------|-----------------------|
| Toevoegen relatie bij toevoegen object | T            | Huidig     | T                | T                | I/T                   |
|----------------------------------------|--------------|------------|------------------|------------------|-----------------------|
| Toevoegen relatie bij wijzigen object  | W            | Oud        | I/W              | T                | -                     |
|                                        |              | Huidig     | I/W              | T                | I/T                   |
|----------------------------------------|--------------|------------|------------------|------------------|-----------------------|
| Wijzigen gerelateerd object            | W            | Oud        | I/W              | I/W              | I/W                   |
|                                        |              | Huidig     | I/W              | I/W              | I/W                   |
|----------------------------------------|--------------|------------|------------------|------------------|-----------------------|
| Corrigeren object                      | "C, F"       | Oud        | I/W              | I/W              | I                     |
|                                        |              | Huidig     | I/W              | I/W              | I                     |
|----------------------------------------|--------------|------------|------------------|------------------|-----------------------|
| Vervangen relatie                      | W            | Oud        | I/W              | R                | I                     |
|                                        |              | Huidig     | I/W              | R                | I/T                   |
|----------------------------------------|--------------|------------|------------------|------------------|-----------------------|
"""
from django.db.models import Manager

from zaakmagazijn.rgbz_mapping.manager import ProxyRelatedManager

from ...stuf import ForeignKeyRelation, OneToManyRelation
from ...stuf.protocols import Nil
from .choices import MutatiesoortChoices
from .objects import KennisgevingObject


class VirtualRelatedManager:
    def __init__(self, django_obj):
        self.django_obj = django_obj

    def create(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self.django_obj, key, value)
        self.django_obj.full_clean()
        self.django_obj.save()
        return self.django_obj

    def get(self, **kwargs):
        return self.django_obj


class BaseOperation:
    """
    Base class for a Operation, which should be created for every supported
    'verwerkingssoort'. Every operation in itself can have zero or more
    relations (relatie-entiteiten) and 0 to 2 related operations (gerelateerde).

    Every node has obj1 (old) and obj2 (new) specified. In the case of a
    mutatiesoort 'T' (creeer* service) obj1 will always be None.
    """

    def __init__(self, stuf_entiteit, obj1, obj2):
        """
        :param stuf_entiteit StUFEntiteit Expected stuf entiteit.
        :param obj1 ComplexModel old situation
        :param obj2 ComplexModel current situation
        """
        self.stuf_entiteit = stuf_entiteit
        self.obj1 = obj1
        self.obj2 = obj2
        self.relations = []

        """
        'gerelateerde' field in the SOAP request. Can be a list either 0, 1 or 2 operations.
        Either no, the old, the current or both operations can be specified.
        """
        self.related = []

    def add_relation(self, relation, operation):
        self.relations.append((relation, operation), )

        if self.obj1 and operation.obj1:
            self.obj1.add_obj_relation(relation, operation.obj1)
        if self.obj2 and operation.obj2:
            self.obj2.add_obj_relation(relation, operation.obj2)

    def add_related(self, fk_name, operation):
        # TODO [TECH]: Make sure self.related is sorted: operation with obj1 first, then
        # operation with obj2.
        self.related.append((fk_name, operation), )

        if self.obj1 and operation.obj1:
            self.obj1.add_obj_related(fk_name, operation.obj1)
        if self.obj2 and operation.obj2:
            self.obj2.add_obj_related(fk_name, operation.obj2)

    @classmethod
    def can_process(cls, stuf_entiteit, entiteit_type, mutatiesoort, obj1, obj2, parent_operation):
        raise NotImplementedError

    def get_related_fk_name(self):
        assert len(self.related) <= 2

        if len(self.related) == 1:
            related_name, _ = self.related[0]
            return related_name

        related_name1, _ = self.related[0]
        related_name2, _ = self.related[1]

        assert related_name1 == related_name2
        return related_name1

    def process_gerelateerde(self, extra_on_create=None):
        """
        A gerelateerde can have both 0, 1 or 2 list entries.
        """

        assert len(self.related) != 0, "Trying to process the gerelateerde, while it isn't defined."

        if len(self.related) == 1:
            related_fk_name, related_operation = self.related[0]
            obj1, obj2 = related_operation.process_fundamenteel(extra_on_create=extra_on_create)
        if len(self.related) == 2:
            _, related_operation1 = self.related[0]
            _, related_operation2 = self.related[1]
            assert related_operation1.obj1 is not None
            assert related_operation2.obj2 is not None

            obj1, _ = related_operation1.process_fundamenteel(extra_on_create=extra_on_create)
            _, obj2 = related_operation2.process_fundamenteel(extra_on_create=extra_on_create)

        return obj1, obj2

    def get_related_manager(self, django_obj, relation):
        related_name = relation.related_name
        if related_name == 'self':
            related_manager = VirtualRelatedManager(django_obj)
            default_kwargs = {}
        else:
            related_attribute = getattr(django_obj, related_name)
            if isinstance(related_attribute, Manager) or isinstance(related_attribute, ProxyRelatedManager):
                related_manager, default_kwargs = related_attribute, {}
            elif callable(related_attribute):
                related_manager, default_kwargs = related_attribute()
            else:
                raise AssertionError('the related_name attribute on the django object is neither a related '
                                     'manager nor a method which returns a related manager and default kwargs')
        return related_manager, default_kwargs

    def process_fake_relations(self):
        """
        Process relatie-entiteiten which are ForeignKeys.
        """
        obj1_kwargs = {}
        obj2_kwargs = {}
        for relation, child_operation in self.relations:
            if (child_operation.related and isinstance(relation, ForeignKeyRelation) and all([field_name == 'self' for field_name, operation in child_operation.related])):
                obj1, obj2 = child_operation.process_gerelateerde()
                obj1_kwargs[relation.fk_name] = obj1
                obj2_kwargs[relation.fk_name] = obj2
            if (isinstance(relation, OneToManyRelation) and relation.related_name == 'self'):
                fk_name = child_operation.get_related_fk_name()
                obj1, obj2 = child_operation.process_gerelateerde()
                obj1_kwargs[fk_name] = obj1
                obj2_kwargs[fk_name] = obj2
        return obj1_kwargs, obj2_kwargs

    def process_relations(self, django_obj):
        """
        :param django_obj The current (huidige) django obj, after any operations (in the current operation) have been performed.
        """

        # Process relatie-entiteiten.
        for relation, child_operation in self.relations:
            if not (child_operation.related and isinstance(relation, ForeignKeyRelation) and all([field_name == 'self' for field_name, operation in child_operation.related])) or (isinstance(relation, OneToManyRelation) and relation.related_name == 'self'):
                child_operation.process_relatie_entiteit(django_obj, relation)

    def process_virtual_fields(self, django_obj, obj):
        """
        Ensures that setters for virtual fields are called.
        """
        for django_field_name, value in obj.get_virtual_obj_kwargs().items():
            setattr(django_obj, django_field_name, value)

    def print_tree(self):
        self._print_tree(self)

    @classmethod
    def _out(cls, msg, indent):
        tabs = '  ' * indent
        print(tabs + msg)

    @classmethod
    def _print_tree(cls, operation, indent=0):
        new_indent = indent + 1
        cls._out('{}('.format(operation.__class__.__name__), indent)
        cls._out('entititeit: {}'.format(operation.stuf_entiteit.get_mnemonic()), indent=new_indent)
        obj1 = str(operation.obj1) if operation.obj1 else 'None'
        obj2 = str(operation.obj2) if operation.obj2 else 'None'
        cls._out('obj1={}'.format(obj1), indent=new_indent)
        cls._out('obj2={}'.format(obj2), indent=new_indent)
        if operation.relations:
            cls._out('relations=[', indent=new_indent)
            for related_name, child_operation in operation.relations:
                cls._print_tree(child_operation, indent=indent + 1)
            cls._out('],', indent=new_indent)
        if operation.related:
            cls._out('related=[', indent=new_indent)
            for related_name, child_operation in operation.related:
                cls._print_tree(child_operation, indent=indent + 1)
            cls._out('])', indent=new_indent)
        cls._out(')', indent)


class IdentifyOperation(BaseOperation):
    """
    Operation used to identify a given entity, this can be either in the
    old or in the current situation.

    Either obj1 or obj2 can be filled.
    """
    verwerkingssoort = 'I'

    @classmethod
    def can_process(cls, stuf_entiteit, entiteit_type, mutatiesoort, obj1, obj2, parent_operation):
        # TODO [TECH]: This does not verify the 'verwerkingssoort' that can be set in the nil case.

        obj1_exists = not (obj1 is None or obj1.is_nil())
        obj2_exists = not (obj2 is None or obj2.is_nil())

        if mutatiesoort == MutatiesoortChoices.toevoeging:
            if not obj1_exists and obj2_exists and obj2.obj_verwerkingssoort == 'I':
                return True
        elif mutatiesoort == MutatiesoortChoices.wijziging:
            if not obj1_exists and obj2_exists and obj2.obj_verwerkingssoort == 'I':
                return True

            if not obj2_exists and obj1_exists and obj1.obj_verwerkingssoort == 'I':
                return True

            if obj1_exists and obj1.obj_verwerkingssoort == 'I' and obj2_exists and obj2.obj_verwerkingssoort == 'I':
                return True

        return False

    def process_relatie_entiteit(self, parent_django_obj, relation):
        """
        See StUF 03.01 - 5.2.6 Het vullen van relatie-entiteiten en gerelateerde entiteiten
            * 9. Mutatiesoort 'W', 'F' of 'C' en verwerkingssoort 'I':Relatie is opgenomen
                 als kerngegeven of omdat gerelateerde
        """
        if isinstance(relation, OneToManyRelation):
            related_manager, default_kwargs = self.get_related_manager(parent_django_obj, relation)

            gerelateerde_obj1, gerelateerde_obj2 = self.process_gerelateerde(extra_on_create=default_kwargs)
            related_fk_name = self.get_related_fk_name()

            if self.obj1:
                extra = {related_fk_name: gerelateerde_obj1}
                self.obj1.get(related_manager=related_manager, extra=extra)
            if self.obj2:
                extra = {related_fk_name: gerelateerde_obj2}
                self.obj2.get(related_manager=related_manager, extra=extra)
            return None
        else:
            raise NotImplementedError

    def process_fundamenteel(self, extra_on_create=None):
        """
        See StUF 03.01 - 5.2.5 Het vullen van de <object> elementen in een topfundamenteel
            * 6. Mutatiesoort 'W', 'F' of 'C' en verwerkingssoort 'I': Identificatie
        """
        django_obj1, django_obj2 = None, None

        # TODO [TECH]: If they're both specified, these should be the same.
        if self.obj1:
            django_obj1 = self.obj1.get()

        if self.obj2:
            django_obj2 = self.obj2.get()

            assert django_obj2
            self.process_relations(django_obj2)

        return django_obj1, django_obj2


class CreateOperation(BaseOperation):
    """
    Create a new entity based on data given in the current situation.
    The old situation should be either Nil or None.

    """
    verwerkingssoort = 'T'

    @classmethod
    def can_process(cls, stuf_entiteit, entiteit_type, mutatiesoort, obj1, obj2, parent_operation):
        obj1_exists = not (obj1 is None or obj1.is_nil())
        obj2_exists = not (obj2 is None or obj2.is_nil())

        if mutatiesoort == MutatiesoortChoices.toevoeging:
            if not obj1_exists and obj2_exists and obj2.obj_verwerkingssoort == 'T':
                return True
        if mutatiesoort == MutatiesoortChoices.wijziging:
            # TODO [TECH]: This does not verify the 'verwerkingssoort' that can be set in the nil case.
            if not obj1_exists and obj2_exists and obj2.obj_verwerkingssoort == 'T':
                return True

        return False

    def process_fundamenteel(self, extra_on_create=None):
        """
        Create the 'fundamenteel' for the new situation

        For mutatiesoort 'T', see: StUF 03.01 - 5.2.5 Het vullen van de <object> elementen in een topfundamenteel
            * 1. Mutatiesoort 'T' en verwerkingssoort 'T': een fundamenteel is relevant geworden voor de zender

        Also, see: StUF 03.01 - 5.2.7 Toevoegen/wijzigen gerelateerde entiteit
        """

        # First do a 'get', to see if the object exists.
        django_model = self.stuf_entiteit.get_model()

        try:
            django_obj = self.obj2.get(raise_fault=False)
        except django_model.DoesNotExist:
            # If not, we need to process any required Foreign Keys first.
            obj1_kwargs, obj2_kwargs = self.process_fake_relations()

            # And then, create the object
            extra_on_create = extra_on_create or {}
            extra_on_create.update(obj2_kwargs)
            django_obj = self.obj2.create(extra_on_create=extra_on_create)

        assert django_obj
        self.process_relations(django_obj)
        self.process_virtual_fields(django_obj, self.obj2)

        return None, django_obj

    def process_relatie_entiteit(self, parent_django_obj, relation):
        """
        See StUF 03.01 - 5.2.6 Het vullen van relatie-entiteiten en gerelateerde entiteiten
            * 1. Mutatiesoort 'T' en verwerkingssoort 'T': Een relatie is relevant in een toevoegkennisgeving
            * 2. Mutatiesoort 'W' en verwerkingssoort 'T': Een relatie wordt toegevoegd in een wijzigkennisgeving
        """
        if isinstance(relation, OneToManyRelation):
            related_manager, default_kwargs = self.get_related_manager(parent_django_obj, relation)

            assert self.obj1 is None or isinstance(self.obj1.spyne_obj, Nil)

            related_fk_name = self.get_related_fk_name()

            if related_fk_name == 'self':
                gerelateerde_obj1, gerelateerde_obj2 = self.process_gerelateerde(extra_on_create=default_kwargs)
                related_manager.add(gerelateerde_obj2)

                # On a relatie-entiteit, which is defined on a Foreign Key, instead of a Many to Many table,
                # no relaties can be defined. i.e. we can't processes them, because they can't exist.
            else:
                # TODO [TECH]: Shouldn't a 'I' happen here first? (Check with standard)

                gerelateerde_obj1, gerelateerde_obj2 = self.process_gerelateerde()
                obj_kwargs = self.obj2.get_obj_kwargs()
                obj_kwargs[related_fk_name] = gerelateerde_obj2
                obj_kwargs.update(default_kwargs)
                new_obj = related_manager.create(**obj_kwargs)

                assert new_obj
                self.process_relations(new_obj)
        else:
            raise NotImplementedError


class DeleteOperation(BaseOperation):
    """
    Delete either a 'gerelateerde' or a fundamenteel.

    obj2 should be filled, obj2 should be empty.
    """
    verwerkingssoort = 'V'

    @classmethod
    def can_process(cls, stuf_entiteit, entiteit_type, mutatiesoort, obj1, obj2, parent_operation):
        if mutatiesoort == MutatiesoortChoices.wijziging:
            obj2_nonexistent = obj2 is None or obj2.is_nil()

            if obj2_nonexistent and obj1 and obj1.obj_verwerkingssoort == cls.verwerkingssoort:
                return True

            obj1_nonexistent = obj1 is None or obj1.is_nil()

            if obj1_nonexistent and obj2 and obj2.obj_verwerkingssoort == cls.verwerkingssoort:
                return True

        return False

    def process_relatie_entiteit(self, parent_django_obj, relation):
        """
        See StUF 03.01 - 5.2.6 Het vullen van relatie-entiteiten en gerelateerde entiteiten
            * 5. Mutatiesoort 'W' en verwerkingssoort 'V': Een relatie is niet langer relevant
        """
        if isinstance(relation, OneToManyRelation):
            related_manager, default_kwargs = self.get_related_manager(parent_django_obj, relation)

            gerelateerde_obj1, _ = self.process_gerelateerde()
            related_fk_name = self.get_related_fk_name()

            extra = default_kwargs.copy()
            extra[related_fk_name] = gerelateerde_obj1
            django_obj = self.obj1.get(related_manager=related_manager, extra=extra)
            django_obj.delete()

            # Als er onderliggende relatie-entiteiten zijn, dan hoeven ze, en kunnen ze niet verwerkt worden
            # omdat het bovenliggende object verwijderd is.
        else:
            raise NotImplementedError

    def process_fundamenteel(self, extra_on_create=None):
        """
        This is not allowed See:

        https://discussie.kinggemeenten.nl/discussie/gemma/stuf-301/lk01-mutatiesoort-w-verwijderen-v-van-een-gerelateerde

        Note: This is also, not easily implemented, because if this method is
        called from a 'process_relatie_entiteit', the expectation is that the object
        still exists.
        """
        raise NotImplementedError


class ReplaceRelationOperation(BaseOperation):
    """
    Both obj1 and obj2 should be filled.
    """
    verwerkingssoort = 'R'

    @classmethod
    def can_process(cls, stuf_entiteit, entiteit_type, mutatiesoort, obj1, obj2, parent_operation):
        if mutatiesoort == MutatiesoortChoices.wijziging:
            if obj1 and obj2 and obj1.obj_verwerkingssoort == 'R' and obj2.obj_verwerkingssoort == 'R':
                return True

        return False

    def process_relatie_entiteit(self, parent_django_obj, relation):
        """
        See StUF 03.01 - 5.2.6 Het vullen van relatie-entiteiten en gerelateerde entiteiten
            * 7. Mutatiesoort 'W' en verwerkingssoort 'R': Een relatie wordt vervangen
        """
        if isinstance(relation, OneToManyRelation):
            related_manager, default_kwargs = self.get_related_manager(parent_django_obj, relation)

            gerelateerde_obj1, gerelateerde_obj2 = self.process_gerelateerde()
            related_fk_name = self.get_related_fk_name()

            extra = default_kwargs.copy()
            extra[related_fk_name] = gerelateerde_obj1
            django_obj = self.obj1.get(related_manager=related_manager, extra=extra)

            setattr(django_obj, related_fk_name, gerelateerde_obj2)
            django_obj.full_clean()
            django_obj.save()

            assert django_obj
            self.process_relations(django_obj)
        else:
            raise NotImplementedError


class EndRelationOperation(DeleteOperation):
    """
    Both obj1 and obj2 should be filled.

    Voor relatie-entiteiten:
        See StUF 03.01 - 5.2.6 Het vullen van relatie-entiteiten en gerelateerde entiteiten
            * 6. Mutatiesoort 'W' en verwerkingssoort 'E': Een relatie wordt beëindigd entiteit
                 wordt gewijzigd/gecorrigeerd
    """
    verwerkingssoort = 'E'


class UpdateOperation(BaseOperation):
    """

    See StUF 03.01 - 5.2.6 Het vullen van relatie-entiteiten en gerelateerde entiteiten
        * 3. Mutatiesoort 'W' en verwerkingssoort 'W': De gegevens van een relatie-entiteit wijzigen in de werkelijkheid
    See StUF 03.01 - 5.2.5 Het vullen van de <object> elementen in een topfundamenteel
        * 2. Mutatiesoort 'W' en verwerkingssoort 'W': een fundamenteel is in de werkelijkheid gewijzigd
    """

    verwerkingssoort = 'W'

    @classmethod
    def can_process(cls, stuf_entiteit, entiteit_type, mutatiesoort, obj1, obj2, parent_operation):
        if mutatiesoort == MutatiesoortChoices.wijziging:
            if obj1 and obj2 and obj1.obj_verwerkingssoort == 'W' and obj2.obj_verwerkingssoort == 'W':
                return True

        return False

    def process_relatie_entiteit(self, parent_django_obj, relation):
        related_manager, default_kwargs = self.get_related_manager(parent_django_obj, relation)
        # TODO [TECH]: Taiga #264 Implementeer process_relatie_entiteit bij verwerkingssoort 'W
        # Also, do something like:
        # self.process_relations(django_obj)

    def process_fundamenteel(self, extra_on_create=None):
        django_obj = self.obj1.get()

        if self.obj1 and self.obj2 and self.obj1.obj_verwerkingssoort == 'W' and self.obj1.obj_verwerkingssoort == 'W':
            obj_kwargs = self.obj2.get_obj_kwargs()
            for key, value in obj_kwargs.items():
                setattr(django_obj, key, value)
            django_obj.full_clean()
            django_obj.save()

        assert django_obj
        self.process_relations(django_obj)

        return django_obj, django_obj


class GroupAttributeOperation(BaseOperation):
    """
    If you imagine really hard, you'll see that the groupattribuut processing is basically just a normal
    operation. That is just a little bit different.
    """

    def __init__(self, stuf_entiteit, obj1, obj2):
        self.stuf_entiteit = stuf_entiteit
        self.obj1 = obj1
        self.obj2 = obj2

        # Pretend we're a normal operation
        self.obj1 = [KennisgevingObject(stuf_entiteit, c) for c in obj1]
        self.obj2 = [KennisgevingObject(stuf_entiteit, c) for c in obj2]
        self.relations = []
        self.related = []

    def add_relation(self, relation, operation):
        """
        GroupAttributes can't have any relations.
        """
        raise NotImplementedError

    def add_related(self, fk_name, operation):
        """
        GroupAttributes can't have any gerelateerde.
        """
        raise NotImplementedError

    def process_relatie_entiteit(self, parent_django_obj, relation):
        """
        Note that 'groepattributen' aren't really relatie-entiteiten. I'm (ab)using the structure to process
        them as such.

        Quote van StUF 3.01 versie 25
            Indien in een kennisgevingbericht een element voor een attribuutwaarde meer dan één keer mag voorkomen,
            dan worden bij het toevoegen, wijzigen of verwijderen van de waarde van dat element alle waarden voor dat
            element in het bericht opgenomen. Bij het toevoegen van een tweede telefoonnummer
            wordt het huidige telefoonnummer dus zowel in het ‘oude’ als het ‘huidige’ voorkomen opgenomen.

        En verdere uitleg hier:
         * https://discussie.kinggemeenten.nl/discussie/gemma/stuf-zkn-310/verwerken-van-kenmerk-een-update-van-een-zaak-zaklk01

        Samengevat betekent dit dat de oude situatie irrelevant is, en dat _alleen_ de huidige situatie
        moet worden overgenomen. Dus, alle oude data wordt verwijderd (in alle gevallen) en de elementen
        in 'huidig' worden opgeslagen.
        """

        if isinstance(relation, ForeignKeyRelation):
            assert len(self.obj1) <= 1 and len(self.obj2) <= 1, 'ForeignKey relations can never have more than one object.'

            if relation.fk_name == 'self':
                fk_obj = parent_django_obj
                if self.obj2:
                    obj_kwargs = self.obj2[0].get_obj_kwargs()

                    for field_name, value in obj_kwargs.items():
                        setattr(fk_obj, field_name, value)
                    fk_obj.save()
            else:
                fk_obj = getattr(parent_django_obj, relation.fk_name)
                if fk_obj is not None:
                    fk_obj.delete()
                    django_model = relation.stuf_entiteit.get_model()

                    new_obj = django_model.objects.create(**self.obj2[0].get_obj_kwargs()) if self.obj2 else None
                    setattr(parent_django_obj, relation.fk_name, new_obj)
                    parent_django_obj.full_clean()
                    parent_django_obj.save()
        elif isinstance(relation, OneToManyRelation):
            related_manager, default_kwargs = self.get_related_manager(parent_django_obj, relation)

            assert len(default_kwargs) == 0, "No default kwargs expected for GroupAttributes."

            related_manager.all().delete()

            django_model = self.stuf_entiteit.get_model()

            for obj in self.obj2:
                related_manager.create(**obj.get_obj_kwargs())


def get_operation(stuf_entiteit, entiteit_type, mutatiesoort, obj1, obj2, parent_operation):
    operation_types = [
        UpdateOperation,
        EndRelationOperation,
        ReplaceRelationOperation,
        DeleteOperation,
        CreateOperation,
        IdentifyOperation,
    ]
    obj1 = KennisgevingObject(stuf_entiteit, obj1) if obj1 else None
    obj2 = KennisgevingObject(stuf_entiteit, obj2) if obj2 else None

    for operation_type in operation_types:
        if (operation_type.can_process(stuf_entiteit, entiteit_type, mutatiesoort, obj1, obj2, parent_operation)):
            return operation_type(stuf_entiteit, obj1, obj2)
