'use client';

import { useMutation } from '@tanstack/react-query';
import { useState, useCallback } from 'react';
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
    sort_order: 'desc',
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

  const executeQuery = useCallback(
    (question: string) => {
      setQueryParams((prev) => {
        const newParams = { ...prev, question, page: 1 };
        queryMutation.mutate(newParams);
        return newParams;
      });
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [],
  );

  const changePage = useCallback(
    (page: number) => {
      setQueryParams((prev) => {
        const newParams = { ...prev, page };
        queryMutation.mutate(newParams);
        return newParams;
      });
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [],
  );

  const applyFilters = useCallback(
    (filters: QueryFilters) => {
      setQueryParams((prev) => {
        const newParams = { ...prev, filters, page: 1 };
        queryMutation.mutate(newParams);
        return newParams;
      });
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [],
  );

  const changeSort = useCallback(
    (sortBy: string, sortOrder: string) => {
      setQueryParams((prev) => {
        const newParams = {
          ...prev,
          sort_by: sortBy as any,
          sort_order: sortOrder as any,
          page: 1,
        };
        queryMutation.mutate(newParams);
        return newParams;
      });
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [],
  );

  const clearHistory = useCallback(() => setQueryHistory([]), []);

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
    clearHistory,
  };
};
