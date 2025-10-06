import { useEffect, useRef, useCallback } from 'react';
import { useQueryClient } from '@tanstack/react-query';

interface DocumentUpdate {
  type: 'document_update';
  document_id: number;
  status: {
    processed: boolean;
    processing_error: string | null;
  };
}

/**
 * WebSocket hook for real-time document status updates
 */
export const useWebSocket = (userId: number = 1) => {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  const queryClient = useQueryClient();
  const isConnecting = useRef(false);

  const connect = useCallback(() => {
    if (isConnecting.current || wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    isConnecting.current = true;

    try {
      // Determine WebSocket URL based on environment
      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsHost = process.env.NEXT_PUBLIC_API_URL?.replace(/^https?:\/\//, '') || 'localhost:8000';
      const wsUrl = `${wsProtocol}//${wsHost}/api/v1/ws/${userId}`;

      console.log(`🔌 Connecting to WebSocket: ${wsUrl}`);

      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log('✅ WebSocket connected');
        isConnecting.current = false;
        
        // Clear any pending reconnection attempts
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
        }
      };

      ws.onmessage = (event) => {
        try {
          const data: DocumentUpdate = JSON.parse(event.data);
          
          if (data.type === 'document_update') {
            console.log(`📬 Document ${data.document_id} update:`, data.status);

            // Update React Query cache with new status
            queryClient.setQueryData(['documents'], (oldData: any) => {
              if (!oldData) return oldData;

              return oldData.map((doc: any) =>
                doc.id === data.document_id
                  ? {
                      ...doc,
                      processed: data.status.processed,
                      processing_error: data.status.processing_error,
                    }
                  : doc
              );
            });

            // Invalidate dashboard stats to refresh counts
            queryClient.invalidateQueries({ queryKey: ['dashboard'] });
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
        isConnecting.current = false;
      };

      ws.onclose = (event) => {
        console.log(`🔌 WebSocket closed (code: ${event.code})`);
        isConnecting.current = false;
        wsRef.current = null;

        // Auto-reconnect after 3 seconds (unless intentionally closed)
        if (event.code !== 1000) {
          console.log('🔄 Reconnecting in 3s...');
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, 3000);
        }
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('Error creating WebSocket:', error);
      isConnecting.current = false;
      
      // Retry connection after 3 seconds
      reconnectTimeoutRef.current = setTimeout(() => {
        connect();
      }, 3000);
    }
  }, [userId, queryClient]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }

    if (wsRef.current) {
      console.log('🔌 Disconnecting WebSocket');
      wsRef.current.close(1000); // Normal closure
      wsRef.current = null;
    }
  }, []);

  // Connect on mount, disconnect on unmount
  useEffect(() => {
    connect();

    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    isConnected: wsRef.current?.readyState === WebSocket.OPEN,
    reconnect: connect,
  };
};
