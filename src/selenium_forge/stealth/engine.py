"""Stealth mode engine for evading bot detection."""

from __future__ import annotations

import random
from typing import Optional

from selenium.webdriver.remote.webdriver import WebDriver

from selenium_forge.core.constants import DEFAULT_USER_AGENTS
from selenium_forge.core.types import StealthConfig
from selenium_forge.exceptions import UserError


class StealthEngine:
    """Applies stealth patches to WebDriver to evade bot detection."""

    # JavaScript to remove WebDriver detection
    JS_REMOVE_WEBDRIVER = """
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    });
    """

    # JavaScript to override permissions
    JS_OVERRIDE_PERMISSIONS = """
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) => (
        parameters.name === 'notifications' ?
            Promise.resolve({ state: Notification.permission }) :
            originalQuery(parameters)
    );
    """

    # JavaScript to mask plugins
    JS_MASK_PLUGINS = """
    Object.defineProperty(navigator, 'plugins', {
        get: () => [
            {
                0: {type: "application/x-google-chrome-pdf", suffixes: "pdf",
                    description: "Portable Document Format", enabledPlugin: Plugin},
                description: "Portable Document Format",
                filename: "internal-pdf-viewer",
                length: 1,
                name: "Chrome PDF Plugin"
            },
            {
                0: {type: "application/pdf", suffixes: "pdf",
                    description: "", enabledPlugin: Plugin},
                description: "",
                filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
                length: 1,
                name: "Chrome PDF Viewer"
            },
            {
                0: {type: "application/x-nacl", suffixes: "",
                    description: "Native Client Executable", enabledPlugin: Plugin},
                1: {type: "application/x-pnacl", suffixes: "",
                    description: "Portable Native Client Executable", enabledPlugin: Plugin},
                description: "",
                filename: "internal-nacl-plugin",
                length: 2,
                name: "Native Client"
            }
        ],
    });
    """

    # JavaScript to randomize canvas fingerprint
    JS_RANDOMIZE_CANVAS = """
    const getImageData = CanvasRenderingContext2D.prototype.getImageData;
    CanvasRenderingContext2D.prototype.getImageData = function() {
        const imageData = getImageData.apply(this, arguments);
        for (let i = 0; i < imageData.data.length; i += 4) {
            imageData.data[i] = imageData.data[i] ^ Math.floor(Math.random() * 10);
        }
        return imageData;
    };
    """

    # JavaScript to randomize WebGL fingerprint
    JS_RANDOMIZE_WEBGL = """
    const getParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(parameter) {
        if (parameter === 37445) {
            return 'Intel Inc.';
        }
        if (parameter === 37446) {
            return 'Intel Iris OpenGL Engine';
        }
        return getParameter.apply(this, arguments);
    };
    """

    # JavaScript to override languages
    JS_OVERRIDE_LANGUAGES = """
    Object.defineProperty(navigator, 'languages', {
        get: () => ['en-US', 'en']
    });
    """

    def __init__(self, config: Optional[StealthConfig] = None) -> None:
        """Initialize stealth engine.

        Args:
            config: Stealth configuration (optional)
        """
        self.config = config or StealthConfig()

    def apply_stealth(self, driver: WebDriver) -> None:
        """Apply stealth patches to WebDriver.

        Args:
            driver: WebDriver instance

        Raises:
            UserError: If stealth patches fail to apply
        """
        if not self.config.enabled:
            return

        try:
            # Execute CDP commands for Chromium-based browsers
            if self._is_chromium_based(driver):
                self._apply_chromium_stealth(driver)

            # Apply JavaScript patches
            self._apply_js_patches(driver)

        except Exception as e:
            # Don't fail if stealth patches fail, just warn
            import warnings
            warnings.warn(f"Failed to apply some stealth patches: {e}")

    def _is_chromium_based(self, driver: WebDriver) -> bool:
        """Check if driver is Chromium-based (Chrome, Edge).

        Args:
            driver: WebDriver instance

        Returns:
            True if Chromium-based, False otherwise
        """
        try:
            driver_name = driver.capabilities.get("browserName", "").lower()
            return driver_name in ("chrome", "msedge", "chromium")
        except Exception:
            return False

    def _apply_chromium_stealth(self, driver: WebDriver) -> None:
        """Apply Chromium-specific stealth patches using CDP.

        Args:
            driver: WebDriver instance
        """
        try:
            # Remove automation flags
            if self.config.remove_automation_flags:
                driver.execute_cdp_cmd(
                    "Page.addScriptToEvaluateOnNewDocument",
                    {"source": self.JS_REMOVE_WEBDRIVER},
                )

            # Override user agent if configured
            if self.config.custom_user_agent:
                driver.execute_cdp_cmd(
                    "Network.setUserAgentOverride",
                    {"userAgent": self.config.custom_user_agent},
                )
            elif self.config.randomize_user_agent:
                user_agent = random.choice(DEFAULT_USER_AGENTS)
                driver.execute_cdp_cmd(
                    "Network.setUserAgentOverride",
                    {"userAgent": user_agent},
                )

            # Set timezone if configured
            if self.config.timezone:
                driver.execute_cdp_cmd(
                    "Emulation.setTimezoneOverride",
                    {"timezoneId": self.config.timezone},
                )

            # Set locale if configured
            if self.config.locale:
                driver.execute_cdp_cmd(
                    "Emulation.setLocaleOverride",
                    {"locale": self.config.locale},
                )

        except Exception as e:
            # Some CDP commands may not be supported
            pass

    def _apply_js_patches(self, driver: WebDriver) -> None:
        """Apply JavaScript patches for stealth.

        Args:
            driver: WebDriver instance
        """
        patches_to_apply = []

        if self.config.hide_webdriver:
            patches_to_apply.append(self.JS_REMOVE_WEBDRIVER)
            patches_to_apply.append(self.JS_OVERRIDE_PERMISSIONS)

        if self.config.mask_fingerprint:
            patches_to_apply.append(self.JS_MASK_PLUGINS)

        if self.config.randomize_canvas:
            patches_to_apply.append(self.JS_RANDOMIZE_CANVAS)

        if self.config.randomize_webgl:
            patches_to_apply.append(self.JS_RANDOMIZE_WEBGL)

        if self.config.languages:
            languages_js = f"""
            Object.defineProperty(navigator, 'languages', {{
                get: () => {self.config.languages}
            }});
            """
            patches_to_apply.append(languages_js)
        else:
            patches_to_apply.append(self.JS_OVERRIDE_LANGUAGES)

        # Apply custom patches if provided
        if self.config.custom_patches:
            patches_to_apply.extend(self.config.custom_patches)

        # Execute all patches
        for patch in patches_to_apply:
            try:
                driver.execute_script(patch)
            except Exception:
                # Continue even if some patches fail
                pass

    def get_random_user_agent(self) -> str:
        """Get a random user agent string.

        Returns:
            Random user agent string
        """
        return random.choice(DEFAULT_USER_AGENTS)

    @staticmethod
    def create_stealth_driver(
        driver: WebDriver,
        config: Optional[StealthConfig] = None,
    ) -> WebDriver:
        """Apply stealth to existing driver.

        Args:
            driver: WebDriver instance
            config: Stealth configuration (optional)

        Returns:
            Driver with stealth applied
        """
        engine = StealthEngine(config)
        engine.apply_stealth(driver)
        return driver
