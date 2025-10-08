'use client';

import axios, {
  AxiosError,
  AxiosInstance,
  InternalAxiosRequestConfig,
} from 'axios';

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
  withCredentials: false, // Set to false since we're using Bearer tokens
});

// Helper to get access token from localStorage
const getAccessToken = (): string | null => {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('access_token');
};

// Request interceptor - add auth token and logging
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Add timestamp for request tracking
    config.metadata = { startTime: Date.now() };

    // CRITICAL: Add auth token if available (browser only)
    if (typeof window !== 'undefined') {
      const token = getAccessToken();

      console.log('==================== API REQUEST ====================');
      console.log(
        `🚀 ${config.method?.toUpperCase()} ${config.baseURL}${config.url}`,
      );
      console.log(
        '📝 Token in localStorage:',
        token ? `YES (${token.length} chars)` : 'NO - MISSING!',
      );

      if (token) {
        // FORCE set Authorization header
        config.headers.Authorization = `Bearer ${token}`;
        console.log(
          '✅ Authorization header SET:',
          config.headers.Authorization ? 'YES' : 'NO - FAILED!',
        );
      } else {
        console.error('❌ NO TOKEN FOUND - Request will FAIL with 401!');
        console.log('💡 localStorage keys:', Object.keys(localStorage));
      }

      console.log('📋 All headers:', JSON.stringify(config.headers, null, 2));
      console.log('====================================================');
    }

    return config;
  },
  (error) => {
    console.error('❌ Request interceptor error:', error);
    return Promise.reject(error);
  },
);

// Response interceptor - handle errors, logging, and auth
apiClient.interceptors.response.use(
  (response) => {
    const duration = Date.now() - (response.config.metadata?.startTime || 0);
    console.log(
      `[API Client] ✓ Response: ${response.config.url} (${duration}ms) - Status: ${response.status}`,
    );
    return response;
  },
  async (error: AxiosError) => {
    const duration = Date.now() - (error.config?.metadata?.startTime || 0);
    console.error(
      `[API Client] ❌ Error: ${error.config?.url} (${duration}ms) - Status: ${error.response?.status}`,
      error.response?.data,
    );

    // Handle authentication errors
    if (error.response?.status === 401) {
      console.warn(
        '[API Client] 🔒 Unauthorized - clearing tokens and redirecting to login',
      );

      // Clear invalid tokens
      if (typeof window !== 'undefined') {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');

        // Redirect to login (only if not already on login page)
        if (!window.location.pathname.includes('/login')) {
          console.log('[API Client] Redirecting to /login');
          window.location.href = '/login';
        }
      }

      throw new Error('Session expired. Please login again.');
    }

    // Handle specific error codes
    if (error.response?.status === 429) {
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
