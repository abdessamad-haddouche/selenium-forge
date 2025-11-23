"""Configuration schema and validation."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from selenium_forge.core.constants import BrowserType, ProxyType
from selenium_forge.core.types import (
    BrowserOptions,
    DriverConfig,
    ProxyConfig,
    StealthConfig,
)
from selenium_forge.exceptions import UserError


class ConfigSchema:
    """Configuration schema definition and validation."""

    REQUIRED_FIELDS: List[str] = ["browser"]

    OPTIONAL_FIELDS: Dict[str, type] = {
        "driver_version": str,
        "driver_path": str,
        "implicit_wait": (int, float),
        "page_load_timeout": (int, float),
        "script_timeout": (int, float),
        "log_level": str,
        "enable_logging": bool,
    }

    VALID_LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    @staticmethod
    def validate_browser_type(browser: str) -> BrowserType:
        """Validate and convert browser type.

        Args:
            browser: Browser type string

        Returns:
            BrowserType enum

        Raises:
            UserError: If browser type is invalid
        """
        try:
            return BrowserType(browser.lower())
        except ValueError:
            valid_browsers = [b.value for b in BrowserType]
            raise UserError(
                f"Invalid browser type: {browser}",
                suggestion=f"Valid browsers: {', '.join(valid_browsers)}",
            )

    @staticmethod
    def validate_proxy_config(proxy_data: Dict[str, Any]) -> ProxyConfig:
        """Validate and create proxy configuration.

        Args:
            proxy_data: Raw proxy configuration data

        Returns:
            ProxyConfig object

        Raises:
            UserError: If proxy configuration is invalid
        """
        required_fields = ["host", "port"]
        for field in required_fields:
            if field not in proxy_data:
                raise UserError(
                    f"Missing required proxy field: {field}",
                    suggestion=f"Proxy config must include: {', '.join(required_fields)}",
                )

        # Validate proxy type
        proxy_type_str = proxy_data.get("type", "http")
        try:
            proxy_type = ProxyType(proxy_type_str.lower())
        except ValueError:
            valid_types = [t.value for t in ProxyType]
            raise UserError(
                f"Invalid proxy type: {proxy_type_str}",
                suggestion=f"Valid proxy types: {', '.join(valid_types)}",
            )

        # Validate port
        port = proxy_data["port"]
        if not isinstance(port, int) or port < 1 or port > 65535:
            raise UserError(
                f"Invalid proxy port: {port}",
                suggestion="Port must be an integer between 1 and 65535",
            )

        return ProxyConfig(
            host=proxy_data["host"],
            port=port,
            proxy_type=proxy_type,
            username=proxy_data.get("username"),
            password=proxy_data.get("password"),
            no_proxy=proxy_data.get("no_proxy"),
        )

    @staticmethod
    def validate_stealth_config(stealth_data: Dict[str, Any]) -> StealthConfig:
        """Validate and create stealth configuration.

        Args:
            stealth_data: Raw stealth configuration data

        Returns:
            StealthConfig object

        Raises:
            UserError: If stealth configuration is invalid
        """
        boolean_fields = [
            "enabled",
            "hide_webdriver",
            "randomize_user_agent",
            "mask_fingerprint",
            "remove_automation_flags",
            "randomize_canvas",
            "randomize_webgl",
            "randomize_audio",
        ]

        # Validate boolean fields
        for field in boolean_fields:
            if field in stealth_data and not isinstance(stealth_data[field], bool):
                raise UserError(
                    f"Stealth config field '{field}' must be a boolean",
                    suggestion=f"Use true or false for {field}",
                )

        return StealthConfig(
            enabled=stealth_data.get("enabled", True),
            hide_webdriver=stealth_data.get("hide_webdriver", True),
            randomize_user_agent=stealth_data.get("randomize_user_agent", True),
            mask_fingerprint=stealth_data.get("mask_fingerprint", True),
            remove_automation_flags=stealth_data.get("remove_automation_flags", True),
            custom_user_agent=stealth_data.get("custom_user_agent"),
            custom_patches=stealth_data.get("custom_patches"),
            randomize_canvas=stealth_data.get("randomize_canvas", True),
            randomize_webgl=stealth_data.get("randomize_webgl", True),
            randomize_audio=stealth_data.get("randomize_audio", True),
            timezone=stealth_data.get("timezone"),
            locale=stealth_data.get("locale"),
            languages=stealth_data.get("languages"),
        )

    @staticmethod
    def validate_browser_options(options_data: Dict[str, Any]) -> BrowserOptions:
        """Validate and create browser options.

        Args:
            options_data: Raw browser options data

        Returns:
            BrowserOptions object

        Raises:
            UserError: If browser options are invalid
        """
        # Validate window size
        window_size = options_data.get("window_size")
        if window_size is not None:
            if not isinstance(window_size, (list, tuple)) or len(window_size) != 2:
                raise UserError(
                    f"Invalid window_size: {window_size}",
                    suggestion="window_size must be a list of two integers: [width, height]",
                )
            if not all(isinstance(x, int) and x > 0 for x in window_size):
                raise UserError(
                    "Window size values must be positive integers",
                    suggestion="Example: window_size: [1920, 1080]",
                )
            window_size = tuple(window_size)

        # Validate extensions
        extensions = options_data.get("extensions", [])
        if not isinstance(extensions, list):
            raise UserError(
                "Extensions must be a list of file paths",
                suggestion="Example: extensions: ['/path/to/ext1.crx', '/path/to/ext2.crx']",
            )

        return BrowserOptions(
            headless=options_data.get("headless", False),
            window_size=window_size,
            start_maximized=options_data.get("start_maximized", False),
            binary_location=options_data.get("binary_location"),
            profile_directory=options_data.get("profile_directory"),
            extensions=extensions,
            disable_images=options_data.get("disable_images", False),
            disable_javascript=options_data.get("disable_javascript", False),
            disable_css=options_data.get("disable_css", False),
            disable_plugins=options_data.get("disable_plugins", False),
            download_directory=options_data.get("download_directory"),
            auto_download=options_data.get("auto_download", True),
            experimental_options=options_data.get("experimental_options", {}),
            arguments=options_data.get("arguments", []),
            preferences=options_data.get("preferences", {}),
        )

    @staticmethod
    def validate_config(config_data: Dict[str, Any]) -> DriverConfig:
        """Validate complete configuration.

        Args:
            config_data: Raw configuration data

        Returns:
            DriverConfig object

        Raises:
            UserError: If configuration is invalid
        """
        # Check required fields
        for field in ConfigSchema.REQUIRED_FIELDS:
            if field not in config_data:
                raise UserError(
                    f"Missing required configuration field: {field}",
                    suggestion=f"Configuration must include: {', '.join(ConfigSchema.REQUIRED_FIELDS)}",
                )

        # Validate browser type
        browser = ConfigSchema.validate_browser_type(config_data["browser"])

        # Validate browser options
        options_data = config_data.get("browser_options", {})
        browser_options = ConfigSchema.validate_browser_options(options_data)

        # Validate proxy configuration
        proxy = None
        if "proxy" in config_data and config_data["proxy"]:
            proxy = ConfigSchema.validate_proxy_config(config_data["proxy"])

        # Validate stealth configuration
        stealth = None
        if "stealth" in config_data and config_data["stealth"]:
            stealth = ConfigSchema.validate_stealth_config(config_data["stealth"])

        # Validate log level
        log_level = config_data.get("log_level", "INFO")
        if log_level.upper() not in ConfigSchema.VALID_LOG_LEVELS:
            raise UserError(
                f"Invalid log level: {log_level}",
                suggestion=f"Valid log levels: {', '.join(ConfigSchema.VALID_LOG_LEVELS)}",
            )

        # Validate timeouts
        for timeout_field in ["implicit_wait", "page_load_timeout", "script_timeout"]:
            timeout_value = config_data.get(timeout_field)
            if timeout_value is not None:
                if not isinstance(timeout_value, (int, float)) or timeout_value < 0:
                    raise UserError(
                        f"Invalid {timeout_field}: {timeout_value}",
                        suggestion=f"{timeout_field} must be a non-negative number",
                    )

        return DriverConfig(
            browser=browser,
            browser_options=browser_options,
            proxy=proxy,
            stealth=stealth,
            driver_version=config_data.get("driver_version"),
            driver_path=config_data.get("driver_path"),
            implicit_wait=config_data.get("implicit_wait", 10.0),
            page_load_timeout=config_data.get("page_load_timeout", 60.0),
            script_timeout=config_data.get("script_timeout", 30.0),
            capabilities=config_data.get("capabilities", {}),
            log_level=log_level.upper(),
            enable_logging=config_data.get("enable_logging", True),
        )


def validate_config(config_data: Dict[str, Any]) -> DriverConfig:
    """Convenience function to validate configuration.

    Args:
        config_data: Raw configuration data

    Returns:
        DriverConfig object

    Raises:
        UserError: If configuration is invalid
    """
    return ConfigSchema.validate_config(config_data)
