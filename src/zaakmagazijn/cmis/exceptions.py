class DMSException(Exception):
    pass


class DocumentExistsError(DMSException):
    pass


class DocumentDoesNotExistError(DMSException):
    pass


class SyncException(DMSException):
    pass


class DocumentConflictException(DMSException):
    pass


class DocumentLockedException(DMSException):
    pass
