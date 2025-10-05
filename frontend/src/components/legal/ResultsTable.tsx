'use client';

import { QueryResponse } from '@/api/types';
import { useMemo } from 'react';

interface Props {
  data: QueryResponse;
}

export const ResultsTable = ({ data }: Props) => {
  // Extract column headers from first result
  const columns = useMemo(() => {
    if (data.results.length === 0) return [];
    
    const firstResult = data.results[0];
    const metadataKeys = Object.keys(firstResult.metadata);
    
    return ['document', ...metadataKeys];
  }, [data.results]);

  if (data.results.length === 0) {
    return (
      <div className="text-center py-12">
        <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <h3 className="mt-2 text-sm font-medium text-gray-900">No documents found</h3>
        <p className="mt-1 text-sm text-gray-500">Try adjusting your query</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Query Info */}
      <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
        <div>
          <p className="font-medium text-gray-900">Query: "{data.question}"</p>
          <p className="text-sm text-gray-500 mt-1">
            Found {data.total_results} result{data.total_results !== 1 ? 's' : ''} 
            {' '}in {data.execution_time_ms}ms
          </p>
        </div>
        <button
          onClick={() => {
            // Export to CSV functionality
            const csv = convertToCSV(data);
            downloadCSV(csv, `query-results-${Date.now()}.csv`);
          }}
          className="px-4 py-2 text-sm bg-white border border-gray-300 rounded-md
                   hover:bg-gray-50 transition-colors"
        >
          Export CSV
        </button>
      </div>

      {/* Results Table */}
      <div className="overflow-x-auto border border-gray-200 rounded-lg">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              {columns.map((column) => (
                <th
                  key={column}
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  {column.replace(/_/g, ' ')}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {data.results.map((result, idx) => (
              <tr key={idx} className="hover:bg-gray-50 transition-colors">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {result.document}
                </td>
                {Object.entries(result.metadata).map(([key, value]) => (
                  <td key={key} className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {value || '-'}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// Helper functions
function convertToCSV(data: QueryResponse): string {
  const headers = ['document', ...Object.keys(data.results[0]?.metadata || {})];
  const rows = data.results.map(r => [
    r.document,
    ...Object.values(r.metadata)
  ]);
  
  return [
    headers.join(','),
    ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
  ].join('\n');
}

function downloadCSV(csv: string, filename: string) {
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  window.URL.revokeObjectURL(url);
}

