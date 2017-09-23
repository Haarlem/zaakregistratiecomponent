from django.test import TestCase

from ...rsgb.tests.factory_models import (
    AdresMetPostcodeFactory, BezoekadresFactory, CorrespondentieadresFactory,
    LocatieadresFactory, PostAdresFactory, VerblijfAdresFactory,
    VerblijfBuitenlandFactory
)
from ..models import VestigingVanZaakBehandelendeOrganisatie
from .factory_models import (
    BetrokkeneFactory, BetrokkeneMetRolFactory, BetrokkeneMetVerzendingFactory,
    KlantcontactFactory, KlantcontactMetVestigingFactory, MedewerkerFactory,
    NatuurlijkPersoonFactory, NietNatuurlijkPersoonFactory,
    OrganisatorischeEenheidFactory, Rol, RolFactory, StatusFactory, Verzending,
    VestigingFactory, VestigingVanZaakBehandelendeOrganisatieFactory,
    ZaakFactory, ZaakTypeFactory
)


class BetrokkeneTestCase(TestCase):
    def test_objects_create_objecttype(self):
        btr = BetrokkeneFactory.create()
        btr.refresh_from_db()
        self.assertEquals(btr.objecttype, 'BTR')
        self.assertEquals(btr._objecttype_model, 'Betrokkene')

    def test_hulpfunctie_relatie_heeft_rol_in_met_gerelateerde_Zaak(self):
        betrokkene = BetrokkeneMetRolFactory.create()
        rollen = list(betrokkene.heeft_rol_in())

        self.assertEqual(len(rollen), 1)
        self.assertEqual(len(Rol.objects.all()), 1)

        rol = Rol.objects.all().first()
        self.assertEqual(betrokkene, rol.betrokkene)

    def test_hulpfunctie_relatie_heeft_ontvangen_of_verzonden_met_informatieobject(self):
        betrokkene = BetrokkeneMetVerzendingFactory.create()
        informatieobjecten = list(betrokkene.heeft_verzonden_of_ontvangen())

        self.assertEqual(len(informatieobjecten), 1)
        self.assertEqual(len(Verzending.objects.all()), 1)

        verzending = Verzending.objects.all().first()
        self.assertEqual(betrokkene, verzending.betrokkene)


class NatuurlijkPersoonTestCase(TestCase):
    def test_hulpfunctie_adres_gegevens_binnenland_met_correspondentieadres__postadres_en_verblijfadres(self):
        correspondentieadres = CorrespondentieadresFactory.create()
        verblijfadres = VerblijfAdresFactory.create()
        postadres = PostAdresFactory.create()

        natuurlijkpersoon = NatuurlijkPersoonFactory.create(verblijfadres=verblijfadres, postadres=postadres,
                                                            correspondentieadres=correspondentieadres)
        adresgegevens = natuurlijkpersoon.adres_gegevens_binnenland()

        self.assertEqual(len(adresgegevens), 3)
        self.assertTrue(verblijfadres in adresgegevens)
        self.assertTrue(correspondentieadres in adresgegevens)
        self.assertTrue(postadres in adresgegevens)

    def test_hulpfunctie_adres_gegevens_buitenland_met_postadres_en_verblijfbuitenland(self):
        postadres = PostAdresFactory.create()
        verblijf_buitenland = VerblijfBuitenlandFactory.create()
        verblijfadres = VerblijfAdresFactory.create()

        natuurlijkpersoon = NatuurlijkPersoonFactory.create(verblijfadres=verblijfadres, postadres=postadres,
                                                            verblijf_buitenland=verblijf_buitenland)
        adresgegevens = natuurlijkpersoon.adres_gegevens_buitenland()

        self.assertEqual(len(adresgegevens), 3)
        self.assertTrue(verblijfadres in adresgegevens)
        self.assertTrue(verblijf_buitenland in adresgegevens)
        self.assertTrue(postadres in adresgegevens)

    def test_save_objecttype(self):
        postadres = PostAdresFactory.create()
        verblijf_buitenland = VerblijfBuitenlandFactory.create()
        verblijfadres = VerblijfAdresFactory.create()

        natuurlijkpersoon = NatuurlijkPersoonFactory.create(verblijfadres=verblijfadres, postadres=postadres,
                                                            verblijf_buitenland=verblijf_buitenland)
        natuurlijkpersoon.refresh_from_db()
        self.assertEquals(natuurlijkpersoon.objecttype, 'NPS')
        self.assertEquals(natuurlijkpersoon._objecttype_model, 'Betrokkene')
        self.assertEquals(natuurlijkpersoon.betrokkene_ptr._betrokkenetype_model, 'NatuurlijkPersoon')
        self.assertEquals(natuurlijkpersoon.betrokkene_ptr.betrokkenetype, 'NPS')

    def test_is_type(self):
        natuurlijkpersoon = NatuurlijkPersoonFactory.create()
        betrokkene = natuurlijkpersoon.betrokkene_ptr
        self.assertEquals(betrokkene.is_type(), natuurlijkpersoon)


