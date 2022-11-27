class ValidationError(ValueError):
    """This exception is used to indicate that a certain requst is lacking or
    has unacceptable data aboard."""

    pass


class RatelimitError(ValueError):
    """This exception is used to indicate that a user has surpassed their
    ratelimit for a certain action."""

    pass


class SpamError(ValueError):
    """This exception is used to indicate that a user has exceeded the allowed
    spamscore."""

    pass
