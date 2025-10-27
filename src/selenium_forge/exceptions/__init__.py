"""Selenium Forge exception system.

This module provides a comprehensive exception hierarchy for selenium-forge,
including base exception classes, domain-specific errors, and utility functions
for exception handling and debugging.
"""

# Base exception classes
from .base import (
    SeleniumForgeError,
    SeleniumForgeWarning,
    CriticalError,
    RetryableError,
    UserError,
    InternalError,
    DeprecationError,
)

# Exception utilities
from .utils import (
    create_error_context,
    format_exception_chain,
    wrap_exception,
    get_exception_hierarchy,
    critical_error,
    user_error,
    retryable_error,
)

# Public API - what users should import
__all__ = [
    # Base exception classes
    "SeleniumForgeError",
    "SeleniumForgeWarning",
    "CriticalError",
    "RetryableError", 
    "UserError",
    "InternalError",
    "DeprecationError",
    
    # Utility functions
    "create_error_context",
    "format_exception_chain",
    "wrap_exception",
    "get_exception_hierarchy",
    
    # Quick error helpers
    "critical_error",
    "user_error", 
    "retryable_error",
]