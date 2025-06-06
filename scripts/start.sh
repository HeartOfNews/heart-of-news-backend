#!/bin/bash

# Start script for the Heart of News backend

set -e

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Start the application
echo "Starting FastAPI application..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 ${RELOAD:+"--reload"}