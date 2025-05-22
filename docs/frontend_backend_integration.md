# Frontend-Backend Integration Guide

This document outlines how the Heart of News frontend application integrates with the backend API. It serves as a reference for developers working on both the frontend and backend components.

## Architecture Overview

The Heart of News application consists of two main components:

1. **Backend**: A FastAPI-based RESTful API that handles data processing, storage, and business logic
2. **Frontend**: A Next.js application that provides the user interface and client-side functionality

The integration between these components follows these principles:

- **REST API**: All communication uses standard HTTP methods over a RESTful API
- **JWT Authentication**: Secure authentication using JSON Web Tokens
- **JSON Data Format**: All data is exchanged in JSON format
- **Stateless Communication**: Each request contains all necessary information

## API Endpoints

The backend exposes the following API endpoints:

### Base URL

The base URL for all API requests is:

- Development: `http://localhost:8000/api/v1`
- Staging: `https://api-staging.heartofnews.com/api/v1`
- Production: `https://api.heartofnews.com/api/v1`

This is configured in the frontend's environment variables as `NEXT_PUBLIC_API_URL`.

### Authentication Endpoints

| Method | Endpoint         | Description                        | Request Body                                       | Response                                         |
|--------|------------------|------------------------------------|----------------------------------------------------|-------------------------------------------------|
| POST   | `/auth/login`    | Authenticate user and get token    | `{ "email": "string", "password": "string" }`      | `{ "access_token": "string", "token_type": "string", "user": User }` |
| POST   | `/auth/register` | Register a new user                | `{ "email": "string", "username": "string", "password": "string" }` | `{ "access_token": "string", "token_type": "string", "user": User }` |
| GET    | `/auth/me`       | Get current user profile           | -                                                  | `User` object                                    |
| POST   | `/auth/refresh`  | Refresh access token               | -                                                  | `{ "access_token": "string", "token_type": "string" }` |

### Article Endpoints

| Method | Endpoint                | Description                      | Query Parameters                                 | Response                                  |
|--------|-------------------------|----------------------------------|--------------------------------------------------|-------------------------------------------|
| GET    | `/articles`             | List articles with pagination    | `page`, `size`, `query`, `source_id`, `category`, `date_from`, `date_to` | `{ "items": Article[], "total": number, "page": number, "size": number, "pages": number }` |
| GET    | `/articles/{id}`        | Get article by ID                | -                                                | `Article` object                          |
| GET    | `/articles/search`      | Search articles                  | `q` (search query)                               | `{ "items": Article[], "total": number, "page": number, "size": number, "pages": number }` |
| POST   | `/articles`             | Create a new article (admin)     | -                                                | `Article` object                          |
| PUT    | `/articles/{id}`        | Update an article (admin)        | -                                                | `Article` object                          |
| DELETE | `/articles/{id}`        | Delete an article (admin)        | -                                                | `{ "message": "Article deleted" }`        |

### Source Endpoints

| Method | Endpoint               | Description                     | Query Parameters                                  | Response                                  |
|--------|------------------------|---------------------------------|---------------------------------------------------|-------------------------------------------|
| GET    | `/sources`             | List sources with pagination    | `page`, `size`                                    | `{ "items": Source[], "total": number, "page": number, "size": number, "pages": number }` |
| GET    | `/sources/{id}`        | Get source by ID                | -                                                 | `Source` object                           |
| POST   | `/sources`             | Create a new source (admin)     | -                                                 | `Source` object                           |
| PUT    | `/sources/{id}`        | Update a source (admin)         | -                                                 | `Source` object                           |
| DELETE | `/sources/{id}`        | Delete a source (admin)         | -                                                 | `{ "message": "Source deleted" }`         |

### Task Endpoints (Admin)

| Method | Endpoint              | Description                     | Request Body                                      | Response                                  |
|--------|-----------------------|---------------------------------|---------------------------------------------------|-------------------------------------------|
| GET    | `/tasks`              | List background tasks           | -                                                 | `{ "items": Task[], "total": number, "page": number, "size": number, "pages": number }` |
| POST   | `/tasks`              | Create a new task               | `{ "task_type": "string", "source_id": "string" }` | `Task` object                             |
| GET    | `/tasks/{id}`         | Get task by ID                  | -                                                 | `Task` object                             |

### Health Check Endpoint

| Method | Endpoint         | Description                        | Response                                 |
|--------|------------------|------------------------------------|------------------------------------------|
| GET    | `/health`        | Check API health                   | `{ "status": "ok", "version": "string" }` |
| GET    | `/health/live`   | Liveness probe                     | `{ "status": "ok" }`                     |
| GET    | `/health/ready`  | Readiness probe                    | `{ "status": "ok", "dependencies": {} }` |

## Data Models

The following TypeScript interfaces define the data structures exchanged between frontend and backend:

### Article

```typescript
interface Article {
  id: string;
  title: string;
  content: string;
  summary: string;
  url: string;
  published_at: string;
  source_id: string;
  source: Source;
  categories: string[];
  image_url?: string;
  bias_score?: BiasScore;
}

interface BiasScore {
  political_bias: number; // -1 to 1 scale (left to right)
  emotional_tone: number; // 0 to 1 scale (neutral to emotional)
  propaganda_techniques: PropagandaTechnique[];
  overall_score: number; // 0 to 1 scale (neutral to biased)
}

interface PropagandaTechnique {
  name: string;
  score: number;
  examples: string[];
}
```

### Source

