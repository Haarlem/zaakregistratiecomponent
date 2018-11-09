from django.conf import settings
from django.db import transaction

from spyne import ServiceBase, rpc

from ...rgbz.choices import JaNee, Rolomschrijving, RolomschrijvingGeneriek
from ...rgbz.models import (
    Betrokkene, Medewerker, OrganisatorischeEenheid, Rol, Status, StatusType,
    Zaak
)
from ..stuf import OneToManyRelation, StUFEntiteit, StUFKerngegevens
from ..stuf.choices import ClientFoutChoices, ServerFoutChoices
from ..stuf.faults import StUFFault
from ..stuf.models import Bv03Bericht
from ..stuf.protocols import Nil
from ..stuf.utils import get_bv03_stuurgegevens
from ..zds import Lk01Builder
from ..zds.entiteiten.betrokkene import OEHVZOEntiteit


class StatusTypeKerngegevens(StUFKerngegevens):
    mnemonic = 'STT'
    model = StatusType
    field_mapping = (
        ('zkt.code', 'zaaktype__zaaktypeidentificatie'),
        # ('zkt.identificatie', 'zaaktype__zaaktypeidentificatie'),
        # ('zkt.omschrijving', 'zaaktype__zaaktypeomschrijving'),
        ('volgnummer', 'statustypevolgnummer'),
        # ('code', ''),
        ('omschrijving', 'statustypeomschrijving'),
        # ('ingangsdatumObject', 'datum_begin_geldigheid_statustype')
    )

# This is a more narrow definition than the one in zds/entiteiten/betrokkene


class MedewerkerEntiteit(StUFEntiteit):
    mnemonic = 'MDW'
    model = Medewerker

    field_mapping = (
        ('identificatie', 'identificatie'),
        ('achternaam', 'achternaam'),
        ('voorletters', 'voorletters'),
        ('voorvoegselAchternaam', 'voorvoegsel_achternaam'),
    )

    matching_fields = (
        'identificatie',
        'achternaam',
        'voorletters',
        'voorvoegselAchternaam',
    )


# This is a more narrow definition than the one in zds/entiteiten/betrokkene
class OrganisatorischeEenheidEntiteit(StUFEntiteit):
    mnemonic = 'OEH'
    model = OrganisatorischeEenheid
    field_mapping = (
        ('identificatie', 'identificatie'),
        ('naam', 'naam'),
    )
    related_fields = (
        OneToManyRelation('isGehuisvestIn', 'self', OEHVZOEntiteit, min_occurs=0, max_occurs=1),
    )

    fields = (
        'identificatie',
        'naam',
        'isGehuisvestIn',
    )
    matching_fields = (
        'identificatie',
        'naam',
    )


class ZAKBTRBTREntiteit(StUFEntiteit):
    model = Rol
    mnemonic = 'ZAKBTRBTR'
    field_mapping = (
        # TODO [KING]: Taiga #221 actualiseerZaakstatus_ZakLk01.object.heeft.isGezetDoor.[rolOmschrijving, rolomschrijvingGeneriek, rolToelichting] zijn verplicht in RGBZ 2.0 maar staan niet in ZDS 1.2.
        # ('rolOmschrijving', 'rolomschrijving'),
        # ('rolomschrijvingGeneriek', 'rolomschrijving_generiek'),
        # ('rolToelichting', 'roltoelichting'),
    )
    gerelateerde = ('rol', (
        ('medewerker', MedewerkerEntiteit),
        ('organisatorischeEenheid', OrganisatorischeEenheidEntiteit),
        # ('vestiging', VestigingEntiteit))  # this was VestiginsObjectEntiteit
    ), )
    fields = (
        'gerelateerde',
        # 'rolOmschrijving',
        # 'rolomschrijvingGeneriek',
        # 'rolToelichting',
    )
    matching_fields = (
        'gerelateerde'
    )


class ZAKSTTBTREntiteit(ZAKBTRBTREntiteit):
    model = Rol
    mnemonic = 'ZAKSTTBTR'


