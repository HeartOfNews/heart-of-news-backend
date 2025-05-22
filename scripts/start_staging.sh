#!/bin/bash
# Start script for the Heart of News backend in staging environment

set -e

# Load environment variables
if [ -f ".env.staging" ]; then
  echo "Loading staging environment variables..."
  export $(grep -v '^#' .env.staging | xargs)
fi

# Create necessary directories
mkdir -p /tmp/prometheus_multiproc
chmod 777 /tmp/prometheus_multiproc

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Configure environment
echo "Configuring for staging environment..."
export ENV_FILE=.env.staging
export ENVIRONMENT=staging
export RELOAD=false

# Start the application
echo "Starting FastAPI application in staging mode..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4 --log-level info