"""Core module for platform detection and system utilities."""

from selenium_forge.core.constants import (
    BrowserType,
    DriverPaths,
    OperatingSystem,
    Architecture,
    DEFAULT_TIMEOUT,
    DEFAULT_PAGE_LOAD_TIMEOUT,
    DEFAULT_SCRIPT_TIMEOUT,
)
from selenium_forge.core.platform import PlatformDetector, SystemInfo
from selenium_forge.core.types import (
    BrowserOptions,
    ProxyConfig,
    StealthConfig,
    DriverConfig,
)

__all__ = [
    # Constants
    "BrowserType",
    "DriverPaths",
    "OperatingSystem",
    "Architecture",
    "DEFAULT_TIMEOUT",
    "DEFAULT_PAGE_LOAD_TIMEOUT",
    "DEFAULT_SCRIPT_TIMEOUT",
    # Platform
    "PlatformDetector",
    "SystemInfo",
    # Types
    "BrowserOptions",
    "ProxyConfig",
    "StealthConfig",
    "DriverConfig",
]
