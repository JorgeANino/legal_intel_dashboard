"""
Database-related fixtures
"""
# Standard library imports
from unittest.mock import AsyncMock, MagicMock

# Third-party imports
import pytest


@pytest.fixture
def mock_database_session():
    """Mock database session for testing"""
    session = AsyncMock()
    session.execute.return_value = MagicMock()
    session.commit.return_value = None
    session.rollback.return_value = None
    session.close.return_value = None
    session.refresh.return_value = None
    session.add.return_value = None
    session.delete.return_value = None
    return session


@pytest.fixture
def mock_database_result():
    """Mock database query result"""
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    result.scalars.return_value.all.return_value = []
    result.scalars.return_value.first.return_value = None
    return result


@pytest.fixture
def mock_user_model():
    """Mock User model instance"""
    user = MagicMock()
    user.id = 1
    user.email = "test@example.com"
    user.full_name = "Test User"
    user.is_active = True
    user.is_superuser = False
    user.hashed_password = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8Kz8KzK"
    return user


@pytest.fixture
def mock_document_model():
    """Mock Document model instance"""
    document = MagicMock()
    document.id = 1
    document.filename = "test_contract.pdf"
    document.file_size = 1024000
    document.upload_date = "2024-01-01T12:00:00Z"
    document.processed = True
    document.processing_error = None
    document.user_id = 1
    return document


@pytest.fixture
def mock_database_connection():
    """Mock database connection"""
    connection = AsyncMock()
    connection.execute.return_value = MagicMock()
    connection.commit.return_value = None
    connection.rollback.return_value = None
    connection.close.return_value = None
    return connection


