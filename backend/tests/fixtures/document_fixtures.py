"""
Document-related fixtures
"""
# Standard library imports
import io
from unittest.mock import MagicMock

# Third-party imports
import pytest


@pytest.fixture
def mock_document_metadata():
    """Mock document metadata for testing"""
    return {
        "id": 1,
        "document_id": 1,
        "parties": ["Company A", "Company B"],
        "agreement_date": "2024-01-01",
        "governing_law": "Delaware",
        "jurisdiction": "Delaware",
        "agreement_type": "Service Agreement",
        "industry": "Technology",
        "geography": "North America",
        "extracted_text": "This is a sample contract text...",
        "created_at": "2024-01-01T12:00:00Z",
        "updated_at": "2024-01-01T12:00:00Z",
    }


@pytest.fixture
def mock_document_chunk():
    """Mock document chunk for testing"""
    return {
        "id": 1,
        "document_id": 1,
        "chunk_index": 0,
        "content": "This is a sample chunk of text from the document.",
        "embedding": [0.1, 0.2, 0.3, 0.4, 0.5],  # Mock embedding vector
        "metadata": {"page": 1, "section": "introduction"},
        "created_at": "2024-01-01T12:00:00Z",
    }


@pytest.fixture
def mock_upload_response():
    """Mock document upload response"""
    return {
        "documents": [
            {
                "id": 1,
                "filename": "test_contract.pdf",
                "file_size": 1024000,
                "upload_date": "2024-01-01T12:00:00Z",
                "processed": False,
                "processing_error": None,
                "user_id": 1,
            }
        ],
        "message": "Documents uploaded successfully",
    }


@pytest.fixture
def mock_processing_task():
    """Mock Celery processing task"""
    task = MagicMock()
    task.id = "task-123"
    task.status = "PENDING"
    task.result = None
    return task


@pytest.fixture
def mock_file_upload():
    """Mock file upload data"""
    return {
        "filename": "test_contract.pdf",
        "content": io.BytesIO(b"PDF content"),
        "content_type": "application/pdf",
        "size": 1024000,
    }


@pytest.fixture
def mock_document_list():
    """Mock list of documents"""
    return [
        {
            "id": 1,
            "filename": "contract_1.pdf",
            "file_size": 1024000,
            "upload_date": "2024-01-01T12:00:00Z",
            "processed": True,
            "processing_error": None,
            "user_id": 1,
        },
        {
            "id": 2,
            "filename": "contract_2.docx",
            "file_size": 2048000,
            "upload_date": "2024-01-02T12:00:00Z",
            "processed": False,
            "processing_error": None,
            "user_id": 1,
        },
    ]


@pytest.fixture
def mock_document_service():
    """Mock document service"""
    service = MagicMock()
    service.upload_document.return_value = {"id": 1, "filename": "test.pdf", "processed": False}
    service.get_document.return_value = {"id": 1, "filename": "test.pdf", "processed": True}
    service.list_documents.return_value = []
    return service