class NietNatuurlijkPersoonTestCase(TestCase):

    def test_hulpfunctie_adres_gegevens_binnenland_met_correspondentieadres_en_postadres(self):
        postadres = PostAdresFactory.create()
        correspondentieadres = CorrespondentieadresFactory.create()

        nietnatuurlijkpersoon = NietNatuurlijkPersoonFactory.create(postadres=postadres,
                                                                    correspondentieadres=correspondentieadres)
        adresgegevens = nietnatuurlijkpersoon.adres_gegevens_binnenland()

        self.assertEqual(len(adresgegevens), 2)
        self.assertTrue(correspondentieadres in adresgegevens)
        self.assertTrue(postadres in adresgegevens)

    def test_hulpfunctie_adres_gegevens_buitenland_met_postadres_en_verblijfbuitenland(self):
        postadres = PostAdresFactory.create()
        verblijf_buitenland = VerblijfBuitenlandFactory.create()

        nietnatuurlijkpersoon = NietNatuurlijkPersoonFactory.create(postadres=postadres,
                                                                    verblijf_buitenland=verblijf_buitenland)
        adresgegevens = nietnatuurlijkpersoon.adres_gegevens_buitenland()

        self.assertEqual(len(adresgegevens), 2)
        self.assertTrue(verblijf_buitenland in adresgegevens)
        self.assertTrue(postadres in adresgegevens)

    def test_save_objecttype(self):
        nnp = NietNatuurlijkPersoonFactory.create()
        nnp.refresh_from_db()
        self.assertEquals(nnp.objecttype, 'NNP')
        self.assertEquals(nnp._betrokkenetype_model, 'NietNatuurlijkPersoon')
        self.assertEquals(nnp._objecttype_model, 'Betrokkene')

    def test_is_type(self):
        nietnatuurlijkpersoon = NietNatuurlijkPersoonFactory.create()
        betrokkene = nietnatuurlijkpersoon.betrokkene_ptr
        self.assertEquals(betrokkene.is_type(), nietnatuurlijkpersoon)


class VestigingTestCase(TestCase):
    def test_hulpfunctie_adres_gegevens_binnenland_met_correspondentieadres_postadres_en_locatieadres(self):
        correspondentieadres = CorrespondentieadresFactory.create()
        locatieadres = LocatieadresFactory.create()
        postadres = PostAdresFactory.create()

        vestiging = VestigingFactory.create(locatieadres=locatieadres, postadres=postadres,
                                            correspondentieadres=correspondentieadres)
        adresgegevens = vestiging.adres_gegevens_binnenland()

        self.assertEqual(len(adresgegevens), 3)
        self.assertTrue(locatieadres in adresgegevens)
        self.assertTrue(correspondentieadres in adresgegevens)
        self.assertTrue(postadres in adresgegevens)

    def test_hulpfunctie_adres_gegevens_buitenland_met_postadres_en_verblijfbuitenland(self):
        postadres = PostAdresFactory.create()
        verblijf_buitenland = VerblijfBuitenlandFactory.create()
        locatieadres = LocatieadresFactory.create()

        vestiging = VestigingFactory.create(locatieadres=locatieadres, postadres=postadres,
                                            verblijf_buitenland=verblijf_buitenland)
        adresgegevens = vestiging.adres_gegevens_buitenland()

        self.assertEqual(len(adresgegevens), 3)
        self.assertTrue(locatieadres in adresgegevens)
        self.assertTrue(verblijf_buitenland in adresgegevens)
        self.assertTrue(postadres in adresgegevens)

    def test_save_objecttype(self):
        ves = VestigingFactory.create()
        ves.refresh_from_db()
        self.assertEquals(ves.objecttype, 'VES')
        self.assertEquals(ves._betrokkenetype_model, 'Vestiging')
        self.assertEquals(ves._objecttype_model, 'Betrokkene')

    def test_is_type(self):
        vestiging = VestigingFactory.create()
        betrokkene = vestiging.betrokkene_ptr
        self.assertEquals(betrokkene.is_type(), vestiging)


class VestigingVanZaakBehandelendeOrganisatieTestCase(TestCase):
    def test_objects_create_objecttype(self):
        vzo = VestigingVanZaakBehandelendeOrganisatieFactory.create()
        vzo.refresh_from_db()
        self.assertEquals(vzo.objecttype, 'VZO')
        self.assertEquals(vzo._vestigingtype_model, 'VestigingVanZaakBehandelendeOrganisatie')
        self.assertEquals(vzo._betrokkenetype_model, 'Vestiging')
        self.assertEquals(vzo._objecttype_model, 'Betrokkene')

        obj = vzo.vestiging_ptr.betrokkene_ptr.object_ptr
        self.assertIs(type(obj.is_type()), VestigingVanZaakBehandelendeOrganisatie)


