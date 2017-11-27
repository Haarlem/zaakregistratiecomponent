import decimal

from django.db import transaction

from spyne import ComplexModel, ServiceBase, Unicode, rpc

from ...rgbz.models import (
    Besluit, BesluitInformatieObject, BesluitType, InformatieObject, Zaak
)
from ..stuf import simple_types
from ..stuf.attributes import entiteittype, noValue, verwerkingssoort
from ..stuf.choices import ClientFoutChoices, ServerFoutChoices
from ..stuf.constants import STUF_XML_NS, ZKN_XML_NS
from ..stuf.faults import StUFFault
from ..stuf.models import Bv03Bericht, Systeem, Tijdstip_e, TijdvakGeldigheid
from ..stuf.utils import get_bv03_stuurgegevens


class VoegBesluitToe_EDC_kerngegevensKennisgeving(ComplexModel):
    __namespace__ = ZKN_XML_NS
    __type_name__ = 'VoegBesluitToe_EDC_kerngegevensKennisgeving'
    _type_info = [
        # Elements
        ('identificatie', simple_types.Refnummer.customize(nillable=True)),  # DocumentIdentificatie-e
        ('dct.omschrijving', simple_types.Omschrijving.customize(nillable=True, min_occurs=0)),  # Omschrijving-e
        ('titel', Unicode.customize(nillable=True, min_occurs=0)),  # DocumentTitel-e
        # Attributes
        ('entiteittype', entiteittype.customize(fixed='EDC')),
        ('verwerkingssoort', verwerkingssoort),
        # <attribute ref="StUF:sleutelVerzendend"/>
        # <attribute ref="StUF:sleutelOntvangend"/>
        # <attribute ref="StUF:sleutelGegevensbeheer"/>
        # <attribute ref="StUF:sleutelSynchronisatie"/>
    ]


class VoegBesluitToe_BSLEDC_kennisgeving(ComplexModel):
    __namespace__ = ZKN_XML_NS
    __type_name__ = 'VoegBesluitToe_BSLEDC_kennisgeving'
    _type_info = [
        # Elements
        ('gerelateerde', VoegBesluitToe_EDC_kerngegevensKennisgeving),
        # <element ref="StUF:extraElementen" minOccurs="0"/>
        # Attributes
        ('entiteittype', entiteittype.customize(fixed='BSLEDC')),
        ('verwerkingssoort', verwerkingssoort),
        ('noValue', noValue)
        # <attribute ref="StUF:aantalVoorkomens"/>
        # <attribute ref="StUF:aardAantal"/>
        # <attribute ref="StUF:sleutelVerzendend"/>
        # <attribute ref="StUF:sleutelOntvangend"/>
        # <attribute ref="StUF:sleutelGegevensbeheer"/>
        # <attribute ref="StUF:sleutelSynchronisatie"/>
    ]


class VoegBesluitToe_BSL_kennisgeving(ComplexModel):
    __namespace__ = ZKN_XML_NS
    __type_name__ = 'VoegBesluitToe_BSL_kennisgeving'
    _type_info = [
        # Elements
        ('identificatie', simple_types.Refnummer.customize(nillable=True)),  # DocumentIdentificatie-e
        ('bst.omschrijving', simple_types.Omschrijving.customize(nillable=True, min_occurs=0)),  # Omschrijving-e
        ('datumBeslissing', simple_types.Datum.customize(nillable=True)),  # Datum-e
        ('toelichting', Unicode.customize(type_name='Toelichting-e', max_len=1000, nillable=True, min_occurs=0)),  # Toelichting-e
        ('ingangsdatumWerking', simple_types.Datum.customize(nillable=True)),
        ('einddatumWerking', simple_types.Datum.customize(nillable=True, min_occurs=0)),  # Datum-e
        ('vervalreden', Unicode.customize(type_name='Vervalreden-e', max_len=40, nillable=True, min_occurs=0)),  # Vervalreden-e
        ('datumPublicatie', simple_types.Datum.customize(nillable=True, min_occurs=0)),  # Datum-e
        ('datumVerzending', simple_types.Datum.customize(nillable=True, min_occurs=0)),  # Datum-e
        ('datumUiterlijkeReactie', simple_types.Datum.customize(nillable=True, min_occurs=0)),  # Datum-e
        ('tijdvakGeldigheid', TijdvakGeldigheid.customize(ref='tijdvakGeldigheid', min_occurs=0)),
        ('tijdstipRegistratie', Tijdstip_e.customize(ref='tijdstipRegistratie', min_occurs=0)),
        ('isVastgelegdIn', VoegBesluitToe_BSLEDC_kennisgeving.customize(nillable=True, min_occurs=0, max_occurs=decimal.Decimal('inf'))),
        # Attributes
        ('entiteittype', entiteittype.customize(fixed='BSL')),
        ('verwerkingssoort', verwerkingssoort),
        # <attribute ref="StUF:sleutelVerzendend"/>
        # <attribute ref="StUF:sleutelOntvangend"/>
        # <attribute ref="StUF:sleutelGegevensbeheer"/>
        # <attribute ref="StUF:sleutelSynchronisatie"/>
    ]


