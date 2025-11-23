"""
Selenium Forge - WebDriver Toolkit

A comprehensive Selenium automation framework with automatic driver management,
cross-platform support, stealth capabilities, and enterprise-grade features.

Quick Start:
    from selenium_forge import SeleniumForge

    # Simple usage
    forge = SeleniumForge(browser="chrome")
    driver = forge.create_driver()
    driver.get("https://example.com")
    driver.quit()

    # With stealth mode
    forge = SeleniumForge(browser="chrome", stealth=True, headless=True)
    driver = forge.create_driver()

    # Context manager
    with SeleniumForge(browser="firefox") as forge:
        driver = forge.create_driver()
        driver.get("https://example.com")

    # From configuration file
    forge = SeleniumForge.from_config("config.yaml")
    driver = forge.create_driver()
"""

__version__ = "0.1.0"
__author__ = "Abdessamad Haddouche"
__email__ = "abdessamad.hadd@gmail.com"


# Package metadata
__title__ = "selenium-forge"
__description__ = "Selenium WebDriver toolkit with automatic setup, stealth mode, and cross-platform support"
__url__ = "https://github.com/abdessamad-haddouche/selenium-forge"
__license__ = "MIT"


# Main API
from selenium_forge.forge import SeleniumForge

# Configuration
from selenium_forge.config import ConfigLoader, DefaultConfigs

# Core types
from selenium_forge.core.types import (
    BrowserOptions,
    DriverConfig,
    ProxyConfig,
    StealthConfig,
    SystemInfo,
)

# Session management
from selenium_forge.session import ForgeContext, SessionManager

# Driver management
from selenium_forge.drivers import DriverFactory, DriverManager

# Stealth and proxy
from selenium_forge.proxy import ProxyManager, ProxyRotator
from selenium_forge.stealth import StealthEngine

# Exceptions
from selenium_forge.exceptions import (
    CriticalError,
    DeprecationError,
    InternalError,
    RetryableError,
    SeleniumForgeError,
    UserError,
)

# Platform utilities
from selenium_forge.core.platform import PlatformDetector

__all__ = [
    # Main API
    "SeleniumForge",
    # Configuration
    "ConfigLoader",
    "DefaultConfigs",
    # Types
    "BrowserOptions",
    "DriverConfig",
    "ProxyConfig",
    "StealthConfig",
    "SystemInfo",
    # Session management
    "ForgeContext",
    "SessionManager",
    # Driver management
    "DriverFactory",
    "DriverManager",
    # Stealth and proxy
    "ProxyManager",
    "ProxyRotator",
    "StealthEngine",
    # Exceptions
    "SeleniumForgeError",
    "UserError",
    "RetryableError",
    "CriticalError",
    "InternalError",
    "DeprecationError",
    # Platform
    "PlatformDetector",
    # Metadata
    "__version__",
    "__author__",
    "__email__",
]