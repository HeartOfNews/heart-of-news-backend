# Heart of News - Production Environment Setup

This document provides detailed instructions for deploying the Heart of News backend to a production environment using Kubernetes.

## Prerequisites

- Kubernetes cluster (GKE, EKS, AKS, or equivalent)
- kubectl configured for your cluster
- Helm 3.x
- Docker registry access (Docker Hub or private registry)
- Domain names configured for your services
- SSL certificates (managed via cert-manager)

## Infrastructure Components

The production deployment consists of the following components:

1. **API Service**
   - FastAPI application running with gunicorn/uvicorn workers
   - Horizontally scalable with auto-scaling
   - Health checks and readiness probes

2. **Background Workers**
   - Celery workers for async task processing
   - Horizontally scalable with auto-scaling
   - Specialized worker pools for different task types

3. **Scheduler**
   - Celery beat for periodic task scheduling
   - Single instance to avoid duplicate tasks

4. **Scraper Service**
   - Dedicated service for news source scraping
   - Horizontally scalable for parallel scraping

5. **Databases and Caching**
   - PostgreSQL database (managed service recommended)
   - Redis for caching and Celery broker
   - Elasticsearch for full-text search

6. **Monitoring Stack**
   - Prometheus for metrics collection
   - Grafana for dashboards and visualization
   - AlertManager for alerting
   - ELK stack for logging

## Kubernetes Resources

The production environment uses the following Kubernetes resources:

- **Deployments**: For stateless components (API, workers, scraper)
- **Services**: For internal and external networking
- **Ingress**: For external access with TLS termination
- **ConfigMaps**: For configuration settings
- **Secrets**: For sensitive configuration
- **HorizontalPodAutoscalers**: For automatic scaling
- **PodDisruptionBudgets**: For availability during node maintenance

## Deployment Steps

### 1. Set Up Prerequisites

1. **Configure kubectl**
   ```bash
   kubectl config use-context your-production-cluster
   ```

2. **Set up cert-manager**
   ```bash
   ./scripts/setup_cert_manager.sh
   ```

3. **Create the namespace**
   ```bash
   kubectl create namespace heart-of-news-production
   ```

### 2. Configure Environment Variables

1. **Create .env.production file**
   ```bash
   cp .env.production.example .env.production
   # Edit .env.production with your production values
   ```

2. **Create Kubernetes secrets**
   ```bash
   # Create secrets directory
   mkdir -p kubernetes/overlays/production/secrets
   # Copy .env.production to secrets directory
   cp .env.production kubernetes/overlays/production/secrets/
   ```

### 3. Deploy to Production

1. **Build and push Docker image**
   ```bash
   # Manually
   docker build -t heartofnews/backend:production-latest .
   docker push heartofnews/backend:production-latest

   # Or using the deployment script
   ./scripts/deploy_production.sh
   ```

2. **Apply Kubernetes manifests**
   ```bash
   # Using kustomize directly
   kubectl apply -k kubernetes/overlays/production

   # Or using the deployment script
   ./scripts/deploy_production.sh
   ```

3. **Verify deployment**
   ```bash
   kubectl -n heart-of-news-production get pods
   kubectl -n heart-of-news-production get services
   kubectl -n heart-of-news-production get ingress
   ```

### 4. Set Up Monitoring

1. **Deploy Prometheus and Grafana**
   ```bash
   kubectl apply -f kubernetes/monitoring/
   ```

2. **Import Grafana dashboards**
   - Access Grafana at https://grafana.heartofnews.com
   - Import dashboards from monitoring/grafana/dashboards

3. **Configure alerts**
   - Configure AlertManager with appropriate notification channels
   - Test alerts to ensure proper delivery

### 5. Production CI/CD

The production deployment can be automated using GitHub Actions:

1. **Configure GitHub Secrets**
   - Add all required secrets as listed in `.github/workflows/production.yml`
   - Add Kubernetes credentials for automated deployment

2. **Merge to Main Branch or Create Release Tag**
   - Merging to `main` branch will trigger deployment
   - Creating a tag like `v1.0.0` will trigger a versioned release

3. **Manual Approval**
   - The workflow includes a manual approval step for production deployment
   - Approve the deployment in GitHub Actions interface

## SSL/TLS Configuration

SSL/TLS certificates are managed using cert-manager:

1. **ClusterIssuer**: Configured to use Let's Encrypt
2. **Certificate**: Automatically provisioned for domains
3. **Ingress**: Configured to use TLS with the provisioned certificates

## Load Testing

Before deploying major changes to production, run load tests:

```bash
# Run load test locally
./load_tests/run_load_test.sh

# Run load test in Kubernetes
./scripts/run_k8s_load_test.sh
```

## Rollback Procedure

If issues are detected in production:

1. **Immediate Rollback**
   ```bash
   kubectl -n heart-of-news-production rollout undo deployment/api
   kubectl -n heart-of-news-production rollout undo deployment/celery-worker
   kubectl -n heart-of-news-production rollout undo deployment/celery-beat
   kubectl -n heart-of-news-production rollout undo deployment/scraper
   ```

2. **Rollback to Specific Version**
   ```bash
   kubectl -n heart-of-news-production rollout undo deployment/api --to-revision=<revision>
   ```

3. **Deploy Previous Known Good Image**
   ```bash
   kubectl -n heart-of-news-production set image deployment/api api=heartofnews/backend:<previous-tag>
   ```

## Disaster Recovery

The following backup and recovery procedures are implemented:

1. **Database Backups**
   - Daily automated backups
   - Point-in-time recovery capability
   - Regular backup testing

2. **Configuration Backups**
   - All configuration stored in version control
   - Kubernetes resources defined as code

3. **Recovery Procedure**
   - Restore database from backup
   - Reapply Kubernetes manifests
   - Verify application functionality

## Security Considerations

The production environment implements the following security measures:

1. **Network Security**
   - All external traffic encrypted with TLS
   - Internal service communication within Kubernetes
   - Network policies to restrict pod communication

2. **Authentication and Authorization**
   - JWT-based authentication with short expiration
   - Role-based access control
   - API rate limiting

3. **Secrets Management**
   - Sensitive data stored in Kubernetes Secrets
   - Limited access to production credentials

4. **Container Security**
   - Non-root users in containers
   - Read-only file systems where possible
   - Limited capabilities
   - Security Context constraints

## Monitoring and Alerting

The production environment is monitored using:

1. **System Metrics**
   - CPU, memory, disk usage
   - Network traffic and latency
   - Container health and restarts

2. **Application Metrics**
   - Request rates and response times
   - Error rates and status codes
   - Database query performance

3. **Business Metrics**
   - Article processing rates
   - Source scraping success rates
   - User activity and engagement

Alerts are configured for:

1. **Critical Issues**
   - Service downtime
   - High error rates
   - Resource exhaustion

2. **Warning Conditions**
   - Elevated response times
   - Increased resource usage
   - Approaching resource limits

## Contact Information

For issues or assistance with production deployment:

- **Technical Contact**: tech@heartofnews.com
- **Operations Team**: ops@heartofnews.com
- **Emergency Support**: +1-555-123-4567