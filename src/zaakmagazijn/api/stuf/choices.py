from djchoices import ChoiceItem, DjangoChoices


class ScopeChoices(DjangoChoices):
    kerngegevens = ChoiceItem('kerngegevens', 'kerngegevens')
    alles = ChoiceItem('alles', 'alles')
    allesZonderMetagegevens = ChoiceItem('allesZonderMetagegevens', 'allesZonderMetagegevens')
    allesMaarKerngegevensGerelateerden = ChoiceItem('allesMaarKerngegevensGerelateerden', 'allesMaarKerngegevensGerelateerden')
    allesZonderMetagegevensMaarKerngegevensGerelateerden = ChoiceItem('allesZonderMetagegevensMaarKerngegevensGerelateerden', 'allesZonderMetagegevensMaarKerngegevensGerelateerden')


class ServerFoutChoices(DjangoChoices):
    stuf001 = ChoiceItem("StUF001", "Versie StUF niet ondersteund")  # "2,3", "De dichtstbijzijnde1 wel ondersteunde versie StUF."
    stuf004 = ChoiceItem("StUF004", "Sectormodel niet ondersteund")  # "2,3", "-"
    stuf007 = ChoiceItem("StUF007", "Versie sectormodel niet ondersteund ")  # "2,3", "De dichtstbijzijnde wel ondersteunde versie sectormodel"
    stuf025 = ChoiceItem("StUF025", "Berichtcode niet ondersteund")  # "2,3"
    stuf031 = ChoiceItem("StUF031", "Entiteittype niet ondersteund")  # "2,3"
    stuf037 = ChoiceItem("StUF037", "Functie niet ondersteund")  # "2,3"
    stuf040 = ChoiceItem("StUF040", "Combinatie van berichtcode, entiteittype en functie niet ondersteund")  # "2,3"
    stuf046 = ChoiceItem("StUF046", "Opslaan bericht niet mogelijk")  # "3"
    stuf049 = ChoiceItem("StUF049", "Proces voor afhandelen synchroon bericht niet beschikbaar")  # "2"
    stuf058 = ChoiceItem("StUF058", "Proces voor afhandelen bericht geeft fout")  # "1,2", "Desgewenst een omschrijving van de fout in het afhandelende proces"
    stuf061 = ChoiceItem("StUF061", "Starten berichtverzending niet mogelijk binnen 5 minuten")  # "2"
    stuf063 = ChoiceItem("StUF063", "Een te wijzigen waarde heeft in de registratie een beginGeldigheid groter dan tbo")  # "2"
    stuf064 = ChoiceItem("StUF064", "Object niet gevonden")  # "2"
    stuf065 = ChoiceItem("StUF065", "tr ≤ de grootste tijdstipRegistratie voor het object in de registratie")  # "2"
    stuf067 = ChoiceItem("StUF067", "Dubbelen voor object gevonden")  # "2"
    stuf094 = ChoiceItem("StUF094", "Ontvangend systeem registreert sleutel in het verzendende systeem niet")  # "1, 2"
    stuf124 = ChoiceItem("StUF124", "Antwoordend systeem ondersteunt afhandelen asynchrone vragen niet")  # "1"
    stuf127 = ChoiceItem("StUF127", "Gebruiker binnen zendend systeem onbekend in antwoordend systeem en nodig voor autorisatie")  # "1, 2"
    stuf130 = ChoiceItem("StUF130", "Beantwoording asynchrone vraag vergt teveel systeemresources")  # "1"
    stuf133 = ChoiceItem("StUF133", "Antwoordend systeem ondersteunt gevraagde sortering niet")  # "1, 2"
    stuf960 = ChoiceItem("StUF960", "Het antwoordende systeem is niet in staat het verzoek af te handelen binnen de connection time out")  # "2"


