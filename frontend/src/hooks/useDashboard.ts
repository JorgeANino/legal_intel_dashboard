'use client';

import { useQuery } from '@tanstack/react-query';

import { dashboardApi } from '@/api/dashboard';

export const useDashboard = () => {
  const {
    data: stats,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => dashboardApi.getStats(),
    staleTime: 60000,
    refetchOnWindowFocus: true,
    retry: 3,
  });

  return {
    stats,
    isLoading,
    error,
    refetch,
  };
};
