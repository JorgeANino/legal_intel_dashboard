'use client';

import { useState } from 'react';

import { queryApi } from '@/api/query';

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

export const useQuerySuggestions = () => {
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSuggestions = async (query: string) => {
    if (query.length < 3) {
      setSuggestions([]);
      return;
    }
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await queryApi.getSuggestions(query);
      setSuggestions(response.suggestions);
    } catch (err: any) {
      console.error('Failed to fetch suggestions:', err);
      setError(err.message || 'Failed to fetch suggestions');
      setSuggestions([]);
    } finally {
      setIsLoading(false);
    }
  };

  const clearSuggestions = () => {
    setSuggestions([]);
    setError(null);
  };

  return { 
    suggestions, 
    isLoading, 
    error, 
    fetchSuggestions, 
    clearSuggestions 
  };
};
