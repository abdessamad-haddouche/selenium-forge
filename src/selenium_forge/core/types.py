"""Type definitions and data structures for selenium-forge."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from selenium_forge.core.constants import BrowserType, ProxyType


@dataclass
class ProxyConfig:
    """Proxy configuration."""

    host: str
    port: int
    proxy_type: ProxyType = ProxyType.HTTP
    username: Optional[str] = None
    password: Optional[str] = None
    no_proxy: Optional[List[str]] = None

    def to_selenium_format(self) -> Dict[str, Any]:
        """Convert to Selenium proxy format.

        Returns:
            Dictionary in Selenium proxy format
        """
        proxy_str = f"{self.host}:{self.port}"
        if self.username and self.password:
            proxy_str = f"{self.username}:{self.password}@{proxy_str}"

        proxy_dict = {
            "proxyType": "manual",
        }

        if self.proxy_type in (ProxyType.HTTP, ProxyType.HTTPS):
            proxy_dict["httpProxy"] = proxy_str
            proxy_dict["sslProxy"] = proxy_str
        elif self.proxy_type in (ProxyType.SOCKS4, ProxyType.SOCKS5):
            proxy_dict["socksProxy"] = proxy_str
            proxy_dict["socksVersion"] = 5 if self.proxy_type == ProxyType.SOCKS5 else 4

        if self.no_proxy:
            proxy_dict["noProxy"] = ",".join(self.no_proxy)

        return proxy_dict

    @classmethod
    def from_url(cls, url: str) -> ProxyConfig:
        """Create ProxyConfig from URL string.

        Args:
            url: Proxy URL (e.g., "http://user:pass@host:port")

        Returns:
            ProxyConfig instance

        Raises:
            ValueError: If URL format is invalid
        """
        from urllib.parse import urlparse

        parsed = urlparse(url)
        if not parsed.hostname or not parsed.port:
            raise ValueError(f"Invalid proxy URL: {url}")

        proxy_type_map = {
            "http": ProxyType.HTTP,
            "https": ProxyType.HTTPS,
            "socks4": ProxyType.SOCKS4,
            "socks5": ProxyType.SOCKS5,
        }

        proxy_type = proxy_type_map.get(parsed.scheme, ProxyType.HTTP)

        return cls(
            host=parsed.hostname,
            port=parsed.port,
            proxy_type=proxy_type,
            username=parsed.username,
            password=parsed.password,
        )


@dataclass
class StealthConfig:
    """Stealth mode configuration."""

    enabled: bool = True
    hide_webdriver: bool = True
    randomize_user_agent: bool = True
    mask_fingerprint: bool = True
    remove_automation_flags: bool = True
    custom_user_agent: Optional[str] = None
    custom_patches: Optional[List[str]] = None

    # Canvas fingerprinting
    randomize_canvas: bool = True

    # WebGL fingerprinting
    randomize_webgl: bool = True

    # Audio fingerprinting
    randomize_audio: bool = True

    # Timezone and locale
    timezone: Optional[str] = None
    locale: Optional[str] = None
    languages: Optional[List[str]] = None


@dataclass
class BrowserOptions:
    """Browser-specific options."""

    # Window and display
    headless: bool = False
    window_size: Optional[tuple[int, int]] = None
    start_maximized: bool = False

    # Browser binary and profile
    binary_location: Optional[str] = None
    profile_directory: Optional[str] = None

    # Extensions
    extensions: List[str] = field(default_factory=list)

    # Performance
    disable_images: bool = False
    disable_javascript: bool = False
    disable_css: bool = False
    disable_plugins: bool = False

    # Downloads
    download_directory: Optional[str] = None
    auto_download: bool = True

    # Experimental options
    experimental_options: Dict[str, Any] = field(default_factory=dict)

    # Additional arguments
    arguments: List[str] = field(default_factory=list)

    # Preferences (browser-specific)
    preferences: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DriverConfig:
    """Complete driver configuration."""

    browser: BrowserType
    browser_options: BrowserOptions = field(default_factory=BrowserOptions)
    proxy: Optional[ProxyConfig] = None
    stealth: Optional[StealthConfig] = None

    # Driver-specific
    driver_version: Optional[str] = None
    driver_path: Optional[Path] = None

    # Timeouts (seconds)
    implicit_wait: float = 10.0
    page_load_timeout: float = 60.0
    script_timeout: float = 30.0

    # Capabilities
    capabilities: Dict[str, Any] = field(default_factory=dict)

    # Logging
    log_level: str = "INFO"
    enable_logging: bool = True

    # Session management
    session_id: Optional[str] = None
    reuse_session: bool = False


@dataclass
class SystemInfo:
    """System information."""

    os: str
    os_version: str
    architecture: str
    python_version: str
    selenium_version: str
    is_wsl: bool = False
    has_display: bool = True


@dataclass
class DriverInfo:
    """WebDriver information."""

    browser: BrowserType
    driver_version: str
    browser_version: Optional[str] = None
    driver_path: Path = field(default_factory=Path)
    last_updated: Optional[str] = None


@dataclass
class SessionInfo:
    """Browser session information."""

    session_id: str
    browser: BrowserType
    created_at: str
    last_activity: str
    is_active: bool = True
    capabilities: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProxyRotationConfig:
    """Proxy rotation configuration."""

    proxies: List[ProxyConfig]
    rotation_strategy: str = "round-robin"  # round-robin, random, least-used
    max_failures_per_proxy: int = 3
    health_check_enabled: bool = True
    health_check_url: str = "https://httpbin.org/ip"
    health_check_timeout: float = 5.0


@dataclass
class PerformanceMetrics:
    """Performance metrics for a session."""

    page_load_time: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    network_requests: int = 0
    errors_count: int = 0
    screenshots_taken: int = 0
