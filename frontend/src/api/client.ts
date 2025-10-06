import axios, { AxiosError, AxiosInstance } from 'axios';

// API base configuration
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
const API_TIMEOUT = 30000; // 30 seconds

// Create axios instance
export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - add auth, logging
apiClient.interceptors.request.use(
  (config) => {
    // Add timestamp for request tracking
    config.metadata = { startTime: Date.now() };

    // Add auth token if available (for future use)
    // const token = localStorage.getItem('auth_token');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }

    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('Request Error:', error);
    return Promise.reject(error);
  },
);

// Response interceptor - handle errors, logging
apiClient.interceptors.response.use(
  (response) => {
    const duration = Date.now() - (response.config.metadata?.startTime || 0);
    console.log(`API Response: ${response.config.url} (${duration}ms)`);
    return response;
  },
  async (error: AxiosError) => {
    const duration = Date.now() - (error.config?.metadata?.startTime || 0);
    console.error(
      `API Error: ${error.config?.url} (${duration}ms)`,
      error.response?.data,
    );

    // Handle specific error codes
    if (error.response?.status === 429) {
      // Rate limit exceeded
      throw new Error('Too many requests. Please wait a moment and try again.');
    }

    if (error.response?.status === 500) {
      throw new Error('Server error. Our team has been notified.');
    }

    if (error.code === 'ECONNABORTED') {
      throw new Error('Request timeout. Please check your connection.');
    }

    if (!error.response) {
      throw new Error('Network error. Please check your connection.');
    }

    return Promise.reject(error);
  },
);

// Helper for file uploads with progress
export const uploadWithProgress = (
  url: string,
  formData: FormData,
  onProgress?: (progress: number) => void,
) => {
  return apiClient.post(url, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent) => {
      if (progressEvent.total && onProgress) {
        const progress = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total,
        );
        onProgress(progress);
      }
    },
  });
};

// Extend AxiosRequestConfig to include metadata
declare module 'axios' {
  export interface AxiosRequestConfig {
    metadata?: {
      startTime: number;
    };
  }
}
