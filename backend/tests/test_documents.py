"""
Detailed tests for document endpoints
"""
# Standard library imports
import io
from unittest.mock import AsyncMock, MagicMock, patch


# Third-party imports


# Local application imports


class TestDocumentUpload:
    """Test document upload functionality"""

    @patch('app.api.v1.endpoints.documents.get_db')
    @patch('app.api.v1.endpoints.documents.get_current_user')
    @patch('app.api.v1.endpoints.documents.document_service')
    @patch('app.api.v1.endpoints.documents.process_document.delay')
    def test_upload_single_pdf(self, mock_celery_task, mock_service, mock_user, mock_db, client, sample_pdf_file, mock_document):
        """Test uploading a single PDF file"""
        # Mock dependencies
        mock_user.return_value = {"id": 1}
        mock_db.return_value.__aenter__.return_value = AsyncMock()

        # Mock document service
        mock_service.upload_document.return_value = mock_document

        # Mock Celery task
        mock_celery_task.return_value = MagicMock(id="task-123")

        # Prepare file upload
        filename, file_content, content_type = sample_pdf_file
        files = {"files": (filename, file_content, content_type)}

        response = client.post("/api/v1/documents/upload", files=files)

        # Should succeed
        assert response.status_code == 200
        data = response.json()
        assert "documents" in data
        assert len(data["documents"]) == 1
        assert data["documents"][0]["filename"] == filename

    @patch('app.api.v1.endpoints.documents.get_db')
    @patch('app.api.v1.endpoints.documents.get_current_user')
    @patch('app.api.v1.endpoints.documents.document_service')
    @patch('app.api.v1.endpoints.documents.process_document.delay')
    def test_upload_multiple_files(self, mock_celery_task, mock_service, mock_user, mock_db, client, sample_pdf_file, sample_docx_file):
        """Test uploading multiple files"""
        # Mock dependencies
        mock_user.return_value = {"id": 1}
        mock_db.return_value.__aenter__.return_value = AsyncMock()

        # Mock document service
        mock_service.upload_document.return_value = {"id": 1, "filename": "test.pdf"}

        # Mock Celery task
        mock_celery_task.return_value = MagicMock(id="task-123")

        # Prepare multiple file uploads
        pdf_filename, pdf_content, pdf_type = sample_pdf_file
        docx_filename, docx_content, docx_type = sample_docx_file

        files = [
            ("files", (pdf_filename, pdf_content, pdf_type)),
            ("files", (docx_filename, docx_content, docx_type))
        ]

        response = client.post("/api/v1/documents/upload", files=files)

        # Should succeed
        assert response.status_code == 200
        data = response.json()
        assert "documents" in data
        assert len(data["documents"]) == 2

    def test_upload_no_files(self, client):
        """Test upload endpoint with no files"""
        response = client.post("/api/v1/documents/upload")
        assert response.status_code == 422

    def test_upload_invalid_file_type(self, client):
        """Test upload with invalid file type"""
        files = {"files": ("test.txt", io.BytesIO(b"text content"), "text/plain")}
        response = client.post("/api/v1/documents/upload", files=files)
        # Should return validation error
        assert response.status_code == 422

    @patch('app.api.v1.endpoints.documents.get_db')
    @patch('app.api.v1.endpoints.documents.get_current_user')
    @patch('app.api.v1.endpoints.documents.document_service')
    def test_upload_service_error(self, mock_service, mock_user, mock_db, client, sample_pdf_file):
        """Test upload when document service fails"""
        # Mock dependencies
        mock_user.return_value = {"id": 1}
        mock_db.return_value.__aenter__.return_value = AsyncMock()

        # Mock service to raise exception
        mock_service.upload_document.side_effect = Exception("Upload failed")

        filename, file_content, content_type = sample_pdf_file
        files = {"files": (filename, file_content, content_type)}

        response = client.post("/api/v1/documents/upload", files=files)

        # Should return error
        assert response.status_code == 500


