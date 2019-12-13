import os
from datetime import datetime, timedelta
from operator import attrgetter
from unittest import skip

from django.utils.translation import ugettext_lazy as _
from auditlog.models import LogEntry
from lxml import etree
from zeep.xsd.const import Nil

from ...rgbz.choices import JaNee, Rolomschrijving
from ...rgbz.tests.factory_models import (
    AnderZaakObjectFactory, BesluitFactory, BuurtObjectFactory,
    EnkelvoudigInformatieObjectFactory, GemeenteObjectFactory,
    MedewerkerFactory, OrganisatorischeEenheidFactory,
    OverigeAdresseerbaarObjectAanduidingObjectFactory, RolFactory,
    StatusFactory, VestigingFactory, WijkObjectFactory, ZaakFactory,
    ZaakObjectFactory
)
from ...rsgb.tests.factory_models import PostAdresFactory
from ...utils.stuf_datetime import stuf_date
from ..stuf.choices import BerichtcodeChoices
from ..stuf.constants import BG_XML_NS
from ..stuf.ordering import ZAKSortering
from .base import BaseSoapTests, BaseTestPlatformTests


class GeefZaakdetails_ZakLv01ZAKOBJTests(BaseSoapTests):
    def setUp(self):
        super().setUp()
        self.status = StatusFactory.create()
        self.zaak = self.status.zaak

    def _do_simple_request(self, raw_response=False):
        client = self._get_client('BeantwoordVraag')
        stuf_factory, zkn_factory, zds_factory = self._get_type_factories(client)

        with client.options(raw_response=raw_response):
            return client.service.geefZaakdetails_ZakLv01(
                stuurgegevens=stuf_factory['ZAK-StuurgegevensLv01'](
                    berichtcode='Lv01',
                    entiteittype='ZAK'),
                parameters=stuf_factory['ZAK-parametersVraagSynchroon'](
                    sortering=1,
                    indicatorVervolgvraag=False),
                scope={
                    'object': zkn_factory['ZAK-vraagScope'](
                        entiteittype='ZAK',  # v
                        scope='alles'
                    ),
                },
                gelijk=zkn_factory['GeefZaakDetails-ZAK-vraagSelectie'](
                    entiteittype='ZAK',  # v
                    identificatie=self.zaak.zaakidentificatie,
                )
            )

    def test_zakobj_adres(self):
        oao_obj = OverigeAdresseerbaarObjectAanduidingObjectFactory.create(
            identificatie='123',
            woonplaatsnaam='Amsterdam',
            naam_openbare_ruimte='Hal',
            huisnummer='117',
            huisletter=None,
            huisnummertoevoeging=None,
            datum_begin_geldigheid_adresseerbaar_object_aanduiding="20170901",
            datum_einde_geldigheid_adresseerbaar_object_aanduiding="20170902",
        )
        ZaakObjectFactory.create(zaak=self.zaak, object=oao_obj)
        response = self._do_simple_request(raw_response=True)
        root = etree.fromstring(response.content)

        antwoord_obj = root.xpath(
            '/soap11env:Envelope/soap11env:Body/zds:geefZaakdetails_ZakLa01/zkn:antwoord/zkn:object', namespaces=self.nsmap)[0]
        self._assert_xpath_results(antwoord_obj, 'zkn:heeftBetrekkingOp/zkn:gerelateerde/zkn:adres/bg:identificatie[text()="123"]', 1, namespaces=self.nsmap)
        self._assert_xpath_results(antwoord_obj, 'zkn:heeftBetrekkingOp/zkn:gerelateerde/zkn:adres/bg:wpl.woonplaatsNaam[text()="Amsterdam"]', 1, namespaces=self.nsmap)
        self._assert_xpath_results(antwoord_obj, 'zkn:heeftBetrekkingOp/zkn:gerelateerde/zkn:adres/bg:huisnummer[text()="117"]', 1, namespaces=self.nsmap)
        self._assert_xpath_results(antwoord_obj, 'zkn:heeftBetrekkingOp/zkn:gerelateerde/zkn:adres/bg:huisletter[@xsi:nil="true"]', 1, namespaces=self.nsmap)
        self._assert_xpath_results(antwoord_obj, 'zkn:heeftBetrekkingOp/zkn:gerelateerde/zkn:adres/bg:huisnummertoevoeging[@xsi:nil="true"]', 1, namespaces=self.nsmap)
        self._assert_xpath_results(antwoord_obj, 'zkn:heeftBetrekkingOp/zkn:gerelateerde/zkn:adres/bg:ingangsdatumObject[text()="20170901"]', 1, namespaces=self.nsmap)
        self._assert_xpath_results(antwoord_obj, 'zkn:heeftBetrekkingOp/zkn:gerelateerde/zkn:adres/bg:einddatumObject[text()="20170902"]', 1, namespaces=self.nsmap)

    def test_zakobj_buurt(self):
        brt_obj = BuurtObjectFactory.create(
            buurtcode='12',
            buurtnaam='Amsterdam',
            geometrie='<test></test>',
            wijkcode='12',
            gemeentecode="1234",
            datum_begin_geldigheid_buurt="20170901",
            datum_einde_geldigheid_buurt="20170902",
        )
        ZaakObjectFactory.create(zaak=self.zaak, object=brt_obj)
        response = self._do_simple_request(raw_response=True)
        root = etree.fromstring(response.content)

        antwoord_obj = root.xpath(
            '/soap11env:Envelope/soap11env:Body/zds:geefZaakdetails_ZakLa01/zkn:antwoord/zkn:object', namespaces=self.nsmap)[0]
        self._assert_xpath_results(antwoord_obj, 'zkn:heeftBetrekkingOp/zkn:gerelateerde/zkn:buurt/bg:buurtCode[text()="12"]', 1, namespaces=self.nsmap)
        self._assert_xpath_results(antwoord_obj, 'zkn:heeftBetrekkingOp/zkn:gerelateerde/zkn:buurt/bg:buurtNaam[text()="Amsterdam"]', 1, namespaces=self.nsmap)
        self._assert_xpath_results(antwoord_obj, 'zkn:heeftBetrekkingOp/zkn:gerelateerde/zkn:buurt/bg:geometrie/test', 1, namespaces=self.nsmap)
        self._assert_xpath_results(antwoord_obj, 'zkn:heeftBetrekkingOp/zkn:gerelateerde/zkn:buurt/bg:gem.gemeenteCode[text()="1234"]', 1, namespaces=self.nsmap)
        self._assert_xpath_results(antwoord_obj, 'zkn:heeftBetrekkingOp/zkn:gerelateerde/zkn:buurt/bg:wyk.wijkCode[text()="12"]', 1, namespaces=self.nsmap)
        self._assert_xpath_results(antwoord_obj, 'zkn:heeftBetrekkingOp/zkn:gerelateerde/zkn:buurt/bg:ingangsdatumObject[text()="20170901"]', 1, namespaces=self.nsmap)
        self._assert_xpath_results(antwoord_obj, 'zkn:heeftBetrekkingOp/zkn:gerelateerde/zkn:buurt/bg:einddatumObject[text()="20170902"]', 1, namespaces=self.nsmap)

    def test_zakobj_enkelvoudig_document(self):
        eio_obj = EnkelvoudigInformatieObjectFactory.create(
            informatieobjectidentificatie='123',
            bronorganisatie='321',
            informatieobjecttype__informatieobjecttypeomschrijving='bla',
            creatiedatum='20170901',
            ontvangstdatum='20170902',
            titel='titel',
        )
        ZaakObjectFactory.create(zaak=self.zaak, object=eio_obj)
        response = self._do_simple_request(raw_response=True)
        root = etree.fromstring(response.content)

        eio_obj.refresh_from_db()

        antwoord_obj = root.xpath(
            '/soap11env:Envelope/soap11env:Body/zds:geefZaakdetails_ZakLa01/zkn:antwoord/zkn:object', namespaces=self.nsmap)[0]
        self._assert_xpath_results(antwoord_obj, 'zkn:heeftBetrekkingOp/zkn:gerelateerde/zkn:enkelvoudigDocument/zkn:identificatie[text()="123"]', 1, namespaces=self.nsmap)
        self._assert_xpath_results(antwoord_obj, 'zkn:heeftBetrekkingOp/zkn:gerelateerde/zkn:enkelvoudigDocument/zkn:dct.omschrijving[text()="bla"]', 1, namespaces=self.nsmap)
        self._assert_xpath_results(antwoord_obj, 'zkn:heeftBetrekkingOp/zkn:gerelateerde/zkn:enkelvoudigDocument/zkn:creatiedatum[text()="20170901"]', 1, namespaces=self.nsmap)
        self._assert_xpath_results(antwoord_obj, 'zkn:heeftBetrekkingOp/zkn:gerelateerde/zkn:enkelvoudigDocument/zkn:ontvangstdatum[text()="20170902"]', 1, namespaces=self.nsmap)
        self._assert_xpath_results(antwoord_obj, 'zkn:heeftBetrekkingOp/zkn:gerelateerde/zkn:enkelvoudigDocument/zkn:titel[text()="titel"]', 1, namespaces=self.nsmap)

    def test_zaakobject_gemeente(self):
        gem_obj = GemeenteObjectFactory.create(
            identificatie='123',
            gemeentenaam='gemeente',
            datum_begin_geldigheid_gemeente='20170901',
            datum_einde_geldigheid_gemeente='20170902',
        )
        ZaakObjectFactory.create(zaak=self.zaak, object=gem_obj)
        response = self._do_simple_request(raw_response=True)
        root = etree.fromstring(response.content)

        antwoord_obj = root.xpath(
            '/soap11env:Envelope/soap11env:Body/zds:geefZaakdetails_ZakLa01/zkn:antwoord/zkn:object', namespaces=self.nsmap)[0]
        self._assert_xpath_results(antwoord_obj, 'zkn:heeftBetrekkingOp/zkn:gerelateerde/zkn:gemeente/bg:gemeenteCode[text()="123"]', 1, namespaces=self.nsmap)
        self._assert_xpath_results(antwoord_obj, 'zkn:heeftBetrekkingOp/zkn:gerelateerde/zkn:gemeente/bg:gemeenteNaam[text()="gemeente"]', 1, namespaces=self.nsmap)
        self._assert_xpath_results(antwoord_obj, 'zkn:heeftBetrekkingOp/zkn:gerelateerde/zkn:gemeente/bg:ingangsdatumObject[text()="20170901"]', 1, namespaces=self.nsmap)
        self._assert_xpath_results(antwoord_obj, 'zkn:heeftBetrekkingOp/zkn:gerelateerde/zkn:gemeente/bg:einddatumObject[text()="20170902"]', 1, namespaces=self.nsmap)

    # def test_zaakobject_gemeentelijkeOpenbareRuimte(self):
    #     # TODO: Implement
    #     pass

    # def test_zaakobject_huishouden(self):
    #     # TODO: Implement
    #     pass

    # def test_zaakobject_inrichtingselement(self):
    #     # TODO: Implement
    #     pass

    # def test_zaakobject_kadastraleOnroerendeZaak(self):
    #     # TODO: Implement
    #     pass

    # def test_zaakobject_kunstwerkdeel(self):
    #     # TODO: Implement
    #     pass

    # def test_zaakobject_maatschappelijkeActiviteit(self):
    #     # TODO: Implement
    #     pass

    def test_zaakobject_medewerker(self):
        mdw_obj = MedewerkerFactory.create(
            medewerkeridentificatie='1234567',
            achternaam='achternaam',
            voorletters='voorletters',
            voorvoegsel_achternaam='abc',
            geslachtsaanduiding='M',
            functie='functie',
            datum_uit_dienst='20170901',
            organisatorische_eenheid__organisatieeenheididentificatie='oeh123',
            organisatorische_eenheid__naam='naam',
            organisatorische_eenheid__naam_verkort='naam_verkort',
            organisatorische_eenheid__omschrijving='omschrijving',
            organisatorische_eenheid__toelichting='toelichting',
            organisatorische_eenheid__telefoonnummer='telefoonnummer',
            organisatorische_eenheid__faxnummer='faxnummer',
            organisatorische_eenheid__emailadres='emailadres',
        )
        ZaakObjectFactory.create(zaak=self.zaak, object=mdw_obj)
        response = self._do_simple_request(raw_response=True)
        root = etree.fromstring(response.content)

        zak_obj = root.xpath(
            '/soap11env:Envelope/soap11env:Body/zds:geefZaakdetails_ZakLa01/zkn:antwoord/zkn:object/zkn:heeftBetrekkingOp/zkn:gerelateerde', namespaces=self.nsmap)[0]
        expected = [
            'zkn:medewerker/zkn:identificatie[text()=\'1234567\']',
            'zkn:medewerker/zkn:achternaam[text()=\'achternaam\']',
            'zkn:medewerker/zkn:voorletters[text()=\'voorletters\']',
            'zkn:medewerker/zkn:voorvoegselAchternaam[text()=\'abc\']',
            'zkn:medewerker/zkn:geslachtsaanduiding[text()=\'M\']',
            'zkn:medewerker/zkn:functie[text()=\'functie\']',
            'zkn:medewerker/zkn:datumUitDienst[text()=\'20170901\']',
            'zkn:medewerker/zkn:hoortBij/zkn:gerelateerde/zkn:identificatie[text()=\'oeh123\']',
            'zkn:medewerker/zkn:hoortBij/zkn:gerelateerde/zkn:naam[text()=\'naam\']',
            'zkn:medewerker/zkn:hoortBij/zkn:gerelateerde/zkn:naamVerkort[text()=\'naam_verkort\']',
            'zkn:medewerker/zkn:hoortBij/zkn:gerelateerde/zkn:omschrijving[text()=\'omschrijving\']',
            'zkn:medewerker/zkn:hoortBij/zkn:gerelateerde/zkn:toelichting[text()=\'toelichting\']',
            'zkn:medewerker/zkn:hoortBij/zkn:gerelateerde/zkn:telefoonnummer[text()=\'telefoonnummer\']',
            'zkn:medewerker/zkn:hoortBij/zkn:gerelateerde/zkn:faxnummer[text()=\'faxnummer\']',
            'zkn:medewerker/zkn:hoortBij/zkn:gerelateerde/zkn:emailadres[text()=\'emailadres\']',
            'zkn:medewerker/zkn:hoortBij/zkn:gerelateerde/zkn:isGehuisvestIn/zkn:gerelateerde/zkn:isEen/zkn:gerelateerde/bg:verblijfsadres/bg:wpl.woonplaatsNaam',
        ]

        for expectation in expected:
            self._assert_xpath_results(zak_obj, expectation, 1, namespaces=self.nsmap)

    # def test_zaakobject_natuurlijkPersoon(self):
    #     # TODO: Implement
    #     pass

    # def test_zaakobject_nietNatuurlijkPersoon(self):
    #     # TODO: Implement
    #     pass

    # def test_zaakobject_openbareRuimte(self):
    #     # TODO: Implement
    #     pass

    # def test_zaakobject_organisatorischeEenheid(self):
    #     # TODO: Implement
    #     pass

    # def test_zaakobject_pand(self):
    #     # TODO: Implement
    #     pass

    # def test_zaakobject_samengesteldDocument(self):
    #     # TODO: Implement
    #     pass

    # def test_zaakobject_spoorbaandeel(self):
    #     # TODO: Implement
    #     pass

    # def test_zaakobject_status(self):
    #     # TODO: Implement
    #     pass

    # def test_zaakobject_terreindeel(self):
    #     # TODO: Implement
    #     pass

    # def test_zaakobject_vestiging(self):
    #     # TODO: Implement
    #     pass

    # def test_zaakobject_waterdeel(self):
    #     # TODO: Implement
    #     pass

    # def test_zaakobject_wegdeel(self):
    #     # TODO: Implement
    #     pass

    # def test_zaakobject_wijk(self):
    #     # TODO: Implement
    #     pass

    # def test_zaakobject_woonplaats(self):
    #     # TODO: Implement
    #     pass

    # def test_zaakobject_wozDeelobject(self):
    #     # TODO: Implement
    #     pass

    # def test_zaakobject_wozObject(self):
    #     # TODO: Implement
    #     pass

    # def test_zaakobject_wozWaarde(self):
    #     # TODO: Implement
    #     pass

    # def test_zaakobject_zakelijkRecht(self):
    #     # TODO: Implement
    #     pass


