"""Session manager for WebDriver lifecycle management."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Dict, Optional

from selenium.webdriver.remote.webdriver import WebDriver

from selenium_forge.core.types import DriverConfig, SessionInfo
from selenium_forge.drivers.factory import DriverFactory
from selenium_forge.exceptions import UserError
from selenium_forge.stealth.engine import StealthEngine


class SessionManager:
    """Manages WebDriver session lifecycle."""

    def __init__(self) -> None:
        """Initialize session manager."""
        self.sessions: Dict[str, Dict] = {}
        self.driver_factory = DriverFactory()

    def create_session(
        self,
        config: DriverConfig,
        session_id: Optional[str] = None,
    ) -> tuple[str, WebDriver]:
        """Create a new browser session.

        Args:
            config: Driver configuration
            session_id: Optional custom session ID

        Returns:
            Tuple of (session_id, driver)

        Raises:
            UserError: If session creation fails
        """
        # Generate session ID if not provided
        if session_id is None:
            session_id = str(uuid.uuid4())

        # Check if session ID already exists
        if session_id in self.sessions:
            raise UserError(
                f"Session ID already exists: {session_id}",
                suggestion="Use a different session ID or close existing session",
            )

        try:
            # Create driver
            driver = self.driver_factory.create_driver(config)

            # Apply stealth mode if configured
            if config.stealth and config.stealth.enabled:
                stealth_engine = StealthEngine(config.stealth)
                stealth_engine.apply_stealth(driver)

            # Store session info
            self.sessions[session_id] = {
                "driver": driver,
                "config": config,
                "created_at": datetime.now().isoformat(),
                "last_activity": datetime.now().isoformat(),
            }

            return session_id, driver

        except Exception as e:
            if isinstance(e, UserError):
                raise
            raise UserError(
                f"Failed to create session: {e}",
                cause=e,
            )

    def get_session(self, session_id: str) -> Optional[WebDriver]:
        """Get WebDriver for session.

        Args:
            session_id: Session ID

        Returns:
            WebDriver instance, or None if not found
        """
        session = self.sessions.get(session_id)
        if session:
            # Update last activity
            session["last_activity"] = datetime.now().isoformat()
            return session["driver"]
        return None

    def close_session(self, session_id: str) -> bool:
        """Close a browser session.

        Args:
            session_id: Session ID to close

        Returns:
            True if session was closed, False if not found
        """
        session = self.sessions.get(session_id)
        if not session:
            return False

        try:
            driver = session["driver"]
            driver.quit()
        except Exception:
            # Ignore errors during cleanup
            pass
        finally:
            del self.sessions[session_id]

        return True

    def close_all_sessions(self) -> int:
        """Close all active sessions.

        Returns:
            Number of sessions closed
        """
        session_ids = list(self.sessions.keys())
        closed_count = 0

        for session_id in session_ids:
            if self.close_session(session_id):
                closed_count += 1

        return closed_count

    def get_session_info(self, session_id: str) -> Optional[SessionInfo]:
        """Get information about a session.

        Args:
            session_id: Session ID

        Returns:
            SessionInfo object, or None if not found
        """
        session = self.sessions.get(session_id)
        if not session:
            return None

        driver = session["driver"]
        config = session["config"]

        try:
            capabilities = driver.capabilities
            is_active = True
        except Exception:
            capabilities = {}
            is_active = False

        return SessionInfo(
            session_id=session_id,
            browser=config.browser,
            created_at=session["created_at"],
            last_activity=session["last_activity"],
            is_active=is_active,
            capabilities=capabilities,
        )

    def list_sessions(self) -> list[SessionInfo]:
        """List all active sessions.

        Returns:
            List of SessionInfo objects
        """
        sessions = []
        for session_id in self.sessions.keys():
            info = self.get_session_info(session_id)
            if info:
                sessions.append(info)
        return sessions

    def get_session_count(self) -> int:
        """Get number of active sessions.

        Returns:
            Session count
        """
        return len(self.sessions)

    def __del__(self) -> None:
        """Cleanup on deletion."""
        self.close_all_sessions()
