// Document types
export interface Document {
  id: number;
  filename: string;
  file_path: string;
  file_size: number;
  file_type: 'pdf' | 'docx';
  upload_date: string;
  processed: boolean;
  processing_error?: string;
  page_count?: number;
  metadata?: DocumentMetadata;
  created_at: string;
}

export interface DocumentMetadata {
  id: number;
  agreement_type?: string;
  governing_law?: string;
  jurisdiction?: string;
  geography?: string;
  industry?: string;
  parties?: string[];
  effective_date?: string;
  expiration_date?: string;
  contract_value?: number;
  currency?: string;
  key_terms?: Record<string, any>;
  confidence_score?: number;
}

// Upload types
export interface UploadResponse {
  total: number;
  successful: number;
  failed: number;
  documents: DocumentUploadResult[];
}

export interface DocumentUploadResult {
  document_id: number;
  filename: string;
  status: 'success' | 'error';
  message: string;
}

// Query types
export interface QueryFilters {
  agreement_types?: string[];
  jurisdictions?: string[];
  industries?: string[];
  geographies?: string[];
  date_range?: {
    start: string;
    end: string;
  };
}

export interface QueryRequest {
  question: string;
  max_results?: number;
  page?: number;
  filters?: QueryFilters;
  sort_by?: 'relevance' | 'date' | 'document_name';
  sort_order?: 'asc' | 'desc';
}

export interface QueryResponse {
  question: string;
  results: QueryResult[];
  total_results: number;
  page: number;
  per_page: number;
  total_pages: number;
  execution_time_ms: number;
  filters_applied?: QueryFilters;
}

export interface QueryResult {
  document: string;
  document_id: number;
  metadata: Record<string, any>;
}

// Dashboard types
export interface DashboardStats {
  total_documents: number;
  processed_documents: number;
  total_pages: number;
  agreement_types: Record<string, number>;
  jurisdictions: Record<string, number>;
  industries: Record<string, number>;
  geographies: Record<string, number>;
}

// Error types
export interface ApiError {
  detail: string;
  status?: number;
}

