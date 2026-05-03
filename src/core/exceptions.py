"""Domain-level exceptions used across all bounded contexts.

Each exception carries an HTTP status code so the Flask error handler can
translate it into a uniform JSON response.
"""
from __future__ import annotations


class DomainError(Exception):
    """Base class for all expected, non-bug domain errors."""

    status_code: int = 400

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self) -> dict:
        return {"error": self.__class__.__name__, "message": self.message}


class NotFoundError(DomainError):
    status_code = 404


class ValidationError(DomainError):
    status_code = 400


class ConflictError(DomainError):
    status_code = 409


class AuthenticationError(DomainError):
    status_code = 401


class AuthorizationError(DomainError):
    status_code = 403


class PaymentFailedError(DomainError):
    status_code = 402


class ExternalServiceError(DomainError):
    status_code = 502
