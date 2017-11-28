
class NoValueError(Exception):
    """
    This is an exception to indicate that we can't make the conversion, and
    it shouldn't be included in the filter/create kwargs.
    """
    pass