class ClientFoutChoices(DjangoChoices):
    stuf010 = ChoiceItem("StUF010", "Combinatie van ontvangende organisatie, applicatie en administratie onbekend")  # "2,3"
    stuf013 = ChoiceItem("StUF013", "Combinatie van zendende organisatie, applicatie en administratie onbekend")  # "2,3"
    stuf016 = ChoiceItem("StUF016", "Combinatie zender en referentienummer niet uniek")  # "2,3"
    stuf019 = ChoiceItem("StUF019", "TijdstipBericht niet groter dan voorgaand TijdstipBericht van zender")  # "2,3"
    stuf022 = ChoiceItem("StUF022", "Berichtcode onbekend")  # "2,3"
    stuf028 = ChoiceItem("StUF028", "Entiteittype onbekend binnen sectormodel")  # "2,3"
    stuf034 = ChoiceItem("StUF034", "Functie onbekend binnen sectormodel")  # "2,3"
    stuf043 = ChoiceItem("StUF043", "Crossreferentienummer niet bekend")  # "2,3"
    stuf052 = ChoiceItem("StUF052", "Het zendende systeem is niet geautoriseerd voor de gevraagde combinatie van berichtcode, entiteittype en functie")  # "1,2"
    stuf055 = ChoiceItem("StUF055", "Berichtbody is niet conform schema in sectormodel")  # "1,2"
    stuf062 = ChoiceItem("StUF062", "<StUF:tijdvakGeldigheid> niet gevuld zoals de standaard voorschrijft")  # "2"
    stuf066 = ChoiceItem("StUF066", "Een te corrigeren entiteit bevat geen te corrigeren element")  # "2"
    stuf068 = ChoiceItem("StUF068", "Toekomstmutatie in Lk02-bericht")  # "2"
    stuf069 = ChoiceItem("StUF069", "Niet alle elementen in historische correctie komen in de registratie voor met waarde en het tijdvakGeldigheid in 'oud'")  # "2"
    stuf070 = ChoiceItem("StUF070", "Synchronisatiebericht historisch niet consistent ")  # "2",  " "
    stuf076 = ChoiceItem("StUF076", "<vanaf> en <totEnMet> bevatten niet dezelfde elementen")  # "1, 2", "De naam van het verschillend voorkomende element"
    stuf079 = ChoiceItem("StUF079", "Een element komt voor in zowel <gelijk> als <vanaf> en <totEnMet>")  # "1, 2", "De naam van het element"
    stuf082 = ChoiceItem("StUF082", "Het attribute StUF:exact is gebruikt op een element binnen <vanaf> of <totEnMet>")  # "1, 2",  " De naam van het element"
    stuf085 = ChoiceItem("StUF085", "Onvolledige datum binnen <vanaf> of <totEnMet>")   # "1, 2",  "De naam van het element met de onvolledige datum."
    stuf088 = ChoiceItem("StUF088", "Meer dan één sleutel gespecificeerd als selectiecriterium")  # "1, 2"
    stuf091 = ChoiceItem("StUF091", "Een sleutel en andere elementen gespecificeerd als selectiecriterium")  # "1, 2"
    stuf097 = ChoiceItem("StUF097", "Zowel het attribute scope als een inhoud gespecificeerd voor het element <scope>")  # "1, 2"
    stuf103 = ChoiceItem("StUF103", "indicatorVervolgvraag is true, maar het element <start> ontbreekt")  # "1, 2"
    stuf106 = ChoiceItem("StUF106", "Het element <start> bevat niet alle elementen gespecificeerd in <vanaf> en <totEnMet>")  # "1.2"
    stuf118 = ChoiceItem("StUF118", "peiltijdstipMaterieel ontbreekt")  # "1, 2"
    stuf119 = ChoiceItem("StUF119", "peiltijdstipFormeel ontbreekt")  # "1, 2"


