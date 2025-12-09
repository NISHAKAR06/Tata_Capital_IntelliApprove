"""Shared exception helpers."""
from __future__ import annotations


class ServiceError(RuntimeError):
    """Base error raised when an integration fails."""


class ValidationError(ServiceError):
    """Raised when downstream validation fails."""


class RetryableError(ServiceError):
    """Raised when the operation can be retried later."""
