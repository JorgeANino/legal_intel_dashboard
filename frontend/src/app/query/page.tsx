'use client';

import { QueryInput } from '@/components/legal/QueryInput';
import { ResultsTable } from '@/components/legal/ResultsTable';
import { useDocumentQuery } from '@/hooks/useDocumentQuery';
import Link from 'next/link';

export default function QueryPage() {
  const { queryResult } = useDocumentQuery();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="text-2xl font-bold text-gray-900 hover:text-primary transition-colors">
              Legal Intel Dashboard
            </Link>
            <nav className="flex gap-4">
              <Link
                href="/"
                className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-primary transition-colors"
              >
                Dashboard
              </Link>
              <Link
                href="/upload"
                className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-primary transition-colors"
              >
                Upload Documents
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="space-y-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Query Documents</h1>
            <p className="mt-2 text-gray-600">
              Ask natural language questions about your legal documents
            </p>
          </div>

          {/* Query Input */}
          <QueryInput />

          {/* Results */}
          {queryResult && (
            <div>
              <ResultsTable data={queryResult} />
            </div>
          )}

          {/* No Results Yet */}
          {!queryResult && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
              <svg
                className="mx-auto h-12 w-12 text-gray-400 mb-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Start Your Search</h3>
              <p className="text-gray-500">
                Enter a question above or try one of the example queries
              </p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

