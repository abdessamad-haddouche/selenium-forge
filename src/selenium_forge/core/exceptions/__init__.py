"""Exception classes for selenium-forge.

This module provides a comprehensive exception hierarchy for handling
all types of errors that can occur in selenium-forge operations.
"""

# Configuration exceptions namespace
from . import config

# Base exceptions
from .base import (  # Base error classes; Utility functions
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

# Configuration Exceptions
from .config import (
    ConfigurationError,
    ConfigValidationError,
    DirectoryAccessError,
    FileAccessError,
    InvalidConfigValueError,
    LogDirectoryError,
    LogFileError,
    LoggingConfigError,
    MissingConfigError,
    NetworkConfigError,
    directory_access_error,
    file_access_error,
    invalid_boolean,
    invalid_file_size,
    invalid_log_level,
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
    # Base exceptions utilities
    "format_exception_chain",
    "create_error_context",
    "wrap_exception",
    # Config namespace
    "config",
    # Generic config exceptions
    "ConfigurationError",
    "InvalidConfigValueError",
    "MissingConfigError",
    "ConfigValidationError",
    "DirectoryAccessError",
    "FileAccessError",
    "NetworkConfigError",
    # Domain-specific exceptions
    "LoggingConfigError",
    "LogDirectoryError",
    "LogFileError",
    # Factory functions
    "directory_access_error",
    "file_access_error",
    "invalid_log_level",
    "invalid_file_size",
    "invalid_boolean",
]
