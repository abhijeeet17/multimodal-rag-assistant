import axios from 'axios';
import { Document, QueryRequest, QueryResponse, FeedbackRequest, HealthResponse } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const checkHealth = async (): Promise<HealthResponse> => {
  const response = await apiClient.get<HealthResponse>('/health');
  return response.data;
};

export const fetchDocuments = async (): Promise<{ total: number; documents: Document[] }> => {
  const response = await apiClient.get('/documents');
  return response.data;
};

export const uploadDocument = async (file: File): Promise<Document> => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await apiClient.post<Document>('/documents/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const deleteDocument = async (documentId: string): Promise<void> => {
  await apiClient.delete(`/documents/${documentId}`);
};

export const queryRAG = async (payload: QueryRequest): Promise<QueryResponse> => {
  const response = await apiClient.post<QueryResponse>('/chat', payload);
  return response.data;
};

export const submitFeedback = async (payload: FeedbackRequest): Promise<void> => {
  await apiClient.post('/feedback', payload);
};

export default apiClient;
