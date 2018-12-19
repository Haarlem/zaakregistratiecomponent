import unittest
from unittest import skip

from django.test import override_settings

from lxml import etree

from zaakmagazijn.api.stuf.choices import BerichtcodeChoices
from zaakmagazijn.rgbz.choices import ArchiefStatus, Rolomschrijving
from zaakmagazijn.rgbz.models import (
    BuurtObject, KadastraalPerceelObject,
    OverigeAdresseerbaarObjectAanduidingObject, Rol, Zaak
)
from zaakmagazijn.rgbz.tests.factory_models import (
    BuurtObjectFactory, KadastraalPerceelObjectFactory, MedewerkerFactory,
    NatuurlijkPersoonFactory, NietNatuurlijkPersoonFactory,
    OrganisatorischeEenheidFactory,
    OverigeAdresseerbaarObjectAanduidingObjectFactory, VestigingFactory,
    ZaakTypeFactory
)

from .base import BaseTestPlatformTests


class MaykincreeerZaak_ZakLk01ZakObjectTests(BaseTestPlatformTests):
    test_files_subfolder = 'maykin_creeerZaak'
    porttype = 'OntvangAsynchroon'

    def setUp(self):
        super().setUp()

        # medewerker wordt geidentificeerd in de .xml bestanden, met
        # '${gemeentecode}56789' wat is vervangen door '0123456789'
        self.medewerker = MedewerkerFactory.create(
            organisatorische_eenheid__organisatieeenheididentificatie='01234',
            medewerkeridentificatie='56789')
        self.assertEqual(self.medewerker.identificatie, '0123456789')

        self.zaak_type = ZaakTypeFactory.create(
            zaaktypeomschrijving='Aanvraag burgerservicenummer behandelen',
            zaaktypeidentificatie='12345678')

        self.context = {
            'gemeentecode': '',
            'referentienummer': self.genereerID(10),

            'datumVandaag': self.genereerdatum(),
            'datumEergisteren': self.genereerdatum(-2),
            'tijdstipRegistratie': self.genereerdatumtijd(),

            'zds_zaaktype_omschrijving': 'Aanvraag burgerservicenummer behandelen',
            'zds_zaaktype_code': '12345678',
        }

    def test_create_buurt(self):
        """
        You can't actually create a BuurtObject, since
        datum_einde_geldigheid_buurt, datum_begin_geldigheid_buurt and identificatie
        are required to create one, and they aren't defined by RGBZ.
        """
        self.context.update(**{
            'buurtcode': '12',
            'buurtnaam': 'Buurtnaam',
            'gem_gemeente_code': '1234',
            'wijk_wijk_code': '12',
            'genereerbesluitident_identificatie_2': '123',
            'genereerzaakident_identificatie_2': self.genereerID(10),
        })
        buurt = BuurtObjectFactory.create(
            buurtcode=self.context['buurtcode'],
            buurtnaam=self.context['buurtnaam'],
            gemeentecode=self.context['gem_gemeente_code'],
            wijkcode=self.context['wijk_wijk_code'],
        )

        vraag = 'creeerZaak_ZakLk01_buurt.xml'
        response = self._do_request(self.porttype, vraag, self.context)

        # Only 1 BuurtObject should've been created.
        self.assertEquals(BuurtObject.objects.count(), 1)

        zaak = Zaak.objects.get()
        self.assertEquals(zaak.zaakobject_set.count(), 1)
        zaakobj = zaak.zaakobject_set.get()
        self.assertEquals(zaakobj.relatieomschrijving, 'omschrijving')
        obj = zaakobj.object
        buurt = obj.is_type()
        self.assertIs(type(buurt), BuurtObject)
        self.assertEquals(buurt.buurtcode, self.context['buurtcode'])
        self.assertEquals(buurt.buurtnaam, self.context['buurtnaam'])
        self.assertEquals(buurt.gemeentecode, self.context['gem_gemeente_code'])
        self.assertEquals(buurt.wijkcode, self.context['wijk_wijk_code'])

    def test_zakobj_enkelvoudig_document(self):
        pass

    def test_zaakobject_gemeente(self):
        pass

    def test_zaakobject_gemeentelijkeOpenbareRuimte(self):
        # TODO: Implement
        pass

    def test_zaakobject_huishouden(self):
        # TODO: Implement
        pass

    def test_zaakobject_inrichtingselement(self):
        # TODO: Implement
        pass

    def test_zaakobject_kadastraleOnroerendeZaak(self):
        """
        You can't actually create a test_zaakobject_kadastraleOnroerendeZaak, since
        datum_begin_geldigheid_kadastrale_onroerende_zaak, datum_einde_geldigheid_kadastrale_onroerende_zaak
        are required to create one, and they aren't defined by RGBZ.
        """
        self.context.update(**{
            'kadastrale_identificatie': '1234567',
            'kadastrale_gemeentecode': '12',
            'kadastrale_sectie': '34',
            'kadastraal_perceelnummer': '56',
            'apr_appartements_index': '78',
            'genereerbesluitident_identificatie_2': '123',
            'genereerzaakident_identificatie_2': self.genereerID(10),
            'ingangsdatum_object': '20170902',
        })

        KadastraalPerceelObjectFactory.create(
            identificatie=self.context['kadastrale_identificatie'],
            kadastrale_aanduiding__kadastralegemeentecode=self.context['kadastrale_gemeentecode'],
            kadastrale_aanduiding__sectie=self.context['kadastrale_sectie'],
            kadastrale_aanduiding__perceelnummer=self.context['kadastraal_perceelnummer'],
            kadastrale_aanduiding__appartementsrechtvolgnummer=self.context['apr_appartements_index'],
        )

        vraag = 'creeerZaak_ZakLk01_koz.xml'
        response = self._do_request(self.porttype, vraag, self.context)

        zaak = Zaak.objects.get()
        self.assertEquals(zaak.zaakobject_set.count(), 1)
        zaakobj = zaak.zaakobject_set.get()
        self.assertEquals(zaakobj.relatieomschrijving, 'omschrijving')
        obj = zaakobj.object
        koz = obj.is_type()
        self.assertIs(type(koz), KadastraalPerceelObject)
        self.assertEquals(koz.identificatie, self.context['kadastrale_identificatie'])

        self.assertEquals(koz.kadastrale_aanduiding.kadastralegemeentecode, self.context['kadastrale_gemeentecode'])
        self.assertEquals(koz.kadastrale_aanduiding.sectie, self.context['kadastrale_sectie'])
        self.assertEquals(koz.kadastrale_aanduiding.perceelnummer, int(self.context['kadastraal_perceelnummer']))
        self.assertEquals(koz.kadastrale_aanduiding.appartementsrechtvolgnummer, int(self.context['apr_appartements_index']))

    def test_zaakobject_kunstwerkdeel(self):
        # TODO: Implement
        pass

    def test_zaakobject_maatschappelijkeActiviteit(self):
        # TODO: Implement
        pass

    def test_zaakobject_medewerker(self):
        # TODO: Implement
        pass

    def test_zaakobject_natuurlijkPersoon(self):
        # TODO: Implement
        pass

    def test_zaakobject_nietNatuurlijkPersoon(self):
        # TODO: Implement
        pass

    def test_zaakobject_openbareRuimte(self):
        # TODO: Implement
        pass

    def test_zaakobject_organisatorischeEenheid(self):
        # TODO: Implement
        pass

    def test_zaakobject_pand(self):
        # TODO: Implement
        pass

    def test_zaakobject_samengesteldDocument(self):
        # TODO: Implement
        pass

    def test_zaakobject_spoorbaandeel(self):
        # TODO: Implement
        pass

    def test_zaakobject_status(self):
        # TODO: Implement
        pass

    def test_zaakobject_terreindeel(self):
        # TODO: Implement
        pass

    def test_zaakobject_vestiging(self):
        # TODO: Implement
        pass

    def test_zaakobject_waterdeel(self):
        # TODO: Implement
        pass

    def test_zaakobject_wegdeel(self):
        # TODO: Implement
        pass

    def test_zaakobject_wijk(self):
        # TODO: Implement
        pass

    def test_zaakobject_woonplaats(self):
        # TODO: Implement
        pass

    def test_zaakobject_wozDeelobject(self):
        # TODO: Implement
        pass

    def test_zaakobject_wozObject(self):
        # TODO: Implement
        pass

    def test_zaakobject_wozWaarde(self):
        # TODO: Implement
        pass

    def test_zaakobject_zakelijkRecht(self):
        # TODO: Implement
        pass


