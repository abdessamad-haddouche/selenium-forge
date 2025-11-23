"""Default configurations for different browsers and scenarios."""

from typing import Any, Dict

from selenium_forge.core.constants import (
    BrowserType,
    DEFAULT_IMPLICIT_WAIT,
    DEFAULT_PAGE_LOAD_TIMEOUT,
    DEFAULT_SCRIPT_TIMEOUT,
)


class DefaultConfigs:
    """Default configurations for various scenarios."""

    # Base configuration applied to all browsers
    BASE_CONFIG: Dict[str, Any] = {
        "implicit_wait": DEFAULT_IMPLICIT_WAIT,
        "page_load_timeout": DEFAULT_PAGE_LOAD_TIMEOUT,
        "script_timeout": DEFAULT_SCRIPT_TIMEOUT,
        "log_level": "INFO",
        "enable_logging": True,
        "browser_options": {
            "headless": False,
            "start_maximized": False,
            "window_size": None,
            "disable_images": False,
            "disable_javascript": False,
            "disable_css": False,
            "auto_download": True,
        },
    }

    # Chrome-specific defaults
    CHROME_CONFIG: Dict[str, Any] = {
        "browser": "chrome",
        "driver_version": "latest",
        "browser_options": {
            "arguments": [
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
            ],
            "preferences": {
                "profile.default_content_setting_values.notifications": 2,
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False,
            },
            "experimental_options": {
                "excludeSwitches": ["enable-automation", "enable-logging"],
                "useAutomationExtension": False,
            },
        },
    }

    # Firefox-specific defaults
    FIREFOX_CONFIG: Dict[str, Any] = {
        "browser": "firefox",
        "driver_version": "latest",
        "browser_options": {
            "arguments": [],
            "preferences": {
                "dom.webdriver.enabled": False,
                "useAutomationExtension": False,
                "marionette.enabled": True,
                "dom.webnotifications.enabled": False,
            },
        },
    }

    # Edge-specific defaults
    EDGE_CONFIG: Dict[str, Any] = {
        "browser": "edge",
        "driver_version": "latest",
        "browser_options": {
            "arguments": [
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
            ],
            "preferences": {
                "profile.default_content_setting_values.notifications": 2,
            },
            "experimental_options": {
                "excludeSwitches": ["enable-automation"],
                "useAutomationExtension": False,
            },
        },
    }

    # Safari-specific defaults
    SAFARI_CONFIG: Dict[str, Any] = {
        "browser": "safari",
        "driver_version": "system",
        "browser_options": {
            "arguments": [],
        },
    }

    # Headless configuration (overlay)
    HEADLESS_CONFIG: Dict[str, Any] = {
        "browser_options": {
            "headless": True,
            "arguments": [
                "--window-size=1920,1080",
                "--disable-gpu",
            ],
        },
    }

    # Stealth mode configuration
    STEALTH_CONFIG: Dict[str, Any] = {
        "stealth": {
            "enabled": True,
            "hide_webdriver": True,
            "randomize_user_agent": True,
            "mask_fingerprint": True,
            "remove_automation_flags": True,
            "randomize_canvas": True,
            "randomize_webgl": True,
            "randomize_audio": True,
        },
    }

    # Performance optimized configuration
    PERFORMANCE_CONFIG: Dict[str, Any] = {
        "browser_options": {
            "disable_images": True,
            "disable_css": False,
            "arguments": [
                "--disable-extensions",
                "--disable-plugins",
                "--disable-infobars",
                "--mute-audio",
            ],
        },
    }

    # Testing configuration
    TESTING_CONFIG: Dict[str, Any] = {
        "browser_options": {
            "headless": True,
            "arguments": [
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
            ],
        },
        "implicit_wait": 5.0,
        "page_load_timeout": 30.0,
    }

    # Mobile emulation configuration
    MOBILE_CONFIG: Dict[str, Any] = {
        "browser_options": {
            "experimental_options": {
                "mobileEmulation": {
                    "deviceName": "iPhone 12 Pro",
                },
            },
        },
    }

    @staticmethod
    def get_browser_defaults(browser: str) -> Dict[str, Any]:
        """Get default configuration for a specific browser.

        Args:
            browser: Browser type (chrome, firefox, edge, safari)

        Returns:
            Default configuration dictionary
        """
        browser = browser.lower()

        # Get browser-specific config
        browser_configs = {
            "chrome": DefaultConfigs.CHROME_CONFIG,
            "firefox": DefaultConfigs.FIREFOX_CONFIG,
            "edge": DefaultConfigs.EDGE_CONFIG,
            "safari": DefaultConfigs.SAFARI_CONFIG,
            "chromium": DefaultConfigs.CHROME_CONFIG,  # Use Chrome config for Chromium
        }

        browser_config = browser_configs.get(browser, DefaultConfigs.CHROME_CONFIG)

        # Merge with base config
        from selenium_forge.config.loader import ConfigLoader

        return ConfigLoader.merge_configs(
            DefaultConfigs.BASE_CONFIG.copy(), browser_config
        )

    @staticmethod
    def get_preset_config(preset: str, browser: str = "chrome") -> Dict[str, Any]:
        """Get a preset configuration.

        Args:
            preset: Preset name (headless, stealth, performance, testing, mobile)
            browser: Browser type

        Returns:
            Preset configuration dictionary
        """
        from selenium_forge.config.loader import ConfigLoader

        # Start with browser defaults
        config = DefaultConfigs.get_browser_defaults(browser)

        # Apply preset overlay
        preset = preset.lower()
        preset_configs = {
            "headless": DefaultConfigs.HEADLESS_CONFIG,
            "stealth": DefaultConfigs.STEALTH_CONFIG,
            "performance": DefaultConfigs.PERFORMANCE_CONFIG,
            "testing": DefaultConfigs.TESTING_CONFIG,
            "mobile": DefaultConfigs.MOBILE_CONFIG,
        }

        if preset in preset_configs:
            config = ConfigLoader.merge_configs(config, preset_configs[preset])

        return config

    @staticmethod
    def get_scenario_config(scenario: str) -> Dict[str, Any]:
        """Get configuration for common automation scenarios.

        Args:
            scenario: Scenario name (web-scraping, testing, bot, data-collection)

        Returns:
            Scenario-specific configuration
        """
        from selenium_forge.config.loader import ConfigLoader

        scenario = scenario.lower()

        if scenario == "web-scraping":
            # Optimized for web scraping
            return ConfigLoader.merge_configs(
                DefaultConfigs.get_browser_defaults("chrome"),
                DefaultConfigs.STEALTH_CONFIG,
                DefaultConfigs.PERFORMANCE_CONFIG,
            )

        elif scenario == "testing":
            # Optimized for automated testing
            return ConfigLoader.merge_configs(
                DefaultConfigs.get_browser_defaults("chrome"),
                DefaultConfigs.TESTING_CONFIG,
            )

        elif scenario == "bot":
            # Optimized for bot operations
            return ConfigLoader.merge_configs(
                DefaultConfigs.get_browser_defaults("chrome"),
                DefaultConfigs.STEALTH_CONFIG,
                {
                    "browser_options": {
                        "headless": True,
                    },
                },
            )

        elif scenario == "data-collection":
            # Optimized for data collection
            return ConfigLoader.merge_configs(
                DefaultConfigs.get_browser_defaults("chrome"),
                DefaultConfigs.PERFORMANCE_CONFIG,
                {
                    "browser_options": {
                        "disable_images": True,
                    },
                },
            )

        else:
            # Default to Chrome with stealth
            return ConfigLoader.merge_configs(
                DefaultConfigs.get_browser_defaults("chrome"),
                DefaultConfigs.STEALTH_CONFIG,
            )
