class ReclaimAPIError(Exception):
    """
    Base class for Reclaim.ai API errors.
    """

    ...


class RecordNotFound(ReclaimAPIError):
    def __init__(self, message):
        self.message = message


class InvalidRecord(ReclaimAPIError):
    def __init__(self, message):
        self.message = message
