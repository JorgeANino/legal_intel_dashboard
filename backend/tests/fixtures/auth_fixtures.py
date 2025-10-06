"""
Authentication-related fixtures
"""
# Standard library imports
from unittest.mock import MagicMock

# Third-party imports
import pytest


@pytest.fixture
def mock_jwt_token():
    """Mock JWT token for testing"""
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZW1haWwiOiJ0ZXN0QGV4YW1wbGUuY29tIn0.test"


@pytest.fixture
def mock_login_credentials():
    """Mock login credentials for testing"""
    return {"email": "test@example.com", "password": "testpassword123"}


@pytest.fixture
def mock_login_response():
    """Mock successful login response"""
    return {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZW1haWwiOiJ0ZXN0QGV4YW1wbGUuY29tIn0.test",
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZW1haWwiOiJ0ZXN0QGV4YW1wbGUuY29tIn0.refresh",
        "token_type": "bearer",
        "user": {"id": 1, "email": "test@example.com", "full_name": "Test User", "is_active": True},
    }


@pytest.fixture
def mock_password_hash():
    """Mock hashed password for testing"""
    return "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8Kz8KzK"


@pytest.fixture
def mock_auth_dependencies():
    """Mock authentication dependencies"""
    return {
        "get_current_user": MagicMock(return_value={"id": 1, "email": "test@example.com"}),
        "verify_password": MagicMock(return_value=True),
        "get_password_hash": MagicMock(
            return_value="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8Kz8KzK"
        ),
    }
