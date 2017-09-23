from django.db.models import CharField, TextField


class StUFDateField(CharField):
    """
    Allow saving (incomplete) dates in a StUF-compatible way.

    The dates are serialized by specifying a 1 character type (V, D, M, J) and
    the rest of the date.

    in the 'V' (volledig) case the date is saved as follows:

    'V20170101'

    in the 'D' case (de datum heeft een waarde maar de dag is onbekend):

    'D201701'

    in the 'M' case (de datum heeft een waarde maar maand en dag zijn onbekend):

    'M2017'

    in the 'J' case (de datum heeft een waarde maar jaar, maand en dag zijn onbekend):

    'J'
    """

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 1 + 8)
        super(StUFDateField, self).__init__(*args, **kwargs)


class StUFDateTimeField(CharField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 1 + 17)
        super(StUFDateTimeField, self).__init__(*args, **kwargs)


class GMLField(TextField):
    pass
