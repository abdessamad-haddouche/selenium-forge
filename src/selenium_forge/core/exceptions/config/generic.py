"""Generic configuration exceptions for selenium-forge.

This module provides base configuration exception classes that can be used
across all configuration domains (logging, driver setup, browser config, etc.).
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Set

from ..base import RetryableError, SeleniumForgeError, UserError

# ================================================================
# Base Config Exception Error Classes
# ================================================================


class ConfigurationError(SeleniumForgeError):
    """Base class for all configuration-related errors."""

    def _get_default_error_code(self) -> str:
        return "SF_CONFIG_ERROR"


class InvalidConfigValueError(UserError):
    """Error for invalid configuration values (generic)."""

    def __init__(
        self,
        message: str,
        config_key: str,
        provided_value: Any,
        valid_values: Optional[Set[str]] = None,
        config_domain: str = "config",
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        """Initialize invalid config value error.

        Args:
            message: Error message
            config_key: The configuration key that failed
            provided_value: The invalid value that was provided
            valid_values: Set of valid values (if applicable)
            config_domain: Configuration domain (logging, driver, browser, etc.)
            error_code: Error code
            context: Context information
            cause: Underlying cause
        """
        # Compute error code if not provided
        if error_code is None:
            error_code = f"SF_INVALID_{config_domain.upper()}_VALUE"

        # Auto-generate suggestion based on valid values
        suggestion = None
        if valid_values:
            valid_list = ", ".join(sorted(valid_values))
            suggestion = f"Use one of: {valid_list}"

        super().__init__(message, error_code, context, cause, suggestion)
        self.config_key = config_key
        self.provided_value = provided_value
        self.valid_values = valid_values or set()
        self.config_domain = config_domain

    def _get_default_error_code(self) -> str:
        return f"SF_INVALID_{getattr(self, 'config_domain', 'CONFIG').upper()}_VALUE"


class MissingConfigError(UserError):
    """Error for required configuration that is missing."""

    def __init__(
        self,
        message: str,
        config_key: str,
        config_domain: str = "config",
        environment_variable: Optional[str] = None,
        config_file: Optional[str] = None,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        """Initialize missing config error.

        Args:
            message: Error message
            config_key: The missing configuration key
            config_domain: Configuration domain
            environment_variable: Environment variable name (if applicable)
            config_file: Config file path (if applicable)
            error_code: Error code
            context: Context information
            cause: Underlying cause
        """
        # Compute error_code if not provided
        if error_code is None:
            error_code = f"SF_MISSING_{config_domain.upper()}_CONFIG"

        # Auto-generate suggestion
        suggestions = []
        if environment_variable:
            suggestions.append(f"Set environment variable: {environment_variable}")
        if config_file:
            suggestions.append(f"Add to config file: {config_file}")

        suggestion = " OR ".join(suggestions) if suggestions else None

        super().__init__(message, error_code, context, cause, suggestion)
        self.config_key = config_key
        self.config_domain = config_domain
        self.environment_variable = environment_variable
        self.config_file = config_file

    def _get_default_error_code(self) -> str:
        return f"SF_MISSING_{getattr(self, 'config_domain', 'CONFIG').upper()}_CONFIG"


class ConfigValidationError(ConfigurationError):
    """Error during configuration validation (generic)."""

    def __init__(
        self,
        message: str,
        config_domain: str = "config",
        validation_errors: Optional[Dict[str, str]] = None,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        """Initialize config validation error.

        Args:
            message: Error message
            config_domain: Configuration domain
            validation_errors: Dictionary of field -> error message
            error_code: Error code
            context: Context information
            cause: Underlying cause
        """
        # Compute error_code if not provided
        if error_code is None:
            error_code = f"SF_{config_domain.upper()}_VALIDATION_ERROR"

        super().__init__(message, error_code, context, cause)
        self.config_domain = config_domain
        self.validation_errors = validation_errors or {}

    def _get_default_error_code(self) -> str:
        return f"SF_{getattr(self, 'config_domain', 'CONFIG').upper()}_VALIDATION_ERROR"

    def add_validation_error(self, field: str, error: str) -> None:
        """Add a validation error for a specific field."""
        self.validation_errors[field] = error

    def __str__(self) -> str:
        """String representation with validation details."""
        base_str = super().__str__()

        if self.validation_errors:
            errors = [
                f"{field}: {error}" for field, error in self.validation_errors.items()
            ]
            base_str += f" | Validation errors: {'; '.join(errors)}"

        return base_str


class DirectoryAccessError(RetryableError):
    """Error related to directory access/creation (generic)."""

    def __init__(
        self,
        message: str,
        directory_path: str,
        operation: str,
        config_domain: str = "config",
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        """Initialize directory access error.

        Args:
            message: Error message
            directory_path: Path to the problematic directory
            operation: Operation that failed (create, write, read, etc.)
            config_domain: Configuration domain
            error_code: Error code
            context: Context information
            cause: Underlying cause
        """
        # Compute error_code if not provided
        if error_code is None:
            error_code = f"SF_{config_domain.upper()}_DIRECTORY_ERROR"

        super().__init__(
            message, error_code, context, cause, max_retries=3, retry_delay=1.0
        )
        self.directory_path = directory_path
        self.operation = operation
        self.config_domain = config_domain

    def _get_default_error_code(self) -> str:
        return f"SF_{getattr(self, 'config_domain', 'CONFIG').upper()}_DIRECTORY_ERROR"


class FileAccessError(RetryableError):
    """Error related to file operations (generic)."""

    def __init__(
        self,
        message: str,
        file_path: str,
        operation: str,
        config_domain: str = "config",
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        """Initialize file access error.

        Args:
            message: Error message
            file_path: Path to the problematic file
            operation: Operation that failed (open, write, read, etc.)
            config_domain: Configuration domain
            error_code: Error code
            context: Context information
            cause: Underlying cause
        """
        if error_code is None:
            error_code = f"SF_{config_domain.upper()}_FILE_ERROR"

        super().__init__(
            message, error_code, context, cause, max_retries=2, retry_delay=0.5
        )
        self.file_path = file_path
        self.operation = operation
        self.config_domain = config_domain

    def _get_default_error_code(self) -> str:
        return f"SF_{getattr(self, 'config_domain', 'CONFIG').upper()}_FILE_ERROR"


class NetworkConfigError(RetryableError):
    """Error related to network configuration."""

    def __init__(
        self,
        message: str,
        url: Optional[str] = None,
        timeout: Optional[float] = None,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        """Initialize network config error.

        Args:
            message: Error message
            url: URL that failed
            timeout: Timeout value used
            error_code: Error code
            context: Context information
            cause: Underlying cause
        """
        super().__init__(
            message, error_code, context, cause, max_retries=3, retry_delay=2.0
        )
        self.url = url
        self.timeout = timeout

    def _get_default_error_code(self) -> str:
        return "SF_NETWORK_CONFIG_ERROR"


# ================================================================
# Factory functions for common scenarios
# ================================================================


def directory_access_error(
    directory_path: str, operation: str, cause: Exception, domain: str = "config"
) -> DirectoryAccessError:
    """Create generic directory access error."""
    return DirectoryAccessError(
        message=f"Cannot {operation} directory: {directory_path}",
        directory_path=directory_path,
        operation=operation,
        config_domain=domain,
        cause=cause,
    )


def file_access_error(
    file_path: str, operation: str, cause: Exception, domain: str = "config"
) -> FileAccessError:
    """Create generic file access error."""
    return FileAccessError(
        message=f"Cannot {operation} file: {file_path}",
        file_path=file_path,
        operation=operation,
        config_domain=domain,
        cause=cause,
    )