class STPcreeerZaak_ZakLk01Tests(BaseTestPlatformTests):
    test_files_subfolder = 'stp_creeerZaak'
    porttype = 'OntvangAsynchroon'

    def setUp(self):
        super().setUp()

        # medewerker wordt geidentificeerd in de .xml bestanden, met
        # '${gemeentecode}56789' wat is vervangen door '0123456789'
        self.medewerker = MedewerkerFactory.create(
            organisatorische_eenheid__organisatieeenheididentificatie='01234',
            medewerkeridentificatie='123456789',
            achternaam='achternaam',
            voorvoegsel_achternaam='voorvoeg',
            voorletters='voorletters',
        )
        self.assertEqual(self.medewerker.identificatie, '01234123456789')

        self.zaak_type = ZaakTypeFactory.create(
            zaaktypeomschrijving='Aanvraag burgerservicenummer behandelen',
            zaaktypeidentificatie='12345678',
            datum_begin_geldigheid_zaaktype='20171001')
        self.context = {
            'gemeentecode': '1234',
            'referentienummer': self.genereerID(10),

            'datumVandaag': self.genereerdatum(),
            'datumEergisteren': self.genereerdatum(-2),
            'tijdstipRegistratie': self.genereerdatumtijd(),

            'zds_zaaktype_omschrijving': 'Aanvraag burgerservicenummer behandelen',
            'zds_zaaktype_code': '12345678',
            'zds_zaaktype_datum': '20171001',
        }

    def _test_response(self, response):
        self.assertEquals(response.status_code, 200, response.content)

        response_root = etree.fromstring(response.content)
        response_berichtcode = response_root.xpath(
            '//stuf:stuurgegevens/stuf:berichtcode', namespaces=self.nsmap
        )[0].text
        self.assertEqual(response_berichtcode, BerichtcodeChoices.bv03, response.content)

    def test_create_01(self):
        """
        creeerZaak_zakLk01 volgnummer 1
        """
        self.assertFalse(Zaak.objects.exists())

        vraag = 'creeerZaak_ZakLk01_01.orig.xml'
        self.context.update(**{
            'genereerbesluitident_identificatie_2': '123',
            'genereerzaakident_identificatie_2': self.genereerID(10),
        })
        response = self._do_request(self.porttype, vraag, self.context, stp_syntax=True)

        self._test_response(response)

        # And now we are supposed to wait for the async processing, but since it is
        # not implemented we can immediately check.

        self.assertTrue(Zaak.objects.exists())
        expected = {
            'zaakidentificatie': self.context['gemeentecode'] + self.context['genereerzaakident_identificatie_2'],
            'bronorganisatie': self.context['gemeentecode'],
            'omschrijving': 'omschrijving',
            'toelichting': None,
            'registratiedatum': self.context['datumVandaag'],
            'verantwoordelijke_organisatie': self.context['gemeentecode'],
            'einddatum': None,
            'startdatum': self.context['datumVandaag'],
            'einddatum_gepland': None,
            'uiterlijke_einddatum_afdoening': None,
            'resultaatomschrijving': None,
            'resultaattoelichting': None,
            'publicatiedatum': None,
            'archiefnominatie': None,
            'archiefstatus': ArchiefStatus.nog_te_archiveren,
            'archiefactiedatum': None,
            'betalingsindicatie': None,
            'laatste_betaaldatum': None,
            'zaaktype_id': self.zaak_type.pk,
        }
        self.assertTrue(Zaak.objects.filter(**expected).exists())
        zaak = Zaak.objects.get(**expected)
        self.assertTrue(Rol.objects.filter(
            zaak=zaak, betrokkene=self.medewerker, rolomschrijving=Rolomschrijving.initiator
        ).exists())

        self._validate_response(response)

        self.assertFalse(zaak.zaakkenmerk_set.exists())

    def test_create_03(self):
        """
        creeerZaak_zakLk01 volgnummer 3
        """
        vraag = 'creeerZaak_ZakLk01_03.orig.xml'
        medewerker = MedewerkerFactory.create(
            medewerkeridentificatie='7007',
            organisatorische_eenheid=None,
        )
        self.assertEqual(medewerker.identificatie, '7007')

        ZaakTypeFactory.create(
            zaaktypeomschrijving='Aanvraag burgerservicenummer behandelen',
            zaaktypeidentificatie='12345679')

        # TODO [TECH]: This should be created in the tests, but the matching-data mismatches
        # with the required information. This can be removed once Issue #250 is solved.
        oeh = OrganisatorischeEenheidFactory.create(
            identificatie='organisatorischeEenheid',
            naam='Naam',
            organisatieeenheididentificatie='organisatorischeEenheid',
            organisatieidentificatie='0',
            gevestigd_in__is_specialisatie_van__identificatie='012345678910',
            gevestigd_in__is_specialisatie_van__handelsnaam=['handelsnaam', ],
        )

        self.assertEquals(OverigeAdresseerbaarObjectAanduidingObject.objects.count(), 0)

        # # In the test this is a 'T', however, the required field 'datum_begin_geldigheid_adresseerbaar_object_aanduiding'
        # # isn't given a value in the StUF test, so we can't possibly create the OverigeAdresseerbaarObjectAanduidingObject object.OverigeAdresseerbaarObjectAanduidingObject
        # # I assume, that the KING test suite assumes that we create this object in our database.
        # OverigeAdresseerbaarObjectAanduidingObjectFactory.create(
        #     identificatie='0123456789101112',
        #     woonplaatsnaam='woonplaatsNaam',
        #     naam_openbare_ruimte='openbareRuimteNaam',
        #     huisnummer=99999,
        #     huisletter='A',
        #     huisnummertoevoeging='',
        #     postcode='1000',
        # )

        self.assertEquals(Zaak.objects.count(), 0)
        self.context.update(**{
            'genereerzaakident_identificatie_4': self.genereerID(10),
            'genereerbesluitident_identificatie_2': '123',
            'genereerzaakident_identificatie_2': self.genereerID(10),
        })
        response = self._do_request(self.porttype, vraag, self.context, stp_syntax=True)

        self._test_response(response)

        self.assertEquals(Zaak.objects.count(), 1)
        expected = {
            'zaakidentificatie': self.context['gemeentecode'] + self.context['genereerzaakident_identificatie_4'],
            'bronorganisatie': self.context['gemeentecode'],
            'archiefstatus': 'Nog te archiveren',
            'verantwoordelijke_organisatie': self.context['gemeentecode'],
            'omschrijving': 'omschrijving',
            'toelichting': 'toelichting',
            'resultaatomschrijving': 'omschrijving',
            'resultaattoelichting': 'toelichting',
            'startdatum': self.context['datumVandaag'],
            'registratiedatum': self.context['datumVandaag'],
            'publicatiedatum': self.context['datumVandaag'],
            'einddatum_gepland': self.context['datumVandaag'],
            'uiterlijke_einddatum_afdoening': self.context['datumVandaag'],
            'einddatum': self.context['datumVandaag'],
            'betalingsindicatie': '(Nog) niet',
            'laatste_betaaldatum': self.context['datumVandaag'],
            'archiefnominatie': None,
            'zaaktype_id': self.zaak_type.pk,
        }
        self.assertTrue(Zaak.objects.filter(**expected).exists())
        zaak = Zaak.objects.get()

        self.assertEquals(zaak.zaakkenmerk_set.filter(
            kenmerk='kenmerk', kenmerk_bron='bron'
        ).count(), 2)

        self.assertEquals(zaak.anderzaakobject_set.filter(
            ander_zaakobject_omschrijving='omschrijving', ander_zaakobject_aanduiding='aanduiding',
            ander_zaakobject_registratie='registratie',
            ander_zaakobject_lokatie__startswith='<gml:OrientableSurface',
        ).count(), 2)

        # Test for resultaat

        self.assertEquals(zaak.zaakopschorting_set.filter(
            indicatie_opschorting='N', reden_opschorting='reden',
        ).count(), 1)

        self.assertEquals(zaak.zaakverlenging_set.filter(
            duur_verlenging=123, reden_verlenging='reden',
        ).count(), 1)

        self.assertEquals(zaak.zaakobject_set.count(), 2)

        self.assertEquals(OverigeAdresseerbaarObjectAanduidingObject.objects.filter(
            object_zaken__in=[zaak, ],
            identificatie='0123456789101112',
            woonplaatsnaam='woonplaatsNaam',
            naam_openbare_ruimte='openbareRuimteNaam',
            huisnummer='99999',
            huisletter='A',
            huisnummertoevoeging='',
        ).count(), 2)

        # De rollen zijn als volgt aangepast van RGBZ 1.0 naar RGBZ 2.0.
        #
        # "Gemachtigde" wordt "Belanghebbende"
        # "Overig" wordt "Adviseur"
        # "Uitvoerder" wordt "Behandelaar"
        # "Verantwoordelijke" wordt "Beslisser"
        # Overige rolbenamingen blijven gelijk.

        # Both 'heeftAlsBelanghebbende' and 'heeftAlsGemachtigde' in RGBZ2 are stored as
        # 'Belanghebbende' and both point to medewerker.
        belanghebbenden = zaak.rol_set.filter(
            rolomschrijving=Rolomschrijving.belanghebbende,
            betrokkene=self.medewerker)
        self.assertEquals(belanghebbenden.count(), 4)

        # heeftAlsInitiator
        initiators = zaak.rol_set.filter(
            rolomschrijving=Rolomschrijving.initiator,
            betrokkene=oeh)
        self.assertEquals(initiators.count(), 1)

        # heeftAlsUitvoerende
        behandelaars = zaak.rol_set.filter(
            rolomschrijving=Rolomschrijving.behandelaar,
            betrokkene=self.medewerker)
        self.assertEquals(behandelaars.count(), 2)

        # heeftAlsVerantwoordelijke
        beslissers = zaak.rol_set.filter(
            rolomschrijving=Rolomschrijving.beslisser,
            betrokkene=self.medewerker)
        self.assertEquals(beslissers.count(), 2)

        # heeftAlsOverigBetrokkene
        adviseurs = zaak.rol_set.filter(
            rolomschrijving=Rolomschrijving.adviseur,
            betrokkene=self.medewerker)
        self.assertEquals(adviseurs.count(), 2)

        self._validate_response(response)

    def test_create_05(self):
        vraag = 'creeerZaak_ZakLk01_05.orig.xml'

        nps = NatuurlijkPersoonFactory.create(burgerservicenummer=self.context['gemeentecode'] + '56789')

        self.context.update(
            genereerzaakident_identificatie_6=self.genereerID(10)
        )
        response = self._do_request(self.porttype, vraag, self.context, stp_syntax=True)

        zaak = Zaak.objects.get()

        # heeftAlsInitiator
        initiators = zaak.rol_set.filter(
            rolomschrijving=Rolomschrijving.initiator,
            betrokkene=nps)
        self.assertEquals(initiators.count(), 1)

        self._test_response(response)
        self._validate_response(response)

    def test_create_07(self):
        vraag = 'creeerZaak_ZakLk01_07.orig.xml'
        nnps = NietNatuurlijkPersoonFactory.create(rsin=self.context['gemeentecode'] + '56789')
        self.context.update(
            creerzaak_identificatie_7=self.genereerID(10)
        )
        response = self._do_request(self.porttype, vraag, self.context, stp_syntax=True)

        zaak = Zaak.objects.get()

        belanghebbenden = zaak.rol_set.filter(
            rolomschrijving=Rolomschrijving.belanghebbende,
            betrokkene=self.medewerker)
        self.assertEquals(belanghebbenden.count(), 1)

        # heeftAlsInitiator
        initiators = zaak.rol_set.filter(
            rolomschrijving=Rolomschrijving.initiator,
            betrokkene=nnps)
        self.assertEquals(initiators.count(), 1)

        self._test_response(response)
        self._validate_response(response)

    def test_create_09(self):
        ves = VestigingFactory.create(identificatie='010203040506')

        vraag = 'creeerZaak_ZakLk01_09.orig.xml'
        self.context.update(
            creerzaak_identificatie_9=self.genereerID(10)
        )
        response = self._do_request(self.porttype, vraag, self.context, stp_syntax=True)

        zaak = Zaak.objects.get()
        initiators = zaak.rol_set.filter(
            rolomschrijving=Rolomschrijving.initiator,
            betrokkene=ves)
        self.assertEquals(initiators.count(), 1)

        self._test_response(response)
        self._validate_response(response)

    def test_create_11(self):
        ves = VestigingFactory.create(identificatie='010203040506')
        vraag = 'creeerZaak_ZakLk01_11.orig.xml'
        self.context.update(
            creerzaak_identificatie_11=self.genereerID(10)
        )
        response = self._do_request(self.porttype, vraag, self.context, stp_syntax=True)

        zaak = Zaak.objects.get()
        initiators = zaak.rol_set.filter(
            rolomschrijving=Rolomschrijving.initiator,
            betrokkene=ves)
        self.assertEquals(initiators.count(), 1)

        self._test_response(response)
        self._validate_response(response)

    def test_create_13(self):
        vraag = 'creeerZaak_ZakLk01_13.orig.xml'

        ves = VestigingFactory.create(identificatie='010203040506')
        mdw56786 = MedewerkerFactory.create(
            medewerkeridentificatie=self.context['gemeentecode'] + '56786',
            organisatorische_eenheid=None,
        )
        mdw56785 = MedewerkerFactory.create(
            medewerkeridentificatie=self.context['gemeentecode'] + '56785',
            organisatorische_eenheid=None,
        )
        mdw56784 = MedewerkerFactory.create(
            medewerkeridentificatie=self.context['gemeentecode'] + '56784',
            organisatorische_eenheid=None,
        )
        mdw56783 = MedewerkerFactory.create(
            medewerkeridentificatie=self.context['gemeentecode'] + '56783',
            organisatorische_eenheid=None,
        )
        mdw56782 = MedewerkerFactory.create(
            medewerkeridentificatie=self.context['gemeentecode'] + '56782',
            organisatorische_eenheid=None,
        )
        mdw56781 = MedewerkerFactory.create(
            medewerkeridentificatie=self.context['gemeentecode'] + '56781',
            organisatorische_eenheid=None,
        )
        self.context.update(
            creerzaak_identificatie_13=self.genereerID(10)
        )
        response = self._do_request(self.porttype, vraag, self.context, stp_syntax=True)

        zaak = Zaak.objects.get()

        # Both 'heeftAlsBelanghebbende' and 'heeftAlsGemachtigde' in RGBZ2 are stored as
        # 'Belanghebbende' and both point to medewerker.
        belanghebbenden = zaak.rol_set.filter(
            rolomschrijving=Rolomschrijving.belanghebbende,
            betrokkene=mdw56781)
        self.assertEquals(belanghebbenden.count(), 1)

        # heeftAlsInitiator
        initiators = zaak.rol_set.filter(
            rolomschrijving=Rolomschrijving.initiator,
            betrokkene=ves)
        self.assertEquals(initiators.count(), 1)

        # heeftAlsUitvoerende
        behandelaars = zaak.rol_set.filter(
            rolomschrijving=Rolomschrijving.behandelaar,
            betrokkene__in=[mdw56782, mdw56783])
        self.assertEquals(behandelaars.count(), 2)

        # heeftAlsVerantwoordelijke
        beslissers = zaak.rol_set.filter(
            rolomschrijving=Rolomschrijving.beslisser,
            betrokkene=mdw56784)
        self.assertEquals(beslissers.count(), 1)

        # heeftAlsOverigBetrokkene
        adviseurs = zaak.rol_set.filter(
            rolomschrijving=Rolomschrijving.adviseur,
            betrokkene__in=[mdw56785, mdw56786])
        self.assertEquals(adviseurs.count(), 2)

        self._test_response(response)
        self._validate_response(response)


