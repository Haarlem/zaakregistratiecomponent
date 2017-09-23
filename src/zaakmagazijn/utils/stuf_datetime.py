import time

from django.utils.translation import ugettext_lazy as _

from djchoices import ChoiceItem, DjangoChoices

DATE_FORMAT = '%Y%m%d'
TIME_FORMAT = '%H%M%S'
DATETIME_FORMAT = '%Y%m%d%H%M%S'
UNKNOWN_DATE_CHAR = ' '


class IndicatieOnvolledigeDatum(DjangoChoices):
    J = ChoiceItem('J', _('de datum heeft een waarde maar jaar, maand en dag zijn onbekend'))
    M = ChoiceItem('M', _('de datum heeft een waarde maar maand en dag zijn onbekend'))
    D = ChoiceItem('D', _('de datum heeft een waarde maar de dag is onbekend'))
    V = ChoiceItem('V', _('datum is volledig'))


def now():
    return time.strftime(DATETIME_FORMAT)


def today():
    return time.strftime(DATE_FORMAT)


def stuf_date(date, type=IndicatieOnvolledigeDatum.V):
    if type == IndicatieOnvolledigeDatum.J:
        return UNKNOWN_DATE_CHAR * 8

    format = DATE_FORMAT
    if type == IndicatieOnvolledigeDatum.M or type == IndicatieOnvolledigeDatum.D:
        format = format.replace('%d', UNKNOWN_DATE_CHAR * 2)
    if type == IndicatieOnvolledigeDatum.M:
        format = format.replace('%m', UNKNOWN_DATE_CHAR * 2)

    return date.strftime(format)


def stuf_datetime(date, type=IndicatieOnvolledigeDatum.V):
    return '{}{}'.format(stuf_date(date, type), date.strftime(TIME_FORMAT))


def indicatie_onvolledige_datum(stuf_date):
    """
    Return the `IndicatieOnvolledigeDatum` based on a given `stuf_date`.

    :param stuf_date: The StUF date string.
    :return: The choice item.
    """
    if stuf_date[0:8] == UNKNOWN_DATE_CHAR * 8:
        return IndicatieOnvolledigeDatum.J
    elif stuf_date[4:8] == UNKNOWN_DATE_CHAR * 4:
        return IndicatieOnvolledigeDatum.M
    elif stuf_date[6:8] == UNKNOWN_DATE_CHAR * 2:
        return IndicatieOnvolledigeDatum.D
    else:
        return IndicatieOnvolledigeDatum.V
