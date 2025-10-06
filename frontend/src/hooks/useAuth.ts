'use client';

import { useContext } from 'react';

import { AuthContext } from '@/context/AuthContext';

/**
 * Hook to access authentication state and methods
 * 
 * Provides access to:
 * - user: Current authenticated user
 * - isLoading: Loading state during auth check
 * - isAuthenticated: Boolean indicating if user is logged in
 * - login: Function to authenticate user
 * - logout: Function to log out user
 * 
 * @throws Error if used outside of AuthProvider
 * 
 * @example
 * ```tsx
 * const { user, login, logout, isAuthenticated } = useAuth();
 * 
 * if (isAuthenticated) {
 *   return <div>Welcome {user.full_name}</div>;
 * }
 * ```
 */
export const useAuth = () => {
  const context = useContext(AuthContext);
  
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
};


