"""Pytest configuration and fixtures for the application tests."""
import sys
import os

# Add backend directory to path so imports work correctly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from src.app import app
from src.config import TestingConfig


@pytest.fixture
def client():
    """Create a test client for the Flask application.
    
    This fixture configures the app in testing mode and provides
    a test client that can be used to make requests to the app.
    """
    app.config.from_object(TestingConfig())
    
    with app.app_context():
        yield app.test_client()


@pytest.fixture
def runner():
    """Create a CLI runner for testing CLI commands."""
    return app.test_cli_runner()


@pytest.fixture
def app_context():
    """Provide application context for tests that need it."""
    with app.app_context():
        yield app
