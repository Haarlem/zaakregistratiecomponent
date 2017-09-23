from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext as _

from zaakmagazijn.async.exceptions import (
    ConsumerException, UnexpectedAnswerException
)

from ....apiauth.models import Application
from ....rgbz.models import Zaak
from ...consumer import Consumer


class Command(BaseCommand):
    help = _('Draag een zaak over aan een andere applicatie.')

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
            '-m', '--message',
            metavar='MESSAGE',
            action='append',
            dest='message',
            help='One or more messages that are sent with the request for transfer.',
        )
        parser.add_argument(
            '--dry-run', '--dryrun',
            action='store_true',
            dest='dryrun',
            default=False,
            help='Only shows the outgoing XML request. No actual request is made.',
        )

    def handle(self, application_name, zaak_id, *args, **options):
        try:
            application = Application.objects.get(name=application_name)
        except Application.DoesNotExist as e:
            raise CommandError('Application "{}" does not exist.'.format(application_name))
        try:
            zaak = Zaak.objects.get(zaakidentificatie=zaak_id)
        except Zaak.DoesNotExist as e:
            raise CommandError('Zaak "{}" does not exist.'.format(zaak_id))

        messages = options.get('message', [])
        dryrun = options.get('dryrun', False)

        consumer = Consumer(application, dryrun=dryrun)

        try:
            result = consumer.overdragenZaak(zaak, messages)
            self.stdout.write('Operation succeeded: {}'.format(result.content if result else '(no response)'))
        except UnexpectedAnswerException as e:
            self.stdout.write('Server returned an error: {}'.format(e))
        except Exception as e:
            self.stdout.write('Operation failed: {}'.format(e))
