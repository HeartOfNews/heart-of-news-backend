# 🏠 Heart of News - Local Development Setup

Complete guide to run Heart of News locally on your computer.

## 📋 Prerequisites

Before starting, make sure you have these installed:

### Required Software
- **Docker Desktop** (latest version)
  - Download: https://www.docker.com/products/docker-desktop/
  - Ensure Docker is running before starting

- **Node.js 18+** 
  - Download: https://nodejs.org/
  - Check version: `node --version`

- **Git** (to clone/manage the project)
  - Download: https://git-scm.com/

### System Requirements
- **RAM**: 4GB minimum, 8GB recommended
- **Disk Space**: 10GB free space
- **OS**: Windows 10+, macOS 10.15+, or Linux

## 🚀 Quick Start (Automatic)

The easiest way to get started:

```bash
# Navigate to the project directory
cd heart-of-news-backend

# Run the automated setup script
./scripts/start_local.sh
```

This script will:
- ✅ Start all backend services (API, Database, Redis, Elasticsearch)
- ✅ Run database migrations
- ✅ Seed the database with sample data
- ✅ Install frontend dependencies
- ✅ Start the frontend development server
- ✅ Provide you with login credentials

## 📱 Access the Application

Once everything is running:

- **🌐 Website**: http://localhost:3000
- **🔗 API**: http://localhost:8000
- **📚 API Docs**: http://localhost:8000/docs

### 👤 Default Login Credentials

- **Admin**: admin@heartofnews.local / admin123
- **Regular User**: user@heartofnews.local / user123
- **Editor**: editor@heartofnews.local / editor123

## 🛠️ Manual Setup (Step by Step)

If you prefer to set up manually or encounter issues:

### 1. Start Backend Services

```bash
# Start all backend services
docker-compose up -d

# Wait for services to be ready (2-3 minutes)
# Check status
docker-compose ps
```

### 2. Setup Database

```bash
# Run migrations
docker-compose exec api alembic upgrade head

# Seed with sample data
docker-compose exec api python scripts/seed_data.py
```

### 3. Start Frontend

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## 🔧 Managing the Application

### Starting Services
```bash
# Start everything
docker-compose up -d

# Start specific service
docker-compose up -d api
```

### Stopping Services
```bash
# Stop everything
docker-compose down

# Stop and remove volumes (reset database)
docker-compose down -v
```

### Viewing Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f db
```

### Rebuilding Services
```bash
# Rebuild all services
docker-compose build

# Rebuild specific service
docker-compose build api
```

## 📊 Service Endpoints

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:3000 | Main website |
| API | http://localhost:8000 | Backend REST API |
| API Docs | http://localhost:8000/docs | Interactive API documentation |
| Database | localhost:5432 | PostgreSQL database |
| Redis | localhost:6379 | Cache and message broker |
| Elasticsearch | http://localhost:9200 | Search engine |

## 🧪 Testing the Application

### Core Features to Test

1. **Authentication**
   - Register new account
   - Login with existing credentials
   - Access admin dashboard (with admin account)

2. **Articles**
   - Browse articles on homepage
   - Search and filter articles
   - View article details with bias analysis
   - Real-time updates (new articles appear automatically)

3. **Admin Features** (login as admin)
   - View admin dashboard
   - Manage articles and sources
   - View system statistics

4. **User Profile**
   - Edit profile information
   - Change password
   - Upload profile picture

### 🔍 Troubleshooting

#### Common Issues

**Docker not starting:**
```bash
# Make sure Docker Desktop is running
docker --version
docker-compose --version
```

**Port conflicts:**
```bash
# Check what's using the ports
lsof -i :3000  # Frontend
lsof -i :8000  # API
lsof -i :5432  # Database

# Kill processes if needed
kill -9 <PID>
```

**Database connection issues:**
```bash
# Reset database
docker-compose down -v
docker-compose up -d
# Wait, then run migrations again
```

**Frontend build issues:**
```bash
# Clear node modules and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Permission issues (Linux/Mac):**
```bash
# Make sure scripts are executable
chmod +x scripts/start_local.sh
```

#### Getting Help

**Check service health:**
```bash
# API health check
curl http://localhost:8000/api/v1/health

# Database check
docker-compose exec db pg_isready -U heartofnews

# View detailed logs
docker-compose logs -f api
```

## 📁 Project Structure

```
heart-of-news-backend/
├── app/                    # Backend Python code
│   ├── api/               # API routes
│   ├── models/            # Database models
│   ├── services/          # Business logic
│   └── main.py           # FastAPI application
├── frontend/              # Next.js frontend
│   ├── src/
│   │   ├── app/          # Pages and layouts
│   │   ├── components/   # React components
│   │   └── lib/          # Utilities
│   └── package.json
├── scripts/               # Setup and utility scripts
├── docker-compose.yml     # Service orchestration
├── .env                   # Backend environment variables
└── README_LOCAL_SETUP.md  # This file
```

## 🎯 Next Steps

Once you have everything running locally:

1. **Explore the Features**: Try all the functionality
2. **Add Content**: Add more news sources in the admin panel
3. **Customize**: Modify the code to suit your needs
4. **Test Thoroughly**: Ensure everything works as expected
5. **Prepare for Production**: Once satisfied, you're ready to deploy!

## 🆘 Need Help?

If you encounter any issues:

1. Check the troubleshooting section above
2. Review the logs: `docker-compose logs -f`
3. Ensure all prerequisites are installed correctly
4. Try the manual setup steps if the automatic script fails

The application should be fully functional locally and ready for production deployment!