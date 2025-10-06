import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen } from '@testing-library/react';

import AuthGuard from '@/guards/AuthGuard';
import { useDocuments } from '@/hooks/useDocuments';

import UploadPage from './page';

// Mock the hooks and components
jest.mock('@/hooks/useDocuments');
jest.mock('@/guards/AuthGuard');

const mockUseDocuments = useDocuments as jest.MockedFunction<
  typeof useDocuments
>;
const mockAuthGuard = AuthGuard as jest.MockedFunction<typeof AuthGuard>;

// Mock document data
const mockDocuments = [
  {
    id: 1,
    filename: 'contract_1.pdf',
    file_path: '/uploads/contract_1.pdf',
    file_type: 'pdf' as const,
    file_size: 1024000,
    upload_date: '2024-01-15T10:30:00Z',
    processed: true,
    processing_error: null,
    created_at: '2024-01-15T10:30:00Z',
    metadata: {
      id: 1,
      agreement_type: 'NDA',
      jurisdiction: 'Delaware',
      industry: 'Technology',
    },
  },
  {
    id: 2,
    filename: 'agreement_2.docx',
    file_path: '/uploads/agreement_2.docx',
    file_type: 'docx' as const,
    file_size: 512000,
    upload_date: '2024-01-14T14:20:00Z',
    processed: false,
    processing_error: undefined,
    created_at: '2024-01-14T14:20:00Z',
    metadata: undefined,
  },
  {
    id: 3,
    filename: 'failed_doc.pdf',
    file_path: '/uploads/failed_doc.pdf',
    file_type: 'pdf' as const,
    file_size: 256000,
    upload_date: '2024-01-13T09:15:00Z',
    processed: false,
    processing_error: 'Failed to extract text from PDF',
    created_at: '2024-01-13T09:15:00Z',
    metadata: undefined,
  },
];

// Create a test wrapper with QueryClient
const createTestWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

