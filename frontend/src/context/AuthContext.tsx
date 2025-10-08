'use client';

import { useRouter } from 'next/navigation';
import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from 'react';
import toast from 'react-hot-toast';

import { authApi, User, LoginCredentials } from '@/api/auth';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextType | undefined>(
  undefined,
);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  // Check for existing session on mount
  useEffect(() => {
    const initAuth = async () => {
      console.log('[Auth] Initializing authentication...');
      const token = localStorage.getItem('access_token');
      const savedUser = localStorage.getItem('user');

      console.log(
        '[Auth] Token found:',
        token ? `Yes (length: ${token.length})` : 'No',
      );
      console.log('[Auth] Saved user found:', savedUser ? 'Yes' : 'No');

      if (token && savedUser) {
        try {
          const parsedUser = JSON.parse(savedUser);
          setUser(parsedUser);
          console.log('[Auth] ✓ Session restored for:', parsedUser.email);
        } catch (error) {
          console.error('[Auth] ❌ Failed to parse saved user:', error);
          localStorage.removeItem('user');
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
        }
      } else {
        console.log('[Auth] No existing session found');
      }

      setIsLoading(false);
    };

    initAuth();
  }, []);

  const login = async (credentials: LoginCredentials) => {
    try {
      console.log('[Auth] Attempting login for:', credentials.email);
      const response = await authApi.login(credentials);

      console.log('[Auth] Login successful, storing tokens');
      console.log('[Auth] Access token length:', response.access_token?.length);
      console.log(
        '[Auth] Refresh token length:',
        response.refresh_token?.length,
      );

      // Store tokens and user info
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('refresh_token', response.refresh_token);
      localStorage.setItem('user', JSON.stringify(response.user));

      // Verify storage
      const storedToken = localStorage.getItem('access_token');
      console.log(
        '[Auth] ✓ Token stored successfully:',
        storedToken ? 'Yes' : 'No',
      );
      console.log(
        '[Auth] ✓ Token verification:',
        storedToken === response.access_token ? 'Match' : 'Mismatch!',
      );

      setUser(response.user);

      toast.success(`Welcome back, ${response.user.full_name}!`);
      console.log('[Auth] Redirecting to dashboard');
      router.push('/');
    } catch (error: any) {
      console.error('[Auth] ❌ Login error:', error);
      toast.error(error.response?.data?.detail || 'Invalid email or password');
      throw error;
    }
  };

  const logout = () => {
    authApi.logout();
    setUser(null);
    toast.success('Logged out successfully');
    router.push('/login');
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
