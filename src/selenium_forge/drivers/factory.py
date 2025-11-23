"""Driver factory for creating configured WebDriver instances."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.safari.options import Options as SafariOptions

from selenium_forge.core.constants import BrowserType
from selenium_forge.core.platform import PlatformDetector
from selenium_forge.core.types import BrowserOptions, DriverConfig, ProxyConfig
from selenium_forge.drivers.manager import DriverManager
from selenium_forge.exceptions import UserError


class DriverFactory:
    """Factory for creating WebDriver instances with full configuration."""

    def __init__(self, driver_manager: Optional[DriverManager] = None) -> None:
        """Initialize driver factory.

        Args:
            driver_manager: Driver manager instance (optional)
        """
        self.driver_manager = driver_manager or DriverManager()

    def create_driver(self, config: DriverConfig) -> WebDriver:
        """Create WebDriver instance from configuration.

        Args:
            config: Driver configuration

        Returns:
            Configured WebDriver instance

        Raises:
            UserError: If driver creation fails
        """
        try:
            if config.browser == BrowserType.CHROME:
                return self._create_chrome_driver(config)
            elif config.browser == BrowserType.FIREFOX:
                return self._create_firefox_driver(config)
            elif config.browser == BrowserType.EDGE:
                return self._create_edge_driver(config)
            elif config.browser == BrowserType.SAFARI:
                return self._create_safari_driver(config)
            else:
                raise UserError(
                    f"Unsupported browser: {config.browser}",
                    suggestion="Supported browsers: chrome, firefox, edge, safari",
                )
        except Exception as e:
            if isinstance(e, UserError):
                raise
            raise UserError(
                f"Failed to create {config.browser} driver: {e}",
                cause=e,
            )

    def _create_chrome_driver(self, config: DriverConfig) -> WebDriver:
        """Create Chrome WebDriver."""
        options = ChromeOptions()

        # Apply browser options
        self._apply_chrome_options(options, config.browser_options)

        # Apply proxy
        if config.proxy:
            self._apply_proxy_chrome(options, config.proxy)

        # Apply capabilities
        for key, value in config.capabilities.items():
            options.set_capability(key, value)

        # Get driver path
        driver_path = config.driver_path or self.driver_manager.get_driver_path(
            BrowserType.CHROME, config.driver_version
        )

        # Create service
        service = ChromeService(executable_path=str(driver_path))

        # Create driver
        driver = webdriver.Chrome(service=service, options=options)

        # Apply timeouts
        self._apply_timeouts(driver, config)

        return driver

    def _create_firefox_driver(self, config: DriverConfig) -> WebDriver:
        """Create Firefox WebDriver."""
        options = FirefoxOptions()

        # Apply browser options
        self._apply_firefox_options(options, config.browser_options)

        # Apply proxy
        if config.proxy:
            self._apply_proxy_firefox(options, config.proxy)

        # Apply capabilities
        for key, value in config.capabilities.items():
            options.set_capability(key, value)

        # Get driver path
        driver_path = config.driver_path or self.driver_manager.get_driver_path(
            BrowserType.FIREFOX, config.driver_version
        )

        # Create service
        service = FirefoxService(executable_path=str(driver_path))

        # Create driver
        driver = webdriver.Firefox(service=service, options=options)

        # Apply timeouts
        self._apply_timeouts(driver, config)

        return driver

    def _create_edge_driver(self, config: DriverConfig) -> WebDriver:
        """Create Edge WebDriver."""
        options = EdgeOptions()

        # Apply browser options
        self._apply_edge_options(options, config.browser_options)

        # Apply proxy
        if config.proxy:
            self._apply_proxy_edge(options, config.proxy)

        # Apply capabilities
        for key, value in config.capabilities.items():
            options.set_capability(key, value)

        # Get driver path
        driver_path = config.driver_path or self.driver_manager.get_driver_path(
            BrowserType.EDGE, config.driver_version
        )

        # Create service
        service = EdgeService(executable_path=str(driver_path))

        # Create driver
        driver = webdriver.Edge(service=service, options=options)

        # Apply timeouts
        self._apply_timeouts(driver, config)

        return driver

    def _create_safari_driver(self, config: DriverConfig) -> WebDriver:
        """Create Safari WebDriver."""
        options = SafariOptions()

        # Safari has limited options support
        # Apply capabilities
        for key, value in config.capabilities.items():
            options.set_capability(key, value)

        # Create driver
        driver = webdriver.Safari(options=options)

        # Apply timeouts
        self._apply_timeouts(driver, config)

        return driver

    def _apply_chrome_options(
        self, options: ChromeOptions, browser_opts: BrowserOptions
    ) -> None:
        """Apply browser options to Chrome."""
        # Headless mode
        if browser_opts.headless:
            options.add_argument("--headless=new")

        # Window size
        if browser_opts.window_size:
            width, height = browser_opts.window_size
            options.add_argument(f"--window-size={width},{height}")

        if browser_opts.start_maximized:
            options.add_argument("--start-maximized")

        # Binary location
        if browser_opts.binary_location:
            options.binary_location = browser_opts.binary_location

        # Profile directory
        if browser_opts.profile_directory:
            options.add_argument(f"--user-data-dir={browser_opts.profile_directory}")

        # Extensions
        for ext_path in browser_opts.extensions:
            options.add_extension(ext_path)

        # Performance options
        if browser_opts.disable_images:
            prefs = options.experimental_options.get("prefs", {})
            prefs["profile.managed_default_content_settings.images"] = 2
            options.add_experimental_option("prefs", prefs)

        if browser_opts.disable_javascript:
            prefs = options.experimental_options.get("prefs", {})
            prefs["profile.managed_default_content_settings.javascript"] = 2
            options.add_experimental_option("prefs", prefs)

        # Download directory
        if browser_opts.download_directory:
            prefs = options.experimental_options.get("prefs", {})
            prefs["download.default_directory"] = str(browser_opts.download_directory)
            prefs["download.prompt_for_download"] = not browser_opts.auto_download
            options.add_experimental_option("prefs", prefs)

        # Custom arguments
        for arg in browser_opts.arguments:
            options.add_argument(arg)

        # Preferences
        if browser_opts.preferences:
            existing_prefs = options.experimental_options.get("prefs", {})
            existing_prefs.update(browser_opts.preferences)
            options.add_experimental_option("prefs", existing_prefs)

        # Experimental options
        for key, value in browser_opts.experimental_options.items():
            if key != "prefs":  # Already handled above
                options.add_experimental_option(key, value)

    def _apply_firefox_options(
        self, options: FirefoxOptions, browser_opts: BrowserOptions
    ) -> None:
        """Apply browser options to Firefox."""
        # Headless mode
        if browser_opts.headless:
            options.add_argument("--headless")

        # Window size
        if browser_opts.window_size:
            width, height = browser_opts.window_size
            options.add_argument(f"--width={width}")
            options.add_argument(f"--height={height}")

        # Binary location
        if browser_opts.binary_location:
            options.binary_location = browser_opts.binary_location

        # Profile directory
        if browser_opts.profile_directory:
            from selenium.webdriver.firefox.firefox_profile import FirefoxProfile

            profile = FirefoxProfile(browser_opts.profile_directory)
            options.profile = profile

        # Performance options
        if browser_opts.disable_images:
            options.set_preference("permissions.default.image", 2)

        if browser_opts.disable_javascript:
            options.set_preference("javascript.enabled", False)

        # Download directory
        if browser_opts.download_directory:
            options.set_preference("browser.download.dir", str(browser_opts.download_directory))
            options.set_preference("browser.download.folderList", 2)
            options.set_preference(
                "browser.download.manager.showWhenStarting",
                not browser_opts.auto_download,
            )

        # Custom arguments
        for arg in browser_opts.arguments:
            options.add_argument(arg)

        # Preferences
        for key, value in browser_opts.preferences.items():
            options.set_preference(key, value)

    def _apply_edge_options(
        self, options: EdgeOptions, browser_opts: BrowserOptions
    ) -> None:
        """Apply browser options to Edge."""
        # Edge uses same options as Chrome
        self._apply_chrome_options(options, browser_opts)  # type: ignore

    def _apply_proxy_chrome(self, options: ChromeOptions, proxy: ProxyConfig) -> None:
        """Apply proxy configuration to Chrome."""
        proxy_dict = proxy.to_selenium_format()
        options.set_capability("proxy", proxy_dict)

    def _apply_proxy_firefox(
        self, options: FirefoxOptions, proxy: ProxyConfig
    ) -> None:
        """Apply proxy configuration to Firefox."""
        proxy_dict = proxy.to_selenium_format()
        options.set_capability("proxy", proxy_dict)

    def _apply_proxy_edge(self, options: EdgeOptions, proxy: ProxyConfig) -> None:
        """Apply proxy configuration to Edge."""
        proxy_dict = proxy.to_selenium_format()
        options.set_capability("proxy", proxy_dict)

    def _apply_timeouts(self, driver: WebDriver, config: DriverConfig) -> None:
        """Apply timeout configurations to driver.

        Args:
            driver: WebDriver instance
            config: Driver configuration
        """
        if config.implicit_wait:
            driver.implicitly_wait(config.implicit_wait)

        if config.page_load_timeout:
            driver.set_page_load_timeout(config.page_load_timeout)

        if config.script_timeout:
            driver.set_script_timeout(config.script_timeout)
