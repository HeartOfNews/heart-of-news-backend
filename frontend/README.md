# Heart of News Frontend

Frontend application for the Heart of News project - an AI-powered, propaganda-free news aggregation and distribution system.

## Overview

Heart of News is designed to deliver information to people without propaganda from any side. This is the frontend application that provides a user interface for:

- Browsing news articles
- Filtering by sources, categories, and topics
- User authentication and profile management
- Admin dashboard for content management
- Visualizing bias detection results

## Technical Stack

- **Framework**: Next.js 14+
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React Context + SWR/React Query
- **Authentication**: JWT with HTTP-only cookies
- **UI Components**: Headless UI + Custom components
- **Testing**: Jest, React Testing Library
- **Linting**: ESLint, Prettier
- **API Integration**: Axios/Fetch API
- **CI/CD**: GitHub Actions

## Getting Started

### Prerequisites

- Node.js 18.17.0 or later
- npm or yarn
- Backend API running (see backend repository)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/HeartOfNews/heart-of-news-frontend.git
cd heart-of-news-frontend
```

2. Install dependencies:
```bash
npm install
# or
yarn install
```

3. Create a .env.local file:
```bash
cp .env.example .env.local
# Edit .env.local with your configuration
```

4. Start the development server:
```bash
npm run dev
# or
yarn dev
```

5. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Development Guidelines

### Directory Structure

```
/heart-of-news-frontend
├── public/               # Static files
├── src/
│   ├── app/              # App router pages and layouts
│   ├── components/       # Reusable components
│   │   ├── ui/           # Basic UI components
│   │   ├── layout/       # Layout components
│   │   └── features/     # Feature-specific components
│   ├── hooks/            # Custom React hooks
│   ├── lib/              # Utility functions
│   ├── api/              # API integration
│   ├── contexts/         # React contexts
│   ├── types/            # TypeScript types and interfaces
│   └── styles/           # Global styles
├── tests/                # Test files
├── .env.example          # Example environment variables
└── next.config.js        # Next.js configuration
```

### Code Style

- Follow ESLint and Prettier configuration
- Use functional components with hooks
- Implement proper type definitions
- Write unit tests for components
- Use semantic HTML elements
- Follow accessibility best practices

## Features

- **Article Browsing**: View and filter news articles
- **Source Management**: Browse and filter by news sources
- **User Authentication**: Sign up, login, profile management
- **Responsive Design**: Mobile-first approach
- **Dark Mode Support**: Toggle between light and dark themes
- **Admin Dashboard**: Manage content and user permissions
- **Bias Visualization**: View bias analysis results

## Deployment

### Development

```bash
npm run dev
# or
yarn dev
```

### Production Build

```bash
npm run build
npm run start
# or
yarn build
yarn start
```

### Deployment Environments

- **Development**: Local development environment
- **Staging**: Test environment mirroring production
- **Production**: Live user-facing environment

## CI/CD Pipeline

Automated build and deployment process:

1. **Pull Request**: Run tests and lint checks
2. **Merge to Develop**: Deploy to staging environment
3. **Merge to Main**: Deploy to production environment

## Contributing

See the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines.

## License

[MIT License](LICENSE)