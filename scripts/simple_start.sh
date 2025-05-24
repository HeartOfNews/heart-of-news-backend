#!/bin/bash

# Heart of News - Simple Local Development Startup
# Alternative startup script for environments without docker-compose

set -e

echo "🚀 Starting Heart of News (Simple Mode)"
echo "======================================="

# Check if Docker is available
if ! docker --version >/dev/null 2>&1; then
    echo "❌ Docker is not available. Please install Docker and try again."
    exit 1
fi

echo "📁 Creating necessary directories..."
mkdir -p logs uploads data/postgres data/redis data/elasticsearch

echo "🗄️  Starting PostgreSQL database..."
docker run -d \
    --name heartofnews-postgres \
    --restart unless-stopped \
    -e POSTGRES_PASSWORD=development_password_2024 \
    -e POSTGRES_USER=heartofnews \
    -e POSTGRES_DB=heartofnews \
    -p 5432:5432 \
    -v "$(pwd)/data/postgres:/var/lib/postgresql/data" \
    postgres:14 || echo "PostgreSQL container already running"

echo "🔄 Starting Redis cache..."
docker run -d \
    --name heartofnews-redis \
    --restart unless-stopped \
    -p 6379:6379 \
    -v "$(pwd)/data/redis:/data" \
    redis:7 || echo "Redis container already running"

echo "🔍 Starting Elasticsearch..."
docker run -d \
    --name heartofnews-elasticsearch \
    --restart unless-stopped \
    -e "discovery.type=single-node" \
    -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" \
    -e "xpack.security.enabled=false" \
    -p 9200:9200 \
    -v "$(pwd)/data/elasticsearch:/usr/share/elasticsearch/data" \
    elasticsearch:8.7.0 || echo "Elasticsearch container already running"

echo "⏳ Waiting for services to start..."
sleep 15

# Check PostgreSQL
echo "🔍 Checking PostgreSQL..."
until docker exec heartofnews-postgres pg_isready -U heartofnews >/dev/null 2>&1; do
    echo "   PostgreSQL is starting up..."
    sleep 2
done
echo "   ✅ PostgreSQL is ready"

# Check Redis
echo "🔍 Checking Redis..."
until docker exec heartofnews-redis redis-cli ping >/dev/null 2>&1; do
    echo "   Redis is starting up..."
    sleep 2
done
echo "   ✅ Redis is ready"

# Check Elasticsearch
echo "🔍 Checking Elasticsearch..."
until curl -s http://localhost:9200/_cluster/health >/dev/null 2>&1; do
    echo "   Elasticsearch is starting up..."
    sleep 3
done
echo "   ✅ Elasticsearch is ready"

echo ""
echo "✅ All backend services are running!"
echo ""
echo "📋 Service Status:"
echo "   🗄️  PostgreSQL: localhost:5432"
echo "   🔄 Redis: localhost:6379"
echo "   🔍 Elasticsearch: http://localhost:9200"
echo ""
echo "🚀 Next steps:"
echo "   1. Install Python dependencies: pip install -r requirements.txt"
echo "   2. Run database migrations: alembic upgrade head"
echo "   3. Seed database: python scripts/seed_data.py"
echo "   4. Start API: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo "   5. In another terminal, start frontend:"
echo "      cd frontend && npm install && npm run dev"
echo ""
echo "🛑 To stop services:"
echo "   docker stop heartofnews-postgres heartofnews-redis heartofnews-elasticsearch"
echo "   docker rm heartofnews-postgres heartofnews-redis heartofnews-elasticsearch"
echo ""

# Keep script running
echo "Press Ctrl+C to exit..."
read -r