class geefZaakdetails_ZakLv01Tests(BaseSoapTests):
    def setUp(self):
        super().setUp()

        self.zaak = ZaakFactory.create()
        self.yesterday = stuf_date(datetime.today() - timedelta(days=1))
        self.two_days_ago = stuf_date(datetime.today() - timedelta(days=2))

    def _do_simple_request(self):
        client = self._get_client('BeantwoordVraag')
        stuf_factory, zkn_factory, zds_factory = self._get_type_factories(client)

        return client.service.geefZaakdetails_ZakLv01(
            stuurgegevens=stuf_factory['ZAK-StuurgegevensLv01'](
                berichtcode='Lv01',
                entiteittype='ZAK'),
            parameters=stuf_factory['ZAK-parametersVraagSynchroon'](
                sortering=1,
                indicatorVervolgvraag=False),
            scope={
                'object': zkn_factory['ZAK-vraagScope'](
                    entiteittype='ZAK',  # v
                    scope='alles',
                ),
            },
            gelijk=zkn_factory['GeefZaakDetails-ZAK-vraagSelectie'](
                entiteittype='ZAK',  # v
                identificatie=self.zaak.zaakidentificatie,
            )
        )

    def test_gelijk(self):
        status1 = StatusFactory.create(zaak=self.zaak, indicatie_laatst_gezette_status=JaNee.ja)
        status2 = StatusFactory.create(zaak=self.zaak, datum_status_gezet=self.yesterday)
        status3 = StatusFactory.create(zaak=self.zaak, datum_status_gezet=self.two_days_ago)

        # Should not show up, because the 'identificatie' field doesn't match.
        other_zaak = ZaakFactory.create()
        other_status = StatusFactory.create(zaak=other_zaak)

        client = self._get_client('BeantwoordVraag')
        stuf_factory, zkn_factory, zds_factory = self._get_type_factories(client)

        response = client.service.geefZaakdetails_ZakLv01(
            stuurgegevens=stuf_factory['ZAK-StuurgegevensLv01'](
                berichtcode='Lv01',
                entiteittype='ZAK',),
            parameters=stuf_factory['ZAK-parametersVraagSynchroon'](
                sortering=1,
                indicatorVervolgvraag=False),
            scope={
                'object': zkn_factory['ZAK-vraagScope'](
                    entiteittype='ZAK',
                    identificatie=Nil,
                    heeft=zkn_factory['ZAKSTT-vraagScope'](
                        entiteittype='ZAKSTT',
                        indicatieLaatsteStatus=Nil,
                        gerelateerde=zkn_factory['STT-vraag'](
                            entiteittype='STT',
                        )
                    ),),
            },
            gelijk=zkn_factory['GeefZaakDetails-ZAK-vraagSelectie'](
                entiteittype='ZAK',
                identificatie=self.zaak.zaakidentificatie,
            )
        )
        self.assertEquals(response.antwoord.object.identificatie._value_1, self.zaak.zaakidentificatie)
        self.assertEquals(len(response.antwoord.object.heeft), 3)

    def test_scope(self):
        status1 = StatusFactory.create(zaak=self.zaak)

        client = self._get_client('BeantwoordVraag')
        stuf_factory, zkn_factory, zds_factory = self._get_type_factories(client)

        with client.options(raw_response=True):
            response = client.service.geefZaakdetails_ZakLv01(
                stuurgegevens=stuf_factory['ZAK-StuurgegevensLv01'](
                    berichtcode='Lv01',
                    entiteittype='ZAK',),
                parameters=stuf_factory['ZAK-parametersVraagSynchroon'](
                    sortering=1,
                    indicatorVervolgvraag=False),
                scope={
                    'object': zkn_factory['ZAK-vraagScope'](
                        entiteittype='ZAK',
                        identificatie=Nil,
                        heeft=zkn_factory['ZAKSTT-vraagScope'](
                            entiteittype='ZAKSTT',
                            indicatieLaatsteStatus=Nil,
                            gerelateerde=zkn_factory['STT-vraag'](
                                entiteittype='STT',
                            ),
                        ),
                    ),
                },
                gelijk=zkn_factory['GeefZaakDetails-ZAK-vraagSelectie'](
                    entiteittype='ZAK',
                    identificatie=self.zaak.zaakidentificatie,
                )
            )

        root = etree.fromstring(response.content)

        # The expectation is that only the selected fields are returned.
        antwoord_obj = root.xpath(
            '/soap11env:Envelope/soap11env:Body/zds:geefZaakdetails_ZakLa01/zkn:antwoord/zkn:object', namespaces=self.nsmap)[0]
        self._assert_xpath_results(antwoord_obj, 'zkn:identificatie', 1, namespaces=self.nsmap)
        self._assert_xpath_results(antwoord_obj, 'zkn:heeft', 1, namespaces=self.nsmap)
        self._assert_xpath_results(antwoord_obj, 'zkn:heeft/zkn:datumStatusGezet', 0, namespaces=self.nsmap)
        self._assert_xpath_results(antwoord_obj, 'zkn:heeft/zkn:indicatieLaatsteStatus', 1, namespaces=self.nsmap)

    @skip('leidtTot is not part of ZDS 1.2')
    def test_leidtTot(self):
        """
        Make sure 'leidtTot' works as expected. This relation is a 'one-to-many' relation, instead of a many-to-many
        relation. It uses the fk_name 'self' in the enititeit to denote this.
        """
        status1 = StatusFactory.create(zaak=self.zaak)
        besluit = BesluitFactory.create(zaak=self.zaak)

        response = self._do_simple_request()

        self.assertEquals(len(response['antwoord']), 1)
        obj = response['antwoord']['object']
        self.assertEquals(len(obj['leidtTot']), 1)
        leidt_tot = obj['leidtTot'][0]

        self.assertEquals(leidt_tot['gerelateerde']['identificatie'], besluit.besluitidentificatie)
        self.assertEquals(leidt_tot['gerelateerde']['bst.omschrijving'], besluit.besluittype.besluittypeomschrijving)

    def test_organisatorische_eenheid(self):
        organisatorische_eenheid = OrganisatorischeEenheidFactory.create(
            naam_verkort='na',
            omschrijving='omschrijving',
            toelichting='toelichting',
            telefoonnummer='1',
            faxnummer='12',
            emailadres='user@internet',
        )
        vestiging = organisatorische_eenheid.gevestigd_in.is_specialisatie_van
        rol = RolFactory.create(zaak=self.zaak, betrokkene=organisatorische_eenheid, rolomschrijving=Rolomschrijving.initiator)

        response = self._do_simple_request()

        antwoord = response['antwoord']
        obj = antwoord['object']

        # heeftAlsInitiator should be returned as expected.
        heeft_als_initiator = obj['heeftAlsInitiator']
        self.assertEquals(len(heeft_als_initiator), 1)
        heeft_als_initiator_first = heeft_als_initiator[0]
        self.assertEquals(heeft_als_initiator_first['entiteittype'], 'ZAKBTRINI')

        # organisatorischeEenheid as well.
        oeh_response = heeft_als_initiator_first['gerelateerde']['organisatorischeEenheid']
        self.assertEquals(oeh_response['entiteittype'], 'OEH')
        expected_oeh = {
            'identificatie': organisatorische_eenheid.identificatie,
            'naam': organisatorische_eenheid.naam,
            'naamVerkort': organisatorische_eenheid.naam_verkort,
            'omschrijving': organisatorische_eenheid.omschrijving,
            'toelichting': organisatorische_eenheid.toelichting,
            'telefoonnummer': organisatorische_eenheid.telefoonnummer,
            'faxnummer': organisatorische_eenheid.faxnummer,
            'emailadres': organisatorische_eenheid.emailadres,
        }
        for key, value in expected_oeh.items():
            self.assertEquals(oeh_response[key]['_value_1'], value)

        gehuisvest_in = oeh_response['isGehuisvestIn']
        self.assertEquals(gehuisvest_in['entiteittype'], 'OEHVZO')

        gehuisvest_in_gerelateerde = gehuisvest_in['gerelateerde']
        self.assertEquals(gehuisvest_in_gerelateerde['entiteittype'], 'VZO')

        is_een = gehuisvest_in_gerelateerde['isEen']
        self.assertEquals(is_een['entiteittype'], 'VZOVES')

        ves = is_een['gerelateerde']
        self.assertEqual(ves['handelsnaam']['_value_1'], vestiging.handelsnaam[0])
        self.assertEqual(ves['vestigingsNummer']['_value_1'], vestiging.vestigingsnummer)
        self.assertEqual(ves['entiteittype'], 'VES')

    def test_is_gezet_door(self):
        """
        Make sure the 'is gezet door' relation works as expected.
        """
        organisatorische_eenheid = OrganisatorischeEenheidFactory.create()
        rol = RolFactory.create(zaak=self.zaak, betrokkene=organisatorische_eenheid, rolomschrijving=Rolomschrijving.initiator)
        status1 = StatusFactory.create(zaak=self.zaak, rol=rol, indicatie_laatst_gezette_status=JaNee.nee)

        response = self._do_simple_request()
        is_gezet_door = response['antwoord']['object']['heeft'][0]['isGezetDoor']
        self.assertEquals(is_gezet_door['entiteittype'], 'ZAKSTTBTR')

        gerelateerde = is_gezet_door['gerelateerde']
        self.assertEquals(gerelateerde['organisatorischeEenheid']['identificatie']['_value_1'], organisatorische_eenheid.identificatie)

    def test_sortering(self):
        """
        Test all sortering options to give back a response. The order itself
        is not checked.
        """
        client = self._get_client('BeantwoordVraag')
        stuf_factory, zkn_factory, zds_factory = self._get_type_factories(client)

        for i in ZAKSortering.keys():
            with client.options(raw_response=True):
                response = client.service.geefZaakdetails_ZakLv01(
                    stuurgegevens=stuf_factory['ZAK-StuurgegevensLv01'](
                        berichtcode='Lv01',
                        entiteittype='ZAK'),
                    parameters=stuf_factory['ZAK-parametersVraagSynchroon'](
                        sortering=i,
                        indicatorVervolgvraag=False),
                    scope={
                        'object': zkn_factory['ZAK-vraagScope'](
                            entiteittype='ZAK',  # v
                            scope='alles',
                        ),
                    },
                    gelijk=zkn_factory['GeefZaakDetails-ZAK-vraagSelectie'](
                        entiteittype='ZAK',  # v
                        identificatie=self.zaak.zaakidentificatie,
                    )
                )

            response_root = etree.fromstring(response.content)
            response_berichtcode = response_root.xpath(
                '//zkn:stuurgegevens/stuf:berichtcode',
                namespaces=self.nsmap
            )[0].text
            self.assertEqual(response_berichtcode, BerichtcodeChoices.la01, response.content)

            response_object_element = response_root.xpath('//zkn:antwoord/zkn:object', namespaces=self.nsmap)[0]
            response_zak_identificatie = response_object_element.xpath('zkn:identificatie', namespaces=self.nsmap)[0].text

            self.assertEqual(response_zak_identificatie, self.zaak.zaakidentificatie)


