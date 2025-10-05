import { apiClient } from './client';
import { QueryRequest, QueryResponse } from './types';

export const queryApi = {
  /**
   * Execute natural language query
   */
  queryDocuments: async (request: QueryRequest): Promise<QueryResponse> => {
    const response = await apiClient.post('/query', request);
    return response.data;
  },
};