class StatusEntiteit(StUFEntiteit):
    mnemonic = 'ZAKSTT'
    model = Status
    field_mapping = (
        ('toelichting', 'statustoelichting'),
        ('datumStatusGezet', 'datum_status_gezet'),
    )
    filter_fields = ('indicatieLaatsteStatus', )
    gerelateerde = ('status_type', StatusTypeKerngegevens)
    related_fields = (
        OneToManyRelation('isGezetDoor', 'self', ZAKSTTBTREntiteit, min_occurs=1, max_occurs=1),
    )
    fields = (
        'gerelateerde',
        'toelichting',
        'datumStatusGezet',
        'isGezetDoor',
    )


class ZaakEntiteit(StUFEntiteit):
    mnemonic = 'ZAK'
    model = Zaak
    field_mapping = (
        ('identificatie', 'zaakidentificatie'),
        ('omschrijving', 'omschrijving'),  # Optioneel
    )
    filter_fields = ('identificatie', )
    # stuurgegevens = ZAK_StuurgegevensLk01
    # input_parameters = ParametersLk01
    related_fields = (
        OneToManyRelation('heeft', 'status_set', StatusEntiteit),
    )
    fields = (
        'identificatie',
        'omschrijving',
        'heeft',
    )


input_builder = Lk01Builder(ZaakEntiteit, 'ActualiseerZaakstatus', update=True)


