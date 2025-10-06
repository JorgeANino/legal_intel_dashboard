'use client';

import { useMutation } from '@tanstack/react-query';
import { useState } from 'react';
import toast from 'react-hot-toast';

import { queryApi } from '@/api/query';
import { QueryRequest, QueryResponse, QueryFilters } from '@/api/types';

export const useDocumentQuery = () => {
  const [queryHistory, setQueryHistory] = useState<QueryResponse[]>([]);
  const [queryParams, setQueryParams] = useState<QueryRequest>({
    question: '',
    max_results: 50,
    page: 1,
    filters: {},
    sort_by: 'relevance',
    sort_order: 'desc'
  });

  const queryMutation = useMutation({
    mutationFn: (request: QueryRequest) => queryApi.queryDocuments(request),
    onSuccess: (data) => {
      // Add to history
      setQueryHistory((prev) => [data, ...prev].slice(0, 10)); // Keep last 10
      
      if (data.total_results === 0) {
        toast('No documents match your query');
      }
    },
    onError: (error: any) => {
      toast.error(error.message || 'Query failed. Please try again.');
    },
  });

  const executeQuery = (question: string) => {
    const newParams = { ...queryParams, question, page: 1 };
    setQueryParams(newParams);
    queryMutation.mutate(newParams);
  };

  const changePage = (page: number) => {
    const newParams = { ...queryParams, page };
    setQueryParams(newParams);
    queryMutation.mutate(newParams);
  };

  const applyFilters = (filters: QueryFilters) => {
    const newParams = { ...queryParams, filters, page: 1 };
    setQueryParams(newParams);
    queryMutation.mutate(newParams);
  };

  const changeSort = (sortBy: string, sortOrder: string) => {
    const newParams = { ...queryParams, sort_by: sortBy as any, sort_order: sortOrder as any, page: 1 };
    setQueryParams(newParams);
    queryMutation.mutate(newParams);
  };

  return {
    executeQuery,
    changePage,
    applyFilters,
    changeSort,
    queryParams,
    isQuerying: queryMutation.isPending,
    queryResult: queryMutation.data,
    queryError: queryMutation.error,
    queryHistory,
    clearHistory: () => setQueryHistory([]),
  };
};

