from django.db import models

from zaakmagazijn.rgbz.choices import ArchiefNominatie, ArchiefStatus, JaNee
from zaakmagazijn.rgbz.models import (
    Status, StatusType, Zaak, ZaakInformatieObject, ZaakType
)
from zaakmagazijn.utils.stuf_datetime import today

from ..base import ModelProxy, ProxyField, ProxyForeignKey, ProxyOneToMany
from ..choices import Rolomschrijving, Zaakniveau
from ..exceptions import NoValueError
from ..manager import ProxyManager
from .betrokkene import RolProxy


class ZaakTypeProxy(ModelProxy):
    fields = (
        # Note: Zaaktypecode deviates from RGBZ 1.0 -> 2.0 mapping. See https://discussie.kinggemeenten.nl/discussie/gemma/ztc/zaaktypecode-ontbreekt-ztc
        ProxyField('zaaktypecode', 'zaaktypeidentificatie'),
        ProxyField(None, 'domein'),
        ProxyField(None, 'rsin'),
        ProxyField('zaaktypeomschrijving', 'zaaktypeomschrijving'),
        ProxyField('zaaktypeomschrijving_generiek', 'zaaktypeomschrijving_generiek'),
        ProxyField('trefwoord', 'trefwoord'),
        ProxyField('doorlooptijd_behandeling', 'doorlooptijd_behandeling'),
        # They call this a 'groupattribute' in the mapping document.
        ProxyField(None, 'doorlooptijd_behandeling'),
        ProxyField(None, 'servicenorm_behandeling'),
        ProxyField('archiefcode', 'archiefclassificatiecode'),
        ProxyField('vertrouwelijk_aanduiding', 'vertrouwelijk_aanduiding'),
        ProxyField('publicatie_indicatie', 'publicatie_indicatie'),
        ProxyField('zaakcategorie', 'zaakcategorie'),
        ProxyField('publicatietekst', 'publicatietekst'),
        ProxyField('datum_begin_geldigheid_zaaktype', 'datum_begin_geldigheid_zaaktype'),
        ProxyField('datum_einde_geldigheid_zaaktype', 'datum_einde_geldigheid_zaaktype'),
    )
    mnemonic = 'ZKT'
    model = ZaakType
    objects = ProxyManager()

    # Implemented as specified but for all practical use cases, the mapping
    # should simply exist. Hence, the code below is commented out.
    # @classmethod
    # def to_rgbz2_zaaktypeidentificatie(cls, kwargs):
    #     raise NoValueError()

    @classmethod
    def to_rgbz2_domein(cls, kwargs):
        raise NoValueError()

    @classmethod
    def to_rgbz2_rsin(cls, kwargs):
        raise NoValueError()

    @classmethod
    def to_rgbz2_doorlooptijd_behandeling(cls, kwargs):
        raise NoValueError()

    @classmethod
    def to_rgbz2_servicenorm_behandeling(cls, kwargs):
        raise NoValueError()


class StatusTypeProxy(ModelProxy):
    fields = (
        # ProxyField('zaaktype__omschrijving', 'zaaktype__zaaktypeomschrijving'),
        ProxyField('volgnummer', 'statustypevolgnummer'),
        ProxyField('omschrijving', 'statustypeomschrijving'),
        ProxyForeignKey('zaaktype', 'zaaktype', ZaakTypeProxy),
    )
    mnemonic = 'STT'
    model = StatusType
    objects = ProxyManager()


