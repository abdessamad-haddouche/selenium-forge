"""Domain-specific configuration exceptions.

This module provides specialized exceptions for different configuration
domains like logging, browser setup, driver management, etc.
"""

from __future__ import annotations

from typing import Any, Optional, Set

from .generic import (
    ConfigValidationError,
    DirectoryAccessError,
    FileAccessError,
    InvalidConfigValueError,
    MissingConfigError,
    NetworkConfigError,
)

# ================================================================
# Logging Configuration Exceptions
# ================================================================


class LoggingConfigError(InvalidConfigValueError):
    """Specialized error for logging configuration."""

    def __init__(
        self,
        message: str,
        config_key: str,
        provided_value: Any,
        valid_values: Optional[Set[str]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            message=message,
            config_key=config_key,
            provided_value=provided_value,
            valid_values=valid_values,
            config_domain="logging",
            **kwargs,
        )


class LogDirectoryError(DirectoryAccessError):
    """Error related to log directory operations."""

    def __init__(
        self, message: str, directory_path: str, operation: str, **kwargs: Any
    ) -> None:
        super().__init__(
            message=message,
            directory_path=directory_path,
            operation=operation,
            config_domain="logging",
            **kwargs,
        )


class LogFileError(FileAccessError):
    """Error related to log file operations."""

    def __init__(
        self, message: str, file_path: str, operation: str, **kwargs: Any
    ) -> None:
        super().__init__(
            message=message,
            file_path=file_path,
            operation=operation,
            config_domain="logging",
            **kwargs,
        )


# ================================================================
# Factory Functions for Logging-Specific Errors
# ================================================================


def invalid_log_level(
    env_var: str, provided_value: str, valid_levels: Set[str]
) -> LoggingConfigError:
    """Create logging-specific invalid log level error."""
    return LoggingConfigError(
        message=f"Invalid log level '{provided_value}' for {env_var}",
        config_key=env_var,
        provided_value=provided_value,
        valid_values=valid_levels,
    )


def invalid_file_size(env_var: str, provided_value: str) -> LoggingConfigError:
    """Create logging-specific invalid file size error."""
    return LoggingConfigError(
        message=f"Invalid file size format '{provided_value}' for {env_var}",
        config_key=env_var,
        provided_value=provided_value,
        valid_values={"1KB", "5MB", "100MB", "1GB"},
    )


def invalid_boolean(env_var: str, provided_value: str) -> LoggingConfigError:
    """Create logging-specific invalid boolean error."""
    return LoggingConfigError(
        message=f"Invalid boolean value '{provided_value}' for {env_var}",
        config_key=env_var,
        provided_value=provided_value,
        valid_values={"true", "false", "1", "0", "yes", "no", "on", "off"},
    )