class BerichtcodeChoices(DjangoChoices):
    bv01 = ChoiceItem('Bv01', 'een bevestigingsbericht als functionele asynchrone respons')
    bv02 = ChoiceItem('Bv02', 'een bevestigingsbericht als functionele synchrone respons op een synchroon bericht')
    bv03 = ChoiceItem('Bv03', 'een bevestigingsbericht als technische synchrone respons op een asynchroon bericht '
                              'waarbij het bericht op basis van berichtstuurgegevens verwerkbaar wordt geacht')
    bv04 = ChoiceItem('Bv04', 'een bevestigingsbericht als technische synchrone respons op een asynchroon bericht, '
                              'dat een check op verwerkbaarheid op basis van de berichtstuurgegevens ontkent')
    di01 = ChoiceItem('Di01', 'een asynchroon inkomend vrij bericht')
    di02 = ChoiceItem('Di02', 'een synchroon inkomend vrij bericht')
    du01 = ChoiceItem('Du01', 'een asynchroon uitgaand vrij bericht (respons op een Di01)')
    du02 = ChoiceItem('Du02', 'een synchroon uitgaand vrij bericht (respons op een Di02)')
    fo01 = ChoiceItem('Fo01', 'een foutbericht als functionele asynchrone respons')
    fo02 = ChoiceItem('Fo02', 'een foutbericht als functionele synchrone respons')
    fo03 = ChoiceItem('Fo03', 'een foutbericht als technische synchrone respons op een asynchroon bericht')
    la01 = ChoiceItem('La01', 'een synchroon antwoordbericht met alleen actuele gegevens')
    la02 = ChoiceItem('La02', 'een asynchroon antwoordbericht met alleen actuele gegevens')
    la03 = ChoiceItem('La03', 'een synchroon antwoordbericht met de gegevens op peiltijdstip zoals nu bekend in de registratie')
    la04 = ChoiceItem('La04', 'een asynchroon antwoordbericht met de gegevens op peiltijdstip zoals nu bekend in de registratie')
    la05 = ChoiceItem('La05', 'een synchroon antwoordbericht met de gegevens op peiltijdstip zoals bekend in de registratie op '
                              'peiltijdstip formele historie')
    la06 = ChoiceItem('La06', 'een asynchroon antwoordbericht met de gegevens op peiltijdstip zoals bekend in de '
                              'registratie op peiltijdstip formele historie')
    la07 = ChoiceItem('La07', 'een synchroon antwoordbericht met materiële historie voor de gevraagde objecten op entiteitniveau')
    la08 = ChoiceItem('La08', 'een asynchroon antwoordbericht met materiële historie voor de gevraagde objecten op entiteitniveau')
    la09 = ChoiceItem('La09', 'een synchroon antwoordbericht met materiële en formele historie voor de gevraagde '
                              'objecten op entiteitniveau')
    la10 = ChoiceItem('La10', 'een asynchroon antwoordbericht met materiële en formele historie voor de gevraagde '
                              'objecten op entiteitniveau')
    la11 = ChoiceItem('La11', 'een synchroon antwoordbericht met materiële historie voor de gevraagde objecten op groepniveau')
    la12 = ChoiceItem('La12', 'een asynchroon antwoordbericht met materiële historie voor de gevraagde objecten op groepniveau')
    la13 = ChoiceItem('La13', 'een synchroon antwoordbericht met materiële en formele historie voor de gevraagde objecten op groepniveau')
    la14 = ChoiceItem('La14', 'een asynchroon antwoordbericht met materiële en formele historie voor de gevraagde objecten op groepniveau')
    lk01 = ChoiceItem('Lk01', 'een asynchroon kennisgevingbericht zonder toekomstmutaties')
    lk02 = ChoiceItem('Lk02', 'een synchroon kennisgevingbericht zonder toekomstmutaties')
    lk03 = ChoiceItem('Lk03', 'een asynchroon samengesteld kennisgevingbericht')
    lk04 = ChoiceItem('Lk04', 'een synchroon samengesteld kennisgevingbericht')
    lk05 = ChoiceItem('Lk05', 'een asynchroon kennisgevingbericht met een toekomstmutatie')
    lk06 = ChoiceItem('Lk06', 'een synchroon kennisgevingbericht met een toekomstmutatie')
    lv01 = ChoiceItem('Lv01', 'een synchroon vraagbericht naar de actuele gegevens')
    lv02 = ChoiceItem('Lv02', 'een asynchroon vraagbericht naar de actuele gegevens')
    lv03 = ChoiceItem('Lv03', 'een synchroon vraagbericht naar de gegevens op peiltijdstip zoals nu bekend in de registratie')
    lv04 = ChoiceItem('Lv04', 'een asynchroon vraagbericht naar de gegevens op peiltijdstip zoals nu bekend in de registratie')
    lv05 = ChoiceItem('Lv05', 'een synchroon vraagbericht naar de gegevens op peiltijdstip zoals bekend in de '
                              'registratie op peiltijdstip formele historie')
    lv06 = ChoiceItem('Lv06', 'een asynchroon vraagbericht naar de gegevens op peiltijdstip zoals bekend in de '
                              'registratie op peiltijdstip formele historie')
    lv07 = ChoiceItem('Lv07', 'een synchroon vraagbericht naar materiële historie voor de gevraagde objecten op entiteitniveau')
    lv08 = ChoiceItem('Lv08', 'een asynchroon vraagbericht naar materiële historie voor de gevraagde objecten op entiteitniveau')
    lv09 = ChoiceItem('Lv09', 'een synchroon vraagbericht naar materiële en formele historie voor de gevraagde objecten op entiteitniveau')
    lv10 = ChoiceItem('Lv10', 'een asynchroon vraagbericht naar materiële en formele historie voor de gevraagde objecten op entiteitniveau')
    lv11 = ChoiceItem('Lv11', 'een synchroon vraagbericht naar materiële historie voor de gevraagde objecten op groepniveau')
    lv12 = ChoiceItem('Lv12', 'een asynchroon vraagbericht naar materiële historie voor de gevraagde objecten op groepniveau')
    lv13 = ChoiceItem('Lv13', 'een synchroon vraagbericht naar materiële en formele historie voor de gevraagde objecten op groepniveau')
    lv14 = ChoiceItem('Lv14', 'een asynchroon vraagbericht naar materiële en formele historie voor de gevraagde objecten op groepniveau')
    sa01 = ChoiceItem('Sa01', 'een asynchroon synchronisatiebericht voor de actuele gegevens')
    sa02 = ChoiceItem('Sa02', 'een synchroon synchronisatiebericht voor de actuele gegevens')
    sa03 = ChoiceItem('Sa03', 'een asynchroon bericht dat vraagt om een asynchroon synchronisatiebericht voor de actuele gegevens')
    sa04 = ChoiceItem('Sa04', 'een synchroon bericht dat vraagt om een synchroon synchronisatiebericht voor de actuele gegevens')
    sh01 = ChoiceItem('Sh01', 'een asynchroon synchronisatiebericht voor de actuele en de historische gegevens')
    sh02 = ChoiceItem('Sh02', 'een synchroon synchronisatiebericht voor de actuele en de historische gegevens')
    sh03 = ChoiceItem('Sh03', 'een asynchroon bericht dat vraagt om een asynchroon synchronisatiebericht voor de '
                              'actuele en historische gegevens')
    sh04 = ChoiceItem('Sh04', 'een synchroon bericht dat vraagt om een synchroon synchronisatiebericht voor de actuele '
                              'en historische gegevens')
    tr01 = ChoiceItem('Tr01', 'een triggerbericht')
