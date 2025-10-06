import { apiClient } from './client';

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export const authApi = {
  /**
   * Authenticate user with email and password
   */
  login: async (credentials: LoginCredentials): Promise<LoginResponse> => {
    const response = await apiClient.post<LoginResponse>(
      '/auth/login',
      credentials,
    );
    return response.data;
  },

  /**
   * Get current user information
   */
  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get<User>('/auth/me');
    return response.data;
  },

  /**
   * Logout (client-side only - clears tokens)
   */
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  },
};
