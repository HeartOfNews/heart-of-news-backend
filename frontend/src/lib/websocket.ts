/**
 * WebSocket service for real-time updates
 */

export type WebSocketMessage = {
  type: string;
  data: any;
};

export type WebSocketSubscriber = (message: WebSocketMessage) => void;

export type ConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'error';

class WebSocketService {
  private socket: WebSocket | null = null;
  private reconnectTimeout: NodeJS.Timeout | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectInterval = 3000; // 3 seconds
  private subscribers: Map<string, Set<WebSocketSubscriber>> = new Map();
  private connectionStatus: ConnectionStatus = 'disconnected';
  private statusListeners: Set<(status: ConnectionStatus) => void> = new Set();

  constructor() {
    // We don't initialize the WebSocket in the constructor
    // to allow dynamic initialization when needed
  }

  /**
   * Initialize the WebSocket connection
   */
  public connect(url?: string): void {
    // Close any existing connection
    this.disconnect();

    // Determine the WebSocket URL
    const wsUrl = url || this.getWebSocketUrl();

    // Update status
    this.setConnectionStatus('connecting');

    try {
      // Create a new WebSocket connection
      this.socket = new WebSocket(wsUrl);

      // Set up event handlers
      this.socket.onopen = this.handleOpen.bind(this);
      this.socket.onmessage = this.handleMessage.bind(this);
      this.socket.onclose = this.handleClose.bind(this);
      this.socket.onerror = this.handleError.bind(this);
    } catch (error) {
      console.error('WebSocket connection error:', error);
      this.setConnectionStatus('error');
      this.scheduleReconnect();
    }
  }

  /**
   * Disconnect the WebSocket
   */
  public disconnect(): void {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }

    // Clear any reconnection timeout
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }

    this.setConnectionStatus('disconnected');
  }

  /**
   * Send a message to the server
   */
  public send(type: string, data: any): boolean {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      console.error('WebSocket is not connected');
      return false;
    }

    try {
      const message: WebSocketMessage = { type, data };
      this.socket.send(JSON.stringify(message));
      return true;
    } catch (error) {
      console.error('Error sending WebSocket message:', error);
      return false;
    }
  }

  /**
   * Subscribe to a specific message type
   */
  public subscribe(type: string, callback: WebSocketSubscriber): () => void {
    // Get or create the set of subscribers for this type
    if (!this.subscribers.has(type)) {
      this.subscribers.set(type, new Set());
    }

    // Add the subscriber
    const subscribersForType = this.subscribers.get(type)!;
    subscribersForType.add(callback);

    // Return an unsubscribe function
    return () => {
      if (this.subscribers.has(type)) {
        const subscribers = this.subscribers.get(type)!;
        subscribers.delete(callback);
        if (subscribers.size === 0) {
          this.subscribers.delete(type);
        }
      }
    };
  }

  /**
   * Subscribe to connection status changes
   */
  public subscribeToStatus(callback: (status: ConnectionStatus) => void): () => void {
    this.statusListeners.add(callback);
    
    // Immediately call with current status
    callback(this.connectionStatus);
    
    return () => {
      this.statusListeners.delete(callback);
    };
  }

  /**
   * Get current connection status
   */
  public getStatus(): ConnectionStatus {
    return this.connectionStatus;
  }

  // Private methods

  private getWebSocketUrl(): string {
    // Convert the API URL to WebSocket URL
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
    
    // Replace http(s):// with ws(s)://
    let wsUrl = apiUrl.replace(/^http/, 'ws');
    
    // Ensure the URL ends with /ws
    if (!wsUrl.endsWith('/ws')) {
      wsUrl = wsUrl.replace(/\/$/, '') + '/ws';
    }
    
    // Append auth token if available
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('authToken');
      if (token) {
        wsUrl += `?token=${token}`;
      }
    }
    
    return wsUrl;
  }

  private handleOpen(event: Event): void {
    console.log('WebSocket connection established');
    this.reconnectAttempts = 0;
    this.setConnectionStatus('connected');
  }

  private handleMessage(event: MessageEvent): void {
    try {
      const message = JSON.parse(event.data) as WebSocketMessage;
      
      // Dispatch to subscribers of this message type
      if (this.subscribers.has(message.type)) {
        const subscribers = this.subscribers.get(message.type)!;
        subscribers.forEach(callback => {
          try {
            callback(message);
          } catch (error) {
            console.error('Error in WebSocket subscriber callback:', error);
          }
        });
      }
      
      // Dispatch to subscribers of the 'all' type
      if (this.subscribers.has('all')) {
        const subscribers = this.subscribers.get('all')!;
        subscribers.forEach(callback => {
          try {
            callback(message);
          } catch (error) {
            console.error('Error in WebSocket subscriber callback:', error);
          }
        });
      }
    } catch (error) {
      console.error('Error parsing WebSocket message:', error, event.data);
    }
  }

  private handleClose(event: CloseEvent): void {
    console.log('WebSocket connection closed:', event.code, event.reason);
    this.socket = null;
    this.setConnectionStatus('disconnected');
    
    // Don't reconnect if the close was clean (code 1000)
    if (event.code !== 1000) {
      this.scheduleReconnect();
    }
  }

  private handleError(event: Event): void {
    console.error('WebSocket error:', event);
    this.setConnectionStatus('error');
    this.scheduleReconnect();
  }

  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('Maximum reconnect attempts reached');
      return;
    }

    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
    }

    this.reconnectTimeout = setTimeout(() => {
      console.log(`Attempting to reconnect (${this.reconnectAttempts + 1}/${this.maxReconnectAttempts})...`);
      this.reconnectAttempts += 1;
      this.connect();
    }, this.reconnectInterval);
  }

  private setConnectionStatus(status: ConnectionStatus): void {
    this.connectionStatus = status;
    
    // Notify all status listeners
    this.statusListeners.forEach(listener => {
      try {
        listener(status);
      } catch (error) {
        console.error('Error in WebSocket status listener:', error);
      }
    });
  }
}

// Create a singleton instance
export const webSocketService = new WebSocketService();

export default webSocketService;