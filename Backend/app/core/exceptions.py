"""Domain exceptions raised by services and mapped to HTTP responses in main.py."""


class DomainError(Exception):
    status_code = 400

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class NotFoundError(DomainError):
    status_code = 404


class ServiceUnavailableError(DomainError):
    """An external service the request depends on could not be used."""

    status_code = 503


class BusinessRuleError(DomainError):
    """A request was well-formed but violates a business rule or workflow state."""

    status_code = 400
