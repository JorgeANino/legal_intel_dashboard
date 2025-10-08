"""
Shared pytest fixtures for all tests
"""
# Standard library imports
import io
import sys
from unittest.mock import AsyncMock, MagicMock, patch

# Third-party imports
import pytest
from fastapi.testclient import TestClient

# Local application imports
from app.core.database import get_db
from app.core.security import get_current_user
from app.main import app
from app.middleware.rate_limit import rate_limit_dependency
from app.models.user import User


# Patch DocumentService globally to prevent filesystem operations
_doc_service_patcher = patch("app.api.v1.endpoints.documents.DocumentService")
_mock_doc_service_class = _doc_service_patcher.start()
_mock_doc_service_instance = MagicMock()
_mock_doc_service_class.return_value = _mock_doc_service_instance
_mock_doc_service_instance.save_uploaded_file = AsyncMock()
_mock_doc_service_instance.get_document = AsyncMock(return_value=None)
_mock_doc_service_instance.list_documents = AsyncMock(return_value=[])

# Make the mock instance available globally for tests
sys.modules[__name__]._mock_doc_service_instance = _mock_doc_service_instance

# Patch Celery tasks globally to prevent Redis connection issues
_celery_task_patcher = patch("app.api.v1.endpoints.documents.process_document_task")
_mock_celery_task = _celery_task_patcher.start()
_mock_celery_task.delay = MagicMock()
_mock_celery_task.apply_async = MagicMock()

# Patch cache service globally to prevent Redis connection issues
_cache_service_patcher = patch("app.api.v1.endpoints.documents.cache_service")
_mock_cache_service = _cache_service_patcher.start()
_mock_cache_service.delete = AsyncMock()
_mock_cache_service.get = AsyncMock(return_value=None)
_mock_cache_service.set = AsyncMock()


def pytest_sessionfinish(session, exitstatus):
    """Clean up patches after all tests are done"""
    _doc_service_patcher.stop()
    _celery_task_patcher.stop()
    _cache_service_patcher.stop()


# Database mocks
async def mock_get_db():
    """Mock database session that returns a mock AsyncSession"""
    mock_session = AsyncMock()

    # Create a mock result object for db.execute() calls
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=None)
    mock_result.scalars = MagicMock()
    mock_result.scalars.return_value.all = MagicMock(return_value=[])
    mock_result.scalars.return_value.first = MagicMock(return_value=None)

    # Set up the session methods
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_session.close = AsyncMock()
    mock_session.refresh = AsyncMock()
    mock_session.add = MagicMock()
    mock_session.delete = AsyncMock()
    mock_session.scalar = AsyncMock(return_value=None)

    yield mock_session


async def mock_get_current_user():
    """Mock user for authenticated endpoints"""
    user = MagicMock(spec=User)
    user.id = 1
    user.email = "test@example.com"
    user.full_name = "Test User"
    user.is_active = True
    user.is_superuser = False
    return user


async def mock_rate_limit():
    """Mock rate limiting - always allow requests in tests"""
    return None


@pytest.fixture
def client():
    """Create a test client for the FastAPI app with mocked dependencies"""
    # Override all external dependencies
    app.dependency_overrides[get_db] = mock_get_db
    app.dependency_overrides[get_current_user] = mock_get_current_user
    app.dependency_overrides[rate_limit_dependency] = mock_rate_limit

    client = TestClient(app)
    yield client

    app.dependency_overrides.clear()


@pytest.fixture
def client_no_auth():
    """Create a test client WITHOUT authentication (for testing auth failures)"""
    # Override only DB and rate limit, not auth
    app.dependency_overrides[get_db] = mock_get_db
    app.dependency_overrides[rate_limit_dependency] = mock_rate_limit

    client = TestClient(app)
    yield client

    app.dependency_overrides.clear()


@pytest.fixture
def mock_user():
    """Mock user data for testing"""
    return {
        "id": 1,
        "email": "test@example.com",
        "full_name": "Test User",
        "is_active": True,
        "is_superuser": False,
    }


@pytest.fixture
def mock_document():
    """Mock document data for testing"""
    document = MagicMock()
    document.id = 1
    document.filename = "test_contract.pdf"
    document.file_type = "application/pdf"
    document.file_path = "/uploads/test_contract.pdf"
    document.file_size = 1024000
    document.upload_date = "2024-01-01T12:00:00Z"
    document.created_at = "2024-01-01T12:00:00Z"
    document.processed = True
    document.processing_error = None
    document.page_count = 5
    document.user_id = 1
    document.doc_metadata = {
        "id": 1,
        "document_id": 1,
        "parties": ["Company A", "Company B"],
        "agreement_date": "2024-01-01",
        "governing_law": "Delaware",
        "jurisdiction": "Delaware",
        "agreement_type": "Service Agreement",
        "industry": "Technology",
        "geography": "North America",
    }
    return document


@pytest.fixture
def sample_pdf_file():
    """Create a sample PDF file for testing"""
    return ("test_contract.pdf", io.BytesIO(b"PDF content"), "application/pdf")


@pytest.fixture
def sample_docx_file():
    """Create a sample DOCX file for testing"""
    return (
        "test_contract.docx",
        io.BytesIO(b"DOCX content"),
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


@pytest.fixture
def mock_dashboard_stats():
    """Mock dashboard statistics for testing"""
    return {
        "total_documents": 10,
        "processed_documents": 8,
        "agreement_types": {"NDA": 3, "Service Agreement": 4, "License Agreement": 1},
        "jurisdictions": {"Delaware": 5, "New York": 3, "California": 2},
        "industries": {"Technology": 6, "Healthcare": 2, "Finance": 2},
        "geographies": {"North America": 8, "Europe": 2},
    }


@pytest.fixture
def mock_query_result():
    """Mock query result for testing"""
    return {
        "results": [
            {
                "document": "contract_1.pdf",
                "governing_law": "Delaware",
                "agreement_type": "Service Agreement",
            },
            {"document": "contract_2.pdf", "governing_law": "New York", "agreement_type": "NDA"},
        ],
        "total_results": 2,
        "query": "Which agreements are governed by Delaware law?",
    }


@pytest.fixture
def mock_database_session():
    """Mock database session for testing"""
    session = AsyncMock()
    session.execute.return_value = MagicMock()
    session.commit.return_value = None
    session.rollback.return_value = None
    session.close.return_value = None
    return session


@pytest.fixture
def mock_redis_client():
    """Mock Redis client for testing"""
    redis_client = AsyncMock()
    redis_client.get.return_value = None
    redis_client.set.return_value = None
    redis_client.delete.return_value = None
    redis_client.publish.return_value = None
    redis_client.close.return_value = None
    return redis_client
