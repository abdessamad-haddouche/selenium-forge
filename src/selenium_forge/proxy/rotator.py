"""Proxy rotation strategies."""

from __future__ import annotations

import random
from collections import defaultdict
from typing import Dict, List, Optional

from selenium_forge.core.types import ProxyConfig, ProxyRotationConfig
from selenium_forge.exceptions import UserError
from selenium_forge.proxy.manager import ProxyManager


class ProxyRotator:
    """Manages proxy rotation with various strategies."""

    def __init__(
        self,
        config: ProxyRotationConfig,
        proxy_manager: Optional[ProxyManager] = None,
    ) -> None:
        """Initialize proxy rotator.

        Args:
            config: Proxy rotation configuration
            proxy_manager: Proxy manager instance (optional)
        """
        self.config = config
        self.proxy_manager = proxy_manager or ProxyManager()
        self.current_index = 0
        self.failure_counts: Dict[str, int] = defaultdict(int)
        self.usage_counts: Dict[str, int] = defaultdict(int)

        # Validate proxies on initialization if health check is enabled
        if self.config.health_check_enabled:
            self._validate_proxies()

    def _validate_proxies(self) -> None:
        """Validate all proxies and remove non-working ones."""
        working_proxies: List[ProxyConfig] = []

        for proxy in self.config.proxies:
            success, _ = self.proxy_manager.validate_proxy(
                proxy,
                timeout=self.config.health_check_timeout,
            )
            if success:
                working_proxies.append(proxy)

        if not working_proxies:
            raise UserError(
                "No working proxies found in rotation pool",
                suggestion="Check proxy configurations and network connectivity",
            )

        self.config.proxies = working_proxies

    def _get_proxy_key(self, proxy: ProxyConfig) -> str:
        """Get unique key for proxy.

        Args:
            proxy: Proxy configuration

        Returns:
            Unique key string
        """
        return f"{proxy.host}:{proxy.port}"

    def get_next_proxy(self) -> ProxyConfig:
        """Get next proxy based on rotation strategy.

        Returns:
            Next proxy configuration

        Raises:
            UserError: If no proxies are available
        """
        if not self.config.proxies:
            raise UserError(
                "No proxies available in rotation pool",
                suggestion="Add proxies to the rotation configuration",
            )

        strategy = self.config.rotation_strategy.lower()

        if strategy == "round-robin":
            return self._get_round_robin_proxy()
        elif strategy == "random":
            return self._get_random_proxy()
        elif strategy == "least-used":
            return self._get_least_used_proxy()
        else:
            # Default to round-robin
            return self._get_round_robin_proxy()

    def _get_round_robin_proxy(self) -> ProxyConfig:
        """Get proxy using round-robin strategy."""
        # Filter out failed proxies
        available_proxies = [
            proxy
            for proxy in self.config.proxies
            if self.failure_counts[self._get_proxy_key(proxy)]
            < self.config.max_failures_per_proxy
        ]

        if not available_proxies:
            # Reset failure counts and try again
            self.failure_counts.clear()
            available_proxies = self.config.proxies

        proxy = available_proxies[self.current_index % len(available_proxies)]
        self.current_index += 1
        self.usage_counts[self._get_proxy_key(proxy)] += 1

        return proxy

    def _get_random_proxy(self) -> ProxyConfig:
        """Get proxy using random strategy."""
        # Filter out failed proxies
        available_proxies = [
            proxy
            for proxy in self.config.proxies
            if self.failure_counts[self._get_proxy_key(proxy)]
            < self.config.max_failures_per_proxy
        ]

        if not available_proxies:
            # Reset failure counts and try again
            self.failure_counts.clear()
            available_proxies = self.config.proxies

        proxy = random.choice(available_proxies)
        self.usage_counts[self._get_proxy_key(proxy)] += 1

        return proxy

    def _get_least_used_proxy(self) -> ProxyConfig:
        """Get proxy using least-used strategy."""
        # Filter out failed proxies
        available_proxies = [
            proxy
            for proxy in self.config.proxies
            if self.failure_counts[self._get_proxy_key(proxy)]
            < self.config.max_failures_per_proxy
        ]

        if not available_proxies:
            # Reset failure counts and try again
            self.failure_counts.clear()
            available_proxies = self.config.proxies

        # Find proxy with least usage
        proxy = min(
            available_proxies,
            key=lambda p: self.usage_counts[self._get_proxy_key(p)],
        )
        self.usage_counts[self._get_proxy_key(proxy)] += 1

        return proxy

    def report_failure(self, proxy: ProxyConfig) -> None:
        """Report proxy failure.

        Args:
            proxy: Failed proxy configuration
        """
        proxy_key = self._get_proxy_key(proxy)
        self.failure_counts[proxy_key] += 1

    def report_success(self, proxy: ProxyConfig) -> None:
        """Report proxy success (resets failure count).

        Args:
            proxy: Successful proxy configuration
        """
        proxy_key = self._get_proxy_key(proxy)
        self.failure_counts[proxy_key] = 0

    def get_statistics(self) -> Dict[str, Dict[str, int]]:
        """Get usage and failure statistics.

        Returns:
            Dictionary with statistics for each proxy
        """
        stats: Dict[str, Dict[str, int]] = {}

        for proxy in self.config.proxies:
            proxy_key = self._get_proxy_key(proxy)
            stats[proxy_key] = {
                "usage_count": self.usage_counts.get(proxy_key, 0),
                "failure_count": self.failure_counts.get(proxy_key, 0),
            }

        return stats

    def reset_statistics(self) -> None:
        """Reset all usage and failure statistics."""
        self.failure_counts.clear()
        self.usage_counts.clear()
        self.current_index = 0
