# Heart of News Deployment Guide

This guide covers the deployment process for the Heart of News backend system across different environments.

## Deployment Environments

Heart of News uses three primary deployment environments:

1. **Development** - Local development environment for individual developers
2. **Staging** - Testing environment that mirrors production
3. **Production** - Live environment for end users

## Development Environment

The development environment is designed for local development and testing.

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/HeartOfNews/heart-of-news-backend.git
   cd heart-of-news-backend
   ```

2. Create a `.env` file:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. Start the development environment with Docker Compose:
   ```bash
   docker-compose up -d
   ```

4. Access the API at http://localhost:8000
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Staging Environment

The staging environment mirrors the production setup and is used for testing before deployment to production.

### Configuration

Staging environment uses:
- Dedicated configuration in `.env.staging`
- Custom Docker Compose file: `docker-compose.staging.yml`
- Automated deployment via GitHub Actions
- Comprehensive monitoring stack

### Infrastructure

- **API**: https://api-staging.heartofnews.com
- **Monitoring**: https://grafana-staging.heartofnews.com
- **Database**: Dedicated PostgreSQL instance
- **Cache**: Redis instance
- **Search**: Elasticsearch cluster

### Deployment Process

The staging environment is automatically deployed when changes are pushed to the `develop` branch:

1. GitHub Actions workflow runs tests and linting
2. Docker image is built and tagged
3. New image is deployed to staging server
4. Database migrations are applied
5. Service health is verified

### Manual Deployment

To manually deploy to staging:

1. SSH into the staging server
2. Navigate to the deployment directory
3. Run the staging deployment script:
   ```bash
   ./scripts/deploy_staging.sh
   ```

### Environment Variables

Required environment variables for staging deployment are documented in `.env.staging.example` and should be configured in:
- GitHub repository secrets (for CI/CD pipeline)
- Server environment (for manual deployment)

See [Staging Setup](staging_setup.md) for detailed instructions.

## Production Environment (Planned)

The production environment is designed for high availability and scalability.

### Architecture

Production will use:
- Kubernetes cluster for container orchestration
- Horizontal Pod Autoscaling for handling load variations
- Ingress controller for traffic management
- Persistent volumes for stateful components
- Production-grade monitoring and alerting

### Deployment Strategy

Production deployment will follow a blue-green deployment strategy:
1. New version is deployed alongside the current version
2. Tests are performed on the new version
3. Traffic is gradually shifted to the new version
4. If issues are detected, traffic is immediately shifted back

### Rollback Procedure

In case of critical issues:
1. Revert to the previous stable image tag
2. Apply the rollback using Kubernetes rolling update
3. Verify system health
4. Investigate root cause

## Monitoring and Observability

All environments include monitoring capabilities:

- **Metrics**: Prometheus for collecting and storing metrics
- **Visualization**: Grafana dashboards for visualization
- **Alerting**: Alertmanager for notifications
- **Logging**: ELK stack for log aggregation and analysis
- **Performance**: APM tools for application performance monitoring

## Backup and Recovery

The system employs the following backup strategies:

- **Database**: Daily automated backups with point-in-time recovery
- **Configuration**: Version-controlled and stored in Git
- **Media**: Regular backups to S3-compatible storage
- **Restoration**: Documented recovery procedures for each component

## Security Considerations

- All environments use TLS for encrypted communications
- Staging and production environments employ strict network policies
- Secrets are managed securely using environment variables
- Regular security audits and updates are performed

## Continuous Integration/Continuous Deployment

The CI/CD pipeline includes:

1. **Continuous Integration**:
   - Automated testing on pull requests
   - Code quality checks
   - Security scanning

2. **Continuous Delivery**:
   - Automated builds of Docker images
   - Image tagging and versioning
   - Push to container registry

3. **Continuous Deployment**:
   - Automated deployment to staging
   - Manual approval for production
   - Post-deployment health verification