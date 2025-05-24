#!/bin/bash

# Heart of News - Local Development Startup Script
# This script sets up and starts the complete application locally

set -e  # Exit on any error

echo "🚀 Starting Heart of News Local Development Environment"
echo "======================================================"

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose >/dev/null 2>&1; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose and try again."
    exit 1
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs uploads

# Set executable permissions
chmod +x scripts/seed_data.py

echo "🐳 Starting backend services with Docker Compose..."
docker-compose down --remove-orphans 2>/dev/null || true
docker-compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 15

# Check if services are healthy
echo "🔍 Checking service health..."

# Check PostgreSQL
until docker-compose exec -T db pg_isready -U heartofnews >/dev/null 2>&1; do
    echo "   PostgreSQL is starting up..."
    sleep 2
done
echo "   ✅ PostgreSQL is ready"

# Check Redis
until docker-compose exec -T redis redis-cli ping >/dev/null 2>&1; do
    echo "   Redis is starting up..."
    sleep 2
done
echo "   ✅ Redis is ready"

# Check Elasticsearch
until curl -s http://localhost:9200/_cluster/health >/dev/null 2>&1; do
    echo "   Elasticsearch is starting up..."
    sleep 3
done
echo "   ✅ Elasticsearch is ready"

# Wait a bit more for the API to be fully ready
echo "⏳ Waiting for API to be ready..."
sleep 10

# Check API health
until curl -s http://localhost:8000/api/v1/health >/dev/null 2>&1; do
    echo "   API is starting up..."
    sleep 3
done
echo "   ✅ API is ready"

echo "🗄️  Running database migrations..."
docker-compose exec -T api alembic upgrade head

echo "🌱 Seeding database with initial data..."
docker-compose exec -T api python scripts/seed_data.py

echo ""
echo "🎉 Backend services are ready!"
echo "   🔗 API: http://localhost:8000"
echo "   📚 API Docs: http://localhost:8000/docs"
echo "   🗄️  Database: localhost:5432"
echo "   🔄 Redis: localhost:6379"
echo "   🔍 Elasticsearch: http://localhost:9200"
echo ""

# Check if Node.js is installed
if ! command -v node >/dev/null 2>&1; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ and try again."
    echo "   Download from: https://nodejs.org/"
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js version 18+ is required. Current version: $(node -v)"
    echo "   Please upgrade Node.js from: https://nodejs.org/"
    exit 1
fi

echo "📦 Installing frontend dependencies..."
cd frontend

# Check if package-lock.json exists, if not, clean install
if [ ! -f package-lock.json ]; then
    echo "   Running fresh npm install..."
    npm install
else
    echo "   Running npm ci for faster install..."
    npm ci
fi

echo "🎨 Starting frontend development server..."
echo "   This will open in a new terminal window..."

# Start frontend in background and capture PID
npm run dev &
FRONTEND_PID=$!

cd ..

echo ""
echo "🎉 HEART OF NEWS IS NOW RUNNING LOCALLY!"
echo "============================================"
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🔗 Backend API: http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo ""
echo "👤 Default Login Credentials:"
echo "   Admin: admin@heartofnews.local / admin123"
echo "   User: user@heartofnews.local / user123"
echo ""
echo "🛑 To stop all services:"
echo "   docker-compose down"
echo "   kill $FRONTEND_PID  # Stop frontend"
echo ""
echo "📝 Logs:"
echo "   docker-compose logs -f     # All services"
echo "   docker-compose logs -f api # Just API"
echo ""

# Keep script running and show logs
echo "📊 Showing live logs (Ctrl+C to exit)..."
docker-compose logs -f