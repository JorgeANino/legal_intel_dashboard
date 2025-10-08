'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/api/client';

export default function DebugPage() {
  const [authStatus, setAuthStatus] = useState<any>(null);
  const [testResult, setTestResult] = useState<any>(null);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = () => {
    const token = localStorage.getItem('access_token');
    const refreshToken = localStorage.getItem('refresh_token');
    const user = localStorage.getItem('user');

    setAuthStatus({
      hasToken: !!token,
      tokenLength: token?.length || 0,
      tokenPreview: token ? token.substring(0, 30) + '...' : 'No token',
      hasRefreshToken: !!refreshToken,
      hasUser: !!user,
      user: user ? JSON.parse(user) : null,
    });
  };

  const testDashboardRequest = async () => {
    try {
      setTestResult({ loading: true });
      const response = await apiClient.get('/dashboard');
      setTestResult({
        success: true,
        data: response.data,
        status: response.status,
      });
    } catch (error: any) {
      setTestResult({
        success: false,
        error: error.message,
        status: error.response?.status,
        details: error.response?.data,
      });
    }
  };

  const clearAuth = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    checkAuthStatus();
    setTestResult(null);
  };

  return (
    <div className='min-h-screen bg-gray-50 p-8'>
      <div className='max-w-4xl mx-auto'>
        <h1 className='text-3xl font-bold mb-8 text-gray-900'>
          🔍 Authentication Debug Page
        </h1>

        {/* Auth Status */}
        <div className='bg-white rounded-lg shadow p-6 mb-6'>
          <h2 className='text-xl font-semibold mb-4 text-gray-800'>
            Authentication Status
          </h2>
          {authStatus && (
            <div className='space-y-2 font-mono text-sm'>
              <div className='flex items-center gap-2'>
                <span
                  className={`inline-block w-3 h-3 rounded-full ${
                    authStatus.hasToken ? 'bg-green-500' : 'bg-red-500'
                  }`}
                />
                <span className='font-semibold'>Has Token:</span>
                <span>{authStatus.hasToken ? 'Yes' : 'No'}</span>
              </div>
              <div>
                <span className='font-semibold'>Token Length:</span>{' '}
                {authStatus.tokenLength}
              </div>
              <div>
                <span className='font-semibold'>Token Preview:</span>{' '}
                {authStatus.tokenPreview}
              </div>
              <div className='flex items-center gap-2'>
                <span
                  className={`inline-block w-3 h-3 rounded-full ${
                    authStatus.hasRefreshToken ? 'bg-green-500' : 'bg-red-500'
                  }`}
                />
                <span className='font-semibold'>Has Refresh Token:</span>
                <span>{authStatus.hasRefreshToken ? 'Yes' : 'No'}</span>
              </div>
              <div className='flex items-center gap-2'>
                <span
                  className={`inline-block w-3 h-3 rounded-full ${
                    authStatus.hasUser ? 'bg-green-500' : 'bg-red-500'
                  }`}
                />
                <span className='font-semibold'>Has User:</span>
                <span>{authStatus.hasUser ? 'Yes' : 'No'}</span>
              </div>
              {authStatus.user && (
                <div className='mt-4 p-4 bg-gray-50 rounded'>
                  <div className='font-semibold mb-2'>User Info:</div>
                  <pre className='text-xs overflow-x-auto'>
                    {JSON.stringify(authStatus.user, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          )}
          <div className='flex gap-4 mt-4'>
            <button
              onClick={checkAuthStatus}
              className='px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition'
            >
              Refresh Status
            </button>
            <button
              onClick={clearAuth}
              className='px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition'
            >
              Clear Auth Data
            </button>
          </div>
        </div>

        {/* Test Dashboard Request */}
        <div className='bg-white rounded-lg shadow p-6 mb-6'>
          <h2 className='text-xl font-semibold mb-4 text-gray-800'>
            Test Dashboard Request
          </h2>
          <button
            onClick={testDashboardRequest}
            className='px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition'
          >
            Test GET /dashboard
          </button>

          {testResult && (
            <div className='mt-4'>
              {testResult.loading ? (
                <div className='text-gray-600'>Loading...</div>
              ) : testResult.success ? (
                <div className='p-4 bg-green-50 border border-green-200 rounded'>
                  <div className='font-semibold text-green-800 mb-2'>
                    ✅ Success (Status: {testResult.status})
                  </div>
                  <pre className='text-xs overflow-x-auto'>
                    {JSON.stringify(testResult.data, null, 2)}
                  </pre>
                </div>
              ) : (
                <div className='p-4 bg-red-50 border border-red-200 rounded'>
                  <div className='font-semibold text-red-800 mb-2'>
                    ❌ Error (Status: {testResult.status})
                  </div>
                  <div className='text-sm text-red-700 mb-2'>
                    {testResult.error}
                  </div>
                  {testResult.details && (
                    <pre className='text-xs overflow-x-auto'>
                      {JSON.stringify(testResult.details, null, 2)}
                    </pre>
                  )}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Instructions */}
        <div className='bg-blue-50 border border-blue-200 rounded-lg p-6'>
          <h2 className='text-xl font-semibold mb-4 text-blue-900'>
            📋 Instructions
          </h2>
          <ol className='list-decimal list-inside space-y-2 text-sm text-blue-800'>
            <li>Check if you have a valid token stored in localStorage</li>
            <li>
              If no token, go to{' '}
              <a href='/login' className='underline'>
                /login
              </a>{' '}
              and sign in
            </li>
            <li>After login, return here and refresh the status</li>
            <li>Test the dashboard request to see if authentication works</li>
            <li>Check the browser console for detailed logs</li>
          </ol>
        </div>

        {/* Links */}
        <div className='mt-6 flex gap-4'>
          <a
            href='/login'
            className='px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 transition'
          >
            Go to Login
          </a>
          <a
            href='/'
            className='px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 transition'
          >
            Go to Dashboard
          </a>
        </div>
      </div>
    </div>
  );
}
