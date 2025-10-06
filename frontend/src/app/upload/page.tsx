'use client';

import { DocumentUpload } from '@/components/legal/DocumentUpload';
import { LoadingSkeleton } from '@/components/ui/LoadingSkeleton';
import AuthGuard from '@/guards/AuthGuard';
import { useDocuments } from '@/hooks/useDocuments';

export default function UploadPage() {
  const { documents, isLoading } = useDocuments();

  return (
    <AuthGuard>
      <div className='max-w-7xl mx-auto px-6 py-8'>
        <div className='space-y-8'>
          <div>
            <h1 className='text-3xl font-bold text-gray-900'>
              Upload Legal Documents
            </h1>
            <p className='mt-2 text-gray-600'>
              Upload PDF or DOCX files for AI-powered metadata extraction and
              analysis
            </p>
          </div>

          {/* Upload Component */}
          <DocumentUpload />

          {/* Recent Documents */}
          <div className='bg-white rounded-lg shadow-sm border border-gray-200 p-6'>
            <h2 className='text-lg font-semibold text-gray-900 mb-4'>
              Recent Documents
            </h2>
            {isLoading ? (
              <LoadingSkeleton />
            ) : documents && documents.length > 0 ? (
              <div className='space-y-3'>
                {documents.slice(0, 10).map((doc) => (
                  <div
                    key={doc.id}
                    className='flex items-center justify-between p-3 bg-gray-50 rounded-lg'
                  >
                    <div className='flex items-center gap-3'>
                      <svg
                        className='w-5 h-5 text-gray-400'
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
                      <div>
                        <p className='text-sm font-medium text-gray-900'>
                          {doc.filename}
                        </p>
                        <p className='text-xs text-gray-500'>
                          {new Date(doc.upload_date).toLocaleDateString()} •{' '}
                          {(doc.file_size / 1024).toFixed(0)} KB
                        </p>
                      </div>
                    </div>
                    <div>
                      {doc.processed ? (
                        <span className='inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800'>
                          Processed
                        </span>
                      ) : doc.processing_error ? (
                        <span
                          className='inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800 cursor-help'
                          title={doc.processing_error}
                        >
                          Failed
                        </span>
                      ) : (
                        <span className='inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800'>
                          Processing...
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className='text-gray-500 text-center py-8'>
                No documents uploaded yet
              </p>
            )}
          </div>
        </div>
      </div>
    </AuthGuard>
  );
}
