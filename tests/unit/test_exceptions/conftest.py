"""Shared utilities for unit tests."""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timezone

@pytest.fixture
def mock_datetime():
    """Mock datetime for consistent testing."""
    fixed_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    with patch('selenium_forge.exceptions.base.datetime') as mock_dt:
        mock_dt.now.return_value = fixed_time
        yield mock_dt

@pytest.fixture
def mock_traceback():
    """Mock traceback for predictable output."""
    with patch('selenium_forge.exceptions.base.traceback') as mock_tb:
        mock_tb.format_exc.return_value = "Mocked traceback"  # Remove the extra part
        yield mock_tb

@pytest.fixture
def suppress_warnings():
    """Suppress warnings during testing."""
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        yield