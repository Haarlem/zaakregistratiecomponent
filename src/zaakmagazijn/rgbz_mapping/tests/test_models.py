from django.test import TestCase

from zaakmagazijn.rgbz.choices import ArchiefNominatie, ArchiefStatus
from zaakmagazijn.rgbz.models import (
    VestigingVanZaakBehandelendeOrganisatie, Zaak
)
from zaakmagazijn.rgbz.tests.factory_models import (
    MedewerkerFactory, NatuurlijkPersoonFactory, NietNatuurlijkPersoonFactory,
    OrganisatorischeEenheidFactory, RolFactory, StatusFactory,
    VestigingFactory, VestigingVanZaakBehandelendeOrganisatieFactory,
    ZaakFactory, ZaakTypeFactory
)

from ..manager import ProxyQuerySet
from ..models import (
    BuurtObjectProxy, MedewerkerProxy, OrganisatorischeEenheidProxy,
    StatusTypeProxy, ZaakProxy, ZaakTypeProxy
)
from ..utils import to_proxy_obj


class ZaakProxyTests(TestCase):
    def setUp(self):
        self.zaak = ZaakFactory.create(zaakidentificatie='123')
        self.zaak2 = ZaakFactory.create(zaakidentificatie='555')
        self.status = StatusFactory.create(zaak=self.zaak)
        self.status2 = StatusFactory.create(zaak=self.zaak2)

    def test_zaak_obj(self):
        """
        Instantiate a Zaak object from kwargs, and save it to the database.
        """

        zaaktype = ZaakTypeProxy.from_django_obj(ZaakTypeFactory.create())
        zaak = ZaakProxy(
            zaakidentificatie=123456789,
            registratiedatum='20170101',
            startdatum='20170101',
            laatste_betaaldatum='20170101',
            archiefnominatie='J',
            zaaktype=zaaktype,
        )
        zaak.save()

        self.assertTrue(Zaak.objects.filter(
            zaakidentificatie=123456789,
            bronorganisatie=1234,
            omschrijving=None,
            toelichting=None,
            registratiedatum='20170101',
            verantwoordelijke_organisatie=1234,
            einddatum=None,
            startdatum='20170101',
            einddatum_gepland=None,
            uiterlijke_einddatum_afdoening=None,
            resultaatomschrijving=None,
            resultaattoelichting=None,
            publicatiedatum=None,
            archiefnominatie=ArchiefNominatie.vernietigen,
            archiefstatus=ArchiefStatus.gearchiveerd,
            archiefactiedatum=None,
            betalingsindicatie=None,
            laatste_betaaldatum='20170101',
        ).exists())

    def test___eq__(self):
        """
        Make sure '___eq__' works as intended, and compares on 'pk'
        """
        self.assertNotEquals(self.zaak, self.zaak2)
        self.assertNotEquals(self.status, self.status2)

        zaak = ZaakProxy.objects.get(zaakidentificatie='123')
        self.assertEquals(zaak, ZaakProxy.from_django_obj(self.zaak))
        zaak2 = ZaakProxy.objects.get(zaakidentificatie='555')
        self.assertEquals(zaak2, ZaakProxy.from_django_obj(self.zaak2))

    def test_related_manager(self):
        zaak = ZaakProxy.objects.get(zaakidentificatie='123')
        status = zaak.status_set.get()

        self.assertEquals(status.datum_status_gezet, self.status.datum_status_gezet)
        self.assertEquals(status.toelichting, self.status.statustoelichting)
        self.assertEquals(status.indicatie_laatst_gezette_status, self.status.indicatie_laatst_gezette_status)
        self.assertEquals(status.status_type, StatusTypeProxy.from_django_obj(self.status.status_type))

    def test_manager_all(self):
        """
        The 'all' method on the manager should return a iterable queryset.
        """
        queryset = ZaakProxy.objects.all()
        self.assertEquals(type(queryset), ProxyQuerySet)
        self.assertIn(ZaakProxy.from_django_obj(self.zaak), list(queryset))

    def test_manager_filter(self):
        """
        The 'filter' method on the manager should return a filtered queryset.
        """
        queryset = ZaakProxy.objects.filter(zaakidentificatie=555)
        self.assertEquals(type(queryset), ProxyQuerySet)
        self.assertNotIn(ZaakProxy.from_django_obj(self.zaak), list(queryset))
        self.assertIn(ZaakProxy.from_django_obj(self.zaak2), list(queryset))

    def test_manager_create(self):
        zaaktype = ZaakTypeProxy.from_django_obj(ZaakTypeFactory.create())
        ZaakProxy.objects.create(
            zaakidentificatie=123456789,
            registratiedatum='20170101',
            startdatum='20170101',
            laatste_betaaldatum='20170101',
            archiefnominatie='J',
            zaaktype=zaaktype,
        )

        self.assertTrue(Zaak.objects.filter(
            zaakidentificatie=123456789,
            bronorganisatie=1234,
            omschrijving=None,
            toelichting=None,
            registratiedatum='20170101',
            verantwoordelijke_organisatie=1234,
            einddatum=None,
            startdatum='20170101',
            einddatum_gepland=None,
            uiterlijke_einddatum_afdoening=None,
            resultaatomschrijving=None,
            resultaattoelichting=None,
            publicatiedatum=None,
            archiefnominatie=ArchiefNominatie.vernietigen,
            archiefstatus=ArchiefStatus.gearchiveerd,
            archiefactiedatum=None,
            betalingsindicatie=None,
            laatste_betaaldatum='20170101',
        ).exists())

    def test_manager_get(self):
        zaak = ZaakProxy.objects.get(zaakidentificatie=self.zaak.zaakidentificatie)

    def test_queryset_all(self):
        """
        The 'all' method on the queryset should return the 'same' queryset.
        """
        queryset = ZaakProxy.objects.all()
        self.assertIn(ZaakProxy.from_django_obj(self.zaak), list(queryset))
        self.assertIn(ZaakProxy.from_django_obj(self.zaak2), list(queryset))

        queryset = queryset.all()
        self.assertIn(ZaakProxy.from_django_obj(self.zaak), list(queryset))
        self.assertIn(ZaakProxy.from_django_obj(self.zaak2), list(queryset))

    def test_queryset_filter(self):
        """
        The 'filter' method on the queryset should return filtered data.
        """
        queryset = ZaakProxy.objects.all()
        self.assertIn(ZaakProxy.from_django_obj(self.zaak), list(queryset))
        self.assertIn(ZaakProxy.from_django_obj(self.zaak2), list(queryset))

        queryset = queryset.filter(zaakidentificatie=555)
        self.assertEquals(type(queryset), ProxyQuerySet)
        self.assertNotIn(ZaakProxy.from_django_obj(self.zaak), list(queryset))
        self.assertIn(ZaakProxy.from_django_obj(self.zaak2), list(queryset))

    def test_queryset_order_by(self):
        pass

    def test_queryset_limit(self):
        pass

    def test_queryset_count(self):
        """
        The 'count' method on the queryset should behave the same as a normal queryset
        """
        queryset = ZaakProxy.objects.all()
        self.assertEquals(queryset.count(), 2)

    def test_get_field(self):
        queryset = ZaakProxy.objects.all()
        obj = list(queryset)[0]
        field = obj.get_field('zaakidentificatie')


class RolProxyTests(TestCase):
    def setUp(self):
        self.zaak = ZaakFactory.create()

    def test_betrokkene_medewerker(self):
        medewerker = MedewerkerFactory.create()
        rol = RolFactory.create(zaak=self.zaak, betrokkene=medewerker)

        proxy_zaak = ZaakProxy.objects.get()
        proxy_rol = proxy_zaak.rol_set.get()
        proxy_betrokkene = proxy_rol.betrokkene
        proxy_medewerker = proxy_betrokkene.is_type()

        self.assertEquals(proxy_medewerker, to_proxy_obj(medewerker))

    def test_betrokkene_organisatorische_eenheid(self):
        oeh = OrganisatorischeEenheidFactory.create()
        rol = RolFactory.create(zaak=self.zaak, betrokkene=oeh)

        proxy_zaak = ZaakProxy.objects.get()
        proxy_rol = proxy_zaak.rol_set.get()
        proxy_betrokkene = proxy_rol.betrokkene
        proxy_oeh = proxy_betrokkene.is_type()

        self.assertEquals(proxy_oeh, to_proxy_obj(oeh))

    def test_betrokkene_natuurlijk_persoon(self):
        oeh = OrganisatorischeEenheidFactory.create()
        rol = RolFactory.create(zaak=self.zaak, betrokkene=oeh)

        proxy_zaak = ZaakProxy.objects.get()
        proxy_rol = proxy_zaak.rol_set.get()
        proxy_betrokkene = proxy_rol.betrokkene
        proxy_oeh = proxy_betrokkene.is_type()

        self.assertEquals(proxy_oeh, to_proxy_obj(oeh))


class OrganisatorischeEenheidEntiteitFactory(TestCase):
    def test_queryset_filter_nested(self):
        oeh = OrganisatorischeEenheidFactory.create(
            gevestigd_in__is_specialisatie_van__identificatie=1234)

        results = OrganisatorischeEenheidProxy.objects.filter(gevestigd_in__is_specialisatie_van__vestigingsnummer=1234).all()

        self.assertIn(to_proxy_obj(oeh), results)


class BuurtObjectProxyTests(TestCase):
    def test_automapper_fields(self):
        fields = BuurtObjectProxy.get_fields(is_field=True)

        expected = {
            'buurtcode',
            'buurtnaam',
            'datum_begin_geldigheid_buurt',
            'datum_einde_geldigheid_buurt',
            'wijkcode',
            'gemeentecode',
            'naam',
            'geometrie',
            'identificatie',
            '_objecttype_model',
            'objecttype',
            'id',
        }
        self.assertEqual({field.rgbz1_name for field in fields}, expected)
