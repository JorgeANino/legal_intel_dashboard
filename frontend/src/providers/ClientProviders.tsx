'use client';

import React from 'react';
import { Toaster } from 'react-hot-toast';

import { AuthProvider } from '@/context/AuthContext';
import { useWebSocket } from '@/hooks/useWebSocket';
import { QueryProvider } from '@/providers/QueryProvider';

// WebSocket wrapper component
function WebSocketProvider({ children }: { children: React.ReactNode }) {
  // Connect WebSocket for real-time document updates
  // User ID hardcoded to 1 for demo (would come from auth in production)
  const { isConnected } = useWebSocket(1);

  return (
    <>
      {children}
      {/* Optional: Show connection status indicator */}
      {!isConnected && (
        <div className='fixed bottom-4 right-4 bg-yellow-100 text-yellow-800 px-3 py-2 rounded-lg text-sm shadow-lg'>
          Reconnecting...
        </div>
      )}
    </>
  );
}

export function ClientProviders({ children }: { children: React.ReactNode }) {
  return (
    <QueryProvider>
      <AuthProvider>
        <WebSocketProvider>{children}</WebSocketProvider>
      </AuthProvider>
      <Toaster position='top-right' />
    </QueryProvider>
  );
}
