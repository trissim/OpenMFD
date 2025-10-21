"""Global pytest configuration for OpenMFD tests."""
import os
import pytest


def pytest_addoption(parser):
    """Add command-line options for test configuration."""
    
    parser.addoption(
        "--skip-slow",
        action="store_true",
        default=False,
        help="Skip slow tests (e.g., OpenSCAD rendering)"
    )
    
    parser.addoption(
        "--skip-openscad",
        action="store_true",
        default=False,
        help="Skip tests that require OpenSCAD"
    )


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests for individual components"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests for component interactions"
    )
    config.addinivalue_line(
        "markers", "slow: Slow tests (e.g., OpenSCAD rendering)"
    )
    config.addinivalue_line(
        "markers", "requires_openscad: Tests that require OpenSCAD to be installed"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection based on command-line options."""
    skip_slow = pytest.mark.skip(reason="--skip-slow option provided")
    skip_openscad = pytest.mark.skip(reason="--skip-openscad option provided")
    
    for item in items:
        if config.getoption("--skip-slow") and "slow" in item.keywords:
            item.add_marker(skip_slow)
        if config.getoption("--skip-openscad") and "requires_openscad" in item.keywords:
            item.add_marker(skip_openscad)


@pytest.fixture
def sample_dims():
    """Sample device dimensions for testing."""
    return [18.0, 9.0, 0.2]


@pytest.fixture
def sample_grid_size():
    """Sample grid size for testing."""
    return [6, 8]


@pytest.fixture
def sample_wafer_size():
    """Sample wafer size for testing."""
    return 150.0


@pytest.fixture
def sample_flat_length():
    """Sample flat edge length for testing."""
    return 57.5
