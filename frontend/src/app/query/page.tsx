'use client';

import { QueryInput } from '@/components/legal/QueryInput';
import { ResultsTable } from '@/components/legal/ResultsTable';
import AuthGuard from '@/guards/AuthGuard';
import { useDocumentQuery } from '@/hooks/useDocumentQuery';

export default function QueryPage() {
  const { queryResult, changePage, applyFilters, changeSort } =
    useDocumentQuery();

  // Mock available filters - in a real app, this would come from the API
  const availableFilters = {
    agreement_types: [
      'NDA',
      'MSA',
      'Service Agreement',
      'License Agreement',
      'Franchise Agreement',
    ],
    jurisdictions: ['Delaware', 'New York', 'California', 'UAE', 'UK'],
    industries: [
      'Technology',
      'Healthcare',
      'Finance',
      'Oil & Gas',
      'Real Estate',
    ],
    geographies: ['North America', 'Europe', 'Middle East', 'Asia'],
  };

  return (
    <AuthGuard>
      <div className='max-w-7xl mx-auto px-6 py-8'>
        <div className='space-y-8'>
          <div>
            <h1 className='text-3xl font-bold text-gray-900'>
              Query Documents
            </h1>
            <p className='mt-2 text-gray-600'>
              Ask natural language questions about your legal documents
            </p>
          </div>

          {/* Query Input */}
          <QueryInput />

          {/* Results */}
          {queryResult && (
            <div>
              <ResultsTable
                data={queryResult}
                onPageChange={changePage}
                onFilterChange={applyFilters}
                onSortChange={changeSort}
                availableFilters={availableFilters}
              />
            </div>
          )}

          {/* No Results Yet */}
          {!queryResult && (
            <div className='bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center'>
              <svg
                className='mx-auto h-12 w-12 text-gray-400 mb-4'
                fill='none'
                stroke='currentColor'
                viewBox='0 0 24 24'
              >
                <path
                  strokeLinecap='round'
                  strokeLinejoin='round'
                  strokeWidth={2}
                  d='M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z'
                />
              </svg>
              <h3 className='text-lg font-medium text-gray-900 mb-2'>
                Start Your Search
              </h3>
              <p className='text-gray-500'>
                Enter a question above or try one of the example queries
              </p>
            </div>
          )}
        </div>
      </div>
    </AuthGuard>
  );
}
