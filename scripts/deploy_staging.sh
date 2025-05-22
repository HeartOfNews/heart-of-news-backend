#!/bin/bash
# Deploy the Heart of News application to staging environment

set -e

# Configuration
DEPLOY_DIR="${DEPLOY_DIR:-/opt/heart-of-news-staging}"
GIT_REPO="https://github.com/your-org/heart-of-news-backend.git"
GIT_BRANCH="develop"
TAG="$(date +%Y%m%d-%H%M%S)"

# Print header
echo "=============================================="
echo "Heart of News - Staging Deployment"
echo "=============================================="
echo "Deployment started at: $(date)"
echo "Deploying to: $DEPLOY_DIR"
echo "Git branch: $GIT_BRANCH"
echo "Tag: $TAG"
echo "=============================================="

# Create deployment directory if it doesn't exist
if [ ! -d "$DEPLOY_DIR" ]; then
  echo "Creating deployment directory..."
  mkdir -p "$DEPLOY_DIR"
fi

# Navigate to deployment directory
cd "$DEPLOY_DIR"

# Check if this is a first-time deployment
if [ ! -d ".git" ]; then
  echo "First-time deployment, cloning repository..."
  git clone -b "$GIT_BRANCH" "$GIT_REPO" .
else
  echo "Updating existing deployment..."
  git fetch --all
  git checkout "$GIT_BRANCH"
  git pull origin "$GIT_BRANCH"
fi

# Create necessary directories
mkdir -p logs
mkdir -p monitoring/prometheus/rules
mkdir -p monitoring/grafana/{provisioning/{datasources,dashboards},dashboards}
mkdir -p monitoring/alertmanager
mkdir -p nginx/{conf.d,ssl,logs}

# Create Prometheus multiproc directory
mkdir -p /tmp/prometheus_multiproc
chmod 777 /tmp/prometheus_multiproc

# Create Nginx configuration if it doesn't exist
if [ ! -f "nginx/conf.d/staging.conf" ]; then
  echo "Creating Nginx configuration..."
  cat > nginx/conf.d/staging.conf << 'EOF'
server {
    listen 80;
    server_name staging.heartofnews.com api-staging.heartofnews.com;
    
    # Redirect HTTP to HTTPS
    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl;
    server_name api-staging.heartofnews.com;
    
    ssl_certificate /etc/nginx/ssl/staging.crt;
    ssl_certificate_key /etc/nginx/ssl/staging.key;
    
    access_log /var/log/nginx/api-staging-access.log;
    error_log /var/log/nginx/api-staging-error.log;
    
    location / {
        proxy_pass http://api:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 443 ssl;
    server_name staging.heartofnews.com;
    
    ssl_certificate /etc/nginx/ssl/staging.crt;
    ssl_certificate_key /etc/nginx/ssl/staging.key;
    
    access_log /var/log/nginx/staging-access.log;
    error_log /var/log/nginx/staging-error.log;
    
    # Placeholder for frontend
    location / {
        return 200 'Heart of News Staging Environment';
        add_header Content-Type text/plain;
    }
}

# Monitoring dashboards with basic auth
server {
    listen 443 ssl;
    server_name grafana-staging.heartofnews.com;
    
    ssl_certificate /etc/nginx/ssl/staging.crt;
    ssl_certificate_key /etc/nginx/ssl/staging.key;
    
    access_log /var/log/nginx/grafana-staging-access.log;
    error_log /var/log/nginx/grafana-staging-error.log;
    
    location / {
        proxy_pass http://grafana:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF
fi

# Make scripts executable
chmod +x scripts/*.sh

# Set the STAGING_TAG in the environment
export STAGING_TAG="$TAG"

# Pull the latest images
echo "Pulling latest Docker images..."
docker-compose -f docker-compose.staging.yml pull

# Start the application
echo "Starting application..."
docker-compose -f docker-compose.staging.yml up -d

# Run database migrations
echo "Running database migrations..."
docker-compose -f docker-compose.staging.yml exec api alembic upgrade head

# Check service status
echo "Checking service status..."
docker-compose -f docker-compose.staging.yml ps

echo "=============================================="
echo "Deployment completed at: $(date)"
echo "Application is now running at: https://api-staging.heartofnews.com"
echo "Grafana dashboards: https://grafana-staging.heartofnews.com"
echo "=============================================="