class ZaakProxy(ModelProxy):
    fields = (
        ProxyField('zaakidentificatie', 'zaakidentificatie'),
        ProxyField(None, 'bronorganisatie'),
        ProxyField('omschrijving', 'omschrijving'),
        ProxyField('toelichting', 'toelichting'),
        ProxyField('registratiedatum', 'registratiedatum'),
        ProxyField('zaakniveau', None, rgbz1_field=models.CharField(
            verbose_name='zaakniveau', max_length=1, choices=Zaakniveau.choices,
            null=False, blank=False)),

        # TODO [KING]: Not part of ZDS 1.2 but needed by RGBZ mapping: https://discussie.kinggemeenten.nl/discussie/gemma/stuf-testplatform/deelzaakindicatie-creeerzaak-volgnr-1-staat-onterecht-op-j
        # ProxyField('deelzakenindicatie', None, rgbz1_field=models.CharField(
        #     verbose_name='deelzakenindicatie', max_length=1, choices=JaNee.choices,
        #     null=False, blank=False)),
        #
        # Workaround:
        ProxyField('deelzakenindicatie', '_deelzaken_indicatie'),

        ProxyField(None, 'verantwoordelijke_organisatie'),
        ProxyField('einddatum', 'einddatum'),
        ProxyField('startdatum', 'startdatum'),
        ProxyField('einddatum_gepland', 'einddatum_gepland'),
        ProxyField('uiterlijke_einddatum_afdoening', 'uiterlijke_einddatum_afdoening'),
        ProxyOneToMany('zaakkenmerk_set', 'zaakkenmerk_set', 'zaakmagazijn.rgbz_mapping.models.ZaakKenmerkProxy'),
        ProxyField('resultaatomschrijving', 'resultaatomschrijving'),
        ProxyField('resultaattoelichting', 'resultaattoelichting'),
        ProxyField('publicatiedatum', 'publicatiedatum'),
        ProxyField('archiefnominatie', 'archiefnominatie'),
        ProxyField(None, 'archiefstatus'),
        ProxyField('datum_vernietiging_dossier', 'archiefactiedatum'),
        ProxyField('betalingsindicatie', 'betalingsindicatie'),
        ProxyField('laatste_betaaldatum', 'laatste_betaaldatum'),
        ProxyOneToMany('zaakopschorting_set', 'zaakopschorting_set', 'zaakmagazijn.rgbz_mapping.models.ZaakOpschortingProxy'),
        ProxyOneToMany('zaakverlenging_set', 'zaakverlenging_set', 'zaakmagazijn.rgbz_mapping.models.ZaakVerlengingProxy'),
        ProxyOneToMany('anderzaakobject_set', 'anderzaakobject_set', 'zaakmagazijn.rgbz_mapping.models.AnderZaakObjectProxy'),

        ProxyField('begin_geldigheid', 'begin_geldigheid'),
        ProxyField('eind_geldigheid', 'eind_geldigheid'),
        ProxyField('tijdstip_registratie', 'tijdstip_registratie'),

        # is van ZAAKTYPE
        ProxyForeignKey('zaaktype', 'zaaktype', ZaakTypeProxy),

        # heeft STATUSsen
        ProxyOneToMany('status_set', 'status_set', 'zaakmagazijn.rgbz_mapping.models.StatusProxy'),

        ProxyOneToMany('zaakobject_set', 'zaakobject_set', 'zaakmagazijn.rgbz_mapping.models.ZaakObjectProxy'),

        ProxyOneToMany('rol_set', 'rol_set', RolProxy),

        ProxyOneToMany('zaakdocument_set', 'zaakinformatieobject_set', 'zaakmagazijn.rgbz_mapping.models.ZaakDocumentProxy'),

        # TODO [KING]: Not part of ZDS 1.2 but needed by RGBZ mapping: https://discussie.kinggemeenten.nl/discussie/gemma/stuf-testplatform/deelzaakindicatie-creeerzaak-volgnr-1-staat-onterecht-op-j
        # ProxyOneToMany('deelzaken', 'deelzaken', 'zaakmagazijn.rgbz_mapping.models.ZaakProxy')
    )
    mnemonic = 'ZAK'
    model = Zaak
    objects = ProxyManager()

    @classmethod
    def to_rgbz1_zaakniveau(cls, obj):
        if obj.hoofdzaak is None:
            return '1'
        return '2'

    # TODO [KING]: Not part of ZDS 1.2 but needed by RGBZ mapping: https://discussie.kinggemeenten.nl/discussie/gemma/stuf-testplatform/deelzaakindicatie-creeerzaak-volgnr-1-staat-onterecht-op-j
    # @classmethod
    # def to_rgbz1_deelzakenindicatie(cls, obj):
    #     # if obj.deelzaken.exists():
    #     #     return JaNee.ja
    #     # return JaNee.nee

    @classmethod
    def to_rgbz1_archiefnominatie(cls, obj):
        if obj.archiefnominatie == ArchiefNominatie.vernietigen:
            return JaNee.ja
        return JaNee.nee

    @classmethod
    def to_rgbz2_bronorganisatie(cls, rgbz1_kwargs):
        return str(rgbz1_kwargs['zaakidentificatie'])[:4]

    @classmethod
    def to_rgbz2_verantwoordelijke_organisatie(cls, rgbz1_kwargs):
        return str(rgbz1_kwargs['zaakidentificatie'])[:4]

    @classmethod
    def to_rgbz2_archiefnominatie(cls, rgbz1_kwargs):
        """
        Indien waarde = "J" en 'Datum vernietiging dossier' heeft een waarde, dan "vernietigen".
        Indien waarde = "J" en 'Datum vernietiging dossier' heeft geen waarde, dan "blijvend bewaren".
        Indien waarde = "N" dan geen waarde.
        """

        if rgbz1_kwargs.get('archiefnominatie') == JaNee.ja:
            if rgbz1_kwargs.get('datum_vernietiging_dossier') is None:
                return ArchiefNominatie.vernietigen
            else:
                return ArchiefNominatie.blijvend_bewaren
        if rgbz1_kwargs.get('archiefnominatie') == JaNee.nee:
            return None

    @classmethod
    def to_rgbz2_archiefstatus(cls, rgbz1_kwargs):
        """
        Indien Archiefnominatie = "J" en 'Datum vernietiging dossier' heeft:
        - een waarde in de toekomst, dan "gearchiveerd",
        - anders: "vernietigd".
        Indien Archiefnominatie = "J" en 'Datum vernietiging dossier' heeft geen waarde, dan "gearchiveerd".
        Indien Archiefnominatie = "N" dan "nog te archiveren".
        """

        if rgbz1_kwargs.get('archiefnominatie') == JaNee.ja:
            if rgbz1_kwargs.get('datum_vernietiging_dossier') is None:
                return ArchiefStatus.gearchiveerd
            elif rgbz1_kwargs.get('datum_vernietiging_dossier') < today():
                return ArchiefStatus.gearchiveerd
            else:
                return ArchiefStatus.vernietigd
        elif rgbz1_kwargs.get('archiefnominatie') == JaNee.nee:
            return ArchiefStatus.nog_te_archiveren

        # TODO [KING]: See https://discussie.kinggemeenten.nl/discussie/gemma/koppelvlak-zs-dms/archiefnominatie-zds-12
        return ArchiefStatus.nog_te_archiveren

    def groep_kenmerken(self):
        return self.zaakkenmerk_set, {}

    def groep_anderzaakobject(self):
        return self.anderzaakobject_set, {}

    def groep_zaakopschorting(self):
        return self.zaakopschorting_set, {}

    def groep_zaakverlenging(self):
        return self.zaakverlenging_set, {}

    # TODO [KING]: Not part of ZDS 1.2 but needed by RGBZ mapping: https://discussie.kinggemeenten.nl/discussie/gemma/stuf-testplatform/deelzaakindicatie-creeerzaak-volgnr-1-staat-onterecht-op-j
    # def heeft_deelzaken(self):
    #     return self.deelzaken, {}

    def heeft_als_belanghebbende(self):
        return self.rol_set, self.rol_set.proxy_model.get_rol_defaults(Rolomschrijving.belanghebbende)

    def heeft_als_gemachtigde(self):
        return self.rol_set, self.rol_set.proxy_model.get_rol_defaults(Rolomschrijving.gemachtigde)

    def heeft_als_initiator(self):
        return self.rol_set, self.rol_set.proxy_model.get_rol_defaults(Rolomschrijving.initiator)

    def heeft_als_uitvoerende(self):
        return self.rol_set, self.rol_set.proxy_model.get_rol_defaults(Rolomschrijving.uitvoerder)

    def heeft_als_verantwoordelijke(self):
        return self.rol_set, self.rol_set.proxy_model.get_rol_defaults(Rolomschrijving.verantwoordelijke)

    def heeft_als_overig_betrokkene(self):
        return self.rol_set, self.rol_set.proxy_model.get_rol_defaults(Rolomschrijving.overig)

