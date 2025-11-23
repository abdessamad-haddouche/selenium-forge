"""Main SeleniumForge API."""

from __future__ import annotations

from pathlib import Path
from types import TracebackType
from typing import Any, Dict, Optional, Type

from selenium.webdriver.remote.webdriver import WebDriver

from selenium_forge.config.defaults import DefaultConfigs
from selenium_forge.config.loader import ConfigLoader
from selenium_forge.core.constants import BrowserType
from selenium_forge.core.platform import PlatformDetector
from selenium_forge.core.types import (
    BrowserOptions,
    DriverConfig,
    ProxyConfig,
    StealthConfig,
    SystemInfo,
)
from selenium_forge.drivers.factory import DriverFactory
from selenium_forge.drivers.manager import DriverManager
from selenium_forge.exceptions import UserError
from selenium_forge.session.manager import SessionManager
from selenium_forge.stealth.engine import StealthEngine


class SeleniumForge:
    """Main API class for Selenium Forge.

    This is the primary interface for creating and managing WebDriver instances
    with automatic configuration, stealth mode, and cross-platform support.

    Example:
        # Simple usage
        forge = SeleniumForge(browser="chrome")
        driver = forge.create_driver()

        # Advanced usage
        forge = SeleniumForge(
            browser="chrome",
            headless=True,
            stealth=True,
            proxy="http://proxy.example.com:8080"
        )
        driver = forge.create_driver()

        # Context manager
        with SeleniumForge(browser="firefox") as forge:
            driver = forge.create_driver()
            driver.get("https://example.com")
    """

    def __init__(
        self,
        browser: str = "chrome",
        headless: bool = False,
        stealth: bool = False,
        proxy: Optional[str] = None,
        config_file: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize Selenium Forge.

        Args:
            browser: Browser type (chrome, firefox, edge, safari)
            headless: Run in headless mode
            stealth: Enable stealth mode
            proxy: Proxy URL (e.g., "http://host:port")
            config_file: Path to configuration file
            **kwargs: Additional configuration options

        Raises:
            UserError: If configuration is invalid
        """
        self.browser = browser
        self.driver_manager = DriverManager()
        self.driver_factory = DriverFactory(self.driver_manager)
        self.session_manager = SessionManager()

        # Build configuration
        self.config = self._build_config(
            browser=browser,
            headless=headless,
            stealth=stealth,
            proxy=proxy,
            config_file=config_file,
            **kwargs,
        )

    def _build_config(
        self,
        browser: str,
        headless: bool,
        stealth: bool,
        proxy: Optional[str],
        config_file: Optional[str],
        **kwargs: Any,
    ) -> DriverConfig:
        """Build driver configuration from parameters.

        Args:
            browser: Browser type
            headless: Headless mode
            stealth: Stealth mode
            proxy: Proxy URL
            config_file: Config file path
            **kwargs: Additional options

        Returns:
            DriverConfig object
        """
        # Start with defaults for browser
        config_dict = DefaultConfigs.get_browser_defaults(browser)

        # Load config file if provided
        if config_file:
            user_config = ConfigLoader.load_yaml(Path(config_file))
            config_dict = ConfigLoader.merge_configs(config_dict, user_config)

        # Apply runtime overrides
        overrides: Dict[str, Any] = {"browser": browser}

        # Browser options overrides
        browser_options: Dict[str, Any] = {}
        if headless:
            browser_options["headless"] = True
        if "window_size" in kwargs:
            browser_options["window_size"] = kwargs["window_size"]
        if "start_maximized" in kwargs:
            browser_options["start_maximized"] = kwargs["start_maximized"]
        if "binary_location" in kwargs:
            browser_options["binary_location"] = kwargs["binary_location"]
        if "profile_directory" in kwargs:
            browser_options["profile_directory"] = kwargs["profile_directory"]
        if "extensions" in kwargs:
            browser_options["extensions"] = kwargs["extensions"]
        if "arguments" in kwargs:
            browser_options["arguments"] = kwargs["arguments"]
        if "preferences" in kwargs:
            browser_options["preferences"] = kwargs["preferences"]

        if browser_options:
            overrides["browser_options"] = browser_options

        # Stealth configuration
        if stealth:
            overrides["stealth"] = {"enabled": True}

        # Proxy configuration
        if proxy:
            proxy_config = ProxyConfig.from_url(proxy)
            overrides["proxy"] = {
                "host": proxy_config.host,
                "port": proxy_config.port,
                "type": proxy_config.proxy_type.value,
                "username": proxy_config.username,
                "password": proxy_config.password,
            }

        # Other overrides
        if "driver_version" in kwargs:
            overrides["driver_version"] = kwargs["driver_version"]
        if "implicit_wait" in kwargs:
            overrides["implicit_wait"] = kwargs["implicit_wait"]
        if "page_load_timeout" in kwargs:
            overrides["page_load_timeout"] = kwargs["page_load_timeout"]
        if "script_timeout" in kwargs:
            overrides["script_timeout"] = kwargs["script_timeout"]
        if "log_level" in kwargs:
            overrides["log_level"] = kwargs["log_level"]

        # Merge and validate
        config_dict = ConfigLoader.merge_configs(config_dict, overrides)
        return ConfigLoader.load_config(overrides=config_dict)

    def create_driver(self, **overrides: Any) -> WebDriver:
        """Create a WebDriver instance.

        Args:
            **overrides: Configuration overrides for this driver

        Returns:
            Configured WebDriver instance

        Example:
            driver = forge.create_driver(headless=True)
        """
        # Apply overrides if provided
        if overrides:
            config = self._build_config(
                browser=self.browser,
                headless=overrides.get("headless", self.config.browser_options.headless),
                stealth=overrides.get("stealth", bool(self.config.stealth)),
                proxy=overrides.get("proxy"),
                config_file=None,
                **overrides,
            )
        else:
            config = self.config

        # Create driver
        driver = self.driver_factory.create_driver(config)

        # Apply stealth if configured
        if config.stealth and config.stealth.enabled:
            stealth_engine = StealthEngine(config.stealth)
            stealth_engine.apply_stealth(driver)

        return driver

    def create_session(self, session_id: Optional[str] = None) -> tuple[str, WebDriver]:
        """Create a managed session.

        Args:
            session_id: Optional custom session ID

        Returns:
            Tuple of (session_id, driver)

        Example:
            session_id, driver = forge.create_session()
            # Use driver
            forge.close_session(session_id)
        """
        return self.session_manager.create_session(self.config, session_id)

    def close_session(self, session_id: str) -> bool:
        """Close a managed session.

        Args:
            session_id: Session ID to close

        Returns:
            True if closed, False if not found
        """
        return self.session_manager.close_session(session_id)

    def close_all_sessions(self) -> int:
        """Close all managed sessions.

        Returns:
            Number of sessions closed
        """
        return self.session_manager.close_all_sessions()

    @classmethod
    def from_config(cls, config_file: str, **overrides: Any) -> SeleniumForge:
        """Create SeleniumForge from configuration file.

        Args:
            config_file: Path to configuration file
            **overrides: Configuration overrides

        Returns:
            SeleniumForge instance

        Example:
            forge = SeleniumForge.from_config("config.yaml")
            driver = forge.create_driver()
        """
        config_path = Path(config_file)
        if not config_path.exists():
            raise UserError(
                f"Configuration file not found: {config_file}",
                suggestion="Check the file path",
            )

        config_dict = ConfigLoader.load_yaml(config_path)
        browser = config_dict.get("browser", "chrome")

        return cls(
            browser=browser,
            config_file=config_file,
            **overrides,
        )

    @classmethod
    def from_preset(cls, preset: str, browser: str = "chrome", **overrides: Any) -> SeleniumForge:
        """Create SeleniumForge from preset configuration.

        Args:
            preset: Preset name (headless, stealth, performance, testing, mobile)
            browser: Browser type
            **overrides: Configuration overrides

        Returns:
            SeleniumForge instance

        Example:
            forge = SeleniumForge.from_preset("stealth", browser="chrome")
            driver = forge.create_driver()
        """
        config_dict = DefaultConfigs.get_preset_config(preset, browser)

        # Extract relevant parameters
        browser_opts = config_dict.get("browser_options", {})
        stealth_config = config_dict.get("stealth", {})

        return cls(
            browser=browser,
            headless=browser_opts.get("headless", False),
            stealth=stealth_config.get("enabled", False),
            **overrides,
        )

    @classmethod
    def for_testing(cls, browser: str = "chrome", **overrides: Any) -> SeleniumForge:
        """Create SeleniumForge optimized for testing.

        Args:
            browser: Browser type
            **overrides: Configuration overrides

        Returns:
            SeleniumForge instance
        """
        return cls.from_preset("testing", browser=browser, **overrides)

    @classmethod
    def for_scraping(cls, browser: str = "chrome", **overrides: Any) -> SeleniumForge:
        """Create SeleniumForge optimized for web scraping.

        Args:
            browser: Browser type
            **overrides: Configuration overrides

        Returns:
            SeleniumForge instance
        """
        return cls.from_preset("web-scraping", browser=browser, **overrides)

    @staticmethod
    def get_system_info() -> SystemInfo:
        """Get system information.

        Returns:
            SystemInfo object
        """
        return PlatformDetector.get_system_info()

    @staticmethod
    def clear_cache() -> int:
        """Clear driver cache.

        Returns:
            Number of items cleared
        """
        manager = DriverManager()
        return manager.clear_cache()

    def __enter__(self) -> SeleniumForge:
        """Context manager entry.

        Returns:
            Self
        """
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """Context manager exit.

        Args:
            exc_type: Exception type
            exc_val: Exception value
            exc_tb: Exception traceback
        """
        self.close_all_sessions()

    def __repr__(self) -> str:
        """String representation.

        Returns:
            String representation
        """
        return (
            f"SeleniumForge(browser='{self.browser}', "
            f"headless={self.config.browser_options.headless}, "
            f"stealth={bool(self.config.stealth)})"
        )
