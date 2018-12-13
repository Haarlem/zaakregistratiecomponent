"""
These orderings should all match the ProxyModel fields.
"""


ZAKSortering = {
    0: [],
    1: ['zaakidentificatie'],
    2: ['zaaktype__zaakcategorie', 'zaaktype__zaaktypeomschrijving_generiek'], # XSD: ['isVan/gerelateerde/zaakCategorie', 'omschrijvingGeneriek'],
    3: ['zaaktype__zaaktypeomschrijving'],
    4: ['omschrijving'],
    5: ['-startdatum', 'omschrijving'],
    6: ['anderzaakobject_set__zaak__zaakidentificatie'],  # XSD: heeftBetrekkingOp/gerelateerde/identificatie
    7: ['rol_set__betrokkene__identificatie'],  # XSD: ['heeftAlsBelanghebbende/gerelateerde/identificatie'],
    8: ['rol_set__betrokkene__identificatie'],  # FIXME XSD:['heeftAlsGemachtigde/gerelateerde/identificatie'],
    9: ['rol_set__betrokkene__identificatie'],  # FIXME XSD:['heeftAlsInitiator/gerelateerde/identificatie'],
    10: ['rol_set__betrokkene__identificatie'],  # FIXME XSD:['heeftAlsUitvoerende/gerelateerde/identificatie'],
    11: ['rol_set__betrokkene__identificatie'],  # FIXME XSD: ['heeftAlsVerantwoordelijke/gerelateerde/identificatie'],
    # FIXME: XSD: ['isDeelzaakVan/gerelateerde/identificatie'] = 'hoofdzaak__zaakidentificatie'?
    12: [],  #
    13: ['zaakobject_set__object__identificatie'],  # XSD:['heeftBetrekkingOp/gerelateerde/identificatie'],
}


BSLSortering = {  # Not currently in use
    0: [],
    1: ['identificatie'],
    2: ['besluittype__besluitcategorie', 'besluittype__besluittypeomschrijving_generiek'],
    3: ['besluittype__besluittypeomschrijving'],
    4: ['-besluitdatum', 'besluittype__besluittypeomschrijving'],
    5: ['-ingangsdatum', 'besluittype__besluittypeomschrijving'],
    6: ['-vervaldatum', 'besluittype__besluittypeomschrijving'],
    7: ['-publicatiedatum', 'besluittype__besluittypeomschrijving'],
    8: ['zaak__zaakidentificatie'],  # isUitkomstVan
    9: ['informatieobject__identificatie'],  # isVastgelegdIn
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
        # FIXME: The RGBZ-mapping makes it impossible to sort on the generic
        # field. Instead, we use the non-generic description.
        'documenttype__documenttypeomschrijving'
        # 'documenttype__documenttypeomschrijving_generiek'
    ],
    3: ['documenttype__documenttypeomschrijving'],
    4: ['documenttitel', 'documentversie'],
    5: ['documentauteur', 'documentversie'],
    6: ['-documentcreatiedatum', 'documenttype__documenttypeomschrijving'],
    7: ['-documentontvangstdatum', 'documenttype__documenttypeomschrijving'],
    8: ['zaakinformatieobject_set__zaak__zaakidentificatie'],
    # FIXME: XSD ['kanVastleggingZijnVan/gerelateerde/identificatie']
    9: [],
}
