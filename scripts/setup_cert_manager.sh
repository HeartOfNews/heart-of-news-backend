#!/bin/bash
# Set up cert-manager for SSL/TLS certificates

set -e

# Configuration
KUBECTL=${KUBECTL:-kubectl}
HELM=${HELM:-helm}
NAMESPACE=${CERT_MANAGER_NAMESPACE:-cert-manager}
VERSION=${CERT_MANAGER_VERSION:-v1.12.3}

# Print header
echo "=============================================="
echo "Heart of News - Setting up cert-manager"
echo "=============================================="
echo "Setup started at: $(date)"
echo "cert-manager version: $VERSION"
echo "Target namespace: $NAMESPACE"
echo "=============================================="

# Create namespace if it doesn't exist
if ! ${KUBECTL} get namespace ${NAMESPACE} &> /dev/null; then
  echo "Creating namespace: ${NAMESPACE}"
  ${KUBECTL} create namespace ${NAMESPACE}
fi

# Add the Jetstack Helm repository
echo "Adding Jetstack Helm repository..."
${HELM} repo add jetstack https://charts.jetstack.io
${HELM} repo update

# Install cert-manager
echo "Installing cert-manager..."
${HELM} upgrade --install cert-manager jetstack/cert-manager \
  --namespace ${NAMESPACE} \
  --version ${VERSION} \
  --set installCRDs=true \
  --set prometheus.enabled=true \
  --set webhook.timeoutSeconds=30

# Wait for cert-manager to be ready
echo "Waiting for cert-manager to be ready..."
${KUBECTL} -n ${NAMESPACE} wait --for=condition=available deployment/cert-manager --timeout=120s
${KUBECTL} -n ${NAMESPACE} wait --for=condition=available deployment/cert-manager-webhook --timeout=120s
${KUBECTL} -n ${NAMESPACE} wait --for=condition=available deployment/cert-manager-cainjector --timeout=120s

# Create ClusterIssuers for Let's Encrypt
echo "Creating ClusterIssuers for Let's Encrypt..."
${KUBECTL} apply -f kubernetes/cert-manager/cluster-issuer.yaml

# Create Certificate for Heart of News
echo "Creating Certificate for Heart of News..."
${KUBECTL} apply -f kubernetes/cert-manager/certificate.yaml

echo "=============================================="
echo "cert-manager setup completed at: $(date)"
echo "ClusterIssuers created: letsencrypt-staging, letsencrypt-prod"
echo "Certificate created: heart-of-news-tls"
echo "=============================================="