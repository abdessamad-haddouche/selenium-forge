"""Proxy management and validation."""

from __future__ import annotations

from typing import List, Optional, Tuple

from selenium_forge.core.types import ProxyConfig
from selenium_forge.exceptions import UserError
from selenium_forge.utils.network import NetworkUtils


class ProxyManager:
    """Manages proxy configurations and validation."""

    def __init__(self) -> None:
        """Initialize proxy manager."""
        self.network_utils = NetworkUtils()

    def validate_proxy(
        self,
        proxy: ProxyConfig,
        timeout: float = 10.0,
    ) -> Tuple[bool, Optional[str]]:
        """Validate proxy configuration.

        Args:
            proxy: Proxy configuration
            timeout: Validation timeout in seconds

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Test basic connectivity
        success, error = self.network_utils.test_proxy(
            proxy,
            timeout=timeout,
        )

        return (success, error)

    def test_proxy_speed(
        self,
        proxy: ProxyConfig,
        test_url: str = "https://httpbin.org/ip",
    ) -> Optional[float]:
        """Test proxy response time.

        Args:
            proxy: Proxy configuration
            test_url: URL to test with

        Returns:
            Response time in seconds, or None if test fails
        """
        import time
        import requests

        try:
            proxy_url = f"{proxy.proxy_type}://"
            if proxy.username and proxy.password:
                proxy_url += f"{proxy.username}:{proxy.password}@"
            proxy_url += f"{proxy.host}:{proxy.port}"

            proxies = {
                "http": proxy_url,
                "https": proxy_url,
            }

            start_time = time.time()
            response = requests.get(test_url, proxies=proxies, timeout=10)
            end_time = time.time()

            if response.status_code == 200:
                return end_time - start_time

        except Exception:
            pass

        return None

    def get_proxy_ip(self, proxy: ProxyConfig) -> Optional[str]:
        """Get public IP when using proxy.

        Args:
            proxy: Proxy configuration

        Returns:
            Public IP address, or None if unavailable
        """
        return self.network_utils.get_public_ip(proxy)

    def load_proxies_from_file(self, file_path: str) -> List[ProxyConfig]:
        """Load proxy list from file.

        File format: one proxy per line
        Format: protocol://[user:pass@]host:port

        Args:
            file_path: Path to proxy list file

        Returns:
            List of ProxyConfig objects

        Raises:
            UserError: If file cannot be loaded
        """
        from pathlib import Path

        path = Path(file_path)
        if not path.exists():
            raise UserError(f"Proxy file not found: {file_path}")

        proxies: List[ProxyConfig] = []

        try:
            with open(path, "r") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue

                    try:
                        proxy = ProxyConfig.from_url(line)
                        proxies.append(proxy)
                    except Exception as e:
                        import warnings
                        warnings.warn(f"Invalid proxy on line {line_num}: {line}")

        except Exception as e:
            raise UserError(
                f"Failed to load proxy file: {e}",
                cause=e,
            )

        return proxies

    def filter_working_proxies(
        self,
        proxies: List[ProxyConfig],
        timeout: float = 10.0,
        max_workers: int = 10,
    ) -> List[ProxyConfig]:
        """Filter list to only working proxies.

        Args:
            proxies: List of proxy configurations
            timeout: Validation timeout per proxy
            max_workers: Maximum concurrent validation workers

        Returns:
            List of working proxies
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed

        working_proxies: List[ProxyConfig] = []

        def test_proxy(proxy: ProxyConfig) -> Optional[ProxyConfig]:
            success, _ = self.validate_proxy(proxy, timeout)
            return proxy if success else None

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(test_proxy, proxy) for proxy in proxies]

            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result:
                        working_proxies.append(result)
                except Exception:
                    continue

        return working_proxies
