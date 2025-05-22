# WebSocket Integration

This document outlines the real-time WebSocket integration between the frontend and backend of the Heart of News application.

## Overview

The WebSocket integration enables real-time updates for:

1. New articles as they are published
2. Article updates (changes to content, bias analysis, etc.)
3. System notifications
4. User-specific notifications

This creates a more dynamic and engaging user experience by providing immediate feedback and updates without requiring page refreshes.

## Architecture

### Backend WebSocket Service

The backend provides a WebSocket endpoint at `/api/v1/ws` that the frontend connects to. This endpoint:

- Authenticates users via token (optional for public data, required for user-specific data)
- Maintains a list of active connections
- Broadcasts messages to relevant subscribers
- Handles reconnection and connection management

### Frontend Integration

The frontend integration consists of several components:

1. **WebSocket Service (`src/lib/websocket.ts`)**
   - Core WebSocket client implementation
   - Handles connection management and reconnection
   - Provides message subscription system
   - Manages connection status

2. **WebSocket Context (`src/contexts/WebSocketContext.tsx`)**
   - React context provider for WebSocket functionality
   - Makes WebSocket methods available throughout the application
   - Handles automatic connection/disconnection based on component lifecycle

3. **Custom Hooks**
   - `useWebSocket`: General WebSocket functionality access
   - `useWebSocketMessage`: Subscribe to specific message types
   - `useArticleUpdates`: Specialized hook for real-time article updates

4. **UI Components**
   - `NotificationCenter`: Displays system and user notifications
   - `NewArticlesNotification`: Notifies users of new articles available

## Message Format

All WebSocket messages follow this format:

```typescript
{
  type: string;  // The message type (e.g., 'article', 'notification')
  data: any;     // The payload, structure depends on the message type
}
```

### Message Types

1. **Article Updates (`article`)**
   ```typescript
   {
     type: 'article',
     data: {
       action: 'new' | 'update' | 'delete',
       article: Article  // Full article object
     }
   }
   ```

2. **Notifications (`notification`)**
   ```typescript
   {
     type: 'notification',
     data: {
       message: string,
       type: 'info' | 'success' | 'warning' | 'error',
       url?: string  // Optional link to navigate to
     }
   }
   ```

3. **System Status (`system`)**
   ```typescript
   {
     type: 'system',
     data: {
       status: string,
       message: string
     }
   }
   ```

## Usage Examples

### Subscribing to WebSocket Messages

```typescript
import { useWebSocketMessage } from '@/hooks/useWebSocketMessage';

function MyComponent() {
  const { lastData, isConnected } = useWebSocketMessage('notification');
  
  // Use lastData to render notifications
  
  return (
    <div>
      {lastData && <div>New notification: {lastData.message}</div>}
    </div>
  );
}
```

### Displaying Real-time Article Updates

```typescript
import { useArticleUpdates } from '@/hooks/useArticleUpdates';

function ArticlesList({ initialArticles }) {
  const { 
    articles, 
    newArticleCount, 
    showNewArticles 
  } = useArticleUpdates(initialArticles);
  
  return (
    <div>
      {newArticleCount > 0 && (
        <button onClick={showNewArticles}>
          Show {newArticleCount} new articles
        </button>
      )}
      
      <div className="articles-grid">
        {articles.map(article => (
          <ArticleCard key={article.id} article={article} />
        ))}
      </div>
    </div>
  );
}
```

## Security Considerations

1. **Authentication**: WebSocket connections authenticate using the same JWT token as the REST API
2. **Connection Validation**: The backend validates each connection and restricts access based on user permissions
3. **Message Validation**: All incoming messages are validated before processing
4. **Rate Limiting**: Connections are rate-limited to prevent abuse

## Performance Considerations

1. **Selective Broadcasting**: The backend only sends messages to clients that need them
2. **Message Batching**: Multiple rapid updates are batched when possible
3. **Reconnection Strategy**: Exponential backoff with jitter is used for reconnection attempts
4. **Connection Health Monitoring**: Both client and server monitor connection health with ping/pong

## Testing

WebSocket functionality can be tested using:

1. The browser's WebSocket API directly
2. Tools like Postman which support WebSocket testing
3. Automated tests using Jest and mock WebSocket servers

## Troubleshooting

Common issues and solutions:

1. **Connection Failures**: Check network connectivity, firewall settings, and authentication token validity
2. **Message Not Received**: Verify subscription to the correct message type and backend broadcast logic
3. **Reconnection Issues**: Check client-side reconnection logic and server-side connection limits