class TestDocumentListing:
    """Test document listing functionality"""

    @patch('app.api.v1.endpoints.documents.get_db')
    @patch('app.api.v1.endpoints.documents.get_current_user')
    @patch('app.api.v1.endpoints.documents.document_service')
    def test_list_documents_success(self, mock_service, mock_user, mock_db, client, mock_document):
        """Test successful document listing"""
        # Mock dependencies
        mock_user.return_value = {"id": 1}
        mock_db.return_value.__aenter__.return_value = AsyncMock()

        # Mock service response
        mock_service.list_documents.return_value = [mock_document]

        response = client.get("/api/v1/documents")

        assert response.status_code == 200
        data = response.json()
        assert "documents" in data
        assert len(data["documents"]) == 1
        assert data["documents"][0]["filename"] == mock_document["filename"]

    @patch('app.api.v1.endpoints.documents.get_db')
    @patch('app.api.v1.endpoints.documents.get_current_user')
    @patch('app.api.v1.endpoints.documents.document_service')
    def test_list_documents_with_pagination(self, mock_service, mock_user, mock_db, client, mock_document):
        """Test document listing with pagination"""
        # Mock dependencies
        mock_user.return_value = {"id": 1}
        mock_db.return_value.__aenter__.return_value = AsyncMock()

        # Mock service response
        mock_service.list_documents.return_value = [mock_document]

        response = client.get("/api/v1/documents?skip=0&limit=10")

        assert response.status_code == 200
        data = response.json()
        assert "documents" in data

    @patch('app.api.v1.endpoints.documents.get_db')
    @patch('app.api.v1.endpoints.documents.get_current_user')
    @patch('app.api.v1.endpoints.documents.document_service')
    def test_list_documents_empty(self, mock_service, mock_user, mock_db, client):
        """Test document listing when no documents exist"""
        # Mock dependencies
        mock_user.return_value = {"id": 1}
        mock_db.return_value.__aenter__.return_value = AsyncMock()

        # Mock service response
        mock_service.list_documents.return_value = []

        response = client.get("/api/v1/documents")

        assert response.status_code == 200
        data = response.json()
        assert "documents" in data
        assert len(data["documents"]) == 0

    def test_list_documents_unauthorized(self, client):
        """Test document listing without authentication"""
        response = client.get("/api/v1/documents")
        assert response.status_code == 401


class TestDocumentRetrieval:
    """Test individual document retrieval"""

    @patch('app.api.v1.endpoints.documents.get_db')
    @patch('app.api.v1.endpoints.documents.get_current_user')
    @patch('app.api.v1.endpoints.documents.document_service')
    def test_get_document_success(self, mock_service, mock_user, mock_db, client, mock_document):
        """Test successful document retrieval"""
        # Mock dependencies
        mock_user.return_value = {"id": 1}
        mock_db.return_value.__aenter__.return_value = AsyncMock()

        # Mock service response
        mock_service.get_document.return_value = mock_document

        response = client.get("/api/v1/documents/1")

        assert response.status_code == 200
        data = response.json()
        assert data["filename"] == mock_document["filename"]
        assert data["id"] == mock_document["id"]

    @patch('app.api.v1.endpoints.documents.get_db')
    @patch('app.api.v1.endpoints.documents.get_current_user')
    @patch('app.api.v1.endpoints.documents.document_service')
    def test_get_document_not_found(self, mock_service, mock_user, mock_db, client):
        """Test document retrieval when document doesn't exist"""
        # Mock dependencies
        mock_user.return_value = {"id": 1}
        mock_db.return_value.__aenter__.return_value = AsyncMock()

        # Mock service response
        mock_service.get_document.return_value = None

        response = client.get("/api/v1/documents/999")

        assert response.status_code == 404

    @patch('app.api.v1.endpoints.documents.get_db')
    @patch('app.api.v1.endpoints.documents.get_current_user')
    @patch('app.api.v1.endpoints.documents.document_service')
    def test_get_document_wrong_user(self, mock_service, mock_user, mock_db, client, mock_document):
        """Test document retrieval for document owned by different user"""
        # Mock dependencies
        mock_user.return_value = {"id": 2}  # Different user
        mock_db.return_value.__aenter__.return_value = AsyncMock()

        # Mock service response - document owned by user 1
        mock_document["user_id"] = 1
        mock_service.get_document.return_value = mock_document

        response = client.get("/api/v1/documents/1")

        # Should return 403 or 404 depending on implementation
        assert response.status_code in [403, 404]

    def test_get_document_unauthorized(self, client):
        """Test document retrieval without authentication"""
        response = client.get("/api/v1/documents/1")
        assert response.status_code == 401


