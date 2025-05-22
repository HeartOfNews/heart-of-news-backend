# Heart of News - Staging Environment Setup

This document provides instructions for setting up and deploying the Heart of News application to a staging environment.

## Prerequisites

- Docker and Docker Compose installed on the staging server
- Git access to the Heart of News repository
- SSH access to the staging server
- DNS records configured for:
  - api-staging.heartofnews.com
  - staging.heartofnews.com
  - grafana-staging.heartofnews.com

## Required Environment Variables

The following environment variables must be configured in the GitHub repository secrets for staging deployment:

| Variable Name | Description |
|---------------|-------------|
| `STAGING_SERVER_IP` | IP address of the staging server |
| `STAGING_SSH_USER` | SSH username for the staging server |
| `STAGING_SSH_KEY` | Private SSH key for accessing the staging server |
| `STAGING_DEPLOY_DIR` | Directory on the staging server where the application will be deployed |
| `STAGING_SECRET_KEY` | Secret key for the staging environment |
| `STAGING_DB_HOST` | Hostname of the PostgreSQL database server |
| `STAGING_DB_USER` | PostgreSQL database username |
| `STAGING_DB_PASSWORD` | PostgreSQL database password |
| `STAGING_REDIS_HOST` | Hostname of the Redis server |
| `STAGING_REDIS_PASSWORD` | Redis password (if applicable) |
| `STAGING_ES_HOST` | Hostname of the Elasticsearch server |
| `STAGING_AWS_ACCESS_KEY` | AWS access key for S3 storage |
| `STAGING_AWS_SECRET_KEY` | AWS secret key for S3 storage |
| `STAGING_SENTRY_DSN` | Sentry DSN for error tracking |
| `STAGING_APM_URL` | Elastic APM server URL |
| `STAGING_DATADOG_API_KEY` | Datadog API key |
| `STAGING_DATADOG_APP_KEY` | Datadog application key |
| `DOCKER_HUB_USERNAME` | Docker Hub username for pushing images |
| `DOCKER_HUB_ACCESS_TOKEN` | Docker Hub access token |

## SSL Certificate Setup

SSL certificates must be configured on the staging server for secure HTTPS access:

1. Place SSL certificate files in the `nginx/ssl` directory:
   - `staging.crt` - Certificate file
   - `staging.key` - Private key file

2. If using Let's Encrypt, set up an automatic renewal process.

## Manual Deployment

To manually deploy to the staging environment:

1. SSH into the staging server
2. Clone the repository (if not already present):
   ```bash
   git clone -b develop https://github.com/your-org/heart-of-news-backend.git /opt/heart-of-news-staging
   ```

3. Navigate to the deployment directory:
   ```bash
   cd /opt/heart-of-news-staging
   ```

4. Create a `.env.staging` file with the required environment variables (see `.env.staging.example`)

5. Run the deployment script:
   ```bash
   chmod +x scripts/deploy_staging.sh
   ./scripts/deploy_staging.sh
   ```

## Monitoring Setup

The staging environment includes a complete monitoring stack with:

- Prometheus for metrics collection
- Grafana for dashboards and visualization
- Alertmanager for alerts
- Elasticsearch and Kibana for logging

Access Grafana dashboards at `https://grafana-staging.heartofnews.com` with the credentials configured in the Docker Compose file.

## Deployment Verification

After deployment, verify that the application is running correctly:

1. Check the API health endpoint:
   ```bash
   curl https://api-staging.heartofnews.com/api/v1/health
   ```

2. Verify all services are running:
   ```bash
   docker-compose -f docker-compose.staging.yml ps
   ```

3. Check the logs for any errors:
   ```bash
   docker-compose -f docker-compose.staging.yml logs api
   ```

## Troubleshooting

If the deployment fails, check the following:

1. Ensure all required environment variables are set
2. Verify that the staging server has sufficient resources (CPU, memory, disk space)
3. Check for any network connectivity issues
4. Examine the Docker Compose logs for specific error messages
5. Verify database migrations completed successfully

For more detailed troubleshooting, see the logs in the `logs` directory.