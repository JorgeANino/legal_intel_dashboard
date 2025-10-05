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
export interface QueryRequest {
  question: string;
  max_results?: number;
}

export interface QueryResponse {
  question: string;
  results: QueryResult[];
  total_results: number;
  execution_time_ms: number;
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

