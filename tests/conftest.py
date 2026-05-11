"""Global pytest configuration for LECS host management test suite.

Provides common hooks, path setup, and shared fixtures available to
all test modules. Per-feature conftest.py files (e.g., in
tests/integration/001-lecs-host-management/) handle feature-specific
fixtures and SHOULD NOT be duplicated here.

This file is automatically discovered by pytest and applies to all
tests under the tests/ directory.
"""

import sys
from pathlib import Path

import pytest

# Path configuration
PROJECT_ROOT = Path(__file__).resolve().parent.parent
TESTS_DIR = PROJECT_ROOT / "tests"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

# Legacy backend path (preserve existing behavior)
_BACKEND_SRC = Path(__file__).resolve().parent.parent / "backend" / "src"
if _BACKEND_SRC.exists() and str(_BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(_BACKEND_SRC))


def pytest_configure(config):
    """Register custom markers and configure test environment.

    Called once at the start of the test session. Registers markers
    used by the LECS host management test suite:

    - e2e: End-to-end tests (Playwright browser automation)
    - integration: Integration tests (API + DB, no browser)
    - slow: Tests that take >5s to execute
    - auth: Authentication/authorization related tests
    - pricing: Billing and cost calculation tests
    - async_lifecycle: Async task state machine tests
    """
    config.addinivalue_line(
        "markers", "e2e: End-to-end tests (Playwright browser automation)"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests (API + database)"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take longer than 5 seconds"
    )
    config.addinivalue_line(
        "markers", "auth: Authentication and authorization tests"
    )
    config.addinivalue_line(
        "markers", "pricing: Billing and cost calculation tests"
    )
    config.addinivalue_line(
        "markers", "async_lifecycle: Async task state machine tests"
    )


def pytest_runtest_setup(item):
    markers = [m.name for m in item.iter_markers()]
    if markers:
        item.user_properties.append(("markers", ",".join(markers)))


@pytest.fixture(scope="session")
def fixtures_path():
    """Return the absolute path to the shared fixtures directory.

    Usage:
        def test_something(fixtures_path):
            data_file = fixtures_path / "mocks" / "billing_data.json"
    """
    return TESTS_DIR / "fixtures"


@pytest.fixture
def factory_path(fixtures_path):
    """Return the path to the factories directory."""
    return fixtures_path / "factories"


@pytest.fixture
def mocks_path(fixtures_path):
    """Return the path to the mocks directory."""
    return fixtures_path / "mocks"
