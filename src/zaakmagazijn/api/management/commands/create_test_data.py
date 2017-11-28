from datetime import datetime, timedelta

from django.core.management.base import BaseCommand

from zaakmagazijn.rgbz.choices import GeslachtsAanduiding
from zaakmagazijn.rgbz.models import (
    BesluitType, InformatieObjectType, Medewerker, NatuurlijkPersoon,
    NietNatuurlijkPersoon, OrganisatorischeEenheid,
    OverigeAdresseerbaarObjectAanduidingObject, StatusType, Vestiging,
    ZaakType
)
from zaakmagazijn.rgbz.tests.factory_models import (
    InformatieObjectTypeFactory, MedewerkerFactory, NatuurlijkPersoonFactory,
    NietNatuurlijkPersoonFactory, OrganisatorischeEenheidFactory,
    OverigeAdresseerbaarObjectAanduidingObjectFactory, VestigingFactory,
    ZaakFactory, ZaakTypeFactory
)
from zaakmagazijn.utils import stuf_datetime


class Command(BaseCommand):
    help = 'Create the required test data for the Zaak- Document services 1.2 test suite on the StUF test platform.'

    context = {
        'gemeentecode': '1234',
    }

    def genereerdatum(self, days_offset=0):
        """
        Return the datetime like genereerdatumtijd,
        but in the short format "yyyyMMdd"

        genereerdatum(2) is equal to STP genereerdatumtijd(2, "yyyyMMdd") for day after tomorrow
        genereerdatum(-1) is equal to STP genereerdatumtijd(-1, "yyyyMMdd") for yesterday
        """
        the_time = datetime.now()

        if days_offset != 0:
            the_time += timedelta(days=days_offset)

        return the_time.strftime(stuf_datetime.DATE_FORMAT)

    def handle(self, *args, **options):

        # Needed for all tests.
        ZaakType.objects.filter(
            zaaktypeomschrijving='Aanvraag burgerservicenummer behandelen',
            zaaktypeidentificatie='12345678',
        ).delete()

        # Medewerker.objects.get_or_create(
        #     medewerkeridentificatie='123456789',
        #     achternaam='achternaam',
        #     voorvoegsel_achternaam='voorvoeg',
        #     voorletters='voorletters',
        #     defaults={
        #         'organisatorische_eenheid': None,
        #     }
        # )

        ZaakTypeFactory.create(
            zaaktypeomschrijving='Aanvraag burgerservicenummer behandelen',
            zaaktypeidentificatie='12345678',
            datum_begin_geldigheid_zaaktype='20171001')

        # Required for 'creeerZaak_zakLk01 volgnummer 3'

        # First do cleanup.
        Medewerker.objects.filter(
            medewerkeridentificatie='7007',
            organisatorische_eenheid__isnull=True
        ).delete()
        ZaakType.objects.filter(
            zaaktypeomschrijving='Aanvraag burgerservicenummer behandelen',
            zaaktypeidentificatie='12345679',
        ).delete()

        try:
            organisatorische_eenheid = OrganisatorischeEenheid.objects.filter(
                identificatie='organisatorischeEenheid',
                naam='Naam',
                organisatieeenheididentificatie='organisatorischeEenheid',
                organisatieidentificatie='0',
                gevestigd_in__is_specialisatie_van__identificatie='012345678910',
                gevestigd_in__is_specialisatie_van__handelsnaam=['handelsnaam', ],
            ).get()
        except OrganisatorischeEenheid.DoesNotExist:
            pass
        else:
            if organisatorische_eenheid.gevestigd_in.is_specialisatie_van:
                organisatorische_eenheid.gevestigd_in.is_specialisatie_van.delete()
            if organisatorische_eenheid.gevestigd_in:
                organisatorische_eenheid.gevestigd_in.delete()

        OverigeAdresseerbaarObjectAanduidingObject.objects.filter(
            identificatie='0123456789101112',
            woonplaatsnaam='woonplaatsNaam',
            naam_openbare_ruimte='openbareRuimteNaam',
            huisnummer=99999,
            huisletter='A',
            huisnummertoevoeging='',
        ).delete()

        MedewerkerFactory.create(
            medewerkeridentificatie='7007',
            organisatorische_eenheid=None,
        )
        zaak_type = ZaakTypeFactory.create(
            zaaktypeomschrijving='Aanvraag burgerservicenummer behandelen',
            zaaktypeidentificatie='12345679')

        status_type1 = StatusType.objects.get_or_create(
            statustypeomschrijving='Intake afgerond',
            statustypevolgnummer='1',
            zaaktype=zaak_type,
        )

        status_type2 = StatusType.objects.get_or_create(
            statustypeomschrijving='Afgerekend',
            statustypevolgnummer='3',
            zaaktype=zaak_type,
        )

        status_type3 = StatusType.objects.get_or_create(
            statustypeomschrijving='Product opgesteld',
            statustypevolgnummer='5',
            zaaktype=zaak_type,
        )

        status_type4 = StatusType.objects.get_or_create(
            statustypeomschrijving='Zaak afgerond',
            statustypevolgnummer='7',
            zaaktype=zaak_type,
        )

        organisatorische_eenheid = OrganisatorischeEenheidFactory.create(
            identificatie='organisatorischeEenheid',
            naam='Naam',
            organisatieeenheididentificatie='organisatorischeEenheid',
            organisatieidentificatie='0',
            gevestigd_in__is_specialisatie_van__identificatie='012345678910',
            gevestigd_in__is_specialisatie_van__handelsnaam=['handelsnaam', ],
        )

        # OverigeAdresseerbaarObjectAanduidingObjectFactory.create(
        #     identificatie='0123456789101112',
        #     woonplaatsnaam='woonplaatsNaam',
        #     naam_openbare_ruimte='openbareRuimteNaam',
        #     huisnummer=99999,
        #     huisletter='A',
        #     huisnummertoevoeging='',
        # )

        # Required for creeerZaak_zakLk01 volgnummer 5

        # Deelzaak en Andere zaak
        ZaakFactory.create(
            zaakidentificatie='0123456789',
            omschrijving='omschrijving',
        )

        NatuurlijkPersoon.objects.filter(
            burgerservicenummer=self.context['gemeentecode'] + '56789'
        ).delete()
        NatuurlijkPersoonFactory.create(burgerservicenummer=self.context['gemeentecode'] + '56789')

        # Required for creeerZaak_zakLk01 volgnummer 7
        NietNatuurlijkPersoon.objects.filter(
            rsin=self.context['gemeentecode'] + '56789'
        ).delete()
        NietNatuurlijkPersoonFactory.create(rsin=self.context['gemeentecode'] + '56789')

        # Required for creeerZaak_zakLk01 volgnummer 9, 11 and 13
        Vestiging.objects.filter(identificatie='010203040506').delete()
        VestigingFactory.create(identificatie='010203040506')

        # Required for creeerZaak_zakLk01 volgnummer 13
        medewerkers = [{
            'medewerkeridentificatie': self.context['gemeentecode'] + '56791',
            'achternaam': 'achternaam22',
            'voorletters': 'voorletters22',
            'voorvoegsel_achternaam': 'voorvoeg22',
            'organisatorische_eenheid': None,
        }, {
            'medewerkeridentificatie': self.context['gemeentecode'] + '56790',
            'achternaam': 'achternaam20',
            'voorletters': 'voorletters20',
            'voorvoegsel_achternaam': 'voorvoeg20',
            'organisatorische_eenheid': None,
        }, {
            'medewerkeridentificatie': self.context['gemeentecode'] + '56789',
            'achternaam': 'achternaam22',
            'voorletters': 'voorletters22',
            'voorvoegsel_achternaam': 'voorvoeg22',
            'organisatorische_eenheid': None,
        }, {
            'medewerkeridentificatie': self.context['gemeentecode'] + '56788',
            'achternaam': 'achternaam2',
            'voorletters': 'voorletters2',
            'voorvoegsel_achternaam': 'voorvoeg2',
            'organisatorische_eenheid': None,
        }, {
            'medewerkeridentificatie': self.context['gemeentecode'] + '56787',
            'achternaam': 'achternaam22',
            'voorletters': 'voorletters22',
            'voorvoegsel_achternaam': 'voorvoeg22',
            'organisatorische_eenheid': None,
        }, {
            'medewerkeridentificatie': self.context['gemeentecode'] + '56786',
            'achternaam': 'achternaam6',
            'voorletters': 'voorletters6',
            'voorvoegsel_achternaam': 'voorvoeg6',
            'organisatorische_eenheid': None,
        }, {
            'medewerkeridentificatie': self.context['gemeentecode'] + '56785',
            'achternaam': 'unknown',
            'voorletters': 'unknown',
            'voorvoegsel_achternaam': 'unknown',
            'organisatorische_eenheid': None,
        }, {
            'medewerkeridentificatie': self.context['gemeentecode'] + '56784',
            'achternaam': 'achternaam22',
            'voorletters': 'voorletters22',
            'voorvoegsel_achternaam': 'voorvoeg22',
            'organisatorische_eenheid': None,
        }, {
            'medewerkeridentificatie': self.context['gemeentecode'] + '56783',
            'achternaam': 'achternaam2',
            'voorletters': 'voorletters2',
            'voorvoegsel_achternaam': 'voorvoeg2',
            'organisatorische_eenheid': None,
        }, {
            'medewerkeridentificatie': self.context['gemeentecode'] + '56782',
            'achternaam': 'achternaam22',
            'voorletters': 'voorletters22',
            'voorvoegsel_achternaam': 'voorvoeg22',
            'organisatorische_eenheid': None,
        }, {
            'medewerkeridentificatie': self.context['gemeentecode'] + '56781',
            'achternaam': 'achternaam2',
            'voorletters': 'voorletters2',
            'voorvoegsel_achternaam': 'voorvoeg2',
            'organisatorische_eenheid': None,
        }, ]
        for medewerker in medewerkers:
            Medewerker.objects.get_or_create(defaults={
                'geslachtsaanduiding': GeslachtsAanduiding.onbekend,
            }, **medewerker)

        InformatieObjectType.objects.filter(informatieobjecttypeomschrijving='omschrijving').delete()
        InformatieObjectType.objects.filter(informatieobjecttypeomschrijving='Aanvraag burgerservicenummer behandelen').delete()
        InformatieObjectTypeFactory.create(informatieobjecttypeomschrijving='omschrijving')
        InformatieObjectTypeFactory.create(informatieobjecttypeomschrijving='Aanvraag burgerservicenummer behandelen')

        oeh2_defaults = {
            'organisatieeenheididentificatie': "0123456785",
            'organisatieidentificatie': "0123456785"[:4],
            'naam': 'naam2',
            'gevestigd_in': organisatorische_eenheid.gevestigd_in,
        }

        organisatorische_eenheid, _ = OrganisatorischeEenheid.objects.get_or_create(
            identificatie="0123456785",
            defaults=oeh2_defaults,
        )

        # For actualiseerZaakstatus volgnummer 1
        OrganisatorischeEenheid.objects.get_or_create(
            identificatie='0123456789',
            organisatieeenheididentificatie="0123456789",
            organisatieidentificatie="0123456789"[:4],
            defaults={
                'naam': '0123456789',
                'gevestigd_in': organisatorische_eenheid.gevestigd_in,
            }
        )

        # For actualiseerZaakstatus volgnummer 5
        # TODO [KING]: Deze organisatorische eenheid is volgens de test ergens anders
        # gevestigd.
        OrganisatorischeEenheid.objects.get_or_create(
            identificatie='01234567890',
            organisatieeenheididentificatie="01234567890",
            organisatieidentificatie="01234567890"[:4],
            defaults={
                'naam': '01234567890',
                'gevestigd_in': organisatorische_eenheid.gevestigd_in,
            }
        )

        NatuurlijkPersoon.objects.filter(
            burgerservicenummer='012345678'
        ).delete()
        natuurlijk_persoon = NatuurlijkPersoonFactory.create(
            burgerservicenummer='012345678',
            naam_geslachtsnaam='geslachtsnaam5',
            naam_voorvoegsel_geslachtsnaam_voorvoegsel='voorvoeg5',
            naam_aanschrijving_voorletters_aanschrijving='voorletters5',
            naam_voornamen='voornamen5',
            geslachtsaanduiding='M',
            geboortedatum_ingeschreven_persoon=self.genereerdatum(),
        )

        NietNatuurlijkPersoon.objects.filter(
            rsin='012345678',
            statutaire_naam='statutaireNaam'
        ).delete()
        niet_natuurlijk_persoon = NietNatuurlijkPersoonFactory.create(
            rsin='012345678',
            statutaire_naam='statutaireNaam'
        )

        # This is the default BesluitType.
        BesluitType.objects.get_or_create(
            besluittypeomschrijving=None,
            defaults={
                'domein': 'dom',
                'rsin': 12345,
                'reactietermijn': 5,
                'publicatie_indicatie': 'J',
                'datum_begin_geldigheid_besluittype': self.genereerdatum(),
            }
        )

        BesluitType.objects.get_or_create(
            besluittypeomschrijving='omschrijving',
            defaults={
                'domein': 'dom',
                'rsin': 12345,
                'reactietermijn': 5,
                'publicatie_indicatie': 'J',
                'datum_begin_geldigheid_besluittype': self.genereerdatum(),
            }
        )
        BesluitType.objects.get_or_create(
            besluittypeomschrijving='bst.omschrijving',
            defaults={
                'domein': 'dom',
                'rsin': 12345,
                'reactietermijn': 5,
                'publicatie_indicatie': 'J',
                'datum_begin_geldigheid_besluittype': self.genereerdatum(),
            }
        )


        BesluitType.objects.get_or_create(
            besluittypeomschrijving='bst.omschrijving3',
            defaults={
                'domein': 'dom',
                'rsin': 12345,
                'reactietermijn': 5,
                'publicatie_indicatie': 'J',
                'datum_begin_geldigheid_besluittype': self.genereerdatum(),
            }
        )
