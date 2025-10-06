import { apiClient, uploadWithProgress } from './client';
import { Document, UploadResponse } from './types';

export const documentsApi = {
  /**
   * Upload multiple documents with progress tracking
   */
  uploadDocuments: async (
    files: File[],
    onProgress?: (progress: number) => void,
  ): Promise<UploadResponse> => {
    const formData = new FormData();
    files.forEach((file) => formData.append('files', file));

    const response = await uploadWithProgress(
      '/documents/upload',
      formData,
      onProgress,
    );
    return response.data;
  },

  /**
   * List all documents with pagination
   */
  listDocuments: async (skip = 0, limit = 100): Promise<Document[]> => {
    const response = await apiClient.get('/documents', {
      params: { skip, limit },
    });
    return response.data;
  },

  /**
   * Get single document by ID
   */
  getDocument: async (id: number): Promise<Document> => {
    const response = await apiClient.get(`/documents/${id}`);
    return response.data;
  },
};
