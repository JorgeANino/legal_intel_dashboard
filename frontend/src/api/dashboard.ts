import { apiClient } from './client';
import { DashboardStats } from './types';

export const dashboardApi = {
  /**
   * Get dashboard statistics (cached)
   */
  getStats: async (): Promise<DashboardStats> => {
    const response = await apiClient.get('/dashboard');
    return response.data;
  },
};