class TestDocumentProcessing:
    """Test document processing status"""

    @patch('app.api.v1.endpoints.documents.get_db')
    @patch('app.api.v1.endpoints.documents.get_current_user')
    @patch('app.api.v1.endpoints.documents.document_service')
    def test_document_processing_status(self, mock_service, mock_user, mock_db, client):
        """Test checking document processing status"""
        # Mock dependencies
        mock_user.return_value = {"id": 1}
        mock_db.return_value.__aenter__.return_value = AsyncMock()

        # Mock document with processing status
        processing_document = {
            "id": 1,
            "filename": "test.pdf",
            "processed": False,
            "processing_error": None,
            "user_id": 1
        }
        mock_service.get_document.return_value = processing_document

        response = client.get("/api/v1/documents/1")

        assert response.status_code == 200
        data = response.json()
        assert not data["processed"]
        assert data["processing_error"] is None

    @patch('app.api.v1.endpoints.documents.get_db')
    @patch('app.api.v1.endpoints.documents.get_current_user')
    @patch('app.api.v1.endpoints.documents.document_service')
    def test_document_processing_error(self, mock_service, mock_user, mock_db, client):
        """Test document with processing error"""
        # Mock dependencies
        mock_user.return_value = {"id": 1}
        mock_db.return_value.__aenter__.return_value = AsyncMock()

        # Mock document with processing error
        error_document = {
            "id": 1,
            "filename": "test.pdf",
            "processed": False,
            "processing_error": "Failed to extract text",
            "user_id": 1
        }
        mock_service.get_document.return_value = error_document

        response = client.get("/api/v1/documents/1")

        assert response.status_code == 200
        data = response.json()
        assert not data["processed"]
        assert data["processing_error"] == "Failed to extract text"


class TestDocumentValidation:
    """Test document validation and constraints"""

    def test_document_id_validation(self, client):
        """Test document ID validation"""
        # Test invalid document ID
        response = client.get("/api/v1/documents/invalid")
        assert response.status_code == 422

    def test_pagination_validation(self, client):
        """Test pagination parameter validation"""
        # Test negative skip
        response = client.get("/api/v1/documents?skip=-1")
        assert response.status_code == 422

        # Test negative limit
        response = client.get("/api/v1/documents?limit=-1")
        assert response.status_code == 422

        # Test too large limit
        response = client.get("/api/v1/documents?limit=10000")
        assert response.status_code == 422


class TestDocumentCaching:
    """Test document caching functionality"""

    @patch('app.api.v1.endpoints.documents.get_db')
    @patch('app.api.v1.endpoints.documents.get_current_user')
    @patch('app.api.v1.endpoints.documents.document_service')
    @patch('app.api.v1.endpoints.documents.cache_service')
    def test_document_caching(self, mock_cache, mock_service, mock_user, mock_db, client, mock_document):
        """Test that document responses are cached"""
        # Mock dependencies
        mock_user.return_value = {"id": 1}
        mock_db.return_value.__aenter__.return_value = AsyncMock()

        # Mock service response
        mock_service.get_document.return_value = mock_document

        # Mock cache service
        mock_cache.get.return_value = None  # Cache miss
        mock_cache.set.return_value = None

        response = client.get("/api/v1/documents/1")

        assert response.status_code == 200
        # Verify cache was checked and set
        mock_cache.get.assert_called_once()
        mock_cache.set.assert_called_once()

    @patch('app.api.v1.endpoints.documents.get_db')
    @patch('app.api.v1.endpoints.documents.get_current_user')
    @patch('app.api.v1.endpoints.documents.document_service')
    @patch('app.api.v1.endpoints.documents.cache_service')
    def test_document_cache_hit(self, mock_cache, mock_service, mock_user, mock_db, client, mock_document):
        """Test document retrieval from cache"""
        # Mock dependencies
        mock_user.return_value = {"id": 1}
        mock_db.return_value.__aenter__.return_value = AsyncMock()

        # Mock cache hit
        mock_cache.get.return_value = mock_document

        response = client.get("/api/v1/documents/1")

        assert response.status_code == 200
        # Verify cache was checked but service wasn't called
        mock_cache.get.assert_called_once()
        mock_service.get_document.assert_not_called()
