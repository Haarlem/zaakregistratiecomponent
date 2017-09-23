from djchoices import ChoiceItem, DjangoChoices


class StatusWoonplaats(DjangoChoices):
    woonplaats_aangewezen = ChoiceItem('Woonplaats aangewezen', 'Woonplaats aangewezen')
    woonplaats_ingetrokken = ChoiceItem('Woonplaats ingetrokken', 'Woonplaats ingetrokken')


class StatusOpenbareRuimte(DjangoChoices):
    naamgeving_uitgegeven = ChoiceItem('Naamgeving uitgegeven', 'Naamgeving uitgegeven')
    naamgeving_ingetrokken = ChoiceItem('Naamgeving ingetrokken', 'Naamgeving ingetrokken')


class TyperingOpenbareRuimte(DjangoChoices):
    weg = ChoiceItem('weg', 'weg')
    water = ChoiceItem('water', 'water')
    spoorbaan = ChoiceItem('spoorbaan', 'spoorbaan')
    terrein = ChoiceItem('terrein', 'terrein')
    kunstwerk = ChoiceItem('kunstwerk', 'kunstwerk')
    landschappelijk_gebied = ChoiceItem('landschappelijk gebied', 'landschappelijk gebied')
    functioneel_gebied = ChoiceItem('functioneel gebied', 'functioneel gebied')
    administratief_gebied = ChoiceItem('administratief gebied', 'administratief gebied')


class TypeObjectCode(DjangoChoices):
    verblijfsobject = ChoiceItem('01', 'verblijfsobject')
    ligplaats = ChoiceItem('02', 'ligplaats')
    standplaats = ChoiceItem('03', 'standplaats')
    pand = ChoiceItem('10', 'pand')
    nummeraanduiding = ChoiceItem('20', 'nummeraanduiding')
    openbare_ruimte = ChoiceItem('30', 'openbare ruimte')
    overig_adreseerbaar_object_aanduiding = ChoiceItem('90', 'overig adreseerbaar object aanduiding')
    overig_gebouwd_object = ChoiceItem('91', 'overig gebouw object')
    overig_benoemd_terrein = ChoiceItem('92', 'overig benoemd terrein')


class AdelijkeTitel(DjangoChoices):
    baron = ChoiceItem('B', 'Baron')
    barones = ChoiceItem('B', 'Barones')
    graaf = ChoiceItem('G', 'Graaf')
    gravin = ChoiceItem('G', 'Gravin')
    hertog = ChoiceItem('H', 'Hertog')
    hertogin = ChoiceItem('H', 'Hertogin')
    Markies = ChoiceItem('M', 'Markies')
    Markiezin = ChoiceItem('M', 'Markiezin')
    prins = ChoiceItem('P', 'Prins')
    prinses = ChoiceItem('P', 'Prinses')
    ridder = ChoiceItem('R', 'Ridder')


class NaamGebruik(DjangoChoices):
    """
    De voorgedefinieerde waarden van naamgebruik volgens de centrale
    voorzieningen. Zie attribuut Naamgebruik van groep A.1.12 Naamgebruik van
    BRP.
    """
    eigen = ChoiceItem('E', 'eigen')
    partner = ChoiceItem('P', 'Partner')
    partner_eigen = ChoiceItem('V', 'Partner, eigen')
    eigen_partner = ChoiceItem('N', 'Eigen, partner')


class PostadresType(DjangoChoices):
    antwoordnummer = ChoiceItem('A', 'Antwoordnummer')
    postbusnummer = ChoiceItem('P', 'Postbusnummer')