```typescript
interface Source {
  id: string;
  name: string;
  url: string;
  rss_feed?: string;
  is_active: boolean;
  reliability_score: number;
  bias_score: number;
}
```

### User

```typescript
interface User {
  id: string;
  email: string;
  username: string;
  role: 'user' | 'admin';
  created_at: string;
}
```

### Task

```typescript
interface Task {
  id: string;
  task_type: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  created_at: string;
  updated_at: string;
  result?: any;
  error?: string;
  source_id?: string;
}
```

## Authentication Flow

The frontend handles authentication through the following flow:

1. **Login/Registration**: User submits credentials via the login or registration form
2. **Token Storage**: Upon successful authentication, the frontend stores the JWT token in localStorage
3. **API Requests**: All subsequent API requests include the JWT token in the Authorization header
4. **Token Refresh**: When the token expires, the frontend attempts to refresh it
5. **Logout**: Upon logout, the token is removed from localStorage

Implementation details:

```typescript
// Example of the API client with authentication
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle authentication errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Handle token refresh or redirect to login
    }
    return Promise.reject(error);
  }
);
```

## Error Handling

The frontend handles API errors using the following approach:

1. **HTTP Status Codes**: The backend uses standard HTTP status codes (200, 400, 401, 403, 404, 500)
2. **Error Responses**: All error responses follow a consistent format: `{ "detail": "Error message" }`
3. **Client-Side Handling**: The frontend catches errors and displays appropriate messages to users

Example of error handling:

```typescript
try {
  const response = await api.get('/articles');
  // Handle successful response
} catch (error) {
  if (error.response) {
    // Backend returned an error response
    const statusCode = error.response.status;
    const errorMessage = error.response.data.detail || 'An error occurred';
    
    switch (statusCode) {
      case 401:
        // Unauthorized - redirect to login
        break;
      case 403:
        // Forbidden - display permission error
        break;
      case 404:
        // Not found - display not found message
        break;
      default:
        // Other errors - display generic error
        break;
    }
  } else if (error.request) {
    // Request was made but no response received (network error)
    // Display network error message
  } else {
    // Something else happened while setting up the request
    // Display generic error message
  }
}
```

## Testing Integration

To ensure proper integration between frontend and backend, we use several testing approaches:

1. **Unit Tests**: Test frontend components and API client in isolation
2. **Integration Tests**: Test API client against mock backend responses
3. **End-to-End Tests**: Test the complete application flow with real backend interaction

The frontend uses Mock Service Worker (MSW) for simulating API responses during testing:

```typescript
// Example of MSW setup for testing
import { setupServer } from 'msw/node';
import { rest } from 'msw';

const server = setupServer(
  rest.get('http://localhost:8000/api/v1/articles', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        items: [/* mock articles */],
        total: 10,
        page: 1,
        size: 10,
        pages: 1,
      })
    );
  }),
  // Other endpoint mocks...
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

## Performance Considerations

To ensure optimal performance of the frontend-backend integration:

1. **Pagination**: All list endpoints support pagination to limit data transfer
2. **Selective Loading**: The frontend requests only the data it needs
3. **Caching**: The frontend implements caching for frequently accessed data
4. **Optimistic Updates**: UI updates optimistically before API confirmation for better UX
5. **Compression**: API responses are compressed to reduce transfer size
6. **Prefetching**: The frontend prefetches likely-to-be-needed data when appropriate

## Security Considerations

Security measures implemented in the frontend-backend integration:

1. **HTTPS**: All API communication uses HTTPS
2. **JWT Authentication**: Secure, short-lived tokens for authentication
3. **CORS**: Proper CORS configuration to restrict API access
4. **Input Validation**: Both frontend and backend validate all inputs
5. **XSS Protection**: Prevention of cross-site scripting attacks
6. **CSRF Protection**: Prevention of cross-site request forgery

## Deployment Strategy

The frontend and backend are deployed using a coordinated strategy:

1. **Independent Deployment**: Frontend and backend can be deployed independently
2. **Version Compatibility**: API versioning ensures backward compatibility
3. **Environment Matching**: Frontend environment (dev/staging/prod) matches backend environment
4. **Feature Flags**: New features can be gradually rolled out using feature flags

## Troubleshooting Common Issues

### CORS Errors

If you encounter CORS errors during development:

1. Ensure the backend has CORS configured correctly for the frontend origin
2. Check that requests include the proper headers
3. Verify that credentials handling is consistent

### Authentication Issues

If authentication is not working:

1. Check that the token is being stored correctly
2. Verify the Authorization header format
3. Ensure the token has not expired
4. Check for token refresh logic issues

### Data Format Issues

If you encounter data format issues:

1. Compare the expected TypeScript interfaces with actual API responses
2. Check for missing fields or incorrect types
3. Ensure dates are formatted consistently

## Environment-Specific Configuration

The frontend uses environment variables to configure API integration for different environments:

```
# .env.development
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# .env.staging
NEXT_PUBLIC_API_URL=https://api-staging.heartofnews.com/api/v1

# .env.production
NEXT_PUBLIC_API_URL=https://api.heartofnews.com/api/v1
```

## Future Enhancements

Planned improvements to the frontend-backend integration:

1. **GraphQL**: Consider adding a GraphQL layer for more efficient data fetching
2. **WebSockets**: Implement real-time updates for certain features
3. **Server-Side Rendering**: Enhance SEO and performance with SSR for article pages
4. **API Client Generation**: Automate TypeScript client generation from OpenAPI specs