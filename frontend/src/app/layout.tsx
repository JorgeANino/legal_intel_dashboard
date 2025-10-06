'use client';

import { Inter } from 'next/font/google';
import './globals.css';
import { QueryProvider } from '@/providers/QueryProvider';
import { AuthProvider } from '@/context/AuthContext';
import { Toaster } from 'react-hot-toast';
import { useWebSocket } from '@/hooks/useWebSocket';

const inter = Inter({ subsets: ['latin'] });

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
        <div className="fixed bottom-4 right-4 bg-yellow-100 text-yellow-800 px-3 py-2 rounded-lg text-sm shadow-lg">
          ⚠️ Reconnecting...
        </div>
      )}
    </>
  );
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <QueryProvider>
          <AuthProvider>
            <WebSocketProvider>
              {children}
            </WebSocketProvider>
          </AuthProvider>
          <Toaster position="top-right" />
        </QueryProvider>
      </body>
    </html>
  );
}