class creeerZaak_ZakLk01RegressionTests(BaseTestPlatformTests):
    test_files_subfolder = 'maykin_creeerZaak'
    porttype = 'OntvangAsynchroon'

    @skip('Pending resolve')
    @override_settings(ZAAKMAGAZIJN_SYSTEEM={'organisatie': '0392', 'applicatie': 'SoapUI', 'administratie': 'test', 'gebruiker': 'David'})
    def test_required_fields_in_datamodel(self):
        """
        See: https://taiga.maykinmedia.nl/project/haarlem-zaakmagazijn/issue/277
        """
        zaak_type = ZaakTypeFactory.create(
            zaaktypeomschrijving='MOR',
            zaaktypeidentificatie='1')

        org_eenheid = OrganisatorischeEenheidFactory.create(
            organisatieeenheididentificatie='DVV/KCC')

        vraag = 'creeerZaak_ZakLk01_taiga277.xml'
        response = self._do_request(self.porttype, vraag)

        self.assertEquals(response.status_code, 200, response.content)

        self.assertEqual(Zaak.objects.all().count(), 1)
        self.assertEqual(Zaak.objects.filter(zaakidentificatie='039288072b1c-54f4-485c-8e83-095621e6jkl6').count(), 1)

    @override_settings(ZAAKMAGAZIJN_SYSTEEM={'organisatie': '0392', 'applicatie': 'SoapUI', 'administratie': 'test', 'gebruiker': 'David'})
    def test_naam_matching_query_does_not_exist(self):
        """
        See: https://taiga.maykinmedia.nl/project/haarlem-zaakmagazijn/issue/281
        """
        zaak_type = ZaakTypeFactory.create(
            zaaktypeomschrijving='MOR',
            zaaktypeidentificatie='1',
            datum_begin_geldigheid_zaaktype='20170831',
        )

        org_eenheid = OrganisatorischeEenheidFactory.create(
            organisatieeenheididentificatie='DVV/KCC')

        vraag = 'creeerZaak_ZakLk01_taiga281.xml'
        response = self._do_request(self.porttype, vraag)

        self.assertEquals(response.status_code, 200, response.content)

        self.assertEqual(Zaak.objects.all().count(), 1)
        self.assertEqual(Zaak.objects.filter(zaakidentificatie='039288072b1c-54f4-485c-8e83-095621e6jk24').count(), 1)

    @override_settings(ZAAKMAGAZIJN_SYSTEEM={'organisatie': '0392', 'applicatie': 'SoapUI', 'administratie': 'test', 'gebruiker': 'David'})
    def test_zaaktype_does_not_exist(self):
        """
        See: https://taiga.maykinmedia.nl/project/haarlem-zaakmagazijn/issue/397
        """
        org_eenheid = OrganisatorischeEenheidFactory.create(
            organisatieeenheididentificatie='DVV/KCC')

        zaak_type = ZaakTypeFactory.create(
            zaaktypeomschrijving='MOR',
            zaaktypeidentificatie='1',
            domein='DVV',
            zaaktypeomschrijving_generiek='Melding Openbare Ruimte',
            rsin=1,
            trefwoord=['MOR'],
            doorlooptijd_behandeling=14,
            vertrouwelijk_aanduiding='OPENBAAR',
            publicatie_indicatie='N',
            zaakcategorie=['Onderhouden','Repareren'],
            datum_begin_geldigheid_zaaktype='20170901',
            datum_einde_geldigheid_zaaktype='21000101',
            organisatorische_eenheid=org_eenheid,
        )

        vraag = 'creeerZaak_ZakLk01_taiga397.xml'
        response = self._do_request(self.porttype, vraag)

        self.assertEquals(response.status_code, 200, response.content)

        self.assertEqual(Zaak.objects.all().count(), 1)
        self.assertEqual(Zaak.objects.filter(zaakidentificatie='2017-0000561').count(), 1)


    @override_settings(ZAAKMAGAZIJN_SYSTEEM={'organisatie': '0392', 'applicatie': 'ZSH', 'administratie': '', 'gebruiker': ''})
    def test_create_zaak_creates_zaakobject_and_related_object(self):
        """
        See: https://taiga.maykinmedia.nl/project/haarlem-zaakmagazijn/issue/407
        """
        org_eenheid = OrganisatorischeEenheidFactory.create(
            organisatieeenheididentificatie='DVV/KCC')

        zaak_type = ZaakTypeFactory.create(
            zaaktypeomschrijving='MOR',
            zaaktypeidentificatie='1',
            domein='DVV',
            zaaktypeomschrijving_generiek='Melding Openbare Ruimte',
            rsin=1,
            trefwoord=['MOR'],
            doorlooptijd_behandeling=14,
            vertrouwelijk_aanduiding='OPENBAAR',
            publicatie_indicatie='N',
            zaakcategorie=['Onderhouden','Repareren'],
            datum_begin_geldigheid_zaaktype='20170901',
            datum_einde_geldigheid_zaaktype='21000101',
            organisatorische_eenheid=org_eenheid,
        )

        vraag = 'creeerZaak_ZakLk01_taiga407.xml'
        response = self._do_request(self.porttype, vraag)

        self.assertEquals(response.status_code, 200, response.content)

        self.assertEqual(Zaak.objects.all().count(), 1)
        zaak = Zaak.objects.get()
        self.assertEqual(zaak.zaakidentificatie, '2018-0000439')

        self.assertEqual(zaak.zaakobject_set.count(), 1)
        zaak_object = zaak.zaakobject_set.get()

        self.assertIsNotNone(zaak_object.object)

        object = zaak_object.object
        openbare_ruimte_object = object.is_type()
        self.assertEqual(openbare_ruimte_object.identificatie, '1234121234567890')

    @override_settings(ZAAKMAGAZIJN_SYSTEEM={'organisatie': '0392', 'applicatie': 'ZSH', 'administratie': '', 'gebruiker': ''})
    def test_create_zaak_with_proper_bronorganisatie(self):
        """
        See: https://taiga.maykinmedia.nl/project/haarlem-zaakmagazijn/issue/411
        """
        org_eenheid = OrganisatorischeEenheidFactory.create(
            organisatieeenheididentificatie='DVV/KCC')

        zaak_type = ZaakTypeFactory.create(
            zaaktypeomschrijving='MOR',
            zaaktypeidentificatie='1',
            domein='DVV',
            zaaktypeomschrijving_generiek='Melding Openbare Ruimte',
            rsin=1,
            trefwoord=['MOR'],
            doorlooptijd_behandeling=14,
            vertrouwelijk_aanduiding='OPENBAAR',
            publicatie_indicatie='N',
            zaakcategorie=['Onderhouden','Repareren'],
            datum_begin_geldigheid_zaaktype='20170901',
            datum_einde_geldigheid_zaaktype='21000101',
            organisatorische_eenheid=org_eenheid,
        )

        vraag = 'creeerZaak_ZakLk01_taiga411.xml'
        response = self._do_request(self.porttype, vraag)

        self.assertEquals(response.status_code, 200, response.content)

        self.assertEqual(Zaak.objects.all().count(), 1)
        zaak = Zaak.objects.get()
        self.assertEqual(zaak.zaakidentificatie, '0392-2017-0000001')
        self.assertEqual(zaak.bronorganisatie, '0392')

    @override_settings(ZAAKMAGAZIJN_SYSTEEM={'organisatie': '0392', 'applicatie': 'ZSH', 'administratie': '', 'gebruiker': ''})
    def test_creeer_zaak_als_2_zaaktypen_aanwezig_zijn_met_dezelfde_begindatum(self):
        """
        See: https://taiga.maykinmedia.nl/project/haarlem-zaakmagazijn/issue/415
        """
        org_eenheid_dvv = OrganisatorischeEenheidFactory.create(
            organisatieeenheididentificatie='DVV/KCC')

        org_eenheid_spl = OrganisatorischeEenheidFactory.create(
            organisatieeenheididentificatie='SPL')

        zaak_type_mor = ZaakTypeFactory.create(
            zaaktypeomschrijving='MOR',
            zaaktypeidentificatie='1',
            datum_begin_geldigheid_zaaktype='20170901',
        )

        zaak_type_ander = ZaakTypeFactory.create(
            zaaktypeomschrijving='ANDER',
            zaaktypeidentificatie='2',
            datum_begin_geldigheid_zaaktype='20170901',
        )

        vraag = 'creeerZaak_ZakLk01_taiga415.xml'
        response = self._do_request(self.porttype, vraag)

        self.assertEquals(response.status_code, 200, response.content)
