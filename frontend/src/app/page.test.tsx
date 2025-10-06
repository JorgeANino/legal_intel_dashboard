import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import DashboardPage from './page';
import { useDashboard } from '@/hooks/useDashboard';
import { useExport } from '@/hooks/useExport';
import AuthGuard from '@/guards/AuthGuard';

// Mock the hooks
jest.mock('@/hooks/useDashboard');
jest.mock('@/hooks/useExport');
jest.mock('@/guards/AuthGuard');
jest.mock('next/navigation');

const mockUseDashboard = useDashboard as jest.MockedFunction<typeof useDashboard>;
const mockUseExport = useExport as jest.MockedFunction<typeof useExport>;
const mockAuthGuard = AuthGuard as jest.MockedFunction<typeof AuthGuard>;

// Mock dashboard stats data
const mockStats = {
  total_documents: 150,
  processed_documents: 140,
  total_pages: 2500,
  agreement_types: {
    'NDA': 45,
    'MSA': 30,
    'Service Agreement': 25,
    'License Agreement': 20,
    'Franchise Agreement': 10
  },
  jurisdictions: {
    'Delaware': 60,
    'New York': 40,
    'California': 30,
    'UAE': 15,
    'UK': 5
  },
  industries: {
    'Technology': 80,
    'Healthcare': 35,
    'Finance': 20,
    'Oil & Gas': 10,
    'Real Estate': 5
  },
  geographies: {
    'North America': 120,
    'Europe': 20,
    'Middle East': 8,
    'Asia': 2
  }
};

