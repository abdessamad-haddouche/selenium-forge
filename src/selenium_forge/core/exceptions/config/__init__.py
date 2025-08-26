"""Configuration exceptions package for selenium-forge."""

# Import all generic config exceptions
# Import domain-specific exceptions
from .domains import (  # Logging exceptions; Factory functions
    LogDirectoryError,
    LogFileError,
    LoggingConfigError,
    invalid_boolean,
    invalid_file_size,
    invalid_log_level,
)
from .generic import (  # Factory functions
    ConfigurationError,
    ConfigValidationError,
    DirectoryAccessError,
    FileAccessError,
    InvalidConfigValueError,
    MissingConfigError,
    NetworkConfigError,
    directory_access_error,
    file_access_error,
)

__all__ = [
    # Generic exceptions
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
