'use client';

import { useQueryClient } from '@tanstack/react-query';
import { useEffect, useRef, useCallback, useState } from 'react';

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
  const isConnectingRef = useRef(false);
  const isMountedRef = useRef(false);
  const [isConnected, setIsConnected] = useState(false);

  const connect = useCallback(() => {
    // Only run in browser and when mounted
    if (typeof window === 'undefined' || !isMountedRef.current) return;
    
    // Prevent duplicate connections
    if (isConnectingRef.current || wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    isConnectingRef.current = true;

    try {
      // Determine WebSocket URL based on environment
      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      // Extract base host from API_URL (remove protocol and any path segments)
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
      const wsHost = apiUrl.replace(/^https?:\/\//, '').split('/')[0];
      const wsUrl = `${wsProtocol}//${wsHost}/api/v1/ws/${userId}`;

      console.log(`Connecting to WebSocket: ${wsUrl}`);

      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        if (!isMountedRef.current) {
          ws.close(1000);
          return;
        }
        
        console.log('WebSocket connected');
        isConnectingRef.current = false;
        setIsConnected(true);
        
        // Clear any pending reconnection attempts
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
          reconnectTimeoutRef.current = undefined;
        }
      };

      ws.onmessage = (event) => {
        if (!isMountedRef.current) return;
        
        try {
          const data: DocumentUpdate = JSON.parse(event.data);
          
          if (data.type === 'document_update') {
            console.log(`Document ${data.document_id} update:`, data.status);

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
        console.error('WebSocket error:', error);
        isConnectingRef.current = false;
        if (isMountedRef.current) {
          setIsConnected(false);
        }
      };

      ws.onclose = (event) => {
        console.log(`WebSocket closed (code: ${event.code})`);
        isConnectingRef.current = false;
        wsRef.current = null;
        
        if (isMountedRef.current) {
          setIsConnected(false);
        }

        // Auto-reconnect after 3 seconds (unless intentionally closed or unmounted)
        if (event.code !== 1000 && isMountedRef.current) {
          console.log('Reconnecting in 3s...');
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, 3000);
        }
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('Error creating WebSocket:', error);
      isConnectingRef.current = false;
      
      // Retry connection after 3 seconds if still mounted
      if (isMountedRef.current) {
        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
        }, 3000);
      }
    }
  }, [userId, queryClient]);

  const disconnect = useCallback(() => {
    // Clear any pending reconnection attempts
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = undefined;
    }

    if (wsRef.current) {
      const ws = wsRef.current;
      const readyState = ws.readyState;
      
      // Only close if not already closing/closed
      if (readyState === WebSocket.OPEN || readyState === WebSocket.CONNECTING) {
        console.log('Disconnecting WebSocket');
        ws.close(1000); // Normal closure
      }
      
      wsRef.current = null;
      setIsConnected(false);
    }
    
    isConnectingRef.current = false;
  }, []);

  // Connect on mount, disconnect on unmount
  useEffect(() => {
    isMountedRef.current = true;
    connect();

    return () => {
      isMountedRef.current = false;
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    isConnected,
    reconnect: connect,
  };
};