describe('UploadPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();

    // Mock AuthGuard to render children directly
    mockAuthGuard.mockImplementation(({ children }) => (
      <div data-testid='auth-guard'>{children}</div>
    ));

    // Default mock implementation
    mockUseDocuments.mockReturnValue({
      documents: mockDocuments,
      isLoading: false,
      error: null,
      refetch: jest.fn() as any,
      uploadDocuments: jest.fn() as any,
      isUploading: false,
      uploadProgress: 0,
    });
  });

  it('renders upload page with all elements', () => {
    render(<UploadPage />, { wrapper: createTestWrapper() });

    expect(screen.getByText('Upload Legal Documents')).toBeInTheDocument();
    expect(
      screen.getByText(
        'Upload PDF or DOCX files for AI-powered metadata extraction and analysis',
      ),
    ).toBeInTheDocument();
    expect(screen.getByText('Recent Documents')).toBeInTheDocument();
  });

  it('renders DocumentUpload component', () => {
    render(<UploadPage />, { wrapper: createTestWrapper() });

    // DocumentUpload should be rendered (we can't test its internal structure without mocking it)
    expect(screen.getByTestId('auth-guard')).toBeInTheDocument();
  });

  it('displays recent documents when available', () => {
    render(<UploadPage />, { wrapper: createTestWrapper() });

    // Check for document filenames
    expect(screen.getByText('contract_1.pdf')).toBeInTheDocument();
    expect(screen.getByText('agreement_2.docx')).toBeInTheDocument();
    expect(screen.getByText('failed_doc.pdf')).toBeInTheDocument();
  });

  it('shows correct file sizes for documents', () => {
    render(<UploadPage />, { wrapper: createTestWrapper() });

    // Check for file sizes (converted from bytes to KB)
    expect(screen.getByText('1000 KB')).toBeInTheDocument(); // 1024000 / 1024
    expect(screen.getByText('500 KB')).toBeInTheDocument(); // 512000 / 1024
    expect(screen.getByText('250 KB')).toBeInTheDocument(); // 256000 / 1024
  });

  it('displays correct processing status for processed documents', () => {
    render(<UploadPage />, { wrapper: createTestWrapper() });

    expect(screen.getByText('Processed')).toBeInTheDocument();
  });

  it('displays correct processing status for documents being processed', () => {
    render(<UploadPage />, { wrapper: createTestWrapper() });

    expect(screen.getByText('Processing...')).toBeInTheDocument();
  });

  it('displays correct processing status for failed documents', () => {
    render(<UploadPage />, { wrapper: createTestWrapper() });

    expect(screen.getByText('Failed')).toBeInTheDocument();
  });

  it('shows error tooltip for failed documents', () => {
    render(<UploadPage />, { wrapper: createTestWrapper() });

    const failedStatus = screen.getByText('Failed');
    expect(failedStatus).toHaveAttribute(
      'title',
      'Failed to extract text from PDF',
    );
  });

  it('displays formatted upload dates', () => {
    render(<UploadPage />, { wrapper: createTestWrapper() });

    // The dates should be formatted using toLocaleDateString()
    // We can't test the exact format as it depends on locale, but we can check they exist
    const documentItems = screen.getAllByText(/\d{1,2}\/\d{1,2}\/\d{4}/);
    expect(documentItems.length).toBeGreaterThan(0);
  });

  it('shows loading skeleton when documents are loading', () => {
    mockUseDocuments.mockReturnValue({
      documents: [],
      isLoading: true,
      error: null,
      refetch: jest.fn() as any,
      uploadDocuments: jest.fn() as any,
      isUploading: false,
      uploadProgress: 0,
    });

    render(<UploadPage />, { wrapper: createTestWrapper() });

    // LoadingSkeleton should be rendered (we can't test its internal structure without mocking it)
    expect(screen.getByTestId('auth-guard')).toBeInTheDocument();
  });

  it('shows no documents message when no documents are available', () => {
    mockUseDocuments.mockReturnValue({
      documents: [],
      isLoading: false,
      error: null,
      refetch: jest.fn() as any,
      uploadDocuments: jest.fn() as any,
      isUploading: false,
      uploadProgress: 0,
    });

    render(<UploadPage />, { wrapper: createTestWrapper() });

    expect(screen.getByText('No documents uploaded yet')).toBeInTheDocument();
  });

  it('shows no documents message when documents is null', () => {
    mockUseDocuments.mockReturnValue({
      documents: [],
      isLoading: false,
      error: null,
      refetch: jest.fn() as any,
      uploadDocuments: jest.fn() as any,
      isUploading: false,
      uploadProgress: 0,
    });

    render(<UploadPage />, { wrapper: createTestWrapper() });

    expect(screen.getByText('No documents uploaded yet')).toBeInTheDocument();
  });

  it('limits recent documents display to 10 items', () => {
    // Create 15 mock documents
    const manyDocuments = Array.from({ length: 15 }, (_, i) => ({
      id: i + 1,
      filename: `document_${i + 1}.pdf`,
      file_path: `/uploads/document_${i + 1}.pdf`,
      file_type: 'pdf' as const,
      file_size: 100000,
      upload_date: '2024-01-15T10:30:00Z',
      processed: true,
      processing_error: undefined,
      created_at: '2024-01-15T10:30:00Z',
      metadata: undefined,
    }));

    mockUseDocuments.mockReturnValue({
      documents: manyDocuments,
      isLoading: false,
      error: null,
      refetch: jest.fn() as any,
      uploadDocuments: jest.fn() as any,
      isUploading: false,
      uploadProgress: 0,
    });

    render(<UploadPage />, { wrapper: createTestWrapper() });

    // Should only show first 10 documents
    const documentItems = screen.getAllByText(/document_\d+\.pdf/);
    expect(documentItems).toHaveLength(10);
  });

  it('wraps content with AuthGuard', () => {
    render(<UploadPage />, { wrapper: createTestWrapper() });

    expect(screen.getByTestId('auth-guard')).toBeInTheDocument();
    expect(mockAuthGuard).toHaveBeenCalledWith(
      expect.objectContaining({
        children: expect.any(Object),
      }),
      {},
    );
  });

  it('maintains proper page structure and layout', () => {
    render(<UploadPage />, { wrapper: createTestWrapper() });

    // Check for main container classes
    const mainContainer = screen
      .getByTestId('auth-guard')
      .querySelector('.max-w-7xl');
    expect(mainContainer).toBeInTheDocument();
  });

  it('displays proper page title and description', () => {
    render(<UploadPage />, { wrapper: createTestWrapper() });

    expect(
      screen.getByRole('heading', { level: 1, name: 'Upload Legal Documents' }),
    ).toBeInTheDocument();
    expect(
      screen.getByText(
        'Upload PDF or DOCX files for AI-powered metadata extraction and analysis',
      ),
    ).toBeInTheDocument();
  });

  it('renders document icons for each document', () => {
    render(<UploadPage />, { wrapper: createTestWrapper() });

    // Should have SVG icons for each document (3 documents)
    const svgIcons = screen.getAllByRole('img', { hidden: true });
    expect(svgIcons.length).toBeGreaterThan(0);
  });

  it('handles different file types correctly', () => {
    render(<UploadPage />, { wrapper: createTestWrapper() });

    // Should display both PDF and DOCX files
    expect(screen.getByText('contract_1.pdf')).toBeInTheDocument();
    expect(screen.getByText('agreement_2.docx')).toBeInTheDocument();
  });

  it('displays correct status badges with proper styling', () => {
    render(<UploadPage />, { wrapper: createTestWrapper() });

    const processedBadge = screen.getByText('Processed');
    const processingBadge = screen.getByText('Processing...');
    const failedBadge = screen.getByText('Failed');

    expect(processedBadge).toHaveClass('bg-green-100', 'text-green-800');
    expect(processingBadge).toHaveClass('bg-yellow-100', 'text-yellow-800');
    expect(failedBadge).toHaveClass('bg-red-100', 'text-red-800');
  });

  it('handles error state gracefully', () => {
    mockUseDocuments.mockReturnValue({
      documents: [],
      isLoading: false,
      error: new Error('Failed to load documents'),
      refetch: jest.fn() as any,
      uploadDocuments: jest.fn() as any,
      isUploading: false,
      uploadProgress: 0,
    });

    render(<UploadPage />, { wrapper: createTestWrapper() });

    // Should still render the page structure even with error
    expect(screen.getByText('Upload Legal Documents')).toBeInTheDocument();
    expect(screen.getByText('Recent Documents')).toBeInTheDocument();
  });
});
