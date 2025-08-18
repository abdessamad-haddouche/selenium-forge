"""Base exception classes for selenium-forge."""

from __future__ import annotations

import traceback
from typing import Any, Dict, List, Optional

# ================================================================
# Base Exception Error Classes
# ================================================================


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
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self._get_default_error_code()
        self.context = context or {}
        self.cause = cause

        # Store traceback information
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
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "context": self.context,
            "cause": str(self.cause) if self.cause else None,
            "traceback": self.traceback_str,
        }

    def add_context(self, key: str, value: Any) -> SeleniumForgeError:
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

        if self.cause:
            parts.append(f"Caused by: {self.cause}")

        return " | ".join(parts)

    def __repr__(self) -> str:
        """Detailed representation of the exception.

        Basic usage:
                error = SeleniumForgeError(
                    message="Element not found",
                    error_code="ELEMENT_MISSING",
                    context={"page": "login.html"},
                    cause=NoSuchElementException("id: login-btn")
                )
            repr(error)
        """
        return (
            f"{self.__class__.__name__}("
            f"message='{self.message}', "
            f"error_code='{self.error_code}', "
            f"context={self.context}, "
            f"cause={self.cause!r})"
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
        """
        super().__init__(message)
        self.message = message
        self.warning_code = warning_code or self._get_default_warning_code()
        self.context = context or {}

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
        return "SF_USER_ERROR"

    def __str__(self) -> str:
        """String representation with suggestion."""
        base_str = super().__str__()
        if self.suggestion:
            base_str += f" | Suggestion: {self.suggestion}"
        return base_str


class InternalError(SeleniumForgeError):
    """Internal error indicating a bug in selenium-forge.

    Used for errors that should never happen and indicate bugs in the library itself.
    """

    def _get_default_error_code(self) -> str:
        return "SF_INTERNAL_ERROR"


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


# ================================================================
# Utility functions for exception handling
# ================================================================


def create_error_context(**kwargs: Any) -> Dict[str, Any]:
    """Create a standardized error context dictionary.

    Args:
        **kwargs: Context key-value pairs

    Returns:
        Standardized context dictionary

    Example:
        try:
            element = driver.find_element(By.ID, "unreliable-task")
        except NoSuchElementException as e:
            context = create_error_context(
                page_url=driver.current_url,
                page_source=driver.page_source[:500] + "...",  # First 500 chars
                cookies=driver.get_cookies(),
                screenshots=[screenshot1, screenshot2],  # PIL Image objects
                js_errors=get_console_errors(driver),  # Custom function
                timestamp=datetime.now(),
                debug_level="critical"
            )
            raise SomeError("Where'd it go?", context=context)

        Returns context with all complex objects forced to strings.

    """

    context: Dict[str, Any] = {}

    for key, value in kwargs.items():
        # If the value is a user-defined object (has __dict__), convert it to a str
        if hasattr(value, "__dict__"):
            context[key] = str(value)
        elif isinstance(value, (list, tuple, set)):
            context[key] = [str(item) for item in value]
        elif isinstance(value, dict):
            context[key] = {k: str(v) for k, v in value.items()}
        else:
            context[key] = value

    return context


def format_exception_chain(exc: Exception) -> str:
    """Format an exception chain for logging.

    When exceptions are chained together (one exception causes another), this function
    traverses the entire chain and formats it into a readable string showing the
    progression from the final exception back to the root cause.

    Args:
        exc: The exception to format (typically the outermost/final exception)

    Returns:
        Formatted exception chain string with " -> " separating each level

    Example:
        try:
            driver.find_element(By.ID, "missing-button").click()
        except NoSuchElementException as selenium_exc:
            element_error = ElementNotFoundError(
                "Button not found",
                cause=selenium_exc
            )
            critical_error = CriticalError(
                "Login failed",
                cause=element_error
            )

            # Use format_exception_chain to see the full story
            chain = format_exception_chain(critical_error)
            logger.error(f"Error: {chain}")

            # Output:
            # [SF_CRITICAL_ERROR] Login failed ->
            # [SF_ELEMENT_NOT_FOUND] Button not found ->
            # NoSuchElementException: Unable to locate element
    """

    parts: List[str] = []
    current: Optional[Exception] = exc

    while current:
        if isinstance(current, SeleniumForgeError):
            parts.append(str(current))
        else:
            parts.append(f"{current.__class__.__name__}: {current}")

        # Process current exception
        current = getattr(current, "__cause__", None)  # Move to the cause (or None)

    return " -> ".join(parts)


def wrap_exception(
    location: str,
    original_exc: Exception,
    error_type: type[SeleniumForgeError] = SeleniumForgeError,
    **context: Any,
) -> SeleniumForgeError:
    """Wrap a non-selenium-forge exception into a selenium-forge exception.

    Args:
        location: Where the error occurred (function, method, property, etc.)
        original_exc: The original exception that was caught
        error_type: Type of selenium-forge exception to create
        **context: Additional context information

    Example:
        # In a method
        def click_element(self, selector: str):
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                element.click()
            except NoSuchElementException as e:
                raise wrap_exception(
                    location="WebDriver.click_element",  # Class.method
                    original_exc=e,
                    error_type=ElementNotFoundError,
                    selector=selector
                )

        # In a function
        def setup_driver():
            try:
                return webdriver.Chrome()
            except WebDriverException as e:
                raise wrap_exception(
                    location="setup_driver",  # Just function name
                    original_exc=e,
                    error_type=RetryableError
                )

        # In a property
        @property
        def current_url(self):
            try:
                return self.driver.current_url
            except WebDriverException as e:
                raise wrap_exception(
                    location="WebDriver.current_url",  # Class.property
                    original_exc=e
                )
    """
    message = f"Error in {location}: {original_exc}"
    error_context = create_error_context(
        location=location,  # Changed from function to location
        original_exception_type=original_exc.__class__.__name__,
        **context,
    )

    return error_type(message=message, context=error_context, cause=original_exc)
