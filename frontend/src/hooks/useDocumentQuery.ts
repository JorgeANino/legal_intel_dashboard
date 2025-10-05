import { useMutation } from '@tanstack/react-query';
import { queryApi } from '@/api/query';
import { QueryRequest, QueryResponse } from '@/api/types';
import { useState } from 'react';
import toast from 'react-hot-toast';

export const useDocumentQuery = () => {
  const [queryHistory, setQueryHistory] = useState<QueryResponse[]>([]);

  const queryMutation = useMutation({
    mutationFn: (request: QueryRequest) => queryApi.queryDocuments(request),
    onSuccess: (data) => {
      // Add to history
      setQueryHistory((prev) => [data, ...prev].slice(0, 10)); // Keep last 10
      
      if (data.total_results === 0) {
        toast('No documents match your query', { icon: 'ℹ️' });
      }
    },
    onError: (error: any) => {
      toast.error(error.message || 'Query failed. Please try again.');
    },
  });

  return {
    executeQuery: queryMutation.mutate,
    isQuerying: queryMutation.isPending,
    queryResult: queryMutation.data,
    queryError: queryMutation.error,
    queryHistory,
    clearHistory: () => setQueryHistory([]),
  };
};

