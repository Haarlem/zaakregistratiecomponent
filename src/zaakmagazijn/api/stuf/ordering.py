
ZAKSortering = {
    0: [],
    1: ['zaakidentificatie'],
    2: ['zaaktype__zaakcategorie', 'zaaktype__zaaktypeomschrijving_generiek'], # XSD: ['isVan/gerelateerde/zaakCategorie', 'omschrijvingGeneriek'],
    3: ['zaaktype__zaaktypeomschrijving'],
    4: ['omschrijving'],
    5: ['-startdatum', 'omschrijving'],
    # TODO [TECH]: Taiga #208
    6: ['ander_zaakobject__zaak__zaakidentificatie'],  # XSD: heeftBetrekkingOp/gerelateerde/identificatie
    7: ['rol__betrokkene__identificatie'],  # XSD: ['heeftAlsBelanghebbende/gerelateerde/identificatie'],
    8: ['rol__betrokkene__identificatie'],  # FIXME XSD:['heeftAlsGemachtigde/gerelateerde/identificatie'],
    9: ['rol__betrokkene__identificatie'],  # FIXME XSD:['heeftAlsInitiator/gerelateerde/identificatie'],
    10: ['rol__betrokkene__identificatie'],  # FIXME XSD:['heeftAlsUitvoerende/gerelateerde/identificatie'],
    11: ['rol__betrokkene__identificatie'],  # FIXME XSD: ['heeftAlsVerantwoordelijke/gerelateerde/identificatie'],
    12: ['hoofdzaak__zaakidentificatie'],  # XSD: ['isDeelzaakVan/gerelateerde/identificatie'],
    13: ['gerelateerde_aan__identificatie'],  # XSD:['heeftBetrekkingOp/gerelateerde/identificatie'],
}

BSLSortering = {  # Not currently in use
    0: [],
    1: ['identificatie'],
    2: ['besluittype__besluitcategorie', 'besluittype__besluittypeomschrijving__generiek'],
    3: ['besluittype__besluittypeomschrijving'],
    4: ['-besluitdatum', 'besluittype__besluittypeomschrijving'],
    5: ['-ingangsdatum', 'besluittype__besluittypeomschrijving'],
    6: ['-vervaldatum', 'besluittype__besluittypeomschrijving'],
    7: ['-publicatiedatum', 'besluittype__besluittypeomschrijving'],
    8: ['zaak__zaakidentificatie'],  # isUitkomstVan
    9: ['informatieobject__informatieobjectidentificatie'],  # isVastgelegdIn
}

BSTSortering = {  # Not currently in use
    0: [],
    1: ['besluitcategorie', 'besluittypeomschrijving_generiek'],
    2: ['besluittypeomschrijving'],
}


EDCSortering = {
    0: [],
    1: ['identificatie'],
    2: [
        'documenttype__documentcategorie',
        # TODO [TECH]: Taiga #208 just on name?
        'documenttype__documenttypeomschrijving_generiek'
    ],
    3: ['documenttype__documenttypeomschrijving'],
    4: ['titel', 'versie'],
    5: ['auteur', 'versie'],
    6: ['-creatiedatum', 'documenttype__documenttypeomschrijving'],
    7: ['-ontvangstdatum', 'documenttype__documenttypeomschrijving'],
    8: ['zaakinformatieobject_set__zaak__identificatie'],
    # TODO [TECH]: Taiga #208
    # FIXME: XSD ['kanVastleggingZijnVan/gerelateerde/identificatie']
    9: [],
}