class geefZaakdetails_ZakLa01Tests(BaseSoapTests):
    antwoord_xpath = '/soap11env:Envelope/soap11env:Body/zds:geefZaakdetails_ZakLa01'

    def setUp(self):
        super().setUp()
        self.status = StatusFactory.create()
        self.zaak = self.status.zaak

    def _do_simple_request(self, raw_response=False):
        """
        Do a simple SOAP request.
        """
        client = self._get_client('BeantwoordVraag')
        stuf_factory, zkn_factory, zds_factory = self._get_type_factories(client)

        with client.options(raw_response=raw_response):
            return client.service.geefZaakdetails_ZakLv01(
                stuurgegevens=stuf_factory['ZAK-StuurgegevensLv01'](
                    berichtcode='Lv01',
                    entiteittype='ZAK'),
                parameters=stuf_factory['ZAK-parametersVraagSynchroon'](
                    sortering=1,
                    indicatorVervolgvraag=False),
                scope={
                    'object': zkn_factory['ZAK-vraagScope'](**{
                        'entiteittype': 'ZAK',
                        'identificatie': Nil,
                        'anderZaakObject': zkn_factory['ZaakobjectGrp'](
                            omschrijving=Nil,
                            aanduiding=Nil,
                            lokatie=Nil,
                            registratie=Nil,
                        ),
                    }),
                },
                gelijk=zkn_factory['GeefZaakDetails-ZAK-vraagSelectie'](
                    entiteittype='ZAK',  # v
                    identificatie=self.zaak.zaakidentificatie,
                )
            )

    def test_gerelateerde_object_antwoord(self):
        vestiging = VestigingFactory.create()
        wijk_object = WijkObjectFactory.create()

        ZaakObjectFactory.create(
            zaak=self.zaak, object=vestiging.object_ptr)
        client = self._get_client('BeantwoordVraag')

        stuf_factory, zkn_factory, zds_factory = self._get_type_factories(client)
        bg_factory = client.type_factory(BG_XML_NS)

        with client.options(raw_response=True):
            result = client.service.geefZaakdetails_ZakLv01(
                stuurgegevens=stuf_factory['ZAK-StuurgegevensLv01'](
                    berichtcode='Lv01',
                    entiteittype='ZAK'),
                parameters=stuf_factory['ZAK-parametersVraagSynchroon'](
                    sortering=1,
                    indicatorVervolgvraag=False),
                scope={
                    'object': zkn_factory['ZAK-vraagScope'](**{
                        'entiteittype': 'ZAK',
                        'identificatie': Nil,
                        'heeftBetrekkingOp': zkn_factory['ZAKOBJ-vraagScope'](
                            entiteittype='ZAKOBJ',  # v
                            gerelateerde=zkn_factory['OBJ-gerelateerdeVraagScope'](
                                _value_1={
                                    'vestiging': bg_factory['VES-zkn-OBJ-vraag'](
                                        entiteittype='VES',  # v
                                        vestigingsNummer=Nil,
                                    ),
                                }
                            ),
                        ),
                    }),
                },
                gelijk=zkn_factory['GeefZaakDetails-ZAK-vraagSelectie'](
                    entiteittype='ZAK',  # v
                    identificatie=self.zaak.zaakidentificatie,
                )
            )
            root = etree.fromstring(result.content)

            # See Stuf 03.01 - 3.2.2 De structuur van een object
            #
            # Het element <gerelateerde> mag ook als kind een <choice> bevatten met twee of meer elementen
            # met een attribute StUF:entiteittype en daarbinnen de elementen voor dat entiteittype. Het element
            # <gerelateerde> heeft dan geen attributes.
            #

            unexpected = [
                'zkn:antwoord/zkn:object/zkn:heeftBetrekkingOp/zkn:gerelateerde[@stuf:entiteittype]',
            ]
            for u in unexpected:
                self._assert_xpath_results(self._get_body_root(root), u, 0, namespaces=self.nsmap)

            expected = [
                'zkn:antwoord/zkn:object/zkn:heeftBetrekkingOp/zkn:gerelateerde',
                'zkn:antwoord/zkn:object/zkn:heeftBetrekkingOp/zkn:gerelateerde/zkn:vestiging[contains(@stuf:entiteittype,\'VES\')]',
                'zkn:antwoord/zkn:object/zkn:heeftBetrekkingOp/zkn:gerelateerde/zkn:vestiging/bg:vestigingsNummer'
            ]
            for e in expected:
                self._assert_xpath_results(self._get_body_root(root), e, 1, namespaces=self.nsmap)

    def test_heeft_als_betrokkene(self):
        """
        ZAKBTRBTR
        """
        medewerker = MedewerkerFactory.create()
        rol = RolFactory.create(
            zaak=self.zaak,
            rolomschrijving=Rolomschrijving.belanghebbende,
            betrokkene=medewerker,
            afwijkend_correspondentie_postadres=PostAdresFactory.create(
                postadres_postcode="1234AA",
                postadrestype="A",
                postbus_of_antwoordnummer="B",
                woonplaatsnaam="woonplaatsnaam"
            )
        )
        client = self._get_client('BeantwoordVraag')

        stuf_factory, zkn_factory, zds_factory = self._get_type_factories(client)

        with client.options(raw_response=True):
            result = client.service.geefZaakdetails_ZakLv01(
                stuurgegevens=stuf_factory['ZAK-StuurgegevensLv01'](
                    berichtcode='Lv01',
                    entiteittype='ZAK'),
                parameters=stuf_factory['ZAK-parametersVraagSynchroon'](
                    sortering=1,
                    indicatorVervolgvraag=False),
                scope={
                    'object': zkn_factory['ZAK-vraagScope'](
                        entiteittype='ZAK',  # v
                        scope='alles'
                    ),
                },
                gelijk=zkn_factory['GeefZaakDetails-ZAK-vraagSelectie'](
                    entiteittype='ZAK',  # v
                    identificatie=self.zaak.zaakidentificatie,
                )
            )
        root = etree.fromstring(result.content)
        expected = [
            'zkn:antwoord/zkn:object/zkn:heeftAlsBelanghebbende/zkn:gerelateerde',
            'zkn:antwoord/zkn:object/zkn:heeftAlsBelanghebbende/zkn:gerelateerde/zkn:medewerker[contains(@stuf:entiteittype,\'MDW\')]',
            'zkn:antwoord/zkn:object/zkn:heeftAlsBelanghebbende/zkn:gerelateerde/zkn:medewerker/zkn:achternaam',
            'zkn:antwoord/zkn:object/zkn:heeftAlsBelanghebbende/zkn:afwijkendCorrespondentieAdres/bg:postcode[text()="1234AA"]',
            'zkn:antwoord/zkn:object/zkn:heeftAlsBelanghebbende/zkn:afwijkendCorrespondentieAdres/bg:sub.postadresType[text()="A"]',
            'zkn:antwoord/zkn:object/zkn:heeftAlsBelanghebbende/zkn:afwijkendCorrespondentieAdres/bg:sub.postadresNummer[text()="B"]',
        ]
        for e in expected:
            self._assert_xpath_results(self._get_body_root(root), e, 1, namespaces=self.nsmap)

    def test_namespace_response(self):
        """
        Verify that the namespace of the response is as expected.
        """
        result = self._do_simple_request(raw_response=True)
        root = etree.fromstring(result.content)
        namespaces = {ns for el in root.iterdescendants() for ns in el.nsmap.values()}

        self.assertIn('http://www.egem.nl/StUF/sector/zkn/0310', namespaces)
        self.assertIn('http://www.egem.nl/StUF/StUF0301', namespaces)
        self.assertIn('http://www.stufstandaarden.nl/koppelvlak/zds0120', namespaces)

    def test_root_element(self):
        """
        Test that the root element in soapenv:Body is called geefZaakdetails_ZakLa01
        and has the namespace 'http://www.stufstandaarden.nl/koppelvlak/zds0120'
        """
        result = self._do_simple_request(raw_response=True)
        root = etree.fromstring(result.content)
        self._assert_xpath_results(root, self.antwoord_xpath, 1, namespaces=self.nsmap)

    def test_stuurgegevens_element(self):
        """
        Test that in the geefZaakdetails_ZakLa01 element there is an element
        called stuurgegevens which has the namespace 'http://www.egem.nl/StUF/sector/zkn/0310'
        """
        result = self._do_simple_request(raw_response=True)
        root = etree.fromstring(result.content)
        self._assert_xpath_results(self._get_body_root(root), 'zkn:stuurgegevens', 1, namespaces=self.nsmap)
        self._assert_xpath_results(self._get_body_root(root), 'zkn:stuurgegevens/stuf:berichtcode[text()="La01"]', 1, namespaces=self.nsmap)
        self._assert_xpath_results(self._get_body_root(root), 'zkn:stuurgegevens/stuf:entiteittype[text()="ZAK"]', 1, namespaces=self.nsmap)

    def test_antwoord_element(self):
        """
        Test that in the geefZaakdetails_ZakLa01 element there is an element
        called antwoord which has the namespace 'http://www.egem.nl/StUF/sector/zkn/0310'
        """
        result = self._do_simple_request(raw_response=True)
        root = etree.fromstring(result.content)
        self._assert_xpath_results(self._get_body_root(root), 'zkn:antwoord', 1, namespaces=self.nsmap)

    def test_object_element(self):
        """
        Test that in the antwoord element there is an element
        called object which has the namespace 'http://www.egem.nl/StUF/sector/zkn/0310'
        """
        result = self._do_simple_request(raw_response=True)
        root = etree.fromstring(result.content)
        self._assert_xpath_results(self._get_body_root(root), 'zkn:antwoord/zkn:object', 1, namespaces=self.nsmap)

    def test_entiteittype_attribute(self):
        """
        Test that the object element has an attribute entiteittype and has the namespace 'http://www.egem.nl/StUF/StUF0301'
        """
        result = self._do_simple_request(raw_response=True)
        root = etree.fromstring(result.content)
        self._assert_xpath_results(self._get_body_root(root), 'zkn:antwoord/zkn:object[@stuf:entiteittype]', 1, namespaces=self.nsmap)

    def test_ander_zaak_object_group(self):
        AnderZaakObjectFactory.create(
            zaak=self.zaak
        )
        result = self._do_simple_request(raw_response=True)
        root = etree.fromstring(result.content)
        self._assert_xpath_results(self._get_body_root(root), 'zkn:antwoord/zkn:object/zkn:anderZaakObject[@stuf:entiteittype]', 0, namespaces=self.nsmap)

    def test_ander_zaak_object_group_content(self):
        AnderZaakObjectFactory.create(
            zaak=self.zaak
        )
        result = self._do_simple_request()

        # TODO [TECH]: Taiga #208 Check for ordering as well, it's not yet implemented on this level.
        response_ander_zaak_objects = result['antwoord']['object']['anderZaakObject']
        ander_zaak_objects = self.zaak.anderzaakobject_set.all()

        response_ander_zaak_objects = sorted(response_ander_zaak_objects, key=attrgetter('omschrijving._value_1'))
        ander_zaak_objects = sorted(ander_zaak_objects, key=attrgetter('ander_zaakobject_omschrijving'))

        self.assertEquals(response_ander_zaak_objects[0].omschrijving._value_1, ander_zaak_objects[0].ander_zaakobject_omschrijving)
        self.assertEquals(response_ander_zaak_objects[0].aanduiding._value_1, ander_zaak_objects[0].ander_zaakobject_aanduiding)
        # TODO [TECH]: Check this is nil
        # self.assertIsNone(response_ander_zaak_objects[0].lokatie)
        self.assertIsNone(response_ander_zaak_objects[0].registratie._value_1)

        self.assertEquals(response_ander_zaak_objects[1].omschrijving._value_1, ander_zaak_objects[1].ander_zaakobject_omschrijving)
        self.assertEquals(response_ander_zaak_objects[1].aanduiding._value_1, ander_zaak_objects[1].ander_zaakobject_aanduiding)
        # TODO [TECH]: Check this is nil
        # self.assertIsNone(response_ander_zaak_objects[1].lokatie)
        self.assertIsNone(response_ander_zaak_objects[1].registratie._value_1)

    def test_ander_zaak_object_lokatie(self):
        """
        The GML 'lokatie' should show up as an XML string in the response.
        """
        files_path = os.path.join(os.path.dirname(__file__), 'files')
        gml_file = open(os.path.join(files_path, 'gml.xml'), 'rb')

        AnderZaakObjectFactory.create(
            zaak=self.zaak,
            ander_zaakobject_lokatie=gml_file.read()
        )
        result = self._do_simple_request(raw_response=True)
        root = etree.fromstring(result.content)
        xpath_query = 'zkn:antwoord/zkn:object/zkn:anderZaakObject/zkn:lokatie/gml:OrientableSurface'
        self._assert_xpath_results(self._get_body_root(root), xpath_query, 1, namespaces=self.nsmap)

    def test_identificatie(self):
        result = self._do_simple_request()
        self.assertEquals(
            result['antwoord']['object']['identificatie']['_value_1'],
            self.zaak.zaakidentificatie
        )


