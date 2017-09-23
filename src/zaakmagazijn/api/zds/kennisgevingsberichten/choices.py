from djchoices import ChoiceItem, DjangoChoices


class MutatiesoortChoices(DjangoChoices):
    toevoeging = ChoiceItem('T')
    wijziging = ChoiceItem('W')
    verwijdering = ChoiceItem('V')
    correctie = ChoiceItem('C')
    correctie_met_historie = ChoiceItem('F')


class VerwerkingssoortChoices(DjangoChoices):
    toevoeging = ChoiceItem('T', 'Een entiteit wordt toegevoegd')
    verwijdering = ChoiceItem('V', 'Een entiteit wordt verwijderd')
    wijziging = ChoiceItem('W', 'Gegevens van een entiteit worden gewijzigd of gecorrigeerd')
    beeindiging = ChoiceItem('E', 'Een relatie-entiteit wordt beëindigd')
    identificering = ChoiceItem('I', 'De entiteit bevat alleen identificerende gegevens')
    vervanging = ChoiceItem('R', 'Een relatie-entiteit wordt vervangen door een andere relatie-entiteit')
    sleutelwijziging = ChoiceItem('S', 'De sleutel van een entiteit wordt gewijzigd')
    ontdubbeling = ChoiceItem('O', 'De entiteit in het eerste <object> element wordt ontdubbeld door het samen te voegen met de entiteit in het tweede <object> element. Er wordt ontdubbeld, omdat beide entiteiten bleken te verwijzen naar hetzelfde object in de werkelijkheid.')


class EntiteitType(DjangoChoices):
    topfundamenteel = ChoiceItem('topfundamenteel')
    gerelateerde = ChoiceItem('gerelateerde')
    relatie_entiteit = ChoiceItem('relatie_entiteit')
    gegevensgroep = ChoiceItem('gegevensgroep')
