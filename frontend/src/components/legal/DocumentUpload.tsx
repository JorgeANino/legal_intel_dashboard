'use client';

import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { useDocuments } from '@/hooks/useDocuments';
import { ErrorDisplay } from '../ui/ErrorDisplay';

const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB
const ACCEPTED_TYPES = {
  'application/pdf': ['.pdf'],
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
};

export const DocumentUpload = () => {
  const { uploadDocuments, isUploading, uploadProgress } = useDocuments();
  const [rejectedFiles, setRejectedFiles] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback(
    (acceptedFiles: File[], rejectedFiles: any[]) => {
      try {
        setRejectedFiles([]);
        setError(null);

        // Validate file sizes
        const validFiles = acceptedFiles.filter((file) => {
          if (file.size > MAX_FILE_SIZE) {
            setRejectedFiles((prev) => [
              ...prev,
              `${file.name}: File too large (max 50MB)`,
            ]);
            return false;
          }
          return true;
        });

        // Show rejected file errors
        rejectedFiles.forEach((rejected) => {
          setRejectedFiles((prev) => [
            ...prev,
            `${rejected.file.name}: Invalid file type (PDF or DOCX only)`,
          ]);
        });

        if (validFiles.length > 0) {
          uploadDocuments(validFiles);
        }
      } catch (err) {
        console.error('Error in onDrop:', err);
        setError('An error occurred while processing files. Please try again.');
      }
    },
    [uploadDocuments]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ACCEPTED_TYPES,
    multiple: true,
    disabled: isUploading,
    onError: (err) => {
      console.error('Dropzone error:', err);
      setError('An error occurred with the file drop zone. Please try again.');
    },
  });

  return (
    <div className="space-y-6">
      <div
        {...getRootProps()}
        className={`
          relative border-2 border-dashed rounded-lg p-12 text-center cursor-pointer
          transition-all duration-200
          ${isDragActive ? 'border-primary bg-primary/10 scale-[1.02]' : 'border-gray-300 hover:border-primary'}
          ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}
        `}
      >
        <input {...getInputProps()} />
        
        <div className="flex flex-col items-center space-y-4">
          <svg
            className="w-16 h-16 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
            />
          </svg>

          {isDragActive ? (
            <p className="text-lg font-medium text-primary">Drop files here...</p>
          ) : (
            <>
              <p className="text-lg font-medium">
                Drag & drop legal documents here, or click to select
              </p>
              <p className="text-sm text-gray-500">
                Supports PDF and DOCX files (max 50MB each)
              </p>
            </>
          )}
        </div>
      </div>

      {/* Upload Progress */}
      {isUploading && (
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="font-medium">Uploading documents...</span>
            <span className="text-gray-500">{uploadProgress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
            <div
              className="bg-primary h-2 rounded-full transition-all duration-300"
              style={{ width: `${uploadProgress}%` }}
            />
          </div>
          <p className="text-sm text-gray-500">
            Processing will continue in the background
          </p>
        </div>
      )}

      {/* General Error */}
      {error && (
        <ErrorDisplay
          title="Upload Error"
          message={error}
          onDismiss={() => setError(null)}
        />
      )}

      {/* Rejected Files */}
      {rejectedFiles.length > 0 && (
        <ErrorDisplay
          title="Some files were rejected"
          errors={rejectedFiles}
          onDismiss={() => setRejectedFiles([])}
        />
      )}
    </div>
  );
};

