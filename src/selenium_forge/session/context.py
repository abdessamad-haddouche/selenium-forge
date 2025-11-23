"""Context managers for WebDriver sessions."""

from __future__ import annotations

from types import TracebackType
from typing import Optional, Type

from selenium.webdriver.remote.webdriver import WebDriver

from selenium_forge.core.types import DriverConfig
from selenium_forge.session.manager import SessionManager


class ForgeContext:
    """Context manager for WebDriver sessions.

    Automatically creates and cleans up WebDriver sessions.

    Example:
        with ForgeContext(config) as driver:
            driver.get("https://example.com")
        # Driver is automatically closed
    """

    def __init__(
        self,
        config: DriverConfig,
        session_manager: Optional[SessionManager] = None,
    ) -> None:
        """Initialize forge context.

        Args:
            config: Driver configuration
            session_manager: Optional session manager (creates new if not provided)
        """
        self.config = config
        self.session_manager = session_manager or SessionManager()
        self.session_id: Optional[str] = None
        self.driver: Optional[WebDriver] = None

    def __enter__(self) -> WebDriver:
        """Enter context and create session.

        Returns:
            WebDriver instance
        """
        self.session_id, self.driver = self.session_manager.create_session(
            self.config
        )
        return self.driver

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """Exit context and cleanup session.

        Args:
            exc_type: Exception type
            exc_val: Exception value
            exc_tb: Exception traceback
        """
        if self.session_id:
            self.session_manager.close_session(self.session_id)


class ForgeSessionManager:
    """Context manager for SessionManager.

    Automatically cleans up all sessions on exit.

    Example:
        with ForgeSessionManager() as manager:
            session_id, driver = manager.create_session(config)
            # Use driver
        # All sessions automatically closed
    """

    def __init__(self) -> None:
        """Initialize session manager context."""
        self.session_manager = SessionManager()

    def __enter__(self) -> SessionManager:
        """Enter context.

        Returns:
            SessionManager instance
        """
        return self.session_manager

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """Exit context and cleanup all sessions.

        Args:
            exc_type: Exception type
            exc_val: Exception value
            exc_tb: Exception traceback
        """
        self.session_manager.close_all_sessions()
