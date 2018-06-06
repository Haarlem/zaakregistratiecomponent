import logging

from lxml import etree
from spyne import ComplexModel, Fault
from spyne.protocol.xml import XmlDocument

from . import simple_types
from ...utils import stuf_datetime
from ..utils import create_unique_id
from .choices import BerichtcodeChoices, ClientFoutChoices, ServerFoutChoices
from .models import BaseStuurgegevens, Systeem
from .utils import get_systeem

logger = logging.getLogger(__name__)


class Fo01BerichtStuurgegevens(BaseStuurgegevens):
    __namespace__ = 'http://www.egem.nl/StUF/StUF0301'
    _type_info = [
        ('zender', Systeem),
        ('ontvanger', Systeem),
        ('referentienummer', simple_types.Refnummer),
        ('tijdstipBericht', simple_types.Tijdstip),
        ('crossRefnummer', simple_types.Refnummer),
    ]


class Fo02BerichtStuurgegevens(BaseStuurgegevens):
    __namespace__ = 'http://www.egem.nl/StUF/StUF0301'


class Fo03BerichtStuurgegevens(BaseStuurgegevens):
    __namespace__ = 'http://www.egem.nl/StUF/StUF0301'
    _type_info = [
        ('zender', Systeem),
        ('ontvanger', Systeem),
        ('referentienummer', simple_types.Refnummer),
        ('tijdstipBericht', simple_types.Tijdstip),
        ('crossRefnummer', simple_types.Refnummer),
    ]


class Foutbericht(ComplexModel):
    __namespace__ = 'http://www.egem.nl/StUF/StUF0301'
    __type_name__ = 'Foutbericht'
    _type_info = [
        ('code', simple_types.Foutcode),
        ('plek', simple_types.Foutplek),
        ('omschrijving', simple_types.Foutomschrijving),
        ('details', simple_types.Foutdetails.customize(min_occurs=0)),
        ('detailsXML', simple_types.FoutdetailsXML.customize(min_occurs=0)),
    ]


class Fo01Bericht(ComplexModel):
    __namespace__ = 'http://www.egem.nl/StUF/StUF0301'
    __type_name__ = 'Fo01Bericht'
    _type_info = [
        ('stuurgegevens', Fo01BerichtStuurgegevens),
        ('body', Foutbericht)
    ]


class Fo02Bericht(ComplexModel):
    __namespace__ = 'http://www.egem.nl/StUF/StUF0301'
    __type_name__ = 'Fo02Bericht'
    _type_info = [
        ('stuurgegevens', Fo02BerichtStuurgegevens),
        ('body', Foutbericht)
    ]


class Fo03Bericht(ComplexModel):
    __namespace__ = 'http://www.egem.nl/StUF/StUF0301'
    __type_name__ = 'Fo03Bericht'
    _type_info = [
        ('stuurgegevens', Fo03BerichtStuurgegevens),
        ('body', Foutbericht)
    ]


class StUFFault(Exception):
    """
    This fault should be raised from the services. Based on the application that this
    exception is raised from, either StufFault or AsyncStufFault is build.
    """

    def __init__(self, stuf_code, stuf_details=None):
        """
        :param stuf_code Error code, which can be any value from ServerFoutChoices or ServerFoutChoices
        :param stuf_details Details of the error message
        """
        self.stuf_code = stuf_code
        self.stuf_details = stuf_details


