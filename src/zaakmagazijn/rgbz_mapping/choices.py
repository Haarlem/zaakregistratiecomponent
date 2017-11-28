from djchoices import ChoiceItem, DjangoChoices


class Zaakniveau(DjangoChoices):
    hoofdzaak = ChoiceItem('1', 'hoofdzaak')
    deelzaken = ChoiceItem('2', 'deelzaken')
    deeldeelzaken = ChoiceItem('3', 'deeldeelzaken')


class Rolomschrijving(DjangoChoices):
    belanghebbende = ChoiceItem('Belanghebbende', 'Belanghebbende')
    gemachtigde = ChoiceItem('Gemachtigde', 'Gemachtigde')
    initiator = ChoiceItem('initiator', 'initiator')
    overig = ChoiceItem('Overig', 'Overig')
    uitvoerder = ChoiceItem('Uitvoerder', 'Uitvoerder')
    verantwoordelijke = ChoiceItem('Verantwoordelijke', 'Verantwoordelijke')


class Subjecttypering(DjangoChoices):
    """
    TODO [TECH]: We should probably be storing either '21' or '23'
    21: Ingeschreven niet-natuurlijk persoon
    23: Ander buitenlands niet-natuurlijk persoon
    """
    innp = ChoiceItem('Ingeschreven niet-natuurlijk persoon', 'Ingeschreven niet-natuurlijk persoon')
    annp = ChoiceItem('Ander buitenlands niet-natuurlijk persoon', 'Ander buitenlands niet-natuurlijk persoon')
