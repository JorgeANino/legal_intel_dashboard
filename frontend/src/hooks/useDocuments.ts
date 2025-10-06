'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import toast from 'react-hot-toast';

import { documentsApi } from '@/api/documents';

export const useDocuments = () => {
  const queryClient = useQueryClient();
  const [uploadProgress, setUploadProgress] = useState(0);

  // Fetch documents list
  const {
    data: documents,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['documents'],
    queryFn: () => documentsApi.listDocuments(),
    staleTime: 60000,
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    refetchOnWindowFocus: true,
  });

  // Upload mutation
  const uploadMutation = useMutation({
    mutationFn: (files: File[]) =>
      documentsApi.uploadDocuments(files, (progress: number) => {
        setUploadProgress(progress);
      }),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });

      toast.success(
        `Successfully uploaded ${data.successful} of ${data.total} documents`,
      );

      setUploadProgress(0);
    },
    onError: (error: any) => {
      toast.error(error.message || 'Upload failed. Please try again.');
      setUploadProgress(0);
    },
  });

  return {
    documents,
    isLoading,
    error,
    refetch,
    uploadDocuments: uploadMutation.mutate,
    isUploading: uploadMutation.isPending,
    uploadProgress,
  };
};
