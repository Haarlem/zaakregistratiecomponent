from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext as _

from ....api.stuf.faults import StUFFault
from ....api.stuf.utils import get_systeem
from ....apiauth.models import Application
from ....rgbz.models import Zaak
from ...consumer import Consumer
from ...exceptions import UnexpectedAnswerException


class Command(BaseCommand):
    help = _('Accepteer of weiger de overdracht van een Zaak.')

    def add_arguments(self, parser):
        parser.add_argument(
            'application_name',
            metavar='APPLICATION_NAME',
            action='store',
            help='Application name, as it is known by the system.',
        )
        parser.add_argument(
            'zaak_id',
            metavar='ZAAK_ID',
            action='store',
            help='Zaak identification, as it is known by the system.'
        )
        parser.add_argument(
            'xrefnumber',
            metavar='XREFNUMBER',
            action='store',
            help='The cross reference number.',
        )
        parser.add_argument(
            '-m', '--message',
            metavar='MESSAGE',
            action='append',
            dest='message',
            help='One or more messages that are sent with the request for transfer.',
        )
        parser.add_argument(
            '-d', '--decline',
            action='store_false',
            dest='accepted',
            default=True,
            help='Decline the Zaak. If not provided the Zaak will be accepted.',
        )
        parser.add_argument(
            '-s', '--sender',
            action='store',
            dest='sender_organisation',
            default=True,
            help='Organisation to use as sender. Required if multiple senders are defined in ZAAKMAGAZIJN_SYSTEEM.',
        )
        parser.add_argument(
            '--dry-run', '--dryrun',
            action='store_true',
            dest='dryrun',
            default=False,
            help='Only shows the outgoing XML request. No actual request is made.',
        )

    def handle(self, application_name, zaak_id, xrefnumber, *args, **options):
        try:
            application = Application.objects.get(name=application_name)
        except Application.DoesNotExist as e:
            raise CommandError('Application "{}" does not exist.'.format(application_name))
        try:
            zaak = Zaak.objects.get(zaakidentificatie=zaak_id)
        except Zaak.DoesNotExist as e:
            raise CommandError('Zaak "{}" does not exist.'.format(zaak_id))

        sender_organisation = options.get('sender_organisation', None)

        # Mock the expected object to pass to ``get_systeem``.
        class Sender(object):
            organisatie = sender_organisation

        try:
            sender = get_systeem(Sender())
        except StUFFault:
            raise CommandError('The sender should be provided using --sender=<organisation> and configured in '
                               'ZAAKMAGAZIJN_SYSTEEM.')

        accepted = options.get('accepted', True)
        messages = options.get('message', [])
        dryrun = options.get('dryrun', False)

        consumer = Consumer(application, dryrun=dryrun)

        try:
            result = consumer.overdragenZaak(
                zaak,
                messages,
                accepted,
                xrefnumber,
                sender,
            )
            self.stdout.write('Operation succeeded: {}'.format(result.content if result else '(no response)'))
        except UnexpectedAnswerException as e:
            self.stdout.write('Server returned an error: {}'.format(e))
        except Exception as e:
            self.stdout.write('Operation failed: {}'.format(e))
