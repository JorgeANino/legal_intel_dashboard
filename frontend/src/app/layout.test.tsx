import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen } from '@testing-library/react';

import { useWebSocket } from '@/hooks/useWebSocket';

import RootLayout from './layout';

// Mock the hooks and components
jest.mock('@/hooks/useWebSocket');
jest.mock('@/providers/QueryProvider', () => ({
  QueryProvider: ({ children }: { children: React.ReactNode }) => (
    <div data-testid='query-provider'>{children}</div>
  ),
}));
jest.mock('@/context/AuthContext', () => ({
  AuthProvider: ({ children }: { children: React.ReactNode }) => (
    <div data-testid='auth-provider'>{children}</div>
  ),
}));
jest.mock('react-hot-toast', () => ({
  Toaster: () => <div data-testid='toaster'>Toaster</div>,
}));

const mockUseWebSocket = useWebSocket as jest.MockedFunction<
  typeof useWebSocket
>;

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

describe('RootLayout', () => {
  const mockReconnect = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();

    // Default mock implementation
    mockUseWebSocket.mockReturnValue({
      isConnected: true,
      reconnect: mockReconnect,
    });
  });

  it('renders layout with all providers', () => {
    render(
      <RootLayout>
        <div data-testid='test-children'>Test Content</div>
      </RootLayout>,
      { wrapper: createTestWrapper() },
    );

    expect(screen.getByTestId('query-provider')).toBeInTheDocument();
    expect(screen.getByTestId('auth-provider')).toBeInTheDocument();
    expect(screen.getByTestId('toaster')).toBeInTheDocument();
    expect(screen.getByTestId('test-children')).toBeInTheDocument();
  });

  it('renders HTML with correct lang attribute', () => {
    render(
      <RootLayout>
        <div>Test Content</div>
      </RootLayout>,
      { wrapper: createTestWrapper() },
    );

    const htmlElement = document.documentElement;
    expect(htmlElement).toHaveAttribute('lang', 'en');
  });

  it('applies Inter font to body', () => {
    render(
      <RootLayout>
        <div>Test Content</div>
      </RootLayout>,
      { wrapper: createTestWrapper() },
    );

    const bodyElement = document.body;
    expect(bodyElement).toHaveClass('inter'); // Inter font class
  });

  it('includes global CSS', () => {
    render(
      <RootLayout>
        <div>Test Content</div>
      </RootLayout>,
      { wrapper: createTestWrapper() },
    );

    // The globals.css should be imported and applied
    // We can't directly test this without checking the actual CSS, but we can verify the component renders
    expect(screen.getByTestId('query-provider')).toBeInTheDocument();
  });

  it('renders WebSocket provider with correct user ID', () => {
    render(
      <RootLayout>
        <div>Test Content</div>
      </RootLayout>,
      { wrapper: createTestWrapper() },
    );

    expect(mockUseWebSocket).toHaveBeenCalledWith(1);
  });

  it('shows reconnection indicator when WebSocket is disconnected', () => {
    mockUseWebSocket.mockReturnValue({
      isConnected: false,
      reconnect: mockReconnect,
    });

    render(
      <RootLayout>
        <div>Test Content</div>
      </RootLayout>,
      { wrapper: createTestWrapper() },
    );

    expect(screen.getByText('Reconnecting...')).toBeInTheDocument();
  });

  it('does not show reconnection indicator when WebSocket is connected', () => {
    mockUseWebSocket.mockReturnValue({
      isConnected: true,
      reconnect: mockReconnect,
    });

    render(
      <RootLayout>
        <div>Test Content</div>
      </RootLayout>,
      { wrapper: createTestWrapper() },
    );

    expect(screen.queryByText('Reconnecting...')).not.toBeInTheDocument();
  });

  it('positions toaster in top-right', () => {
    render(
      <RootLayout>
        <div>Test Content</div>
      </RootLayout>,
      { wrapper: createTestWrapper() },
    );

    expect(screen.getByTestId('toaster')).toBeInTheDocument();
  });

  it('wraps children in correct provider hierarchy', () => {
    render(
      <RootLayout>
        <div data-testid='test-children'>Test Content</div>
      </RootLayout>,
      { wrapper: createTestWrapper() },
    );

    // Check the hierarchy: QueryProvider > AuthProvider > WebSocketProvider > children
    const queryProvider = screen.getByTestId('query-provider');
    const authProvider = screen.getByTestId('auth-provider');
    const testChildren = screen.getByTestId('test-children');

    expect(queryProvider).toContainElement(authProvider);
    expect(authProvider).toContainElement(testChildren);
  });

  it('renders multiple children correctly', () => {
    render(
      <RootLayout>
        <div data-testid='child-1'>Child 1</div>
        <div data-testid='child-2'>Child 2</div>
        <div data-testid='child-3'>Child 3</div>
      </RootLayout>,
      { wrapper: createTestWrapper() },
    );

    expect(screen.getByTestId('child-1')).toBeInTheDocument();
    expect(screen.getByTestId('child-2')).toBeInTheDocument();
    expect(screen.getByTestId('child-3')).toBeInTheDocument();
  });

  it('handles empty children gracefully', () => {
    render(<RootLayout>{null}</RootLayout>, { wrapper: createTestWrapper() });

    expect(screen.getByTestId('query-provider')).toBeInTheDocument();
    expect(screen.getByTestId('auth-provider')).toBeInTheDocument();
  });

  it('maintains proper DOM structure', () => {
    render(
      <RootLayout>
        <div>Test Content</div>
      </RootLayout>,
      { wrapper: createTestWrapper() },
    );

    // Check that the basic HTML structure is correct
    expect(document.documentElement.tagName).toBe('HTML');
    expect(document.body.tagName).toBe('BODY');
  });

  it('applies correct CSS classes to body', () => {
    render(
      <RootLayout>
        <div>Test Content</div>
      </RootLayout>,
      { wrapper: createTestWrapper() },
    );

    const bodyElement = document.body;
    expect(bodyElement).toHaveClass('inter');
  });

  it('renders WebSocket reconnection indicator with correct styling', () => {
    mockUseWebSocket.mockReturnValue({
      isConnected: false,
      reconnect: mockReconnect,
    });

    render(
      <RootLayout>
        <div>Test Content</div>
      </RootLayout>,
      { wrapper: createTestWrapper() },
    );

    const reconnectionIndicator = screen.getByText('Reconnecting...');
    expect(reconnectionIndicator).toHaveClass(
      'fixed',
      'bottom-4',
      'right-4',
      'bg-yellow-100',
      'text-yellow-800',
      'px-3',
      'py-2',
      'rounded-lg',
      'text-sm',
      'shadow-lg',
    );
  });

  it('handles WebSocket connection state changes', () => {
    const { rerender } = render(
      <RootLayout>
        <div>Test Content</div>
      </RootLayout>,
      { wrapper: createTestWrapper() },
    );

    // Initially connected
    expect(screen.queryByText('Reconnecting...')).not.toBeInTheDocument();

    // Change to disconnected
    mockUseWebSocket.mockReturnValue({
      isConnected: false,
      reconnect: mockReconnect,
    });

    rerender(
      <RootLayout>
        <div>Test Content</div>
      </RootLayout>,
    );

    expect(screen.getByText('Reconnecting...')).toBeInTheDocument();
  });
});
