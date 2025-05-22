#!/bin/bash
# Production deployment script for Heart of News backend

set -e

# Configuration
KUBECTL=${KUBECTL:-kubectl}
KUSTOMIZE=${KUSTOMIZE:-kustomize}
NAMESPACE=${NAMESPACE:-heart-of-news-production}
GIT_TAG=$(git describe --tags --always)
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
IMAGE_TAG=${IMAGE_TAG:-"production-${GIT_TAG}-${TIMESTAMP}"}
DOCKER_REPO=${DOCKER_REPO:-"heartofnews/backend"}
FULL_IMAGE="${DOCKER_REPO}:${IMAGE_TAG}"

# Print header
echo "=============================================="
echo "Heart of News - Production Deployment"
echo "=============================================="
echo "Deployment started at: $(date)"
echo "Git tag: $GIT_TAG"
echo "Image tag: $IMAGE_TAG"
echo "Target namespace: $NAMESPACE"
echo "=============================================="

# Build and push Docker image
echo "Building and pushing Docker image: ${FULL_IMAGE}"
docker build -t ${FULL_IMAGE} -f Dockerfile.production .
docker push ${FULL_IMAGE}

# Update kustomization.yaml with the new image tag
echo "Updating Kustomize configuration with new image tag..."
cd kubernetes/overlays/production

# Use either sed or yq based on availability
if command -v yq &> /dev/null; then
  yq eval ".images[0].newTag = \"${IMAGE_TAG}\"" -i kustomization.yaml
else
  # Fallback to sed if yq is not available
  sed -i "s/newTag: production-.*/newTag: ${IMAGE_TAG}/" kustomization.yaml
fi

# Apply Kubernetes manifests using Kustomize
echo "Applying Kubernetes manifests..."
${KUSTOMIZE} build . | ${KUBECTL} apply -f -

# Wait for deployments to roll out
echo "Waiting for deployments to roll out..."
${KUBECTL} -n ${NAMESPACE} rollout status deployment/api
${KUBECTL} -n ${NAMESPACE} rollout status deployment/celery-worker
${KUBECTL} -n ${NAMESPACE} rollout status deployment/celery-beat
${KUBECTL} -n ${NAMESPACE} rollout status deployment/scraper

# Verify deployment
echo "Verifying deployment health..."
API_URL="https://api.heartofnews.com/api/v1/health"
echo "Checking API health at: ${API_URL}"
if curl -s -f "${API_URL}" > /dev/null; then
  echo "API is healthy."
else
  echo "WARNING: API health check failed. Please investigate!"
fi

# Clean up old resources
echo "Cleaning up old resources..."
# Find deployments more than 5 versions old and remove them
for DEPLOYMENT in api celery-worker celery-beat scraper; do
  OLD_REVISIONS=$(${KUBECTL} -n ${NAMESPACE} rollout history deployment/${DEPLOYMENT} | grep -v "REVISION" | sort -nr | tail -n +6 | awk '{print $1}')
  for REV in ${OLD_REVISIONS}; do
    echo "Removing old revision ${REV} of ${DEPLOYMENT}..."
    ${KUBECTL} -n ${NAMESPACE} rollout undo deployment/${DEPLOYMENT} --to-revision=${REV}
    ${KUBECTL} -n ${NAMESPACE} rollout undo deployment/${DEPLOYMENT}
  done
done

echo "=============================================="
echo "Deployment completed at: $(date)"
echo "Application is now running at: https://api.heartofnews.com"
echo "=============================================="