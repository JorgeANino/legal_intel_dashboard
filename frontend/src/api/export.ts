import { apiClient } from './client';
import { QueryFilters } from './types';

export interface ExportRequest {
  question: string;
  user_id: number;
  max_results?: number;
  filters?: QueryFilters;
  filename?: string;
  template?: string;
}

export interface DashboardExportRequest {
  user_id: number;
  include_charts?: boolean;
  date_range?: {
    start: string;
    end: string;
  };
  format?: string;
}

export const exportApi = {
  /**
   * Export query results as CSV
   */
  exportQueryResultsCSV: async (request: ExportRequest): Promise<Blob> => {
    const response = await apiClient.post('/export/query-results/csv', request, {
      responseType: 'blob'
    });
    return response.data;
  },

  /**
   * Export query results as PDF
   */
  exportQueryResultsPDF: async (request: ExportRequest): Promise<Blob> => {
    const response = await apiClient.post('/export/query-results/pdf', request, {
      responseType: 'blob'
    });
    return response.data;
  },

  /**
   * Export dashboard report as PDF
   */
  exportDashboardReportPDF: async (request: DashboardExportRequest): Promise<Blob> => {
    const response = await apiClient.post('/export/dashboard-report/pdf', request, {
      responseType: 'blob'
    });
    return response.data;
  }
};