class geefZaakdetails_Fo02BerichtTests(BaseSoapTests):
    antwoord_xpath = '/soap11env:Envelope/soap11env:Body/soap11env:Fault/detail/stuf:Fo02Bericht'

    def test_validation_error_message(self):
        client = self._get_client('BeantwoordVraag', strict=False)

        self.status = StatusFactory.create()
        self.zaak = self.status.zaak

        #
        # This is what we hope to receive.
        #
        # <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:stuf="http://www.egem.nl/StUF/StUF0301">
        #   <soapenv:Body>
        #     <soapenv:Fault>
        #       <faultcode>?</faultcode>
        #       <faultstring xml:lang="?">?</faultstring>
        #       <!--Optional:-->
        #       <faultactor>?</faultactor>
        #       <!--Optional:-->
        #       <detail>
        #         <stuf:Fo02Bericht>
        #           <stuf:stuurgegevens>
        #             <stuf:berichtcode>Fo02</stuf:berichtcode>
        #           </stuf:stuurgegevens>
        #           <stuf:body>
        #             <stuf:code>?</stuf:code>
        #             <stuf:plek>?</stuf:plek>
        #             <stuf:omschrijving>?</stuf:omschrijving>
        #           </stuf:body>
        #         </stuf:Fo02Bericht>
        #         <!--You may enter ANY elements at this point-->
        #       </detail>
        #     </soapenv:Fault>
        #   </soapenv:Body>
        # </soapenv:Envelope>

        stuf_factory, zkn_factory, zds_factory = self._get_type_factories(client)
        with client.options(raw_response=True):
            response = client.service.geefZaakdetails_ZakLv01(
                stuurgegevens=stuf_factory['ZAK-StuurgegevensLv01'](
                    berichtcode='Lv01',
                    entiteittype='AAA'),
                parameters=stuf_factory['ZAK-parametersVraagSynchroon'](
                    sortering=99,  # Is too high.
                    indicatorVervolgvraag=False),
                scope={
                    'object': zkn_factory['ZAK-vraagScope'](
                        entiteittype='ZAK',
                        identificatie=Nil),
                },
                gelijk=zkn_factory['GeefZaakDetails-ZAK-vraagSelectie'](
                    entiteittype='ZAK',  # v
                    identificatie=self.zaak.zaakidentificatie,
                )
            )
        root = etree.fromstring(response.content)
        #
        # These should be part of spyne's testsuite.
        #
        self._assert_xpath_results(root, '/soap11env:Envelope/soap11env:Body/soap11env:Fault/detail', 1, namespaces=self.nsmap)

        expected_once = [
            'stuf:stuurgegevens',
            'stuf:stuurgegevens/stuf:berichtcode[text()="Fo02"]',
            'stuf:body',
            'stuf:body/stuf:code[text()="StUF055"]',
            'stuf:body/stuf:plek[text()="client"]',
        ]
        for expectation in expected_once:
            self._assert_xpath_results(self._get_body_root(root), expectation, 1, namespaces=self.nsmap)


