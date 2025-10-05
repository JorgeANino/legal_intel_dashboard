"""
Document models for Legal Intel Dashboard
"""
from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey, ARRAY, DECIMAL, Date, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Document(Base):
    """Document model for storing uploaded legal documents"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False, index=True)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    file_type = Column(String(10))  # pdf, docx
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    processed = Column(Boolean, default=False, index=True)
    processing_error = Column(Text, nullable=True)
    raw_text = Column(Text, nullable=True)
    page_count = Column(Integer)
    user_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    doc_metadata = relationship("DocumentMetadata", back_populates="document", uselist=False, cascade="all, delete-orphan")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Document(id={self.id}, filename='{self.filename}')>"


class DocumentMetadata(Base):
    """Metadata extracted from legal documents"""
    __tablename__ = "document_metadata"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey('documents.id', ondelete='CASCADE'), unique=True, index=True)
    agreement_type = Column(String(100), index=True)
    governing_law = Column(String(100), index=True)
    jurisdiction = Column(String(100))
    geography = Column(String(100))
    industry = Column(String(100), index=True)
    parties = Column(ARRAY(String), nullable=True)
    effective_date = Column(Date, nullable=True)
    expiration_date = Column(Date, nullable=True)
    contract_value = Column(DECIMAL(15, 2), nullable=True)
    currency = Column(String(10), nullable=True)
    key_terms = Column(JSONB, nullable=True)
    confidence_score = Column(Float)
    extracted_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="doc_metadata")
    
    def __repr__(self):
        return f"<DocumentMetadata(id={self.id}, type='{self.agreement_type}')>"


class DocumentChunk(Base):
    """Text chunks with embeddings for semantic search and RAG"""
    __tablename__ = "document_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey('documents.id', ondelete='CASCADE'), index=True)
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    chunk_size = Column(Integer)
    # Vector embedding for semantic search (1536 dimensions for OpenAI text-embedding-3-small)
    embedding = Column(ARRAY(Float), nullable=True)
    chunk_metadata = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="chunks")
    
    def __repr__(self):
        return f"<DocumentChunk(id={self.id}, doc_id={self.document_id}, idx={self.chunk_index})>"


class Query(Base):
    """Query audit trail"""
    __tablename__ = "queries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    query_text = Column(Text, nullable=False)
    query_type = Column(String(50))  # interrogation, search, analysis
    results = Column(JSONB)
    execution_time_ms = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    def __repr__(self):
        return f"<Query(id={self.id}, user_id={self.user_id})>"

