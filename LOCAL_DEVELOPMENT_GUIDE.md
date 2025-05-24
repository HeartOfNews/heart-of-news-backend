# 🏠 Heart of News - Complete Local Development Guide

This guide will help you run Heart of News locally on your computer, bringing it to a state of complete readiness.

## 📋 Prerequisites

### Required Software
1. **Docker** (latest version)
   - Windows/Mac: Download Docker Desktop from https://www.docker.com/products/docker-desktop/
   - Linux: Install Docker CE from your package manager

2. **Python 3.9+**
   - Download from https://www.python.org/downloads/
   - Check: `python --version`

3. **Node.js 18+**
   - Download from https://nodejs.org/
   - Check: `node --version`

4. **Git** (optional, for version control)

### System Requirements
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 10GB free space
- **OS**: Windows 10+, macOS 10.15+, or Linux

## 🚀 Option 1: Automated Setup (Recommended)

### For Docker Compose Users
If you have Docker Compose installed:

```bash
cd heart-of-news-backend
./scripts/start_local.sh
```

### For Docker-Only Users
If you only have Docker:

```bash
cd heart-of-news-backend
./scripts/simple_start.sh
```

## 🛠️ Option 2: Manual Setup (Step by Step)

### Step 1: Start Database Services

#### Using Individual Docker Containers:

```bash
# Create data directories
mkdir -p data/{postgres,redis,elasticsearch}

# Start PostgreSQL
docker run -d \
    --name heartofnews-postgres \
    -e POSTGRES_PASSWORD=development_password_2024 \
    -e POSTGRES_USER=heartofnews \
    -e POSTGRES_DB=heartofnews \
    -p 5432:5432 \
    -v "$(pwd)/data/postgres:/var/lib/postgresql/data" \
    postgres:14

# Start Redis
docker run -d \
    --name heartofnews-redis \
    -p 6379:6379 \
    -v "$(pwd)/data/redis:/data" \
    redis:7

# Start Elasticsearch
docker run -d \
    --name heartofnews-elasticsearch \
    -e "discovery.type=single-node" \
    -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" \
    -e "xpack.security.enabled=false" \
    -p 9200:9200 \
    -v "$(pwd)/data/elasticsearch:/usr/share/elasticsearch/data" \
    elasticsearch:8.7.0
```

Wait 2-3 minutes for services to start, then verify:

```bash
# Check PostgreSQL
docker exec heartofnews-postgres pg_isready -U heartofnews

# Check Redis
docker exec heartofnews-redis redis-cli ping

# Check Elasticsearch
curl http://localhost:9200/_cluster/health
```

### Step 2: Setup Python Backend

```bash
# Install Python dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Seed database with sample data
python scripts/seed_data.py
```

### Step 3: Start Backend API

```bash
# Start the API server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: http://localhost:8000

### Step 4: Setup Frontend

Open a new terminal:

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The website will be available at: http://localhost:3000

## 🎯 Access the Application

### 🌐 Website URLs
- **Main Website**: http://localhost:3000
- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### 👤 Default Login Credentials
- **Admin**: admin@heartofnews.local / admin123
- **User**: user@heartofnews.local / user123
- **Editor**: editor@heartofnews.local / editor123

## 🧪 Testing Your Local Setup

### 1. Basic Functionality Test

1. **Open the website**: http://localhost:3000
2. **Browse articles**: You should see sample articles
3. **Login**: Use admin@heartofnews.local / admin123
4. **Admin access**: Navigate to the admin dashboard
5. **Search**: Try searching for articles
6. **Profile**: Visit your profile page

### 2. API Test

Visit http://localhost:8000/docs to test API endpoints directly.

### 3. Real-time Features Test

1. Login to the website
2. Open the admin panel in another tab
3. Add a new article from admin panel
4. Check if it appears in the main feed

## 🔧 Managing Your Local Environment

### Starting Services
```bash
# Start all Docker services
docker start heartofnews-postgres heartofnews-redis heartofnews-elasticsearch

# Start Python API (in project root)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start frontend (in frontend directory)
npm run dev
```

### Stopping Services
```bash
# Stop Python API: Ctrl+C in terminal
# Stop frontend: Ctrl+C in terminal

# Stop Docker services
docker stop heartofnews-postgres heartofnews-redis heartofnews-elasticsearch
```

### Resetting Database
```bash
# Stop and remove database container
docker stop heartofnews-postgres
docker rm heartofnews-postgres

# Remove data
rm -rf data/postgres

# Start fresh database
docker run -d --name heartofnews-postgres \
    -e POSTGRES_PASSWORD=development_password_2024 \
    -e POSTGRES_USER=heartofnews \
    -e POSTGRES_DB=heartofnews \
    -p 5432:5432 \
    postgres:14

# Wait and run migrations again
sleep 10
alembic upgrade head
python scripts/seed_data.py
```

## 🐛 Troubleshooting

### Common Issues

#### "Port already in use"
```bash
# Check what's using the port
lsof -i :3000  # Frontend
lsof -i :8000  # API
lsof -i :5432  # Database

# Kill the process
kill -9 <PID>
```

#### "Docker container already exists"
```bash
# Remove existing containers
docker rm -f heartofnews-postgres heartofnews-redis heartofnews-elasticsearch
```

#### "Database connection failed"
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Check logs
docker logs heartofnews-postgres

# Restart PostgreSQL
docker restart heartofnews-postgres
```

#### "Frontend build issues"
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Getting Detailed Information

```bash
# Check API logs
# (API logs appear in the terminal where you ran uvicorn)

# Check Docker container logs
docker logs heartofnews-postgres
docker logs heartofnews-redis
docker logs heartofnews-elasticsearch

# Check service status
docker ps

# Test database connection
docker exec -it heartofnews-postgres psql -U heartofnews -d heartofnews
```

## 📊 Development Tools

### Database Management
```bash
# Access PostgreSQL directly
docker exec -it heartofnews-postgres psql -U heartofnews -d heartofnews

# Common queries
SELECT * FROM users;
SELECT * FROM sources;
SELECT * FROM articles;
```

### Redis Management
```bash
# Access Redis CLI
docker exec -it heartofnews-redis redis-cli

# Common commands
KEYS *
GET some_key
FLUSHALL  # Clear all data
```

### API Testing
- Interactive docs: http://localhost:8000/docs
- Health check: http://localhost:8000/api/v1/health

## 🎯 Ready for Production?

Once everything works locally:

1. ✅ All features function correctly
2. ✅ You can login and use admin features
3. ✅ Articles display properly with bias scores
4. ✅ Search and filtering work
5. ✅ Real-time updates function

You're ready to deploy to production hosting!

## 🆘 Need Help?

If you encounter issues:

1. **Check Prerequisites**: Ensure Docker, Python, and Node.js are installed
2. **Follow Steps**: Go through the manual setup step by step
3. **Check Logs**: Look at service logs for error messages
4. **Try Reset**: Remove containers and start fresh
5. **Check Resources**: Ensure sufficient RAM/disk space

Your local Heart of News should be fully functional and ready for production deployment!