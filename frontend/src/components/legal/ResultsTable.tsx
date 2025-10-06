'use client';

import { useMemo, useState } from 'react';

import { QueryResponse, QueryFilters } from '@/api/types';
import { Pagination } from '@/components/ui/Pagination';
import { useExport } from '@/hooks/useExport';

import { QueryFilters as QueryFiltersComponent } from './QueryFilters';

interface Props {
  data: QueryResponse;
  onPageChange?: (page: number) => void;
  onFilterChange?: (filters: QueryFilters) => void;
  _onSortChange?: (sortBy: string, sortOrder: string) => void;
  availableFilters?: {
    agreement_types: string[];
    jurisdictions: string[];
    industries: string[];
    geographies: string[];
  };
}

export const ResultsTable = ({
  data,
  onPageChange,
  onFilterChange,
  _onSortChange,
  availableFilters,
}: Props) => {
  const [exportFormat, setExportFormat] = useState<'csv' | 'pdf'>('csv');
  const { exportToCSV, exportToPDF, isExporting } = useExport();

  const handleExport = async () => {
    try {
      if (exportFormat === 'csv') {
        await exportToCSV(data);
      } else {
        await exportToPDF(data);
      }
      // Error handling is done in the hook
    } catch {
      // Catch block required but error handled in hook
    }
  };

  // Extract column headers from first result
  const columns = useMemo(() => {
    if (data.results.length === 0) return [];

    const firstResult = data.results[0];
    const metadataKeys = Object.keys(firstResult.metadata);

    return ['document', ...metadataKeys];
  }, [data.results]);

  if (data.results.length === 0) {
    return (
      <div className='text-center py-12'>
        <svg
          className='mx-auto h-12 w-12 text-gray-400'
          fill='none'
          stroke='currentColor'
          viewBox='0 0 24 24'
        >
          <path
            strokeLinecap='round'
            strokeLinejoin='round'
            strokeWidth={2}
            d='M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z'
          />
        </svg>
        <h3 className='mt-2 text-sm font-medium text-gray-900'>
          No documents found
        </h3>
        <p className='mt-1 text-sm text-gray-500'>Try adjusting your query</p>
      </div>
    );
  }

  return (
    <div className='space-y-4'>
      {/* Filters Section */}
      {availableFilters && onFilterChange && (
        <QueryFiltersComponent
          onFilterChange={onFilterChange}
          availableFilters={availableFilters}
          currentFilters={data.filters_applied}
        />
      )}

      {/* Query Info and Export Controls */}
      <div className='flex items-center justify-between p-4 bg-gray-50 rounded-lg'>
        <div>
          <p className='font-medium text-gray-900'>
            Query: &ldquo;{data.question}&rdquo;
          </p>
          <p className='text-sm text-gray-500 mt-1'>
            Found {data.total_results} result
            {data.total_results !== 1 ? 's' : ''} in {data.execution_time_ms}ms
            {data.page && data.total_pages && (
              <span>
                {' '}
                • Page {data.page} of {data.total_pages}
              </span>
            )}
          </p>
        </div>

        <div className='flex items-center space-x-4'>
          <select
            value={exportFormat}
            onChange={(e) => setExportFormat(e.target.value as 'csv' | 'pdf')}
            className='border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
          >
            <option value='csv'>CSV</option>
            <option value='pdf'>PDF</option>
          </select>

          <button
            onClick={handleExport}
            disabled={isExporting}
            className='px-4 py-2 text-sm bg-white border border-gray-300 rounded-md
                     hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed'
          >
            {isExporting
              ? 'Exporting...'
              : `Export ${exportFormat.toUpperCase()}`}
          </button>
        </div>
      </div>

      {/* Results Table */}
      <div className='overflow-x-auto border border-gray-200 rounded-lg'>
        <table className='min-w-full divide-y divide-gray-200'>
          <thead className='bg-gray-50'>
            <tr>
              {columns.map((column) => (
                <th
                  key={column}
                  className='px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider'
                >
                  {column.replace(/_/g, ' ')}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className='bg-white divide-y divide-gray-200'>
            {data.results.map((result, idx) => (
              <tr key={idx} className='hover:bg-gray-50 transition-colors'>
                <td className='px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900'>
                  {result.document}
                </td>
                {Object.entries(result.metadata).map(([key, value]) => (
                  <td
                    key={key}
                    className='px-6 py-4 whitespace-nowrap text-sm text-gray-500'
                  >
                    {value || '-'}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {data.total_pages && data.total_pages > 1 && onPageChange && (
        <div className='mt-4'>
          <Pagination
            currentPage={data.page}
            totalPages={data.total_pages}
            onPageChange={onPageChange}
          />
        </div>
      )}
    </div>
  );
};
