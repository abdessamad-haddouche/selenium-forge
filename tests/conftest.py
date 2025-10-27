"""Global test configuration for selenium-forge."""

import pytest
from pathlib import Path

# Project constants
PROJECT_ROOT = Path(__file__).parent.parent
TEST_DATA_DIR = Path(__file__).parent / "fixtures"

@pytest.fixture(scope="session")
def project_root():
    """Project root directory."""
    return PROJECT_ROOT

@pytest.fixture(scope="session") 
def test_data_dir():
    """Test fixtures directory."""
    return TEST_DATA_DIR

# Pytest configuration
def pytest_configure(config):
    """Add custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests")