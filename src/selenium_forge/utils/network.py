"""Network utilities for connectivity and proxy management."""

from __future__ import annotations

import socket
from typing import Optional, Tuple
from urllib.parse import urlparse

import requests

from selenium_forge.core.types import ProxyConfig
from selenium_forge.exceptions import RetryableError, UserError


class NetworkUtils:
    """Network-related utilities."""

    @staticmethod
    def check_connectivity(
        host: str = "8.8.8.8",
        port: int = 53,
        timeout: float = 5.0,
    ) -> bool:
        """Check if internet connectivity is available.

        Args:
            host: Host to connect to (default: Google DNS)
            port: Port to connect to
            timeout: Connection timeout in seconds

        Returns:
            True if connected, False otherwise
        """
        try:
            socket.create_connection((host, port), timeout=timeout)
            return True
        except (socket.error, socket.timeout):
            return False

    @staticmethod
    def check_url_accessible(url: str, timeout: float = 10.0) -> bool:
        """Check if URL is accessible.

        Args:
            url: URL to check
            timeout: Request timeout in seconds

        Returns:
            True if accessible, False otherwise
        """
        try:
            response = requests.head(url, timeout=timeout, allow_redirects=True)
            return response.status_code < 500
        except Exception:
            return False

    @staticmethod
    def test_proxy(
        proxy_config: ProxyConfig,
        test_url: str = "https://httpbin.org/ip",
        timeout: float = 10.0,
    ) -> Tuple[bool, Optional[str]]:
        """Test if proxy is working.

        Args:
            proxy_config: Proxy configuration
            test_url: URL to test with
            timeout: Request timeout in seconds

        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Build proxy URL
            proxy_url = f"{proxy_config.proxy_type}://"
            if proxy_config.username and proxy_config.password:
                proxy_url += f"{proxy_config.username}:{proxy_config.password}@"
            proxy_url += f"{proxy_config.host}:{proxy_config.port}"

            proxies = {
                "http": proxy_url,
                "https": proxy_url,
            }

            response = requests.get(test_url, proxies=proxies, timeout=timeout)
            if response.status_code == 200:
                return (True, None)
            else:
                return (False, f"HTTP {response.status_code}")

        except requests.exceptions.ProxyError as e:
            return (False, f"Proxy error: {e}")
        except requests.exceptions.Timeout:
            return (False, "Timeout")
        except requests.exceptions.ConnectionError as e:
            return (False, f"Connection error: {e}")
        except Exception as e:
            return (False, f"Unknown error: {e}")

    @staticmethod
    def get_public_ip(
        proxy: Optional[ProxyConfig] = None,
        timeout: float = 10.0,
    ) -> Optional[str]:
        """Get public IP address.

        Args:
            proxy: Optional proxy configuration
            timeout: Request timeout in seconds

        Returns:
            Public IP address, or None if unavailable
        """
        try:
            proxies = None
            if proxy:
                proxy_url = f"{proxy.proxy_type}://"
                if proxy.username and proxy.password:
                    proxy_url += f"{proxy.username}:{proxy.password}@"
                proxy_url += f"{proxy.host}:{proxy.port}"
                proxies = {"http": proxy_url, "https": proxy_url}

            response = requests.get(
                "https://api.ipify.org?format=json",
                proxies=proxies,
                timeout=timeout,
            )
            if response.status_code == 200:
                return response.json().get("ip")
        except Exception:
            pass

        return None

    @staticmethod
    def parse_proxy_url(proxy_url: str) -> ProxyConfig:
        """Parse proxy URL into ProxyConfig.

        Args:
            proxy_url: Proxy URL (e.g., "http://user:pass@host:port")

        Returns:
            ProxyConfig object

        Raises:
            UserError: If URL is invalid
        """
        try:
            return ProxyConfig.from_url(proxy_url)
        except ValueError as e:
            raise UserError(
                f"Invalid proxy URL: {proxy_url}",
                cause=e,
                suggestion="Format: protocol://[user:pass@]host:port",
            )

    @staticmethod
    def get_free_port(host: str = "127.0.0.1") -> int:
        """Get a free port on the system.

        Args:
            host: Host to bind to

        Returns:
            Free port number
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, 0))
            s.listen(1)
            port = s.getsockname()[1]
        return port

    @staticmethod
    def is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
        """Check if port is in use.

        Args:
            port: Port number
            host: Host to check

        Returns:
            True if port is in use, False otherwise
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((host, port))
                return False
            except socket.error:
                return True

    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format.

        Args:
            url: URL to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    @staticmethod
    def resolve_hostname(hostname: str, timeout: float = 5.0) -> Optional[str]:
        """Resolve hostname to IP address.

        Args:
            hostname: Hostname to resolve
            timeout: Resolution timeout in seconds

        Returns:
            IP address, or None if resolution fails
        """
        try:
            socket.setdefaulttimeout(timeout)
            return socket.gethostbyname(hostname)
        except (socket.gaierror, socket.timeout):
            return None
        finally:
            socket.setdefaulttimeout(None)
