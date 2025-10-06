import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { useRouter } from 'next/navigation';

import { useAuth } from '@/hooks/useAuth';

import LoginPage from './page';

// Mock the hooks
jest.mock('@/hooks/useAuth');
jest.mock('next/navigation');

const mockUseAuth = useAuth as jest.MockedFunction<typeof useAuth>;
const mockUseRouter = useRouter as jest.MockedFunction<typeof useRouter>;

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

describe('LoginPage', () => {
  const mockLogin = jest.fn();
  const mockPush = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();

    mockUseRouter.mockReturnValue({
      push: mockPush,
      back: jest.fn(),
      forward: jest.fn(),
      refresh: jest.fn(),
      replace: jest.fn(),
      prefetch: jest.fn(),
    } as any);

    // Default mock implementation
    mockUseAuth.mockReturnValue({
      user: null,
      isLoading: false,
      isAuthenticated: false,
      login: mockLogin,
      logout: jest.fn(),
    });
  });

  it('renders login form with all elements', () => {
    render(<LoginPage />, { wrapper: createTestWrapper() });

    expect(screen.getByText('Legal Intel Dashboard')).toBeInTheDocument();
    expect(
      screen.getByText('Sign in to access your documents'),
    ).toBeInTheDocument();
    expect(screen.getByLabelText('Email address')).toBeInTheDocument();
    expect(screen.getByLabelText('Password')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Sign in' })).toBeInTheDocument();
  });

  it('has pre-filled test credentials', () => {
    render(<LoginPage />, { wrapper: createTestWrapper() });

    const emailInput = screen.getByLabelText('Email address');
    const passwordInput = screen.getByLabelText('Password');

    expect(emailInput).toHaveValue('test@example.com');
    expect(passwordInput).toHaveValue('testpassword123');
  });

  it('displays test credentials information', () => {
    render(<LoginPage />, { wrapper: createTestWrapper() });

    expect(screen.getByText('Test Credentials')).toBeInTheDocument();
    expect(screen.getByText('test@example.com')).toBeInTheDocument();
    expect(screen.getByText('testpassword123')).toBeInTheDocument();
  });

  it('updates email input when user types', () => {
    render(<LoginPage />, { wrapper: createTestWrapper() });

    const emailInput = screen.getByLabelText('Email address');
    fireEvent.change(emailInput, { target: { value: 'new@example.com' } });

    expect(emailInput).toHaveValue('new@example.com');
  });

  it('updates password input when user types', () => {
    render(<LoginPage />, { wrapper: createTestWrapper() });

    const passwordInput = screen.getByLabelText('Password');
    fireEvent.change(passwordInput, { target: { value: 'newpassword' } });

    expect(passwordInput).toHaveValue('newpassword');
  });

  it('calls login function when form is submitted', async () => {
    render(<LoginPage />, { wrapper: createTestWrapper() });

    const submitButton = screen.getByRole('button', { name: 'Sign in' });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'testpassword123',
      });
    });
  });

  it('calls login with updated credentials when form is submitted', async () => {
    render(<LoginPage />, { wrapper: createTestWrapper() });

    const emailInput = screen.getByLabelText('Email address');
    const passwordInput = screen.getByLabelText('Password');
    const submitButton = screen.getByRole('button', { name: 'Sign in' });

    fireEvent.change(emailInput, { target: { value: 'user@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'userpassword' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith({
        email: 'user@example.com',
        password: 'userpassword',
      });
    });
  });

  it('shows loading state when submitting', async () => {
    mockLogin.mockImplementation(
      () => new Promise((resolve) => setTimeout(resolve, 100)),
    );

    render(<LoginPage />, { wrapper: createTestWrapper() });

    const submitButton = screen.getByRole('button', { name: 'Sign in' });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('Signing in...')).toBeInTheDocument();
    });

    expect(submitButton).toBeDisabled();
  });

  it('redirects to home page when user is already authenticated', () => {
    mockUseAuth.mockReturnValue({
      user: {
        id: 1,
        email: 'test@example.com',
        full_name: 'Test User',
        is_active: true,
      },
      isLoading: false,
      isAuthenticated: true,
      login: mockLogin,
      logout: jest.fn(),
    });

    render(<LoginPage />, { wrapper: createTestWrapper() });

    expect(mockPush).toHaveBeenCalledWith('/');
  });

  it('does not render form when user is authenticated', () => {
    mockUseAuth.mockReturnValue({
      user: {
        id: 1,
        email: 'test@example.com',
        full_name: 'Test User',
        is_active: true,
      },
      isLoading: false,
      isAuthenticated: true,
      login: mockLogin,
      logout: jest.fn(),
    });

    render(<LoginPage />, { wrapper: createTestWrapper() });

    expect(screen.queryByLabelText('Email address')).not.toBeInTheDocument();
    expect(screen.queryByLabelText('Password')).not.toBeInTheDocument();
  });

  it('prevents form submission with empty email', () => {
    render(<LoginPage />, { wrapper: createTestWrapper() });

    const emailInput = screen.getByLabelText('Email address');
    const submitButton = screen.getByRole('button', { name: 'Sign in' });

    fireEvent.change(emailInput, { target: { value: '' } });
    fireEvent.click(submitButton);

    // Form should not submit due to HTML5 validation
    expect(mockLogin).not.toHaveBeenCalled();
  });

  it('prevents form submission with empty password', () => {
    render(<LoginPage />, { wrapper: createTestWrapper() });

    const passwordInput = screen.getByLabelText('Password');
    const submitButton = screen.getByRole('button', { name: 'Sign in' });

    fireEvent.change(passwordInput, { target: { value: '' } });
    fireEvent.click(submitButton);

    // Form should not submit due to HTML5 validation
    expect(mockLogin).not.toHaveBeenCalled();
  });

  it('validates email format', () => {
    render(<LoginPage />, { wrapper: createTestWrapper() });

    const emailInput = screen.getByLabelText('Email address');
    expect(emailInput).toHaveAttribute('type', 'email');
    expect(emailInput).toHaveAttribute('required');
  });

  it('validates password is required', () => {
    render(<LoginPage />, { wrapper: createTestWrapper() });

    const passwordInput = screen.getByLabelText('Password');
    expect(passwordInput).toHaveAttribute('type', 'password');
    expect(passwordInput).toHaveAttribute('required');
  });

  it('has proper accessibility attributes', () => {
    render(<LoginPage />, { wrapper: createTestWrapper() });

    const emailInput = screen.getByLabelText('Email address');
    const passwordInput = screen.getByLabelText('Password');

    expect(emailInput).toHaveAttribute('autoComplete', 'email');
    expect(passwordInput).toHaveAttribute('autoComplete', 'current-password');
  });

  it('displays proper branding and footer', () => {
    render(<LoginPage />, { wrapper: createTestWrapper() });

    expect(screen.getByText('Legal Intel Dashboard')).toBeInTheDocument();
    expect(
      screen.getByText('Production-grade document intelligence platform'),
    ).toBeInTheDocument();
  });

  it('handles login errors gracefully', async () => {
    const consoleError = jest
      .spyOn(console, 'error')
      .mockImplementation(() => {});
    mockLogin.mockRejectedValue(new Error('Login failed'));

    render(<LoginPage />, { wrapper: createTestWrapper() });

    const submitButton = screen.getByRole('button', { name: 'Sign in' });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalled();
    });

    // Error should be handled by AuthContext, not displayed in component
    expect(screen.queryByText('Login failed')).not.toBeInTheDocument();

    consoleError.mockRestore();
  });
});
