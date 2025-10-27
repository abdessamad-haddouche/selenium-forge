"""Base exception classes for selenium-forge."""

from __future__ import annotations

import traceback
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, TypeVar

# ================================================================
# Base Classes
# ================================================================

T = TypeVar("T", bound="SeleniumForgeError")

class SeleniumForgeError(Exception):
    """Base exception for all selenium-forge errors.

    This is the root exception that all other selenium-forge exceptions inherit
    from. It provides common functionality like error codes, context information,
    and structured error reporting.
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        """
        Initialize the base exception.

        Args:
            message: Human-readable error message
            error_code: Unique error code for programmatic handling
            context: Additional context information for debugging
            cause: The underlying exception that caused this error
            timestamp: The time when the error occurred
            traceback_str: Formatted traceback of the cause exception
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self._get_default_error_code()
        self.context = context or {}
        self.cause = cause
        self.timestamp = datetime.now(timezone.utc)
        self.traceback_str = traceback.format_exc() if cause else None

    def _get_default_error_code(self) -> str:
        """Get the default error code for this exception type."""
        return f"SF_{self.__class__.__name__.upper()}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for structured logging/reporting.

        Returns:
            Dictionary representation of the exception
        """
        return {
            "message": self.message,
            "error_code": self.error_code,
            "error_type": self.__class__.__name__,
            "context": self.context,
            "cause": str(self.cause) if self.cause else None,
            "traceback": self.traceback_str,
            "timestamp": self.timestamp.isoformat(), 
        }
    
    def add_context(self: T, key: str, value: Any) -> T:
        """Add context information to the exception.

        Args:
            key: Context key
            value: Context value

        Returns:
            Self for method chaining

        Examples:
            Basic usage:
                error = SeleniumForgeError("Failed")
                error.add_context("retry_count", 3)

            Method chaining:
                (SeleniumForgeError("Browser crashed")
                    .add_context("url", "https://example.com")
                    .add_context("browser", "Chrome"))
        """
        self.context[key] = value
        return self
    
    def __str__(self) -> str:
        """String representation of the exception."""
        parts = [f"[{self.error_code}] {self.message}"]

        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            parts.append(f"Context: {context_str}")

        return " | ".join(parts)
    
    def __repr__(self) -> str:
        """Detailed representation of the exception."""
        return (
            f"{self.__class__.__name__}("
            f"message='{self.message}', "
            f"error_code='{self.error_code}', "
            f"context={self.context}, "
            f"cause={self.cause!r})" # !r = repr(), shows type + value
        )


class SeleniumForgeWarning(UserWarning):
    """Base warning class for selenium-forge warnings.

    Used for non-fatal issues that users should be aware of.
    """
    
    def __init__(
        self,
        message: str,
        warning_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the warning.

        Args:
            message: Warning message
            warning_code: Unique warning code
            context: Additional context information
            timestamp: The time when the warning occurred
        """
        super().__init__(message)
        self.message = message
        self.warning_code = warning_code or self._get_default_warning_code()
        self.context = context or {}
        self.timestamp = datetime.now(timezone.utc)

    def _get_default_warning_code(self) -> str:
        """Get the default warning code for this warning type."""
        return f"SF_WARNING_{self.__class__.__name__.upper()}"
    
    def __str__(self) -> str:
        """String representation of the warning."""
        parts = [f"[{self.warning_code}] {self.message}"]

        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            parts.append(f"Context: {context_str}")

        return " | ".join(parts)


# ================================================================
# Core Exception Categories
# ================================================================


class CriticalError(SeleniumForgeError):
    """Critical error that should stop execution immediately.

    Used for errors that indicate fundamental problems that cannot be recovered from.
    """
    
    def _get_default_error_code(self) -> str:
        return "SF_CRITICAL_ERROR"


class RetryableError(SeleniumForgeError):
    """Error that might be resolved by retrying the operation.

    Used for transient errors like network issues, temporary file locks, etc.
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ) -> None:
        """Initialize retryable error.

        Args:
            message: Error message
            error_code: Error code
            context: Context information
            cause: Underlying cause
            max_retries: Maximum number of retries suggested
            retry_delay: Suggested delay between retries (seconds)
        """
        super().__init__(message, error_code, context, cause)
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def _get_default_error_code(self) -> str:
        return "SF_RETRYABLE_ERROR"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict with retry information."""
        data = super().to_dict()
        data.update({
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
        })

        return data


class UserError(SeleniumForgeError):
    """Error caused by incorrect user input or configuration.

    Used for errors that are the user's responsibility to fix.
    """
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
        suggestion: Optional[str] = None,
    ) -> None:
        """Initialize user error.

        Args:
            message: Error message
            error_code: Error code
            context: Context information
            cause: Underlying cause
            suggestion: Suggested fix for the user
        """
        super().__init__(message, error_code, context, cause)
        self.suggestion = suggestion

    def _get_default_error_code(self) -> str:
        """Get default error code for user errors."""
        return "SF_USER_ERROR"
    
    def __str__(self) -> str:
        """String representation with suggestions."""
        base_str = super().__str__()
        if self.suggestion:
            base_str += f" | Suggestion: {self.suggestion}"
        
        return base_str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict with suggestion."""
        data = super().to_dict()
        if self.suggestion:
            data["suggestion"] = self.suggestion
        
        return data


class InternalError(SeleniumForgeError):
    """Internal error indicating a bug in selenium-forge.

    Used for errors that should never happen and indicate bugs in the library itself.
    """

    def _get_default_error_code(self) -> str:
        return "SF_INTERNAL_ERROR"

 
# ================================================================
# Lifecycle and Development Errors
# ================================================================


class DeprecationError(SeleniumForgeError):
    """Error indicating use of deprecated functionality.

    Used when deprecated features are used and strict mode is enabled.
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
        deprecated_in: Optional[str] = None,
        removed_in: Optional[str] = None,
        alternative: Optional[str] = None,
    ) -> None:
        """Initialize deprecation error.

        Args:
            message: Error message
            error_code: Error code
            context: Context information
            cause: Underlying cause
            deprecated_in: Version when feature was deprecated
            removed_in: Version when feature will be removed
            alternative: Suggested alternative
        """
        super().__init__(message, error_code, context, cause)
        self.deprecated_in = deprecated_in
        self.removed_in = removed_in
        self.alternative = alternative

    def _get_default_error_code(self) -> str:
        return "SF_DEPRECATION_ERROR"
    
    def __str__(self) -> str:
        """String representation with deprecation info."""
        parts = [super().__str__()]

        if self.deprecated_in:
            parts.append(f"Deprecated in: {self.deprecated_in}")

        if self.removed_in:
            parts.append(f"Will be removed in: {self.removed_in}")

        if self.alternative:
            parts.append(f"Use instead: {self.alternative}")

        return " | ".join(parts)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict with deprecation info."""
        data = super().to_dict()
        data.update({
            "deprecated_in": self.deprecated_in,
            "removed_in": self.removed_in,
            "alternative": self.alternative,
        })
        return data