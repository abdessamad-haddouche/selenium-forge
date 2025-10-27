"""Exception handling utilities for selenium-forge."""

from __future__ import annotations

import inspect
from typing import Any, Dict, List, Optional
from pathlib import Path

from .base import SeleniumForgeError, CriticalError, UserError, RetryableError


# ================================================================
# Context and Data Processing Utilities
# ================================================================


def create_error_context(**kwargs: Any) -> Dict[str, Any]:
    """Create a standardized error context dictionary.

    Args:
        **kwargs: Context key-value pairs

    Returns:
        Standardized context dictionary

    Example:
        context = create_error_context(
            page_url=driver.current_url,
            element_selector="#login-btn",
            retry_count=3,
            browser_name="chrome"
        )
    """
    context: Dict[str, Any] = {}

    for key, value in kwargs.items():
        # Handle Path objects by converting to string
        if isinstance(value, Path):
            context[key] = str(value)
        # Handle complex custom objects by converting them to strings
        elif hasattr(value, "__dict__") and not isinstance(value, (str, int, float, bool)):
            context[key] = str(value)
        # Handle lists, tuples, and sets by converting complex items inside to strings
        elif isinstance(value, (list, tuple, set)):
            context[key] = [
                str(item) if hasattr(item, "__dict__") and not isinstance(item, (str, int, float, bool))
                else item
                for item in value
            ]
        # Handle dictionaries by converting complex values to strings
        elif isinstance(value, dict):
            context[key] = {
                k: str(v) if hasattr(v, "__dict__") and not isinstance(v, (str, int, float, bool))
                else v
                for k, v in value.items()
            }
        # Handle simple types directly
        else:
            context[key] = value

    return context


# ================================================================
# Exception Chain Analysis and Formatting
# ================================================================


def format_exception_chain(exc: Exception) -> str:
    """Format an exception chain for logging and debugging.
    
    This function traverses the complete chain of exceptions that led to an error,
    showing the progression from the final exception back to the root cause.
    Python exceptions can be chained together using __cause__ (explicit chaining)
    or __context__ (implicit chaining), and this function follows both types.
    
    Args:
        exc: The exception to format (typically the outermost/final exception)
        
    Returns:
        Formatted string showing the complete exception chain with " -> " 
        separating each level, from final exception to root cause
        
    Example:
        try:
            # Original selenium error
            driver.find_element(By.ID, "missing-button").click()
        except NoSuchElementException as selenium_exc:
            # Wrap in custom exception
            element_error = ElementNotFoundError(
                "Login button not found",
                cause=selenium_exc
            )
            element_error.__cause__ = selenium_exc  # Set Python's chaining
            
            try:
                raise element_error
            except ElementNotFoundError as elem_exc:
                # Another layer of wrapping
                critical_error = CriticalError(
                    "Authentication failed", 
                    cause=elem_exc
                )
                critical_error.__cause__ = elem_exc
                
                # Format the complete chain
                chain = format_exception_chain(critical_error)
                print(chain)
                
                # Output:
                # [SF_CRITICAL_ERROR] Authentication failed -> 
                # [SF_ELEMENT_NOT_FOUND] Login button not found -> 
                # NoSuchElementException: Unable to locate element: {"method":"id","selector":"missing-button"}
    """
    parts: List[str] = []
    current: Optional[Exception] = exc

    # Traverse the exception chain backwards from final exception to root cause
    while current:
        if isinstance(current, SeleniumForgeError):
            # Use our custom __str__ method for formatting with error codes
            parts.append(str(current))
        else:
            # Format standard Python exceptions with class name and message
            parts.append(f"{current.__class__.__name__}: {current}")
        
        # Move to the next exception in the chain
        current = getattr(current, "__cause__", None) or getattr(current, "__context__", None)

    return " -> ".join(parts)


def wrap_exception(
    location: str,
    original_exc: Exception,
    error_type: type[SeleniumForgeError] = SeleniumForgeError,
    **context: Any,
) -> SeleniumForgeError:
    """Wrap a non-selenium-forge exception into a selenium-forge exception.
    
    This function converts low-level Python exceptions (like FileNotFoundError, 
    ConnectionError) into domain-specific Selenium Forge exceptions while preserving
    the original error information through exception chaining.
    
    Args:
        location: Where the error occurred (function name, method, operation)
        original_exc: The original exception that was caught
        error_type: Type of selenium-forge exception to create (defaults to base SeleniumForgeError)
        **context: Additional context information for debugging (browser, url, retry_count, etc.)
        
    Returns:
        Wrapped SeleniumForgeError with proper chaining to original exception
    
        Example:
        def download_chromedriver():
            try:
                response = requests.get("https://chromedriver.storage.googleapis.com/LATEST_RELEASE")
                return response.text
            except requests.ConnectionError as e:
                # Wrap low-level network error into domain-specific error
                raise wrap_exception(
                    location="download_chromedriver",
                    original_exc=e,
                    error_type=DriverInstallationError,
                    browser="chrome",
                    url="https://chromedriver.storage.googleapis.com/LATEST_RELEASE",
                    retry_count=0
                )
                
        # Usage result:
        try:
            download_chromedriver()
        except DriverInstallationError as e:
            print(str(e))
            # Output: [SF_DRIVER_INSTALLATION_ERROR] Error in download_chromedriver: HTTPSConnectionPool(host='chromedriver.storage.googleapis.com', port=443)
            
            print(format_exception_chain(e))
            # Output: [SF_DRIVER_INSTALLATION_ERROR] Error in download_chromedriver: Connection failed -> 
            #         ConnectionError: HTTPSConnectionPool(host='chromedriver.storage.googleapis.com', port=443)
    """
    message = f"Error in {location}: {original_exc}"
    
    error_context = create_error_context(
        location=location,
        original_exception_type=original_exc.__class__.__name__,
        **context,
    )

    # Create the wrapped exception
    wrapped = error_type(message=message, context=error_context, cause=original_exc)
    
    # Set up explicit exception chaining
    wrapped.__cause__ = original_exc
    
    return wrapped


