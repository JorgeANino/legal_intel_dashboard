"""
Pydantic schemas for documents
"""
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class DocumentBase(BaseModel):
    filename: str
    file_type: str


class DocumentCreate(DocumentBase):
    pass


class DocumentMetadataResponse(BaseModel):
    id: int
    agreement_type: Optional[str] = None
    governing_law: Optional[str] = None
    jurisdiction: Optional[str] = None
    geography: Optional[str] = None
    industry: Optional[str] = None
    parties: Optional[List[str]] = None
    effective_date: Optional[date] = None
    expiration_date: Optional[date] = None
    contract_value: Optional[float] = None
    currency: Optional[str] = None
    key_terms: Optional[Dict[str, Any]] = None
    confidence_score: Optional[float] = None
    
    class Config:
        from_attributes = True


class DocumentResponse(DocumentBase):
    id: int
    file_path: str
    file_size: Optional[int] = None
    upload_date: datetime
    processed: bool
    processing_error: Optional[str] = None
    page_count: Optional[int] = None
    doc_metadata: Optional[DocumentMetadataResponse] = Field(None, serialization_alias="metadata")
    created_at: datetime
    
    class Config:
        from_attributes = True


class DocumentUploadResponse(BaseModel):
    document_id: int
    filename: str
    status: str
    message: str


class BatchUploadResponse(BaseModel):
    total: int
    successful: int
    failed: int
    documents: List[DocumentUploadResponse]


class QueryRequest(BaseModel):
    question: str = Field(..., description="Natural language question")
    max_results: Optional[int] = Field(10, ge=1, le=100)


class QueryResultRow(BaseModel):
    document: str
    document_id: int
    metadata: Dict[str, Any] = {}


class QueryResponse(BaseModel):
    question: str
    results: List[QueryResultRow]
    total_results: int
    execution_time_ms: int


class DashboardStats(BaseModel):
    total_documents: int
    processed_documents: int
    total_pages: int
    agreement_types: Dict[str, int]
    jurisdictions: Dict[str, int]
    industries: Dict[str, int]
    geographies: Dict[str, int]

class ExtractedMetadata(BaseModel):
    """
    Pydantic model for structured metadata extraction from legal documents.
    Used with LangChain's PydanticOutputParser to enforce schema compliance.
    """
    
    agreement_type: Optional[str] = Field(
        None,
        description="Type of agreement (e.g., NDA, MSA, Franchise Agreement, Service Agreement, License Agreement)"
    )
    governing_law: Optional[str] = Field(
        None,
        description="Governing law jurisdiction (e.g., UAE, UK, Delaware, New York, California)"
    )
    jurisdiction: Optional[str] = Field(
        None,
        description="Specific jurisdiction mentioned in the agreement"
    )
    geography: Optional[str] = Field(
        None,
        description="Geographic region (e.g., Middle East, Europe, North America, Asia)"
    )
    industry: Optional[str] = Field(
        None,
        description="Industry sector (e.g., Technology, Oil & Gas, Healthcare, Finance, Real Estate)"
    )
    parties: List[str] = Field(
        default_factory=list,
        description="Names of parties mentioned in the agreement"
    )
    effective_date: Optional[str] = Field(
        None,
        description="Effective date in YYYY-MM-DD format"
    )
    expiration_date: Optional[str] = Field(
        None,
        description="Expiration date in YYYY-MM-DD format"
    )
    contract_value: Optional[float] = Field(
        None,
        description="Numeric contract value"
    )
    currency: Optional[str] = Field(
        None,
        description="Currency code (e.g., USD, EUR, AED, GBP)"
    )
    key_terms: Dict[str, Any] = Field(
        default_factory=dict,
        description="Important terms and clauses found in the document"
    )
    confidence_score: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Confidence score of the extraction (0-1)"
    )

