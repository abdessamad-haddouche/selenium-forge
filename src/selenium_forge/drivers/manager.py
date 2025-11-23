"""WebDriver download and version management."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

import requests

from selenium_forge.core.constants import BrowserType, OperatingSystem, Architecture
from selenium_forge.core.platform import PlatformDetector
from selenium_forge.core.types import DriverInfo
from selenium_forge.exceptions import RetryableError, UserError
from selenium_forge.utils.download import Downloader
from selenium_forge.utils.filesystem import FileSystemManager


class DriverManager:
    """Manages WebDriver downloads, caching, and versioning."""

    def __init__(self, cache_dir: Optional[Path] = None) -> None:
        """Initialize driver manager.

        Args:
            cache_dir: Custom cache directory (optional)
        """
        self.cache_dir = cache_dir or PlatformDetector.get_cache_dir() / "drivers"
        FileSystemManager.ensure_directory(self.cache_dir)
        self.downloader = Downloader()
        self.metadata_file = self.cache_dir / "metadata.json"
        self.metadata = self._load_metadata()

    def _load_metadata(self) -> Dict:
        """Load driver metadata from cache."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_metadata(self) -> None:
        """Save driver metadata to cache."""
        try:
            with open(self.metadata_file, "w") as f:
                json.dump(self.metadata, f, indent=2)
        except Exception:
            pass

    def get_driver_path(
        self,
        browser: BrowserType,
        version: Optional[str] = None,
    ) -> Path:
        """Get path to WebDriver, downloading if necessary.

        Args:
            browser: Browser type
            version: Specific version (use 'latest' or None for latest)

        Returns:
            Path to WebDriver executable

        Raises:
            UserError: If driver cannot be obtained
        """
        # For Safari, return system driver path
        if browser == BrowserType.SAFARI:
            return self._get_safari_driver()

        # Check cache first
        cached_path = self._get_cached_driver(browser, version)
        if cached_path and cached_path.exists():
            return cached_path

        # Download driver
        return self._download_driver(browser, version)

    def _get_safari_driver(self) -> Path:
        """Get Safari WebDriver (safaridriver).

        Returns:
            Path to safaridriver

        Raises:
            UserError: If safaridriver is not available
        """
        try:
            result = subprocess.run(
                ["which", "safaridriver"],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0 and result.stdout.strip():
                return Path(result.stdout.strip())
        except Exception:
            pass

        raise UserError(
            "Safari WebDriver (safaridriver) not found",
            suggestion="Safari WebDriver is built into macOS. Enable it using: sudo safaridriver --enable",
        )

    def _get_cached_driver(
        self,
        browser: BrowserType,
        version: Optional[str],
    ) -> Optional[Path]:
        """Get cached driver if available and fresh.

        Args:
            browser: Browser type
            version: Driver version

        Returns:
            Path to cached driver, or None
        """
        browser_key = browser.value
        if browser_key not in self.metadata:
            return None

        driver_info = self.metadata[browser_key]

        # Check if version matches (if specified)
        if version and version != "latest":
            if driver_info.get("version") != version:
                return None

        # Check if cache is too old (more than 7 days)
        last_updated = driver_info.get("last_updated")
        if last_updated:
            try:
                last_update_date = datetime.fromisoformat(last_updated)
                if datetime.now() - last_update_date > timedelta(days=7):
                    return None
            except Exception:
                pass

        # Check if driver file exists
        driver_path = Path(driver_info.get("path", ""))
        if driver_path.exists():
            return driver_path

        return None

    def _download_driver(
        self,
        browser: BrowserType,
        version: Optional[str] = None,
    ) -> Path:
        """Download WebDriver for specified browser.

        Args:
            browser: Browser type
            version: Driver version (None or 'latest' for latest)

        Returns:
            Path to downloaded driver

        Raises:
            UserError: If download fails
        """
        os_type = PlatformDetector.detect_os()
        arch = PlatformDetector.detect_architecture()

        if browser == BrowserType.CHROME:
            return self._download_chromedriver(version, os_type, arch)
        elif browser == BrowserType.FIREFOX:
            return self._download_geckodriver(version, os_type, arch)
        elif browser == BrowserType.EDGE:
            return self._download_edgedriver(version, os_type, arch)
        else:
            raise UserError(
                f"Automatic driver download not supported for {browser}",
                suggestion=f"Manually download {browser} driver and specify path",
            )

    def _download_chromedriver(
        self,
        version: Optional[str],
        os_type: OperatingSystem,
        arch: Architecture,
    ) -> Path:
        """Download ChromeDriver."""
        try:
            # Use webdriver-manager for simplicity
            from webdriver_manager.chrome import ChromeDriverManager
            from webdriver_manager.core.os_manager import ChromeType

            manager = ChromeDriverManager()
            driver_path = Path(manager.install())

            # Update metadata
            self._update_metadata(
                BrowserType.CHROME,
                str(driver_path),
                self._get_driver_version(driver_path),
            )

            return driver_path

        except ImportError:
            raise UserError(
                "webdriver-manager not installed",
                suggestion="Install with: pip install webdriver-manager",
            )
        except Exception as e:
            raise UserError(
                f"Failed to download ChromeDriver: {e}",
                cause=e,
            )

    def _download_geckodriver(
        self,
        version: Optional[str],
        os_type: OperatingSystem,
        arch: Architecture,
    ) -> Path:
        """Download GeckoDriver (Firefox)."""
        try:
            from webdriver_manager.firefox import GeckoDriverManager

            manager = GeckoDriverManager()
            driver_path = Path(manager.install())

            self._update_metadata(
                BrowserType.FIREFOX,
                str(driver_path),
                self._get_driver_version(driver_path),
            )

            return driver_path

        except ImportError:
            raise UserError(
                "webdriver-manager not installed",
                suggestion="Install with: pip install webdriver-manager",
            )
        except Exception as e:
            raise UserError(
                f"Failed to download GeckoDriver: {e}",
                cause=e,
            )

    def _download_edgedriver(
        self,
        version: Optional[str],
        os_type: OperatingSystem,
        arch: Architecture,
    ) -> Path:
        """Download EdgeDriver."""
        try:
            from webdriver_manager.microsoft import EdgeChromiumDriverManager

            manager = EdgeChromiumDriverManager()
            driver_path = Path(manager.install())

            self._update_metadata(
                BrowserType.EDGE,
                str(driver_path),
                self._get_driver_version(driver_path),
            )

            return driver_path

        except ImportError:
            raise UserError(
                "webdriver-manager not installed",
                suggestion="Install with: pip install webdriver-manager",
            )
        except Exception as e:
            raise UserError(
                f"Failed to download EdgeDriver: {e}",
                cause=e,
            )

    def _get_driver_version(self, driver_path: Path) -> str:
        """Get version of driver executable.

        Args:
            driver_path: Path to driver

        Returns:
            Version string
        """
        try:
            result = subprocess.run(
                [str(driver_path), "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            if result.returncode == 0:
                # Extract version number from output
                import re

                version_match = re.search(r"(\d+\.\d+\.\d+(?:\.\d+)?)", result.stdout)
                if version_match:
                    return version_match.group(1)
        except Exception:
            pass

        return "unknown"

    def _update_metadata(
        self,
        browser: BrowserType,
        driver_path: str,
        version: str,
    ) -> None:
        """Update driver metadata.

        Args:
            browser: Browser type
            driver_path: Path to driver
            version: Driver version
        """
        self.metadata[browser.value] = {
            "path": driver_path,
            "version": version,
            "last_updated": datetime.now().isoformat(),
        }
        self._save_metadata()

    def get_driver_info(self, browser: BrowserType) -> Optional[DriverInfo]:
        """Get information about cached driver.

        Args:
            browser: Browser type

        Returns:
            DriverInfo object, or None if not cached
        """
        browser_key = browser.value
        if browser_key not in self.metadata:
            return None

        data = self.metadata[browser_key]
        return DriverInfo(
            browser=browser,
            driver_version=data.get("version", "unknown"),
            driver_path=Path(data.get("path", "")),
            last_updated=data.get("last_updated"),
        )

    def clear_cache(self, browser: Optional[BrowserType] = None) -> int:
        """Clear driver cache.

        Args:
            browser: Specific browser to clear (None for all)

        Returns:
            Number of items cleared
        """
        if browser:
            # Clear specific browser
            browser_key = browser.value
            if browser_key in self.metadata:
                driver_path = Path(self.metadata[browser_key].get("path", ""))
                if driver_path.exists():
                    FileSystemManager.delete_path(driver_path, ignore_errors=True)
                del self.metadata[browser_key]
                self._save_metadata()
                return 1
            return 0
        else:
            # Clear all
            count = len(self.metadata)
            FileSystemManager.clean_directory(self.cache_dir)
            self.metadata.clear()
            self._save_metadata()
            return count

    def is_driver_available(self, browser: BrowserType) -> bool:
        """Check if driver is available (cached or can be downloaded).

        Args:
            browser: Browser type

        Returns:
            True if available, False otherwise
        """
        if browser == BrowserType.SAFARI:
            try:
                self._get_safari_driver()
                return True
            except Exception:
                return False

        # Check if cached
        cached = self._get_cached_driver(browser, None)
        if cached and cached.exists():
            return True

        # Check if can be downloaded
        return PlatformDetector.check_internet_connection()
