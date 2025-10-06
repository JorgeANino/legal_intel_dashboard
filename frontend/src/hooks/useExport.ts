import { useState } from 'react';
import { exportApi, ExportRequest, DashboardExportRequest } from '@/api/export';
import { QueryResponse, DashboardStats } from '@/api/types';
import toast from 'react-hot-toast';

export const useExport = () => {
  const [isExporting, setIsExporting] = useState(false);

  const downloadFile = (blob: Blob, filename: string) => {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  };

  const exportToCSV = async (data: QueryResponse) => {
    setIsExporting(true);
    try {
      const request: ExportRequest = {
        question: data.question,
        user_id: 1, // Mock user ID
        max_results: data.total_results,
        filters: data.filters_applied,
        filename: `query-results-${Date.now()}`
      };

      const blob = await exportApi.exportQueryResultsCSV(request);
      downloadFile(blob, `query-results-${Date.now()}.csv`);
      
      toast.success('CSV exported successfully!');
    } catch (error: any) {
      console.error('CSV export failed:', error);
      toast.error('Failed to export CSV. Please try again.');
      throw error;
    } finally {
      setIsExporting(false);
    }
  };

  const exportToPDF = async (data: QueryResponse) => {
    setIsExporting(true);
    try {
      const request: ExportRequest = {
        question: data.question,
        user_id: 1, // Mock user ID
        max_results: data.total_results,
        filters: data.filters_applied,
        filename: `query-results-${Date.now()}`
      };

      const blob = await exportApi.exportQueryResultsPDF(request);
      downloadFile(blob, `query-results-${Date.now()}.pdf`);
      
      toast.success('PDF exported successfully!');
    } catch (error: any) {
      console.error('PDF export failed:', error);
      toast.error('Failed to export PDF. Please try again.');
      throw error;
    } finally {
      setIsExporting(false);
    }
  };

  const exportDashboardReport = async (stats: DashboardStats) => {
    setIsExporting(true);
    try {
      const request: DashboardExportRequest = {
        user_id: 1, // Mock user ID
        include_charts: true
      };

      const blob = await exportApi.exportDashboardReportPDF(request);
      const filename = `dashboard-report-${new Date().toISOString().split('T')[0]}.pdf`;
      downloadFile(blob, filename);
      
      toast.success('Dashboard report exported successfully!');
    } catch (error: any) {
      console.error('Dashboard export failed:', error);
      toast.error('Failed to export dashboard report. Please try again.');
      throw error;
    } finally {
      setIsExporting(false);
    }
  };

  return {
    exportToCSV,
    exportToPDF,
    exportDashboardReport,
    isExporting
  };
};