# EigenschappenProxy


class StatusProxy(ModelProxy):
    fields = (
        ProxyField('toelichting', 'statustoelichting'),
        ProxyField('datum_status_gezet', 'datum_status_gezet'),
        ProxyField('indicatie_laatst_gezette_status', 'indicatie_laatst_gezette_status'),
        ProxyForeignKey('status_type', 'status_type', StatusTypeProxy),
        ProxyForeignKey('rol', 'rol', RolProxy),
        ProxyForeignKey('zaak', 'zaak', 'zaakmagazijn.rgbz_mapping.models.ZaakProxy'),
    )
    mnemonic = 'ZAKSTT'
    model = Status
    objects = ProxyManager()

    def is_gezet_door(self):
        assert self.rol.zaak == self.zaak
        return self.rol.betrokkene


class ZaakDocumentProxy(ModelProxy):
    model = ZaakInformatieObject
    mnemonic = 'ZAKEDC'
    fields = (
        ProxyField('zaakdocumenttitel', 'titel'),
        ProxyField('zaakdocumentbeschrijving', 'beschrijving'),
        ProxyField('registratiedatum', 'registratiedatum'),
        ProxyForeignKey('status', 'status', StatusProxy),
        ProxyForeignKey('zaak', 'zaak', ZaakProxy),
        ProxyForeignKey('informatieobject', 'informatieobject', 'zaakmagazijn.rgbz_mapping.models.EnkelvoudigDocumentProxy'),

        ProxyField('begin_geldigheid', 'begin_geldigheid'),
        ProxyField('eind_geldigheid', 'eind_geldigheid'),
        ProxyField('begin_relatie', 'begin_relatie'),
        ProxyField('eind_relatie', 'eind_relatie'),
        ProxyField('tijdstip_registratie', 'tijdstip_registratie'),
    )

# ZaakObject

# ZakenRelatie