class ActualiseerZaakstatus(ServiceBase):
    """
    De "actualiseer Zaakstatus"-service biedt ZSC's de mogelijkheid om een
    nieuwe status aan een lopende zaak toe te voegen middels een
    kennisgevingsbericht. Indien de nieuwe status gelijk is aan de eindstatus
    (zoals vastgelegd in de ZTC van de gemeente) dient het ZS de betreffende
    zaak af te sluiten.

    Zie: ZDS 1.2, paragraaf 4.1.3
    """
    input_model = input_builder.create_model()
    output_model = Bv03Bericht

    @rpc(input_model, _body_style="bare", _out_message_name="{http://www.egem.nl/StUF/StUF0301}Bv03Bericht", _returns=output_model)
    def actualiseerZaakstatus_ZakLk01(ctx, data):
        """
        Een lopende zaak heeft een nieuwe status bereikt.
        """

        # Eisen aan ZS:
        #
        # * Het ZS beschikt over de zaakkenmerken die in de ZTC zijn
        #   vastgelegd en kan bepalen of de statustype-omschrijving die door
        #   de ZSC wordt ingevuld, in de ZTC staat. In geval het statustype
        #   niet voorkomt, stuurt het ZS een StUF-foutbericht.
        # * Het ZS kan aan de hand van informatie uit de ZTC bepalen of een
        #   status een eindstatus van een zaak is en indien een zaak een
        #   eindstatus bereikt, het proces in gang te zetten om de zaak af te
        #   sluiten. Het gaat hierbij onder meer om archivering van
        #   zaakgegevens. Het proces en de benodigde functionaliteit hiervoor
        #   maken geen onderdeel uit van deze specificatie.
        # * Het ZS bepaalt of de aangeleverde status de meest recente status
        #   van de zaak is en bepaalt de waarde "indicatie laatst gezette
        #   status". De Indicatie laatst gezette status is afleidbaar uit de
        #   historie van het attribuut "Datum status gezet" van alle statussen
        #   bij de desbetreffende zaak

        # Interactie tussen ZSC en ZS:
        #
        # De ZSC stuurt een kennisgeving naar het ZS waarin aangegeven wordt
        # dat voor de zaak met de aangegeven zaakidentificatie een nieuwe
        # status geldt.

        oud = data.object[0]
        huidig = data.object[1]

        # Zaak object should exist.
        try:
            zaak_obj = Zaak.objects.get(zaakidentificatie=oud.identificatie)
        except Zaak.DoesNotExist:
            raise StUFFault(ServerFoutChoices.stuf064, stuf_details='Zaak met identificatie {} bestaat niet'.format(oud.identificatie))

        # Basic validation
        if oud.verwerkingssoort != 'W':
            raise StUFFault(ClientFoutChoices.stuf055, stuf_details='Verwacht (oud) object@verwerkingssoort="W".')

        if oud.heeft[0].verwerkingssoort != 'T':
            raise StUFFault(ClientFoutChoices.stuf055, stuf_details='Verwacht (oud) heeft@verwerkingssoort="T".')

        if huidig.verwerkingssoort != 'W':
            raise StUFFault(ClientFoutChoices.stuf055, stuf_details='Verwacht (huidig) object@verwerkingssoort="W".')

        if huidig.heeft[0].verwerkingssoort != 'T':
            raise StUFFault(ClientFoutChoices.stuf055, stuf_details='Verwacht (huidig) heeft@verwerkingssoort="T".')

        # Eis #1
        status_type_filter_kwargs = {
            'statustypeomschrijving': huidig.heeft[0].gerelateerde.omschrijving,
            'statustypevolgnummer': huidig.heeft[0].gerelateerde.volgnummer,
        }
        zaak_type_identificatie = huidig.heeft[0].gerelateerde.__getattribute__('zkt.code')
        if zaak_type_identificatie:
            status_type_filter_kwargs['zaaktype__zaaktypeidentificatie'] = zaak_type_identificatie

        try:
            status_type_obj = StatusType.objects.get(**status_type_filter_kwargs)
        except StatusType.DoesNotExist:
            raise StUFFault(ServerFoutChoices.stuf064, stuf_details='Statustype bestaat niet')
        except StatusType.MultipleObjectsReturned:
            raise StUFFault(ServerFoutChoices.stuf064, stuf_details='Statustype is niet uniek identificeerbaar')

        # TODO [KING]: Taiga #223 Het ZS kan aan de hand van informatie uit de ZTC bepalen of een status een eindstatus van een zaak is.

        # Actual creation of the Status object.
        zaksttbtr = huidig.heeft[0].isGezetDoor
        if zaksttbtr.gerelateerde.organisatorischeEenheid:
            btr_identificatie = zaksttbtr.gerelateerde.organisatorischeEenheid.identificatie
        elif zaksttbtr.gerelateerde.medewerker:
            btr_identificatie = zaksttbtr.gerelateerde.medewerker.identificatie
        else:
            raise StUFFault(ClientFoutChoices.stuf055, stuf_details='Verwacht (huidig) gerelateerde.organisatorischeEenheid of gerelateerde.medewerker.')

        betrokkene_obj = Betrokkene.objects.get(identificatie=btr_identificatie)

        # TODO [KING]: Taiga #221
        zakbtrbtr_rolomschrijving = ''  # zaksttbtr.rolOmschrijving
        zakbtrbtr_rolomschrijving_generiek = ''  # zaksttbtr.rolomschrijvingGeneriek
        zakbtrbtr_roltoelichting = ''  # zaksttbtr.rolToelichting

        zakstt_datum_status_gezet = huidig.heeft[0].datumStatusGezet.data
        zakstt_toelichting = huidig.heeft[0].toelichting
        if isinstance(zakstt_toelichting, Nil):
            zakstt_toelichting = None

        with transaction.atomic():
            rol = Rol.objects.create(
                zaak=zaak_obj,
                betrokkene=betrokkene_obj,
                # TODO [KING]: Taiga #221
                rolomschrijving=zakbtrbtr_rolomschrijving or Rolomschrijving.behandelaar,
                rolomschrijving_generiek=zakbtrbtr_rolomschrijving_generiek or RolomschrijvingGeneriek.behandelaar,
                roltoelichting=zakbtrbtr_roltoelichting
            )

            # TODO [KING]: There is a unique constraint on zaak and
            # datum_status_gezet. One of the tests in the STP creates two
            # different statuses on the same zaak, on the same date. I've
            # overwritten the date with a datetime below but we still have to
            # wait one second so that we don't re-use the same timestamp, and
            # violate the unique constraint.
            if settings.ZAAKMAGAZIJN_STUF_TESTPLATFORM:
                import time
                time.sleep(1)

            Status.objects.create(
                zaak=zaak_obj,
                status_type=status_type_obj,
                datum_status_gezet=zakstt_datum_status_gezet,
                statustoelichting=zakstt_toelichting,
                rol=rol,
            )

            # Eis #3
            laatst_gezette_status = zaak_obj.status_set.order_by('-datum_status_gezet').first()
            laatst_gezette_status.indicatie_laatst_gezette_status = JaNee.ja
            laatst_gezette_status.save()

            zaak_obj.status_set.exclude(pk=laatst_gezette_status.pk).update(indicatie_laatst_gezette_status=JaNee.nee)

        return {
            'stuurgegevens': get_bv03_stuurgegevens(data),
        }
