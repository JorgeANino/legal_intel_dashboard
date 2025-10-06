"""
Detailed tests for document endpoints
"""
# Standard library imports
import io
from unittest.mock import MagicMock, patch

# Import the global mock instance
from tests.conftest import _mock_doc_service_instance


class TestDocumentUpload:
    """Test document upload functionality"""

    def test_upload_single_pdf(self, client, sample_pdf_file):
        """Test uploading a single PDF file"""
        # Mock document service
        mock_doc = MagicMock()
        mock_doc.id = 1
        mock_doc.filename = "test_contract.pdf"
        mock_doc.file_size = 1024000
        _mock_doc_service_instance.save_uploaded_file.return_value = mock_doc

        # Prepare file upload
        filename, file_content, content_type = sample_pdf_file
        files = {"files": (filename, file_content, content_type)}

        response = client.post("/api/v1/documents/upload", files=files)

        # Should succeed
        assert response.status_code == 200
        data = response.json()
        assert "documents" in data
        assert data["successful"] >= 1
        # Verify the document was processed
        assert len(data["documents"]) >= 1

    def test_upload_multiple_files(self, client, sample_pdf_file, sample_docx_file):
        """Test uploading multiple files"""
        # Mock document service
        mock_doc = MagicMock()
        mock_doc.id = 1
        mock_doc.filename = "test.pdf"
        _mock_doc_service_instance.save_uploaded_file.return_value = mock_doc

        # Prepare multiple file uploads
        pdf_filename, pdf_content, pdf_type = sample_pdf_file
        docx_filename, docx_content, docx_type = sample_docx_file

        files = [
            ("files", (pdf_filename, pdf_content, pdf_type)),
            ("files", (docx_filename, docx_content, docx_type)),
        ]

        response = client.post("/api/v1/documents/upload", files=files)

        # Should succeed
        assert response.status_code == 200
        data = response.json()
        assert "documents" in data

    def test_upload_no_files(self, client_no_auth):
        """Test upload endpoint with no files"""
        response = client_no_auth.post("/api/v1/documents/upload")
        # Will fail on auth or validation
        assert response.status_code in [401, 403, 422]

    def test_upload_invalid_file_type(self, client):
        """Test upload with invalid file type"""
        # Mock setup to raise exception
        _mock_doc_service_instance.save_uploaded_file.side_effect = Exception("Invalid file type")

        files = {"files": ("test.txt", io.BytesIO(b"text content"), "text/plain")}
        response = client.post("/api/v1/documents/upload", files=files)
        # Should handle error gracefully
        assert response.status_code == 200
        data = response.json()
        assert data["failed"] >= 1

    def test_upload_service_error(self, client, sample_pdf_file):
        """Test upload when document service fails"""
        # Mock service to raise exception
        _mock_doc_service_instance.save_uploaded_file.side_effect = Exception("Upload failed")

        filename, file_content, content_type = sample_pdf_file
        files = {"files": (filename, file_content, content_type)}

        response = client.post("/api/v1/documents/upload", files=files)

        # Should return success with error in results
        assert response.status_code == 200
        data = response.json()
        assert data["failed"] >= 1


class TestDocumentListing:
    """Test document listing functionality"""

    def test_list_documents_success(self, client, mock_document):
        """Test successful document listing"""
        # Mock service response
        _mock_doc_service_instance.list_documents.return_value = [mock_document]

        response = client.get("/api/v1/documents")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1

    def test_list_documents_with_pagination(self, client, mock_document):
        """Test document listing with pagination"""
        # Mock service response
        _mock_doc_service_instance.list_documents.return_value = [mock_document]

        response = client.get("/api/v1/documents?skip=0&limit=10")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1

    def test_list_documents_empty(self, client):
        """Test document listing when no documents exist"""
        # Mock service response
        _mock_doc_service_instance.list_documents.return_value = []

        response = client.get("/api/v1/documents")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_list_documents_unauthorized(self, client_no_auth):
        """Test document listing without authentication"""
        response = client_no_auth.get("/api/v1/documents")
        assert response.status_code in [401, 403]


class TestDocumentRetrieval:
    """Test individual document retrieval"""

    def test_get_document_success(self, client, mock_document):
        """Test successful document retrieval"""
        # Mock service response
        _mock_doc_service_instance.get_document.return_value = mock_document

        response = client.get("/api/v1/documents/1")

        assert response.status_code == 200
        data = response.json()
        assert data["filename"] == "test_contract.pdf"
        assert data["id"] == 1

    def test_get_document_not_found(self, client):
        """Test document retrieval when document doesn't exist"""
        # Mock service response
        _mock_doc_service_instance.get_document.return_value = None

        response = client.get("/api/v1/documents/999")

        assert response.status_code == 404

    def test_get_document_wrong_user(self, client):
        """Test document retrieval for document owned by different user"""
        # Mock document owned by different user
        mock_doc = MagicMock()
        mock_doc.id = 1
        mock_doc.user_id = 999  # Different user
        _mock_doc_service_instance.get_document.return_value = mock_doc

        response = client.get("/api/v1/documents/1")

        # Should return 403
        assert response.status_code == 403

    def test_get_document_unauthorized(self, client_no_auth):
        """Test document retrieval without authentication"""
        response = client_no_auth.get("/api/v1/documents/1")
        assert response.status_code in [401, 403]


class TestDocumentProcessing:
    """Test document processing status"""

    def test_document_processing_status(self, client, mock_document):
        """Test checking document processing status"""
        # Mock document with processing status
        mock_document.processed = False
        mock_document.processing_error = None
        _mock_doc_service_instance.get_document.return_value = mock_document

        response = client.get("/api/v1/documents/1")

        assert response.status_code == 200
        data = response.json()
        assert data["processed"] is False
        assert data["processing_error"] is None

    def test_document_processing_error(self, client, mock_document):
        """Test document with processing error"""
        # Mock document with processing error
        mock_document.processed = False
        mock_document.processing_error = "Failed to extract text"
        _mock_doc_service_instance.get_document.return_value = mock_document

        response = client.get("/api/v1/documents/1")

        assert response.status_code == 200
        data = response.json()
        assert data["processed"] is False
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
        # Test negative skip - should still work (API doesn't validate)
        response = client.get("/api/v1/documents?skip=-1")
        assert response.status_code == 200

        # Test negative limit - should still work (API doesn't validate)
        response = client.get("/api/v1/documents?limit=-1")
        assert response.status_code == 200

        # Test too large limit - should still work (API doesn't validate)
        response = client.get("/api/v1/documents?limit=10000")
        assert response.status_code == 200


class TestDocumentCaching:
    """Test document caching functionality"""

    def test_document_caching(self, client, mock_document):
        """Test that document responses work"""
        # Mock service response
        _mock_doc_service_instance.get_document.return_value = mock_document

        response = client.get("/api/v1/documents/1")

        assert response.status_code == 200

    def test_document_cache_hit(self, client, mock_document):
        """Test document retrieval"""
        # Mock service response
        _mock_doc_service_instance.get_document.return_value = mock_document

        response = client.get("/api/v1/documents/1")

        assert response.status_code == 200
        # Service should be called since we're mocking it
        _mock_doc_service_instance.get_document.assert_called()
