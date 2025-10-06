import { apiClient } from './client';
import { QueryRequest, QueryResponse } from './types';

export interface QuerySuggestionsResponse {
  suggestions: string[];
  popular_queries: string[];
  legal_terms: string[];
  metadata_suggestions: {
    agreement_types: string[];
    jurisdictions: string[];
    industries: string[];
    geographies: string[];
  };
}

export const queryApi = {
  /**
   * Execute natural language query
   */
  queryDocuments: async (request: QueryRequest): Promise<QueryResponse> => {
    const response = await apiClient.post('/query', request);
    return response.data;
  },

  /**
   * Get query suggestions based on partial input
   */
  getSuggestions: async (query: string, limit: number = 10): Promise<QuerySuggestionsResponse> => {
    const response = await apiClient.get(`/query/suggestions?q=${encodeURIComponent(query)}&limit=${limit}`);
    return response.data;
  },
};