class KlantContactTestCase(TestCase):
    # def test_validatie_relatie_met_geen_relatie_deelnemers(self):
    #     with self.assertRaises(ValidationError):
    #         KlantcontactFactory.create(vestiging=None)

    def test_hulpfunctie_relatie_heeft_plaats_gevonden_met_vestiging(self):
        klantcontact = KlantcontactMetVestigingFactory()
        natuurlijk_persoon, klantcontact_vestiging = klantcontact.heeft_plaats_gevonden_met()

        self.assertIsNone(natuurlijk_persoon)
        self.assertIsNotNone(klantcontact_vestiging)

    def test_hulpfunctie_relatie_is_gevoerd_door(self):
        medewerker = MedewerkerFactory.create()
        klantcontact = KlantcontactFactory.create(medewerker=medewerker)
        self.assertEqual(medewerker, klantcontact.is_gevoerd_door())

    def test_hulpfunctie_betrekking_op(self):
        zaak = ZaakFactory.create()
        klantcontact = KlantcontactFactory.create(zaak=zaak)
        self.assertEqual(klantcontact.heeft_betrekking_op(), zaak)


class OrganisatorischeTestCase(TestCase):

    def test_hulpfunctie_relatie_is_verantwoordelijk_voor(self):
        org = OrganisatorischeEenheidFactory.create()
        zaaktype1 = ZaakTypeFactory.create(organisatorische_eenheid=org)
        zaaktype2 = ZaakTypeFactory.create(organisatorische_eenheid=org)
        self.assertEqual(len(org.is_verantwoordelijk_voor()), 2)
        self.assertTrue(zaaktype1 in org.is_verantwoordelijk_voor())
        self.assertTrue(zaaktype2 in org.is_verantwoordelijk_voor())

    def test_hulpfunctie_relatie_is_gehuisvest_in(self):
        vestiging = VestigingVanZaakBehandelendeOrganisatieFactory.create()
        org = OrganisatorischeEenheidFactory.create(gevestigd_in=vestiging)
        self.assertEqual(org.is_gehuisvest_in(), vestiging)

    def test_save_objecttype(self):
        org_eenheid = OrganisatorischeEenheidFactory.create()

        org_eenheid.refresh_from_db()
        self.assertEquals(org_eenheid._betrokkenetype_model, 'OrganisatorischeEenheid')
        self.assertEquals(org_eenheid.betrokkenetype, 'OEH')

    def test_is_type(self):
        org_eenheid = OrganisatorischeEenheidFactory.create()
        betrokkene = org_eenheid.betrokkene_ptr
        self.assertEquals(betrokkene.is_type(), org_eenheid)


class MedewerkerTestCase(TestCase):
    def test_hulpfunctie_relatie_hoort_bij(self):
        org_eenheid = OrganisatorischeEenheidFactory.create()
        medewerker = MedewerkerFactory.create(organisatorische_eenheid=org_eenheid)
        self.assertEqual(medewerker.hoort_bij(), org_eenheid)

    def test_hulpfunctie_is_verantwoordelijk_voor(self):
        medewerker = MedewerkerFactory.create()
        org_eenheid = OrganisatorischeEenheidFactory.create(
            verantwoordelijke=medewerker)
        zaaktype1 = ZaakTypeFactory.create(
            medewerker=medewerker)
        zaaktype2 = ZaakTypeFactory.create(
            medewerker=medewerker)
        self.assertEqual(org_eenheid, medewerker.is_verantwoordelijk_voor()[0])
        # Check of beide zaaktypes in de queryset zitten
        self.assertTrue(zaaktype1 in medewerker.is_verantwoordelijk_voor()[1])
        self.assertTrue(zaaktype2 in medewerker.is_verantwoordelijk_voor()[1])

    def test_hulpfunctie_is_contactpersoon_voor(self):
        org_eenheid = OrganisatorischeEenheidFactory.create()
        medewerker = MedewerkerFactory.create(organisatorische_eenheid=org_eenheid)
        self.assertEqual(medewerker.hoort_bij(), org_eenheid)

    def test_save_objecttype(self):
        org_eenheid = OrganisatorischeEenheidFactory.create()
        medewerker = MedewerkerFactory.create(organisatorische_eenheid=org_eenheid)

        medewerker.refresh_from_db()
        self.assertEquals(medewerker._betrokkenetype_model, 'Medewerker')
        self.assertEquals(medewerker.betrokkenetype, 'MDW')

    def test_is_type(self):
        org_eenheid = OrganisatorischeEenheidFactory.create()
        medewerker = MedewerkerFactory.create(organisatorische_eenheid=org_eenheid)
        betrokkene = medewerker.betrokkene_ptr
        self.assertEquals(betrokkene.is_type(), medewerker)


class RolTestCase(TestCase):
    def test_hulpfunctie_zet_als_betrokkene(self):
        rol = RolFactory.create()
        status1 = StatusFactory(rol=rol)
        status2 = StatusFactory(rol=rol)

        self.assertEqual(len(rol.zet_als_betrokkene()), 2)
        self.assertTrue(status1 in rol.zet_als_betrokkene())
        self.assertTrue(status2 in rol.zet_als_betrokkene())
