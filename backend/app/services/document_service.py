"""
Document service for handling document operations
"""
# Standard library imports
import hashlib
from pathlib import Path

# Third-party imports
from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

# Local application imports
from app.models.document import Document


class DocumentService:
    """
    Service for handling document operations including upload, storage, and retrieval.

    Manages document lifecycle from upload through storage to database record creation.
    Supports PDF and DOCX formats with validation and file size limits.

    Attributes:
        UPLOAD_DIR: Directory path for storing uploaded documents.
        ALLOWED_EXTENSIONS: Set of allowed file extensions.
        MAX_FILE_SIZE: Maximum file size in bytes (50MB).
    """

    UPLOAD_DIR = Path("/app/uploads")
    ALLOWED_EXTENSIONS = {".pdf", ".docx"}
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

    def __init__(self) -> None:
        """
        Initialize the document service and ensure upload directory exists.

        Creates the upload directory if it doesn't exist.
        """
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    async def save_uploaded_file(
        self, file: UploadFile, user_id: int, db: AsyncSession
    ) -> Document:
        """
        Save uploaded file to disk and create database record.

        Validates file type and size, generates unique filename using MD5 hash,
        saves file to disk, and creates a database record for tracking.

        Args:
            file: FastAPI UploadFile object containing the uploaded document.
            user_id: ID of the user uploading the document.
            db: Async database session for creating the record.

        Returns:
            Document: Created document database record with generated ID.

        Raises:
            ValueError: If file type is not allowed or file size exceeds limit.

        Example:
            >>> service = DocumentService()
            >>> doc = await service.save_uploaded_file(upload_file, user_id=1, db=session)
            >>> print(f"Document saved: {doc.id}")
        """
        # Validate file
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in self.ALLOWED_EXTENSIONS:
            raise ValueError(f"Invalid file type. Allowed: {self.ALLOWED_EXTENSIONS}")

        # Read file content
        content = await file.read()
        file_size = len(content)

        if file_size > self.MAX_FILE_SIZE:
            raise ValueError(f"File too large. Max size: {self.MAX_FILE_SIZE} bytes")

        # Generate unique filename
        file_hash = hashlib.md5(content).hexdigest()
        safe_filename = f"{file_hash}_{file.filename}"
        file_path = self.UPLOAD_DIR / safe_filename

        # Save to disk
        with open(file_path, "wb") as f:
            f.write(content)

        # Create database record
        document = Document(
            filename=file.filename,
            file_path=str(file_path),
            file_size=file_size,
            file_type=file_ext[1:],  # Remove the dot
            user_id=user_id,
            processed=False,
        )

        db.add(document)
        await db.commit()
        await db.refresh(document)

        return document

    async def get_document(self, document_id: int, db: AsyncSession) -> Document | None:
        """
        Retrieve a document by its ID with metadata eagerly loaded.

        Args:
            document_id: Unique identifier of the document to retrieve.
            db: Async database session for query execution.

        Returns:
            Document object if found, None otherwise. Includes eagerly loaded
            metadata relationship to prevent N+1 queries.

        Example:
            >>> service = DocumentService()
            >>> doc = await service.get_document(123, db)
            >>> if doc:
            >>>     print(f"Found: {doc.filename}")
        """
        result = await db.execute(
            select(Document)
            .options(selectinload(Document.doc_metadata))
            .where(Document.id == document_id)
        )
        return result.scalar_one_or_none()

    async def list_documents(
        self, user_id: int, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[Document]:
        """
        List documents for a specific user with pagination.

        Args:
            user_id: ID of the user whose documents to retrieve.
            db: Async database session for query execution.
            skip: Number of records to skip (for pagination). Defaults to 0.
            limit: Maximum number of records to return. Defaults to 100.

        Returns:
            List of Document objects ordered by upload date (newest first).
            Metadata is eagerly loaded to prevent N+1 queries.

        Example:
            >>> service = DocumentService()
            >>> docs = await service.list_documents(user_id=1, db=session, skip=0, limit=20)
            >>> print(f"Found {len(docs)} documents")
        """
        result = await db.execute(
            select(Document)
            .options(selectinload(Document.doc_metadata))
            .where(Document.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(Document.upload_date.desc())
        )
        return list(result.scalars().all())
