from django.conf import settings

from lxml import etree
from zeep import Client

from ..api.stuf.choices import BerichtcodeChoices
from ..api.utils import create_unique_id
from ..apiauth.choices import EndpointTypeChoices
from ..utils import stuf_datetime
from .exceptions import ConsumerException, UnexpectedAnswerException


class Consumer(object):
    def __init__(self, application, dryrun=False):
        self.application = application
        self.dryrun = dryrun

        self.endpoints = dict(application.endpoint_set.values_list('type', 'url'))

        self.namespaces = {
            'zkn': 'http://www.egem.nl/StUF/sector/zkn/0310',
            'stuf': 'http://www.egem.nl/StUF/StUF0301',
            'zds': 'http://www.stufstandaarden.nl/koppelvlak/zds0120',
            'soap11env': 'http://schemas.xmlsoap.org/soap/envelope/'
        }

    def request(self, endpoint_type, operation_name, data):
        if endpoint_type not in EndpointTypeChoices.values.keys():
            raise ValueError('Invalid value for endpoint_type: {}'.format(endpoint_type))

        client = Client(self.endpoints[endpoint_type])
        for prefix, url in self.namespaces.items():
            client.set_ns_prefix(prefix, url)

        if self.dryrun:
            root = client.create_message(client.service, operation_name, **data)
            print(etree.tostring(root, pretty_print=True).decode('utf-8'))
            return None

        # CommunicationLogEntry.objects.log(data, direction=CommunicationDirectionChoices.outgoing)

        with client.options(raw_response=True):
            response = client.service[operation_name](**data)

        try:
            response_root = etree.fromstring(response.content)
            response_berichtcode = response_root.xpath('//stuf:stuurgegevens/stuf:berichtcode', namespaces=self.namespaces)[0].text
        except IndexError as e:
            raise ConsumerException('Server returned unexpected or invalid XML.')
        except Exception as e:
            raise ConsumerException('Server returned invalid XML.')

        # CommunicationLogEntry.objects.log(response, direction=CommunicationDirectionChoices.incomming)

        if response_berichtcode != BerichtcodeChoices.bv03:
            raise UnexpectedAnswerException('Expected "Bv03" but got "{}".'.format(response_berichtcode))

        return response

    def overdragenZaak(self, zaak, accepted, cross_ref_nummer, melding=None):
        if melding is not None and not isinstance(melding, (list, tuple)):
            melding = [melding, ]

        referentienummer = create_unique_id()
        berichtcode = BerichtcodeChoices.du01
        functie = 'overdragenZaak'
        operation_name = '{}_{}'.format(functie, berichtcode)

        if accepted:
            antwoord = 'Overdracht geaccepteerd'
        else:
            antwoord = 'Overdracht geweigerd'

        data = {
            'stuurgegevens': {
                'berichtcode': berichtcode,
                'zender': settings.ZAAKMAGAZIJN_SYSTEEM,
                'ontvanger': self.application.zender_as_dict(),
                'referentienummer': referentienummer,
                'tijdstipBericht': stuf_datetime.now(),
                'crossRefnummer': cross_ref_nummer,
                'functie': functie,
            },
            'object': {
                # Attributes
                'entiteittype': 'ZAK',
                'functie': 'entiteit',
                # Elements
                'identificatie': zaak.zaakidentificatie,
                'antwoord': antwoord,
            }
        }
        if melding:
            data['melding'] = melding

        return self.request(EndpointTypeChoices.ontvang_asynchroon, operation_name, data)
