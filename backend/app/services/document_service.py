"""
Document service for handling document operations
"""
import os
import hashlib
from pathlib import Path
from typing import List
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.document import Document
from app.core.config import settings


class DocumentService:
    """Service for handling document operations"""
    
    UPLOAD_DIR = Path("/app/uploads")
    ALLOWED_EXTENSIONS = {'.pdf', '.docx'}
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    
    def __init__(self):
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    async def save_uploaded_file(
        self,
        file: UploadFile,
        user_id: int,
        db: AsyncSession
    ) -> Document:
        """Save uploaded file to disk and create database record"""
        
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
            processed=False
        )
        
        db.add(document)
        await db.commit()
        await db.refresh(document)
        
        return document
    
    async def get_document(self, document_id: int, db: AsyncSession) -> Document:
        """Get document by ID"""
        result = await db.execute(
            select(Document).where(Document.id == document_id)
        )
        return result.scalar_one_or_none()
    
    async def list_documents(
        self,
        user_id: int,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[Document]:
        """List documents for a user"""
        result = await db.execute(
            select(Document)
            .where(Document.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(Document.upload_date.desc())
        )
        return list(result.scalars().all())