class STPgeefZaakdetails_ZakLv01Tests(BaseTestPlatformTests):
    porttype = 'BeantwoordVraag'
    maxDiff = None
    test_files_subfolder = 'stp_geefZaakdetails'

    def setUp(self):
        super().setUp()

        self.zaak = ZaakFactory.create()

    def _test_response(self, response):
        self.assertEquals(response.status_code, 200, response.content)

        response_root = etree.fromstring(response.content)
        response_berichtcode = response_root.xpath('//zkn:stuurgegevens/stuf:berichtcode', namespaces=self.nsmap)[0].text
        self.assertEqual(response_berichtcode, BerichtcodeChoices.la01, response.content)

        response_object_element = response_root.xpath('//zkn:antwoord/zkn:object', namespaces=self.nsmap)[0]

        response_zaak_id = response_object_element.xpath('zkn:identificatie', namespaces=self.nsmap)[0].text
        self.assertEqual(response_zaak_id, self.zaak.zaakidentificatie, response.content)

    def test_geefZaakdetails_ZakLv01_01(self):
        vraag = 'geefZaakdetails_ZakLv01_01.xml'
        context = {
            'referentienummer': self.genereerID(10),
            'genereerzaakident_identificatie_2': self.zaak.zaakidentificatie,
            'gemeentecode': '',
        }
        response = self._do_request(self.porttype, vraag, context)

        self._test_response(response)

    def test_geefZaakdetails_ZakLv01_03(self):
        vraag = 'geefZaakdetails_ZakLv01_03.xml'
        context = {
            'referentienummer': self.genereerID(10),
            'gemeentecode': '',
            'genereerzaakident_identificatie_4': self.zaak.zaakidentificatie,
        }
        response = self._do_request(self.porttype, vraag, context)

        self._test_response(response)

    def test_geefZaakdetails_ZakLv01_05(self):
        vraag = 'geefZaakdetails_ZakLv01_05.xml'
        context = {
            'referentienummer': self.genereerID(10),
            'gemeentecode': '',
            'genereerzaakident_identificatie_4': self.zaak.zaakidentificatie,
        }
        response = self._do_request(self.porttype, vraag, context)

        self._test_response(response)

    def test_geefZaakdetails_ZakLv01_07(self):
        vraag = 'geefZaakdetails_ZakLv01_07.xml'
        context = {
            'referentienummer': self.genereerID(10),
            'gemeentecode': '',
            'genereerzaakident_identificatie_6': self.zaak.zaakidentificatie,
        }
        response = self._do_request(self.porttype, vraag, context)

        self._test_response(response)

        root = etree.fromstring(response.content)
        response_root = etree.fromstring(response.content)
        response_object_element = response_root.xpath('//zkn:antwoord/zkn:object', namespaces=self.nsmap)[0]

        # bronorganisatie was not specified, so shouldn't be returned.
        self.assertEquals(len(response_object_element.xpath('zkn:bronorganisatie', namespaces=self.nsmap)), 0)

        # identificatie and omschrijver were specified and should be returned.
        self.assertEquals(len(response_object_element.xpath('zkn:identificatie', namespaces=self.nsmap)), 1)
        self.assertEquals(len(response_object_element.xpath('zkn:omschrijving', namespaces=self.nsmap)), 1)

    def test_geefZaakdetails_ZakLv01_09(self):
        vraag = 'geefZaakdetails_ZakLv01_09.xml'
        context = {
            'referentienummer': self.genereerID(10),
            'gemeentecode': '',
            'creerzaak_identificatie_7': self.zaak.zaakidentificatie,
        }
        response = self._do_request(self.porttype, vraag, context)

        self._test_response(response)

    def test_geefZaakdetails_ZakLv01_11(self):
        vraag = 'geefZaakdetails_ZakLv01_11.xml'
        context = {
            'referentienummer': self.genereerID(10),
            'gemeentecode': '',
            'creerzaak_identificatie_9': self.zaak.zaakidentificatie,
        }
        response = self._do_request(self.porttype, vraag, context)

        self._test_response(response)

    def test_geefZaakdetails_ZakLv01_13(self):
        vraag = 'geefZaakdetails_ZakLv01_13.xml'
        context = {
            'referentienummer': self.genereerID(10),
            'gemeentecode': '',
            'creerzaak_identificatie_11': self.zaak.zaakidentificatie,
        }
        response = self._do_request(self.porttype, vraag, context)

        self._test_response(response)

    def test_geefZaakdetails_ZakLv01_15(self):
        vraag = 'geefZaakdetails_ZakLv01_15.xml'
        context = {
            'referentienummer': self.genereerID(10),
            'gemeentecode': '',
            'creerzaak_identificatie_13': self.zaak.zaakidentificatie,
        }
        response = self._do_request(self.porttype, vraag, context)

        self._test_response(response)


