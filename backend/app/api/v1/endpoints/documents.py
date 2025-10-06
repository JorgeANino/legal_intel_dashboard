"""
Document upload and management endpoints
"""
# Standard library imports
import traceback

# Third-party imports
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

# Local application imports
from app.core.database import get_db
from app.core.security import get_current_user
from app.middleware.cache import cache_service
from app.middleware.rate_limit import rate_limit_dependency
from app.models.user import User
from app.schemas.document import BatchUploadResponse, DocumentResponse, DocumentUploadResponse
from app.services.document_service import DocumentService
from app.tasks.document_tasks import process_document_task


router = APIRouter()


@router.post("/upload", response_model=BatchUploadResponse)
async def upload_documents(
    files: list[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _rate_limit: None = Depends(rate_limit_dependency),
):
    """
    Upload multiple legal documents (Protected - requires JWT token)

    - Accepts PDF and DOCX files
    - Triggers async processing for each document
    - Returns upload status for each file

    Rate limit: 10 requests per minute
    Max file size: 50MB per file
    Authorization: Bearer <JWT token>
    """
    service = DocumentService()
    results = []
    successful = 0
    failed = 0

    user_id = current_user.id

    for file in files:
        try:
            # Save file and create database record
            document = await service.save_uploaded_file(file, user_id, db)

            # Trigger async processing
            print(f"Dispatching Celery task for document {document.id}")
            task_result = process_document_task.delay(document.id)
            print(f"Task dispatched: {task_result.id} for document {document.id}")

            results.append(
                DocumentUploadResponse(
                    document_id=document.id,
                    filename=document.filename,
                    status="success",
                    message="Upload successful, processing started",
                )
            )
            successful += 1

        except Exception as e:
            print(f"ERROR: Error in upload: {e}")
            traceback.print_exc()
            results.append(
                DocumentUploadResponse(
                    document_id=0, filename=file.filename, status="error", message=str(e)
                )
            )
            failed += 1

    # Invalidate dashboard cache for user after uploads
    if successful > 0:
        await cache_service.delete(f"dashboard_stats:user:{user_id}")

    return BatchUploadResponse(
        total=len(files), successful=successful, failed=failed, documents=results
    )


@router.get("", response_model=list[DocumentResponse])
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all documents for the current user (Protected - requires JWT token)

    Authorization: Bearer <JWT token>
    """
    service = DocumentService()

    documents = await service.list_documents(current_user.id, db, skip, limit)
    return documents


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get document details by ID (Protected - requires JWT token)

    Authorization: Bearer <JWT token>
    """
    service = DocumentService()
    document = await service.get_document(document_id, db)

    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    # Verify user owns this document
    if document.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this document"
        )

    return document
