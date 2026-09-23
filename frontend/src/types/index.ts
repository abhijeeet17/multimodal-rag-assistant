export type DocumentStatus = 'UPLOADED' | 'PROCESSING' | 'COMPLETED' | 'FAILED';

export interface Document {
  id: string;
  filename: string;
  file_type: string;
  file_size: number;
  status: DocumentStatus;
  total_pages: number;
  error_message?: string;
  created_at: string;
  updated_at: string;
}

export interface Citation {
  document: string;
  page: number;
  chunk_id?: string;
  snippet?: string;
}

export interface QueryRequest {
  question: string;
  document_ids?: string[];
  session_id?: string;
  top_k?: number;
}

export interface QueryResponse {
  question: string;
  answer: string;
  citations: Citation[];
  retrieved_chunks?: Record<string, any>[];
  session_id?: string;
  message_id?: string;
}

export interface FeedbackRequest {
  message_id?: string;
  question: string;
  answer: string;
  retrieved_chunks?: Record<string, any>[];
  is_helpful: boolean;
  user_comment?: string;
}

export interface HealthResponse {
  status: string;
  version: string;
  environment: string;
  database: string;
}
