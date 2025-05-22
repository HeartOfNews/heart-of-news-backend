import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import webSocketService, { 
  WebSocketMessage, 
  ConnectionStatus, 
  WebSocketSubscriber 
} from '../lib/websocket';

// Define the context shape
interface WebSocketContextType {
  connectionStatus: ConnectionStatus;
  connect: (url?: string) => void;
  disconnect: () => void;
  send: (type: string, data: any) => boolean;
  subscribe: (type: string, callback: WebSocketSubscriber) => () => void;
}

// Create context with default values
const WebSocketContext = createContext<WebSocketContextType>({
  connectionStatus: 'disconnected',
  connect: () => {},
  disconnect: () => {},
  send: () => false,
  subscribe: () => () => {},
});

interface WebSocketProviderProps {
  children: ReactNode;
  autoConnect?: boolean;
}

export const WebSocketProvider: React.FC<WebSocketProviderProps> = ({ 
  children, 
  autoConnect = true 
}) => {
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>(
    webSocketService.getStatus()
  );

  useEffect(() => {
    // Subscribe to connection status changes
    const unsubscribe = webSocketService.subscribeToStatus(setConnectionStatus);

    // Auto-connect if enabled
    if (autoConnect) {
      webSocketService.connect();
    }

    // Cleanup on unmount
    return () => {
      unsubscribe();
      webSocketService.disconnect();
    };
  }, [autoConnect]);

  // Create context value
  const contextValue: WebSocketContextType = {
    connectionStatus,
    connect: webSocketService.connect.bind(webSocketService),
    disconnect: webSocketService.disconnect.bind(webSocketService),
    send: webSocketService.send.bind(webSocketService),
    subscribe: webSocketService.subscribe.bind(webSocketService),
  };

  return (
    <WebSocketContext.Provider value={contextValue}>
      {children}
    </WebSocketContext.Provider>
  );
};

// Custom hook for using WebSocket
export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  
  if (!context) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  
  return context;
};

export default WebSocketContext;