class GeefZaakdetails_AuditlogTests(BaseTestPlatformTests):
    porttype = 'BeantwoordVraag'
    maxDiff = None
    test_files_subfolder = 'stp_geefZaakdetails'

    def setUp(self):
        super().setUp()

        self.zaak = ZaakFactory.create()

    def _test_response(self, response):
        self.assertEquals(response.status_code, 200, response.content)

        response_root = etree.fromstring(response.content)
        response_berichtcode = response_root.xpath('//zkn:stuurgegevens/stuf:berichtcode', namespaces=self.nsmap)[0].text
        self.assertEqual(response_berichtcode, BerichtcodeChoices.la01, response.content)

        response_object_element = response_root.xpath('//zkn:antwoord/zkn:object', namespaces=self.nsmap)[0]

        response_zaak_id = response_object_element.xpath('zkn:identificatie', namespaces=self.nsmap)[0].text
        self.assertEqual(response_zaak_id, self.zaak.zaakidentificatie, response.content)

    def test_geefZaakdetails_ZakLv01_01(self):
        vraag = 'geefZaakdetails_ZakLv01_01.xml'
        context = {
            'referentienummer': self.genereerID(10),
            'genereerzaakident_identificatie_2': self.zaak.zaakidentificatie,
            'gemeentecode': '',
        }

        count = LogEntry.objects.count()

        response = self._do_request(self.porttype, vraag, context)

        self._test_response(response)
        self.assertEqual(LogEntry.objects.count(), count + 1)

        log_entry = LogEntry.objects.latest()
        self.assertEqual(log_entry.action, LogEntry.Action.READ)
        self.assertEqual(log_entry.get_action_display(), _("read"))
        self.assertEqual(log_entry.content_type.model, 'zaak')
        self.assertEqual(log_entry.additional_data['functie'], 'geefZaakdetails_ZakLv01')
        self.assertEqual(log_entry.additional_data['zender']['organisatie'], 'KING')
