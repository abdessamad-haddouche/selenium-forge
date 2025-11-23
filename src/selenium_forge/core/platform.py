"""Platform detection and system utilities."""

from __future__ import annotations

import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Optional

import platformdirs

from selenium_forge.core.constants import Architecture, BrowserType, OperatingSystem
from selenium_forge.core.types import SystemInfo
from selenium_forge.exceptions import InternalError, UserError


class PlatformDetector:
    """Detects platform information and system capabilities."""

    @staticmethod
    def detect_os() -> OperatingSystem:
        """Detect the operating system.

        Returns:
            Operating system type

        Raises:
            UserError: If OS is not supported
        """
        system = platform.system().lower()

        if system == "windows":
            return OperatingSystem.WINDOWS
        elif system == "darwin":
            return OperatingSystem.MACOS
        elif system == "linux":
            # Check if running under WSL
            if PlatformDetector.is_wsl():
                return OperatingSystem.WSL
            return OperatingSystem.LINUX
        else:
            raise UserError(
                f"Unsupported operating system: {system}",
                suggestion="Selenium Forge supports Windows, macOS, and Linux",
            )

    @staticmethod
    def is_wsl() -> bool:
        """Check if running under Windows Subsystem for Linux.

        Returns:
            True if running under WSL, False otherwise
        """
        try:
            # Check for WSL in /proc/version
            if Path("/proc/version").exists():
                with open("/proc/version", "r") as f:
                    version_info = f.read().lower()
                    return "microsoft" in version_info or "wsl" in version_info

            # Check for WSL environment variable
            if "WSL_DISTRO_NAME" in os.environ:
                return True

        except Exception:
            pass

        return False

    @staticmethod
    def detect_architecture() -> Architecture:
        """Detect system architecture.

        Returns:
            System architecture type

        Raises:
            UserError: If architecture is not supported
        """
        machine = platform.machine().lower()

        if machine in ("amd64", "x86_64", "x64"):
            return Architecture.X64
        elif machine in ("i386", "i686", "x86"):
            return Architecture.X86
        elif machine in ("arm64", "aarch64"):
            return Architecture.ARM64
        elif machine.startswith("arm"):
            return Architecture.ARM
        else:
            raise UserError(
                f"Unsupported architecture: {machine}",
                suggestion="Selenium Forge supports x64, x86, ARM64, and ARM architectures",
            )

    @staticmethod
    def has_display() -> bool:
        """Check if system has a display server.

        Returns:
            True if display is available, False otherwise
        """
        # Windows always has display
        if platform.system() == "Windows":
            return True

        # macOS always has display
        if platform.system() == "Darwin":
            return True

        # Linux: check for DISPLAY environment variable
        if "DISPLAY" in os.environ:
            return True

        # Check for Wayland
        if "WAYLAND_DISPLAY" in os.environ:
            return True

        return False

    @staticmethod
    def get_python_version() -> str:
        """Get Python version.

        Returns:
            Python version string
        """
        return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

    @staticmethod
    def get_selenium_version() -> str:
        """Get installed Selenium version.

        Returns:
            Selenium version string
        """
        try:
            import selenium

            return selenium.__version__
        except (ImportError, AttributeError):
            return "unknown"

    @staticmethod
    def get_system_info() -> SystemInfo:
        """Get comprehensive system information.

        Returns:
            SystemInfo object with all system details
        """
        return SystemInfo(
            os=str(PlatformDetector.detect_os()),
            os_version=platform.version(),
            architecture=str(PlatformDetector.detect_architecture()),
            python_version=PlatformDetector.get_python_version(),
            selenium_version=PlatformDetector.get_selenium_version(),
            is_wsl=PlatformDetector.is_wsl(),
            has_display=PlatformDetector.has_display(),
        )

    @staticmethod
    def get_cache_dir() -> Path:
        """Get the cache directory for selenium-forge.

        Returns:
            Path to cache directory
        """
        cache_dir = Path(platformdirs.user_cache_dir("selenium-forge", "selenium-forge"))
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir

    @staticmethod
    def get_config_dir() -> Path:
        """Get the configuration directory for selenium-forge.

        Returns:
            Path to config directory
        """
        config_dir = Path(
            platformdirs.user_config_dir("selenium-forge", "selenium-forge")
        )
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir

    @staticmethod
    def get_data_dir() -> Path:
        """Get the data directory for selenium-forge.

        Returns:
            Path to data directory
        """
        data_dir = Path(platformdirs.user_data_dir("selenium-forge", "selenium-forge"))
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir

    @staticmethod
    def find_browser_binary(browser: BrowserType) -> Optional[Path]:
        """Find browser binary on the system.

        Args:
            browser: Browser type to find

        Returns:
            Path to browser binary, or None if not found
        """
        from selenium_forge.core.constants import BROWSER_PATHS

        os_type = PlatformDetector.detect_os()
        paths = BROWSER_PATHS.get(os_type, {}).get(browser, [])

        for path_str in paths:
            # Expand environment variables
            path_str = os.path.expandvars(path_str)
            path = Path(path_str)

            if path.exists():
                return path

        # Try to find in PATH
        binary_names = {
            BrowserType.CHROME: ["google-chrome", "chrome", "chromium"],
            BrowserType.FIREFOX: ["firefox"],
            BrowserType.EDGE: ["microsoft-edge", "msedge"],
            BrowserType.SAFARI: ["safari"],
        }

        for binary_name in binary_names.get(browser, []):
            try:
                if os_type == OperatingSystem.WINDOWS:
                    # Use where on Windows
                    result = subprocess.run(
                        ["where", binary_name],
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                else:
                    # Use which on Unix-like systems
                    result = subprocess.run(
                        ["which", binary_name],
                        capture_output=True,
                        text=True,
                        check=False,
                    )

                if result.returncode == 0 and result.stdout.strip():
                    return Path(result.stdout.strip().split("\n")[0])

            except Exception:
                continue

        return None

    @staticmethod
    def get_browser_version(browser_path: Path) -> Optional[str]:
        """Get browser version from binary.

        Args:
            browser_path: Path to browser binary

        Returns:
            Browser version string, or None if unable to determine
        """
        if not browser_path.exists():
            return None

        try:
            # Try different version commands based on browser
            commands = [
                [str(browser_path), "--version"],
                [str(browser_path), "-version"],
                [str(browser_path), "version"],
            ]

            for cmd in commands:
                try:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=5,
                        check=False,
                    )
                    if result.returncode == 0 and result.stdout.strip():
                        # Extract version number
                        import re

                        version_match = re.search(
                            r"(\d+\.\d+\.\d+(?:\.\d+)?)", result.stdout
                        )
                        if version_match:
                            return version_match.group(1)
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    continue

        except Exception:
            pass

        return None

    @staticmethod
    def check_internet_connection(timeout: float = 5.0) -> bool:
        """Check if internet connection is available.

        Args:
            timeout: Connection timeout in seconds

        Returns:
            True if internet is available, False otherwise
        """
        import socket

        try:
            # Try to connect to Google DNS
            socket.create_connection(("8.8.8.8", 53), timeout=timeout)
            return True
        except (socket.error, socket.timeout):
            return False

    @staticmethod
    def get_free_port() -> int:
        """Get a free port on the system.

        Returns:
            Free port number
        """
        import socket

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            s.listen(1)
            port = s.getsockname()[1]
        return port
