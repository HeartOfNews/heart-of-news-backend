#!/bin/bash
# Start script for the Heart of News backend in production environment

set -e

# Load environment variables
if [ -f ".env.production" ]; then
  echo "Loading production environment variables..."
  export $(grep -v '^#' .env.production | xargs)
fi

# Set required environment variables
export ENV_FILE=.env.production
export ENVIRONMENT=production
export RELOAD=false

# Create necessary directories
mkdir -p /tmp/prometheus_multiproc
chmod 777 /tmp/prometheus_multiproc

# Wait for database to be ready
echo "Waiting for database connection..."
python -m app.scripts.wait_for_db --timeout 60

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Start the application with proper worker configuration
echo "Starting FastAPI application in production mode..."
if [ "${K8S_POD_NAME}" != "" ]; then
  echo "Running in Kubernetes environment: ${K8S_POD_NAMESPACE}/${K8S_POD_NAME} on node ${K8S_NODE_NAME}"
fi

# Use gunicorn with uvicorn workers for production
gunicorn app.main:app \
  --workers ${GUNICORN_WORKERS:-4} \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile - \
  --log-level ${LOG_LEVEL:-info} \
  --timeout 120 \
  --graceful-timeout 30