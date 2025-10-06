"""
Shared pytest fixtures for all tests
"""
# Standard library imports
import io
from unittest.mock import AsyncMock, MagicMock

# Third-party imports
import pytest
from fastapi.testclient import TestClient

# Local application imports
from app.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def mock_user():
    """Mock user data for testing"""
    return {
        "id": 1,
        "email": "test@example.com",
        "full_name": "Test User",
        "is_active": True,
        "is_superuser": False
    }


@pytest.fixture
def mock_document():
    """Mock document data for testing"""
    return {
        "id": 1,
        "filename": "test_contract.pdf",
        "file_size": 1024000,
        "upload_date": "2024-01-01T12:00:00Z",
        "processed": True,
        "processing_error": None,
        "user_id": 1,
        "metadata": {
            "id": 1,
            "document_id": 1,
            "parties": ["Company A", "Company B"],
            "agreement_date": "2024-01-01",
            "governing_law": "Delaware",
            "jurisdiction": "Delaware",
            "agreement_type": "Service Agreement",
            "industry": "Technology",
            "geography": "North America"
        }
    }


@pytest.fixture
def sample_pdf_file():
    """Create a sample PDF file for testing"""
    return ("test_contract.pdf", io.BytesIO(b"PDF content"), "application/pdf")


@pytest.fixture
def sample_docx_file():
    """Create a sample DOCX file for testing"""
    return ("test_contract.docx", io.BytesIO(b"DOCX content"), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")


@pytest.fixture
def mock_dashboard_stats():
    """Mock dashboard statistics for testing"""
    return {
        "total_documents": 10,
        "processed_documents": 8,
        "agreement_types": {
            "NDA": 3,
            "Service Agreement": 4,
            "License Agreement": 1
        },
        "jurisdictions": {
            "Delaware": 5,
            "New York": 3,
            "California": 2
        },
        "industries": {
            "Technology": 6,
            "Healthcare": 2,
            "Finance": 2
        },
        "geographies": {
            "North America": 8,
            "Europe": 2
        }
    }


@pytest.fixture
def mock_query_result():
    """Mock query result for testing"""
    return {
        "results": [
            {
                "document": "contract_1.pdf",
                "governing_law": "Delaware",
                "agreement_type": "Service Agreement"
            },
            {
                "document": "contract_2.pdf",
                "governing_law": "New York",
                "agreement_type": "NDA"
            }
        ],
        "total_results": 2,
        "query": "Which agreements are governed by Delaware law?"
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