class VoegBesluitToe_ZAK_kerngegevensKennisgeving(ComplexModel):
    __namespace__ = ZKN_XML_NS
    __type_name__ = 'VoegBesluitToe_ZAK_kerngegevensKennisgeving'
    _type_info = [
        # Elements
        ('identificatie', simple_types.Refnummer),
        # Attributes
        ('entiteittype', entiteittype.customize(fixed='ZAK')),
        ('verwerkingssoort', verwerkingssoort),
        # <attribute ref="StUF:sleutelVerzendend"/>
        # <attribute ref="StUF:sleutelOntvangend"/>
        # <attribute ref="StUF:sleutelGegevensbeheer"/>
        # <attribute ref="StUF:sleutelSynchronisatie"/>
    ]


class VoegBesluitToe_object(ComplexModel):
    __namespace__ = ZKN_XML_NS
    __type_name__ = 'VoegBesluitToe_object'
    _type_info = [
        ('besluit', VoegBesluitToe_BSL_kennisgeving),
        ('zaak', VoegBesluitToe_ZAK_kerngegevensKennisgeving)
    ]


class Di01_Stuurgegevens_vbt(ComplexModel):
    __namespace__ = STUF_XML_NS
    __type_name__ = 'Di01_Stuurgegevens_vbt'
    _type_info = [
        ('berichtcode', simple_types.Berichtcode.customize(fixed='Di01')),
        ('zender', Systeem),
        ('ontvanger', Systeem),
        ('referentienummer', simple_types.Refnummer),
        ('tijdstipBericht', simple_types.Tijdstip),
        ('functie', simple_types.FunctievoegBesluitToe),
    ]


class Di01_VoegBesluitToe(ComplexModel):
    __namespace__ = ZKN_XML_NS
    __type_name__ = 'Di01_VoegBesluitToe'
    _type_info = [
        ('stuurgegevens', Di01_Stuurgegevens_vbt),
        ('object', VoegBesluitToe_object),
    ]


class VoegBesluitToe(ServiceBase):
    """
    De "voeg besluit toe"-service biedt de mogelijkheid voor een ZSC om een
    besluit toe te voegen aan de registratie van het ZS. Er dient altijd een
    geldige besluitidentificatie aangeleverd te worden. De ZSC kan hiervoor
    zelf een besluitidentificatie genereren of de ZSC kan gebruik maken van de
    "genereerBesluitIdentificatie"-service om een geldige zaakidentificatie op
    te vragen. Relateren aan de zaak waar dit besluit in vastgelegd wordt
    gebeurt door in het bericht de kerngegevens van de gerelateerde zaak op te
    nemen.

    Zie: ZDS 1.2, paragraaf 4.1.7
    """
    @rpc(Di01_VoegBesluitToe, _body_style="bare", _out_message_name="{http://www.egem.nl/StUF/StUF0301}Bv03Bericht", _returns=Bv03Bericht)
    def voegBesluitToe_Di01(ctx, data):
        """
        In een Zaak is een besluit genomen welke moet worden vastgelegd.
        """

        # Eisen aan ZS:
        #
        # Het ZS verwerkt berichten asynchroon en direct ("near realtime");

        besluit = data.object.besluit
        bst_omschrijving = getattr(besluit, 'bst.omschrijving', None)

        # if bst_omschrijving is None:
        #    raise StUFFault(ServerFoutChoices.stuf064, stuf_details='')

        try:
            besluit_type = BesluitType.objects.get(
                besluittypeomschrijving=bst_omschrijving,
            )
        except BesluitType.DoesNotExist as e:
            raise StUFFault(ServerFoutChoices.stuf064, stuf_details=str(e))

        zaak = data.object.zaak
        zaken_objs = Zaak.objects.filter(zaakidentificatie=zaak.identificatie)

        if not zaken_objs.exists():
            raise StUFFault(ServerFoutChoices.stuf064)

        if Besluit.objects.filter(identificatie=besluit.identificatie).exists():
            raise StUFFault(ServerFoutChoices.stuf046)

        # TODO [TECH]: Why are theses referenced, but unused?
        try:
            datum_begin = besluit.tijdvakGeldigheid.beginGeldigheid.data
        except AttributeError:
            raise StUFFault(ClientFoutChoices.stuf062)

        try:
            datum_einde = besluit.tijdvakGeldigheid.eindGeldigheid.data
        except AttributeError:
            datum_einde = None

        with transaction.atomic():
            besluit_obj = Besluit.objects.create(
                identificatie=besluit.identificatie,
                besluitdatum=besluit.datumBeslissing,
                besluittoelichting=besluit.toelichting,
                ingangsdatum=besluit.ingangsdatumWerking,
                vervaldatum=besluit.einddatumWerking,
                vervalreden=besluit.vervalreden,
                publicatiedatum=besluit.datumPublicatie,
                verzenddatum=besluit.datumVerzending,
                uiterlijke_reactiedatum=besluit.datumUiterlijkeReactie,
                # TODO [KING]: Taiga #210 (BSL) Element "tijdstipRegistratie" in "voegBesluitToe" ontbreekt in RGBZ
                # ???=besluit.tijdstipRegistratie,
                zaak=zaken_objs[0],
                besluittype=besluit_type,
            )

            if besluit.isVastgelegdIn:
                for bsledc in besluit.isVastgelegdIn:
                    edc_identificatie = bsledc.gerelateerde.identificatie
                    informatie_object = InformatieObject.objects.get(informatieobjectidentificatie=edc_identificatie)

                    BesluitInformatieObject.objects.create(
                        besluit=besluit_obj,
                        informatieobject=informatie_object,
                    )

        return {
            'stuurgegevens': get_bv03_stuurgegevens(data),
        }