// Create a test wrapper with QueryClient
const createTestWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('DashboardPage', () => {
  const mockExportDashboardReport = jest.fn();
  const mockRefetch = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock AuthGuard to render children directly
    mockAuthGuard.mockImplementation(({ children }) => <div data-testid="auth-guard">{children}</div>);
    
    // Default mock implementations
    mockUseDashboard.mockReturnValue({
      stats: mockStats,
      isLoading: false,
      error: null,
      refetch: mockRefetch,
    });

    mockUseExport.mockReturnValue({
      exportDashboardReport: mockExportDashboardReport,
      isExporting: false,
    });
  });

  it('renders dashboard page with all components', () => {
    render(<DashboardPage />, { wrapper: createTestWrapper() });

    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Overview of your legal document collection')).toBeInTheDocument();
    expect(screen.getByText('Export Report')).toBeInTheDocument();
  });

  it('displays dashboard statistics when loaded', () => {
    render(<DashboardPage />, { wrapper: createTestWrapper() });

    // Check for stats cards
    expect(screen.getByText('150')).toBeInTheDocument(); // total_documents
    expect(screen.getByText('140')).toBeInTheDocument(); // processed_documents
    expect(screen.getByText('2,500')).toBeInTheDocument(); // total_pages

    // Check for industry coverage table
    expect(screen.getByText('Industry Coverage')).toBeInTheDocument();
    expect(screen.getByText('Technology')).toBeInTheDocument();
    expect(screen.getByText('80')).toBeInTheDocument();

    // Check for geographic coverage table
    expect(screen.getByText('Geographic Coverage')).toBeInTheDocument();
    expect(screen.getByText('North America')).toBeInTheDocument();
    expect(screen.getByText('120')).toBeInTheDocument();
  });

  it('shows loading skeletons when data is loading', () => {
    mockUseDashboard.mockReturnValue({
      stats: null,
      isLoading: true,
      error: null,
      refetch: mockRefetch,
    });

    render(<DashboardPage />, { wrapper: createTestWrapper() });

    // Check for loading skeletons
    const skeletons = screen.getAllByTestId('card-skeleton');
    expect(skeletons).toHaveLength(4); // 4 stat cards

    // Check for chart loading placeholders
    const chartPlaceholders = screen.getAllByText(/animate-pulse/);
    expect(chartPlaceholders.length).toBeGreaterThan(0);
  });

  it('displays error state when there is an error', () => {
    const errorMessage = 'Failed to load dashboard data';
    mockUseDashboard.mockReturnValue({
      stats: null,
      isLoading: false,
      error: new Error(errorMessage),
      refetch: mockRefetch,
    });

    render(<DashboardPage />, { wrapper: createTestWrapper() });

    expect(screen.getByText('Failed to load dashboard')).toBeInTheDocument();
    expect(screen.getByText(errorMessage)).toBeInTheDocument();
    expect(screen.getByText('Retry')).toBeInTheDocument();
  });

  it('calls refetch when retry button is clicked', () => {
    mockUseDashboard.mockReturnValue({
      stats: null,
      isLoading: false,
      error: new Error('Test error'),
      refetch: mockRefetch,
    });

    render(<DashboardPage />, { wrapper: createTestWrapper() });

    const retryButton = screen.getByText('Retry');
    fireEvent.click(retryButton);

    expect(mockRefetch).toHaveBeenCalledTimes(1);
  });

  it('calls export function when export button is clicked', () => {
    render(<DashboardPage />, { wrapper: createTestWrapper() });

    const exportButton = screen.getByText('Export Report');
    fireEvent.click(exportButton);

    expect(mockExportDashboardReport).toHaveBeenCalledWith(mockStats);
  });

  it('disables export button when exporting', () => {
    mockUseExport.mockReturnValue({
      exportDashboardReport: mockExportDashboardReport,
      isExporting: true,
    });

    render(<DashboardPage />, { wrapper: createTestWrapper() });

    const exportButton = screen.getByText('Exporting...');
    expect(exportButton).toBeDisabled();
  });

  it('disables export button when no stats available', () => {
    mockUseDashboard.mockReturnValue({
      stats: null,
      isLoading: false,
      error: null,
      refetch: mockRefetch,
    });

    render(<DashboardPage />, { wrapper: createTestWrapper() });

    const exportButton = screen.getByText('Export Report');
    expect(exportButton).toBeDisabled();
  });

  it('renders all agreement types in the chart', () => {
    render(<DashboardPage />, { wrapper: createTestWrapper() });

    // Check that all agreement types are present
    expect(screen.getByText('NDA')).toBeInTheDocument();
    expect(screen.getByText('MSA')).toBeInTheDocument();
    expect(screen.getByText('Service Agreement')).toBeInTheDocument();
    expect(screen.getByText('License Agreement')).toBeInTheDocument();
    expect(screen.getByText('Franchise Agreement')).toBeInTheDocument();
  });

  it('renders all jurisdictions in the chart', () => {
    render(<DashboardPage />, { wrapper: createTestWrapper() });

    // Check that all jurisdictions are present
    expect(screen.getByText('Delaware')).toBeInTheDocument();
    expect(screen.getByText('New York')).toBeInTheDocument();
    expect(screen.getByText('California')).toBeInTheDocument();
    expect(screen.getByText('UAE')).toBeInTheDocument();
    expect(screen.getByText('UK')).toBeInTheDocument();
  });

  it('handles empty stats gracefully', () => {
    const emptyStats = {
      total_documents: 0,
      processed_documents: 0,
      total_pages: 0,
      agreement_types: {},
      jurisdictions: {},
      industries: {},
      geographies: {}
    };

    mockUseDashboard.mockReturnValue({
      stats: emptyStats,
      isLoading: false,
      error: null,
      refetch: mockRefetch,
    });

    render(<DashboardPage />, { wrapper: createTestWrapper() });

    expect(screen.getByText('0')).toBeInTheDocument();
    expect(screen.getByText('Industry Coverage')).toBeInTheDocument();
    expect(screen.getByText('Geographic Coverage')).toBeInTheDocument();
  });

  it('wraps content with AuthGuard', () => {
    render(<DashboardPage />, { wrapper: createTestWrapper() });

    expect(screen.getByTestId('auth-guard')).toBeInTheDocument();
    expect(mockAuthGuard).toHaveBeenCalledWith(
      expect.objectContaining({
        children: expect.any(Object)
      }),
      {}
    );
  });
});
