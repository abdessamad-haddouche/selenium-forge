"""Constants and enumerations for selenium-forge."""

from enum import Enum
from typing import Dict, List


class BrowserType(str, Enum):
    """Supported browser types."""

    CHROME = "chrome"
    FIREFOX = "firefox"
    EDGE = "edge"
    SAFARI = "safari"
    CHROMIUM = "chromium"

    def __str__(self) -> str:
        return self.value


class OperatingSystem(str, Enum):
    """Supported operating systems."""

    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "macos"
    WSL = "wsl"  # Windows Subsystem for Linux

    def __str__(self) -> str:
        return self.value


class Architecture(str, Enum):
    """System architecture types."""

    X64 = "x64"
    X86 = "x86"
    ARM64 = "arm64"
    ARM = "arm"

    def __str__(self) -> str:
        return self.value


class ProxyType(str, Enum):
    """Proxy protocol types."""

    HTTP = "http"
    HTTPS = "https"
    SOCKS4 = "socks4"
    SOCKS5 = "socks5"

    def __str__(self) -> str:
        return self.value


# ================================================================
# Timeout Defaults
# ================================================================

DEFAULT_TIMEOUT = 30  # seconds
DEFAULT_PAGE_LOAD_TIMEOUT = 60  # seconds
DEFAULT_SCRIPT_TIMEOUT = 30  # seconds
DEFAULT_IMPLICIT_WAIT = 10  # seconds
DEFAULT_DOWNLOAD_TIMEOUT = 300  # seconds (5 minutes)

# ================================================================
# Driver Version Defaults
# ================================================================

# Latest stable versions as fallback
DEFAULT_DRIVER_VERSIONS: Dict[BrowserType, str] = {
    BrowserType.CHROME: "latest",
    BrowserType.FIREFOX: "latest",
    BrowserType.EDGE: "latest",
    BrowserType.SAFARI: "system",  # Safari uses system driver
}

# ================================================================
# Path Defaults
# ================================================================


class DriverPaths:
    """Default driver storage paths."""

    # Base cache directory name
    CACHE_DIR_NAME = ".selenium-forge"

    # Driver subdirectories
    DRIVERS_SUBDIR = "drivers"
    PROFILES_SUBDIR = "profiles"
    EXTENSIONS_SUBDIR = "extensions"
    TEMP_SUBDIR = "temp"

    # Config file names
    DEFAULT_CONFIG_NAME = "selenium-forge.yaml"
    USER_CONFIG_NAME = ".selenium-forge.yaml"


# ================================================================
# Browser Binary Paths
# ================================================================

# Common browser installation paths by OS
BROWSER_PATHS: Dict[OperatingSystem, Dict[BrowserType, List[str]]] = {
    OperatingSystem.WINDOWS: {
        BrowserType.CHROME: [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe",
        ],
        BrowserType.FIREFOX: [
            r"C:\Program Files\Mozilla Firefox\firefox.exe",
            r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
        ],
        BrowserType.EDGE: [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        ],
    },
    OperatingSystem.LINUX: {
        BrowserType.CHROME: [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser",
            "/snap/bin/chromium",
        ],
        BrowserType.FIREFOX: [
            "/usr/bin/firefox",
            "/usr/bin/firefox-esr",
            "/snap/bin/firefox",
        ],
        BrowserType.EDGE: [
            "/usr/bin/microsoft-edge",
            "/usr/bin/microsoft-edge-stable",
        ],
    },
    OperatingSystem.MACOS: {
        BrowserType.CHROME: [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        ],
        BrowserType.FIREFOX: [
            "/Applications/Firefox.app/Contents/MacOS/firefox",
        ],
        BrowserType.EDGE: [
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        ],
        BrowserType.SAFARI: [
            "/Applications/Safari.app/Contents/MacOS/Safari",
        ],
    },
    OperatingSystem.WSL: {
        BrowserType.CHROME: [
            "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe",
            "/mnt/c/Program Files (x86)/Google/Chrome/Application/chrome.exe",
        ],
        BrowserType.FIREFOX: [
            "/mnt/c/Program Files/Mozilla Firefox/firefox.exe",
            "/mnt/c/Program Files (x86)/Mozilla Firefox/firefox.exe",
        ],
        BrowserType.EDGE: [
            "/mnt/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
            "/mnt/c/Program Files/Microsoft/Edge/Application/msedge.exe",
        ],
    },
}

# ================================================================
# WebDriver Download URLs
# ================================================================

DRIVER_URLS: Dict[BrowserType, str] = {
    BrowserType.CHROME: "https://googlechromelabs.github.io/chrome-for-testing/",
    BrowserType.FIREFOX: "https://github.com/mozilla/geckodriver/releases",
    BrowserType.EDGE: "https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/",
}

# ================================================================
# Stealth Mode Defaults
# ================================================================

# Default user agents
DEFAULT_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
]

# Stealth JavaScript patches
STEALTH_PATCHES = [
    "webdriver",
    "chrome.runtime",
    "permissions",
    "plugins",
    "languages",
    "webgl.vendor",
    "navigator.vendor",
]

# ================================================================
# Performance & Resource Limits
# ================================================================

MAX_SESSIONS = 10  # Maximum concurrent sessions
DEFAULT_POOL_SIZE = 3  # Default driver pool size
MAX_RETRY_ATTEMPTS = 3  # Maximum retry attempts for recoverable errors
RETRY_DELAY = 2.0  # Delay between retries in seconds

# Memory limits (MB)
MAX_MEMORY_PER_BROWSER = 2048
WARNING_MEMORY_THRESHOLD = 1536

# ================================================================
# Logging Configuration
# ================================================================

LOG_FORMAT = "[%(asctime)s] %(levelname)s [%(name)s] %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
DEFAULT_LOG_LEVEL = "INFO"

# ================================================================
# Feature Flags
# ================================================================

ENABLE_EXPERIMENTAL_FEATURES = False
ENABLE_PERFORMANCE_MONITORING = True
ENABLE_SCREENSHOT_ON_ERROR = True
ENABLE_AUTO_CLEANUP = True
