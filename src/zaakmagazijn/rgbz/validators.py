import re

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.deconstruct import deconstructible

from unidecode import unidecode


@deconstructible
class AlphanumericExcludingDiacritic(object):
    """
    Alle alfanumerieke tekens m.u.v. diacrieten.
    """

    def __init__(self, start=0):
        self.start = start

    def __call__(self, value):
        stripped_value = value[self.start:]
        non_diactric = unidecode(stripped_value)
        non_diactric.encode('ascii')
        if stripped_value != non_diactric:
            raise ValidationError(
                'Waarde "{0}" mag geen diakrieten of non-ascii tekens bevatten{1}'.format(
                    value, ' na de eerste {0} karakters'.format(self.start) if self.start else ''
                )
            )

    def __eq__(self, other_start):
        return self.start == other_start.start


# Default validator for entire string.
alphanumeric_excluding_diacritic = AlphanumericExcludingDiacritic()


def validate_id(value):
    """
    Volgens KING betekent alfanumeriek voor IDS, dat er alleen cijfers,
    letters en streepjes mogen voorkomen.
    """
    if re.search('^[0-9]{4}', value) is None:
        raise ValidationError('Identificatie waarde moet beginnen met de gemeentecode')

    if re.search('^[a-zA-Z0-9\-\_]+$', value) is None:
        raise ValidationError('Identificatie waarde mag alleen letters, cijfers en streepjes bevatten')


def validate_physical_file_name(value):
    """
    Alle in fysieke bestandsnamen toegestane tekens.
    See: https://msdn.microsoft.com/en-us/library/windows/desktop/aa365247(v=vs.85).aspx
    """
    result = re.search('[\x00-\x1f\<\>\:\"\/\\\|\?\*]', value)
    if result is not None:
        raise ValidationError('Bestandsnaam "{}" mag niet de waarde "{}" bevatten.'.format(value, result.group()))


def validate_continuous_numbers(value):
    """
    Aaneengesloten cijfers.
    """
    result = re.match('[0-9]*', value).group()
    if result != value:
        raise ValidationError('Waarde "{}" is niet een serie van aaneengesloten cijfers.'.format(value))


validate_nen360id = RegexValidator(
    regex='^[A-Z]{2}.[A-Z]{5}.[0-9]{16}$',
    message="Het veld moet voldoen aan het NEN360ID-formaat, wat het volgende patroon heeft: "
            "NL.IMGEO.xxxx. Het 1e deel is de landcode, het 2e deel is de code "
            "voor het sectormodel. Het derde deel is de combinatie van de "
            "(viercijferige) gemeentecode (volgens BRP stamtabel A.5.4 "
            "Gemeente), de tweecijferige code voor het type geoobject (01) en een "
            "voor het betreffende objecttype binnen een gemeente unieke "
            "tiencijferige objectvolgnummer. Identificatie is maximaal 25 "
            "alfanumerieke tekens lang.Zie voor verdere specificaties datatype "
            "NEN3610ID.")


def validate_non_negative_string(value):
    """
    Validate a string containing a integer to be non-negative.
    """
    error = False
    try:
        n = int(value)
    except ValueError:
        error = True
    if error or n < 0:
        raise ValidationError(
            'De waarde moet een niet-negatief getal zijn.')