# ================================================================
# Introspection and Documentation Utilities
# ================================================================


def get_exception_hierarchy() -> Dict[str, List[str]]:
    """Get the exception hierarchy for documentation and debugging.
    
    This function uses Python's introspection capabilities to analyze all exception
    classes defined in the current module and map out their inheritance relationships.
    It's useful for generating documentation, understanding the exception structure,
    and debugging inheritance issues in the exception system.
    
    Returns:
        Dictionary mapping exception class names to lists of their direct base class names.
        Only includes classes that inherit from Exception (excludes the base Exception class itself).
    
    Example:
        # Get the complete exception hierarchy
        hierarchy = get_exception_hierarchy()
        
        # Print the hierarchy in a readable format
        for exception_name, base_classes in hierarchy.items():
            print(f"{exception_name} inherits from: {', '.join(base_classes)}")
            
        # Output might look like:
        # SeleniumForgeError inherits from: Exception
        # CriticalError inherits from: SeleniumForgeError
        # RetryableError inherits from: SeleniumForgeError
        # UserError inherits from: SeleniumForgeError
        # BrowserError inherits from: SeleniumForgeError
        # DriverError inherits from: BrowserError
        # ElementNotFoundError inherits from: BrowserError
    """
    import inspect

    hierarchy = {}

    # Get the current module where SeleniumForgeError is defined
    current_module = inspect.getmodule(SeleniumForgeError)
    if current_module:
        # Inspect all classes in this module
        for name, obj in inspect.getmembers(current_module, inspect.isclass):
            # Only include classes that inherit from Exception (but not Exception itself)
            if issubclass(obj, Exception) and obj != Exception:
                # Get the direct base classes that are also exceptions
                bases = [base.__name__ for base in obj.__bases__ if issubclass(base, Exception)]
                hierarchy[name] = bases
    
    return hierarchy


# ================================================================
# Exception Creation Helpers
# ================================================================

            
def critical_error(message: str, **context: Any) -> CriticalError:
    """Quick helper to create critical errors with standarized context.

    Args:
        message: Human-readable error message describing the critical failure
        **context: Additional context information for debugging (browser, platform, operation, etc.)
        
    Returns:
        CriticalError instance with standardized context and error code
    
    Example:
        # System-level failure
        if not os.path.exists("/usr/bin"):
            raise critical_error(
                "System directory missing",
                platform="linux",
                directory="/usr/bin",
                operation="browser_detection"
            )
    """
    return CriticalError(message, context=create_error_context(**context))


def user_error(
    message: str,
    suggestion: Optional[str] = None,
    **context: Any
) -> UserError:
    """Quick helper to create user errors with suggestions and standardized context.
    
    Args:
        message: Human-readable error message describing what the user did wrong
        suggestion: Optional helpful suggestion for how to fix the problem
        **context: Additional context information for debugging (invalid_value, expected_format, etc.)
        
    Returns:
        UserError instance with suggestion and standardized context

    Example:
        # Invalid configuration value
        if browser not in ["chrome", "firefox", "edge", "safari"]:
            raise user_error(
                f"Unsupported browser: '{browser}'",
                suggestion="Use one of: chrome, firefox, edge, safari",
                provided_browser=browser,
                valid_browsers=["chrome", "firefox", "edge", "safari"],
                config_section="browser.default"
            )
    """
    return UserError(message, suggestion=suggestion, context=create_error_context(**context))


def retryable_error(
    message: str, 
    max_retries: int = 3, 
    retry_delay: float = 1.0,
    **context: Any
) -> RetryableError:
    """Quick helper to create retryable errors with retry configuration and standarized context.
    
    Args:
        message: Human-readable error message describing the transient failure
        max_retries: Maximum number of retries suggested for this error (default: 3)
        retry_delay: Suggested delay between retries in seconds (default: 1.0)
        **context: Additional context information for debugging (url, timeout, attempt_number, etc.)
        
    Returns:
        RetryableError instance with retry parameters and standardized context
    Example:
        # Network connectivity issues
        try:
            response = requests.get(download_url, timeout=30)
        except requests.Timeout as e:
            raise retryable_error(
                f"Download timeout after 30 seconds",
                max_retries=5,
                retry_delay=2.0,
                url=download_url,
                timeout_duration=30,
                attempt_number=current_attempt,
                network_status="timeout"
            )
    """
    return RetryableError(
        message, 
        max_retries=max_retries,
        retry_delay=retry_delay,
        context=create_error_context(**context)
    )