class SpyneStUFFault(Fault):
    """
    Spyne representation of a StUF fault message.

    See: Protocolbindingen voor StUF, chapter 4

    Ten behoeve van foutafhandeling kent SOAP het <SOAP:fault> element. De elementen van het
    <SOAP:fault> element worden gevuld op basis van de elementen binnen het StUF-foutbericht:

    * Het element <SOAP:faultcode> wordt gevuld met de namespace qualifier voor de namespace
    “http://schemas.xmlsoap.org/soap/envelope/ “ gevolgd door een ':' en de waarde van <StUF:plek>
    binnen het foutbericht, bijvoorbeeld “SOAP-ENV:Client”.
    * Het element <SOAP:faultstring> wordt gevuld met de waarde van <StUF:omschrijving>
    binnen het foutbericht.
    * Het element <SOAP:details> wordt gevuld met het StUF-foutbericht.
    * Het element <SOAP:faultactor> wordt niet opgenomen in het <SOAP:fault> element.

    Het is de verantwoordelijkheid van het systeem dat een verzoek verwerkt om het <SOAP:fault> element
    correct te vullen.
    """
    __type_name__ = 'StUFFault'

    berichtcode = BerichtcodeChoices.fo02

    def __init__(self, stuf_berichtcode, stuf_code, stuf_details=None, stuurgegevens_zender=None):
        detail, stuf_plek, stuf_omschrijving = \
            self.build_stuf_fault_detail(stuf_berichtcode, stuf_code, stuf_details, stuurgegevens_zender)

        super().__init__(faultcode=stuf_plek, faultstring=stuf_omschrijving, faultactor='', detail=detail)

    @staticmethod
    def build_stuf_fault_detail(stuf_berichtcode, stuf_code, stuf_details=None, stuurgegevens_zender=None):
        """
        Creates the detail contents of the SOAP Fault message.
        """
        if stuf_berichtcode not in [BerichtcodeChoices.fo01, BerichtcodeChoices.fo02, BerichtcodeChoices.fo03]:
            raise ValueError(
                'Unknown value for "stuf_berichtcode": {}. It should be in '
                '`BerichtcodeChoices`'.format(stuf_berichtcode))

        if stuf_code in ServerFoutChoices.values.keys():
            stuf_plek = 'server'
            stuf_omschrijving = ServerFoutChoices.values.get(stuf_code)
        elif stuf_code in ClientFoutChoices.values.keys():
            stuf_plek = 'client'
            stuf_omschrijving = ClientFoutChoices.values.get(stuf_code)
        else:
            raise ValueError(
                'Unknown value for "stuf_code": {}. It should be in `ServerFoutChoices` or '
                '`ClientFoutChoices`'.format(stuf_code))

        stuurgegevens_data = {
            'berichtcode': stuf_berichtcode,
        }
        if stuf_berichtcode != BerichtcodeChoices.fo02:
            stuurgegevens_data.update({
                'zender': get_systeem(stuurgegevens_zender.ontvanger),
                'ontvanger': {
                    'organisatie': '',
                    'applicatie': '',
                    'administratie': '',
                    'gebruiker': '',
                },
                'referentienummer': create_unique_id(),
                'tijdstipBericht': stuf_datetime.now(),
                'crossRefnummer': '',
            })

            try:
                stuurgegevens_data.update({
                    'ontvanger': {
                        'organisatie': stuurgegevens_zender.zender.organisatie,
                        'applicatie': stuurgegevens_zender.zender.applicatie,
                        'administratie': stuurgegevens_zender.zender.administratie,
                        'gebruiker': stuurgegevens_zender.zender.gebruiker,
                    },
                    'crossRefnummer': stuurgegevens_zender.referentienummer
                })
            except AttributeError:
                # It is not defined in StUF 3.01 - 4.4.3 Regels voor foutberichten
                # how to handle the situation where no proper stuurgegevens were
                # sent.
                pass

        mapping = {
            BerichtcodeChoices.fo01: (Fo01Bericht, Fo01BerichtStuurgegevens),
            BerichtcodeChoices.fo02: (Fo02Bericht, Fo02BerichtStuurgegevens),
            BerichtcodeChoices.fo03: (Fo03Bericht, Fo03BerichtStuurgegevens),
        }
        Bericht, Stuurgegevens = mapping.get(stuf_berichtcode)

        detail_part = Bericht(
            stuurgegevens=Stuurgegevens(
                **stuurgegevens_data
            ),
            body=Foutbericht(
                code=stuf_code,
                plek=stuf_plek,
                omschrijving=stuf_omschrijving,
                details=stuf_details,
            )
        )

        element = etree.Element('detail')
        XmlDocument().to_parent(None, detail_part.__class__, detail_part, element, detail_part.get_namespace())
        detail = element[0]

        return detail, stuf_plek, stuf_omschrijving

    @classmethod
    def from_details(cls, stuf_code, details, service_context, stuurgegevens_zender=None):
        return cls(
            cls.berichtcode,
            stuf_code, stuf_details=details, stuurgegevens_zender=stuurgegevens_zender
        )

    @classmethod
    def from_fault(cls, fault, service_context, stuurgegevens_zender=None):
        return cls(
            cls.berichtcode,
            ServerFoutChoices.stuf058,
            stuf_details=str(fault.detail), stuurgegevens_zender=stuurgegevens_zender
        )

    @classmethod
    def from_exception(cls, exception, service_context, stuurgegevens_zender=None):
        # Normalize the StUFFault, overwriting the berichtcode, with the berichtcode from the app
        # and using the stuurgegevens as found in the exception handler.
        if isinstance(exception, StUFFault):
            return cls(
                cls.berichtcode,
                exception.stuf_code, stuf_details=exception.stuf_details, stuurgegevens_zender=stuurgegevens_zender
            )

        return cls(
            cls.berichtcode,
            ServerFoutChoices.stuf058, stuf_details=str(exception), stuurgegevens_zender=stuurgegevens_zender
        )


class SpyneAsyncStUFFault(SpyneStUFFault):
    berichtcode = BerichtcodeChoices.fo03
