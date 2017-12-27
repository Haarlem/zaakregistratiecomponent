from spyne import ServiceBase, rpc

from zaakmagazijn.rgbz_mapping.models import (
    EnkelvoudigDocumentProxy, ZaakDocumentProxy, ZaakProxy
)

from ..stuf import OneToManyRelation, StUFEntiteit
from ..stuf.models import (
    EDC_parametersVraagSynchroon, ParametersAntwoordSynchroon
)
from ..zds import La01Builder, Lv01Builder


class ZaakEntiteit(StUFEntiteit):
    mnemonic = 'ZAK'
    model = ZaakProxy
    field_mapping = (
        ('identificatie', 'zaakidentificatie'),
    )


class ZaakInformatieObjectEntiteit(StUFEntiteit):
    mnemonic = 'EDCZAK'
    model = ZaakDocumentProxy
    gerelateerde = ('zaak', ZaakEntiteit)
    field_mapping = ()


class EnkelvoudigInformatieObjectEntiteit(StUFEntiteit):
    mnemonic = 'EDC'
    model = EnkelvoudigDocumentProxy
    field_mapping = (
        ('identificatie', 'identificatie'),
        ('dct.omschrijving', 'documenttype__documenttypeomschrijving'),
        ('dct.omschrijvingGeneriek', 'documenttype__documenttypeomschrijving_generiek'),
        ('dct.categorie', 'documenttype__documentcategorie'),
        ('creatiedatum', 'documentcreatiedatum'),
        ('ontvangstdatum', 'documentontvangstdatum'),
        # TODO [KING]: Taiga #236 De velden titel, beschrijving, etc. staan ook op EDCZAK in geefZaakdocumentLezen maar worden niet gemapped.
        ('titel', 'documenttitel'),
        ('beschrijving', 'documentbeschrijving'),
        ('formaat', 'documentformaat'),
        ('taal', 'documenttaal'),
        ('versie', 'documentversie'),
        ('status', 'documentstatus'),
        ('verzenddatum', 'documentverzenddatum'),
        ('vertrouwelijkAanduiding', 'vertrouwlijkaanduiding'),
        ('auteur', 'documentauteur'),
        ('link', 'documentlink'),
        ('inhoud', '_inhoud'),
    )
    filter_fields = ('identificatie',)
    input_parameters = EDC_parametersVraagSynchroon
    output_parameters = ParametersAntwoordSynchroon
    related_fields = (
        OneToManyRelation('isRelevantVoor', 'zaakinformatieobject_set', ZaakInformatieObjectEntiteit),
    )
    file_fields = ('inhoud',)


input_builder = Lv01Builder(EnkelvoudigInformatieObjectEntiteit, 'GeefZaakdocumentLezen')
output_builder = La01Builder(EnkelvoudigInformatieObjectEntiteit, 'GeefZaakdocumentLezen')


class GeefZaakdocumentLezen(ServiceBase):
    """
    De "geef Zaakdocument Lezen"-service biedt DSC's de mogelijkheid om een
    kopie van een document behorende bij een ZAAK op te vragen uit het DMS
    middels een vraag-/antwoordinteractie. Het ZS benadert het DMS middels CMIS
    om het gewenste document op te halen en in een StUFantwoordbericht terug te
    sturen naar de DSC.

    Zie ZDS 1.2, paragraaf 4.3.2
    """
    input_model = input_builder.create_model()
    output_model = output_builder.create_model()

    @rpc(input_model, _body_style="bare", _out_message_name="geefZaakdocumentLezen_EdcLa01", _returns=output_model)
    def geefZaakdocumentLezen_EdcLv01(ctx, data):
        """
        Een document dat tot een lopende zaak behoort, wordt opgevraagd.
        """

        # Eisen aan ZS:
        #
        # Er gelden geen aanvullende eisen.

        # Interactie tussen DSC en ZS:
        #
        # Tussen DSC en ZS is een vraag-/antwoordinteractie.

        # Interactie tussen ZS en DMS:
        #
        # Het geefZaakdocumentLezen_EdcLv01 bericht wordt vertaald naar
        # CMIS-operatie(s) zodanig dat het ZS een geefZaakdocumentLezen_EdcLa01
        # antwoordbericht voor de ZSC kan genereren met de gevraagde elementen.
        # In Tabel 3 is een mapping aangegeven tussen de StUF-ZKN-elementen en
        # CMIS-properties om de vertaling uit te voeren.

        return output_builder.create_data(data, GeefZaakdocumentLezen.output_model)
