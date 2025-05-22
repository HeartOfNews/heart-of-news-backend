import { useEffect, useState, useCallback } from 'react';
import { useWebSocket } from '../contexts/WebSocketContext';
import { WebSocketMessage } from '../lib/websocket';

/**
 * Hook to subscribe to specific WebSocket message types
 * @param messageType The message type to subscribe to, or 'all' for all messages
 * @returns Object containing the latest message and functions to handle messages
 */
export function useWebSocketMessage<T = any>(messageType: string) {
  const { subscribe, connectionStatus } = useWebSocket();
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const [messageHistory, setMessageHistory] = useState<WebSocketMessage[]>([]);

  // Process incoming message
  const handleMessage = useCallback((message: WebSocketMessage) => {
    setLastMessage(message);
    setMessageHistory(prev => [...prev, message]);
  }, []);

  // Set up subscription to messages
  useEffect(() => {
    // Only subscribe when connected
    if (connectionStatus === 'connected') {
      const unsubscribe = subscribe(messageType, handleMessage);
      return unsubscribe;
    }
    return () => {};
  }, [messageType, subscribe, handleMessage, connectionStatus]);

  // Clear message history
  const clearMessages = useCallback(() => {
    setMessageHistory([]);
    setLastMessage(null);
  }, []);

  // Get typed data from the last message
  const lastData = lastMessage?.data as T | undefined;

  return {
    lastMessage,
    lastData,
    messageHistory,
    clearMessages,
    isConnected: connectionStatus === 'connected',
    connectionStatus,
  };
}

export default useWebSocketMessage;