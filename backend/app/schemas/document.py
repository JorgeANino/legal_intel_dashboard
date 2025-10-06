"""
Pydantic schemas for documents
"""
# Standard library imports
from datetime import date, datetime
from typing import Any

# Third-party imports
from pydantic import BaseModel, Field


class DocumentBase(BaseModel):
    filename: str
    file_type: str


class DocumentCreate(DocumentBase):
    pass


class DocumentMetadataResponse(BaseModel):
    id: int
    agreement_type: str | None = None
    governing_law: str | None = None
    jurisdiction: str | None = None
    geography: str | None = None
    industry: str | None = None
    parties: list[str] | None = None
    effective_date: date | None = None
    expiration_date: date | None = None
    contract_value: float | None = None
    currency: str | None = None
    key_terms: dict[str, Any] | None = None
    confidence_score: float | None = None

    class Config:
        from_attributes = True


class DocumentResponse(DocumentBase):
    id: int
    file_path: str
    file_size: int | None = None
    upload_date: datetime
    processed: bool
    processing_error: str | None = None
    page_count: int | None = None
    doc_metadata: DocumentMetadataResponse | None = Field(None, serialization_alias="metadata")
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
    documents: list[DocumentUploadResponse]


class QueryRequest(BaseModel):
    question: str = Field(..., description="Natural language question")
    max_results: int | None = Field(10, ge=1, le=100)
    page: int | None = Field(1, ge=1)
    filters: dict[str, Any] | None = None
    sort_by: str | None = Field("relevance", description="Sort by: relevance, date, document_name")
    sort_order: str | None = Field("desc", description="Sort order: asc, desc")


class QueryResultRow(BaseModel):
    document: str
    document_id: int
    metadata: dict[str, Any] = {}


class QueryResponse(BaseModel):
    question: str
    results: list[QueryResultRow]
    total_results: int
    page: int
    per_page: int
    total_pages: int
    execution_time_ms: int
    filters_applied: dict[str, Any] | None = None


class DashboardStats(BaseModel):
    total_documents: int
    processed_documents: int
    total_pages: int
    agreement_types: dict[str, int]
    jurisdictions: dict[str, int]
    industries: dict[str, int]
    geographies: dict[str, int]


class QuerySuggestionsResponse(BaseModel):
    """Response model for query suggestions"""
    suggestions: list[str]
    popular_queries: list[str]
    legal_terms: list[str]
    metadata_suggestions: dict[str, list[str]]


class QueryFilters(BaseModel):
    """Filter options for query results"""
    agreement_types: list[str] | None = None
    jurisdictions: list[str] | None = None
    industries: list[str] | None = None
    geographies: list[str] | None = None
    date_range: dict[str, str] | None = None  # {"start": "2024-01-01", "end": "2024-12-31"}


class ExportRequest(BaseModel):
    """Request model for exporting query results"""
    question: str
    user_id: int
    max_results: int | None = 1000
    filters: QueryFilters | None = None
    filename: str | None = "query-results"
    template: str | None = "default"


class DashboardExportRequest(BaseModel):
    """Request model for exporting dashboard reports"""
    user_id: int
    include_charts: bool = True
    date_range: dict[str, str] | None = None
    format: str = "pdf"


class ExtractedMetadata(BaseModel):
    """
    Pydantic model for structured metadata extraction from legal documents.
    Used with LangChain's PydanticOutputParser to enforce schema compliance.
    """

    agreement_type: str | None = Field(
        None,
        description="Type of agreement (e.g., NDA, MSA, Franchise Agreement, Service Agreement, License Agreement)",
    )
    governing_law: str | None = Field(
        None,
        description="Governing law jurisdiction (e.g., UAE, UK, Delaware, New York, California)",
    )
    jurisdiction: str | None = Field(
        None, description="Specific jurisdiction mentioned in the agreement"
    )
    geography: str | None = Field(
        None, description="Geographic region (e.g., Middle East, Europe, North America, Asia)"
    )
    industry: str | None = Field(
        None,
        description="Industry sector (e.g., Technology, Oil & Gas, Healthcare, Finance, Real Estate)",
    )
    parties: list[str] = Field(
        default_factory=list, description="Names of parties mentioned in the agreement"
    )
    effective_date: str | None = Field(None, description="Effective date in YYYY-MM-DD format")
    expiration_date: str | None = Field(None, description="Expiration date in YYYY-MM-DD format")
    contract_value: float | None = Field(None, description="Numeric contract value")
    currency: str | None = Field(None, description="Currency code (e.g., USD, EUR, AED, GBP)")
    key_terms: dict[str, Any] = Field(
        default_factory=dict, description="Important terms and clauses found in the document"
    )
    confidence_score: float = Field(
        default=0.7, ge=0.0, le=1.0, description="Confidence score of the extraction (0-1)"
    )
