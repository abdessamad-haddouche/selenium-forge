"""
Exception handling for selenium-forge
"""

from typing import Optional, Dict, Any, List
from enum import Enum


class ErrorCode(Enum):
    """Error codes for selenium-forge exceptions"""
    # Driver related errors
    DRIVER_INSTALL_FAILED = "DRIVER_001"
    DRIVER_NOT_FOUND = "DRIVER_002"

    # Configuration errors
    CONFIG_INVALID = "CONFIG_001"
    CONFIG_TEMPLATE_NOT_FOUND = "CONFIG_002"
    CONFIG_VALIDATION_FAILED = "CONFIG_003"
    CONFIG_FILE_NOT_FOUND = "CONFIG_004"


class SeleniumForgeError(Exception):
    """
    Base exception for selenium-forge with rich error information
    
    Args:
        message: Human-readable error message
        error_code: Unique error code for programmatic handling
        details: Additional error context
        suggestions: List of suggested solutions
        docs_url: URL to relevant documentation
    """
    def __init__(
        self,
        message: str,
        error_code: Optional[ErrorCode] = None,
        details: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None,
        docs_url: Optional[str] = None,
        original_exception: Optional[Exception] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.suggestions = suggestions or []
        self.docs_url = docs_url
        self.original_exception = original_exception

        super().__init__(self.message)
    
    def __str__(self) -> str:
        """Rich string representation"""
        lines = [f"SeleniumForgeError: {self.message}"]

        if self.error_code:
            lines.append(f"Error Code: {self.error_code.value}")

        if self.details:
            lines.append("Details:")
            for key, value in self.details.items():
                lines.append(f"  {key}: {value}")
        
        if self.suggestions:
            lines.append("Suggestions:")
            for suggestion in self.suggestions:
                lines.append(f"  • {suggestion}")
        
        if self.docs_url:
            lines.append(f"Documentation: {self.docs_url}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/API responses"""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "error_message": self.error_code.value if self.error_code else None,
            "details": self.details,
            "suggestions": self.suggestions,
            "docs_url": self.docs_url
        }


class DriverInstallError(SeleniumForgeError):
    """Raised when WebDriver cannot be installed"""
    pass


class DriverNotFoundError(SeleniumForgeError):
    """Raised when WebDriver cannot be found"""
    pass


class InvalidConfigError(SeleniumForgeError):
    """Raised when the configuration contains invalid values"""
    pass


class ConfigTemplateNoteFoundError(SeleniumForgeError):
    """Raised when the expected configuration template file is missing"""
    pass


class ConfigValidationError(SeleniumForgeError):
    """Raised when config schema or rules are not met"""
    pass


if __name__ == "__main__":
    error = SeleniumForgeError(
        message="Failed to install the web driver due to timeout",
        error_code=ErrorCode.DRIVER_INSTALL_FAILED,
        details={
            "os": "Linux",
            "driver": "chromedriver",
            "timeout": "30s",
            "attempts": 3
        },
        suggestions=[
            "Verify internet connectivity",
            "Try running the installer with elevated permissions",
            "Use the manual driver installation guide"
        ],
        docs_url="https://docs.seleniumforge.dev/driver-installation",
        original_exception=TimeoutError("Connection to the download server timed out")
    )

    print(error.to_dict())
