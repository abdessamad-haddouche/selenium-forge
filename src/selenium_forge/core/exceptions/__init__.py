"""Exception classes for selenium-forge.

This module provides a comprehensive exception hierarchy for handling
all types of errors that can occur in selenium-forge operations.
"""

# Base exceptions
from .base import (
    CriticalError,
    DeprecationError,
    InternalError,
    RetryableError,
    SeleniumForgeError,
    SeleniumForgeWarning,
    UserError,
    create_error_context,
    format_exception_chain,
    wrap_exception,
)

__all__ = [
    # Base exceptions
    "SeleniumForgeError",
    "SeleniumForgeWarning",
    "CriticalError",
    "RetryableError",
    "UserError",
    "InternalError",
    "DeprecationError",
    # Utility functions
    "format_exception_chain",
    "create_error_context",
    "wrap_exception",
]
