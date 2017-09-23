See: http://www.gemmaonline.nl/images/gemmaonline/3/32/7_Metamodel_informatiemodellen_KING_Kadaster_in_ontwikkeling_20150930.pdf

**AN**n (waarbij n=1,2,3,...)

    Alle alfanumerieke tekens, speciale tekens en diakrieten gebaseerd op de
    tekenset UTF8, minimale lengte is tenminste 1, maximale lengte is n. De 1e
    positie mag géén spatie bevatten.

    Opmerking: Numerieke velden met voorloopnullen worden opgenomen als
    alfanumeriek veld. Bij metagegeven Waardenverzameling attribuutsoort is dit
    dan verder gespecificeerd.

**AN**

    Alle alfanumerieke tekens, speciale tekens en diakrieten gebaseerd op de
    tekenset UTF8, de minimale lengte is tenminste 1, de maximale lengte is
    onbepaald.

    De 1e positie mag géén spatie bevatten.

    Opmerking: Numerieke velden met voorloopnullen worden opgenomen als
    alfanumeriek veld. Bij metagegeven Waardenverzameling attribuutsoort is dit
    dan gespecificeerd.

**N**n (waarbij n=1,2,3,...)

    Geheel getal met maximale lengte n en de minimale lengte is tenminste 1.

    Betreft altijd een geheel getal zonder voorloopnullen. Getal met
    voorloopnullen wordt gespecificeerd met ANn of AN.

    Als een geheel getal negatief kan zijn dan altijd een extra positie
    hiervoor reserveren. Voorbeeld: formaat relatieve hoogteligging is N2 omdat
    het een negatief getal kan zijn bijvoorbeeld -3.

    Een getal met formaat N1 is altijd positief.

**N**n,d (waarbij n=2,3,4... en d=1,2,3,...)

    Gebroken getal met maximaal n cijfers voor de komma en maximaal d cijfers
    achter de komma.

    Er geldt altijd dat n ≥ 1 en d ≥ 1 zijn met n en d natuurlijke getallen.

    Betreft altijd een gebroken getal zonder voorloopnullen. Getal met
    voorloopnullen wordt gespecificeerd met ANn of AN

    Als een gebroken getal negatief kan zijn dan altijd een extra positie
    hiervoor reserveren. Voorbeeld een attribuutsoort met mogelijke waarden
    -2,2 of 4,5. Formaat attribuutsoort is dan uitgedrukt als 2,1.

**N**

    Geheel getal, lengte is minimaal 1 en maximale lengte is verder onbepaald.

**INDIC**

    Indicatie met mogelijke waarden J of N

**DATUM**

    4-cijferig jaar, 2-cijferig maand, 2-cijferig dag uitgedrukt in yyyy-mm-dd

**DT**

    yyyy-mm-ddThh:mm:ss

**JAAR**

    4-cijferig jaar uitgedrukt in yyyy

**URI**

    Unieke identificatie op internet conform RFC3986 en de URI-strategie Linked
    Open Data.

    Gestandaardiseerde manier om op het internet dingen (pagina's met
    informatie, objecten, datasets) uniek te identificeren.

**DATUM?**

    Dit is DatumMogelijkOnvolledig conform project GAB. Er is gekozen voor een
    kortere, meer praktisch hanteerbare naam. Er kan gekozen worden om DATUM?
    Te isoleren, door deze alleen toe te passen waar dit nodig is, door een
    union te definiëren met daarin een keuze tussen DATUM? en DATUM.

    De keuze van een periode in de Gregoriaanse kalender, al naar gelang de
    beschikbare datumelementen, uit de onderliggende subformaten datum,
    jaarMaand of jaar.

**DT?**

    Een datum met een mogelijke datum tijd waarbij minimaal het jaar bekend is.
    Mogelijke voorkomens zijn (uitputtend):

        yyyy-mm-ddThh:mm:ss
        yyyy-mm-ddThh:mm:??
        yyyy-mm-ddThh:??:??
        yyyy-mm-ddT??:??:??
        yyyy-mm-??T??:??:??
        yyyy-??-??T??:??:??

**TXT**

    Alle alfanumerieke tekens, speciale tekens en diakrieten met newlines of
    HTML opmaak e.d. Mag starten met spatie. De maximale lengte is onbepaald.
