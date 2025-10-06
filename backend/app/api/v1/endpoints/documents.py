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
from app.middleware.cache import cache_service
from app.middleware.rate_limit import rate_limit_dependency
from app.schemas.document import BatchUploadResponse, DocumentResponse, DocumentUploadResponse
from app.services.document_service import DocumentService
from app.tasks.document_tasks import process_document_task


router = APIRouter()


@router.post("/upload", response_model=BatchUploadResponse)
async def upload_documents(
    files: list[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
    _rate_limit: None = Depends(rate_limit_dependency),
):
    """
    Upload multiple legal documents

    - Accepts PDF and DOCX files
    - Triggers async processing for each document
    - Returns upload status for each file

    Rate limit: 10 requests per minute
    Max file size: 50MB per file
    """
    service = DocumentService()
    results = []
    successful = 0
    failed = 0

    # Mock user_id (replace with actual auth)
    user_id = 1

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
async def list_documents(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """List all documents for the current user"""
    service = DocumentService()
    user_id = 1  # Mock user_id

    documents = await service.list_documents(user_id, db, skip, limit)
    return documents


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: int, db: AsyncSession = Depends(get_db)):
    """Get document details by ID"""
    service = DocumentService()
    document = await service.get_document(document_id, db)

    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    return document
