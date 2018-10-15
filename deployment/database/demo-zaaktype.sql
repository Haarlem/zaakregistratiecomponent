/*
* Add DEMO Organisatorische Eenheid and Vestiginging 
*/
INSERT INTO public.rgbz_object (identificatie, _objecttype_model, objecttype) VALUES ('DEMO', 'Betrokkene', 'OEH');
INSERT INTO public.rgbz_object (identificatie, _objecttype_model, objecttype) VALUES ('Demo Vestiging', 'Vestiging', 'VZO');
INSERT INTO public.rgbz_betrokkene (object_ptr_id, _betrokkenetype_model, betrokkenetype) VALUES ((select id from rgbz_object where identificatie='DEMO'), 'OrganisatorischeEenheid', 'OEH');
INSERT INTO public.rgbz_betrokkene (object_ptr_id, _betrokkenetype_model, betrokkenetype) VALUES ((select id from rgbz_object where identificatie='Demo Vestiging'), 'Vestiging', 'VZO');
INSERT INTO public.rgbz_vestiging (betrokkene_ptr_id, telefoonnummer, emailadres, faxnummer, naam, handelsnaam, verkorte_naam, datum_aanvang, datum_beeindiging, _vestigingtype_model, correspondentieadres_id, locatieadres_id, postadres_id, rekeningnummer_id, verblijf_buitenland_id) VALUES ((select id from rgbz_object where identificatie='Demo Vestiging'), null, null, null, null, '{''VestigingVanZaakBehandelendeOrganisatie''}', null, '20180101', null, 'VestigingVanZaakBehandelendeOrganisatie', null, null, null, null, null);
INSERT INTO public.rgbz_vestigingvanzaakbehandelendeorganisatie (is_specialisatie_van_id, id) VALUES ((select id from rgbz_object where identificatie='Demo Vestiging'), (select id from rgbz_object where identificatie='Demo Vestiging'));
INSERT INTO public.rgbz_organisatorischeeenheid (betrokkene_ptr_id, organisatieidentificatie, datum_ontstaan, datum_opheffing, naam, telefoonnummer, emailadres, faxnummer, organisatieeenheididentificatie, naam_verkort, omschrijving, toelichting, contactpersoon_id, verantwoordelijke_id, gevestigd_in_id) VALUES ((select id from rgbz_object where identificatie='DEMO'), 1, '20180101', null, 'Demo Organisatorische Eenheid', null, null, null, 'DEMO', 'Demo', 'Demo Organisatorische Eenheid', null, null, null, 2);

/*
* Add DEMO casetype 
*/
INSERT INTO public.rgbz_zaaktype (zaaktypeidentificatie, zaaktypeomschrijving, domein, zaaktypeomschrijving_generiek, rsin, trefwoord, doorlooptijd_behandeling, servicenorm_behandeling, archiefclassificatiecode, vertrouwelijk_aanduiding, publicatie_indicatie, zaakcategorie, publicatietekst, datum_begin_geldigheid_zaaktype, datum_einde_geldigheid_zaaktype, medewerker_id, organisatorische_eenheid_id) VALUES (1, 'DEMO', 'DEMO', 'Demonstratie zaaktype', 1, '{''DEMO''}', 14, null, null, 'OPENBAAR', 'N', null, null, '20180101', '21000101', null, 1);

/*
*Add DEMO_DOCUMENT documenttype
*/ 
INSERT INTO public.rgbz_informatieobjecttypeomschrijvinggeneriek (informatieobjecttypeomschrijving_generiek, definitie_informatieobjecttypeomschrijving_generiek, herkomst_informatieobjecttypeomschrijving_generiek, hierarchie_informatieobjecttypeomschrijving_generiek, opmerking_informatieobjecttypeomschrijving_generiek, begin_geldigheid_informatieobjecttypeomschrijving_generiek, einde_geldigheid_informatieobjecttypeomschrijving_generiek) VALUES ('DEMO_DOC', 'Demo document', 'Demo', 'Demo', null, '20180101', null);
INSERT INTO public.rgbz_informatieobjecttype (informatieobjecttypeomschrijving, domein, rsin, informatieobjectcategorie, informatieobjecttypetrefwoord, datum_begin_geldigheid_informatieobjecttype, datum_einde_geldigheid_informatieobjecttype, informatieobjecttypeomschrijving_generiek_id) VALUES ('DEMO_DOCUMENT', 'DEMO', 1, 'document', null, '20180101', null, (select id from rgbz_informatieobjecttypeomschrijvinggeneriek where informatieobjecttypeomschrijving_generiek='DEMO_DOC'));