#!/bin/bash
# Script to run Kubernetes-based load testing

set -e

# Configuration
KUBECTL=${KUBECTL:-kubectl}
NAMESPACE=${NAMESPACE:-"heart-of-news-production"}
HOST=${HOST:-"https://api.heartofnews.com"}
USERS=${USERS:-200}
SPAWN_RATE=${SPAWN_RATE:-10}
RUN_TIME=${RUN_TIME:-"10m"}
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
JOB_NAME="heart-of-news-load-test-${TIMESTAMP}"

# Print test configuration
echo "=============================================="
echo "Heart of News - Kubernetes Load Testing"
echo "=============================================="
echo "Test started at: $(date)"
echo "Target URL: $HOST"
echo "Namespace: $NAMESPACE"
echo "Number of users: $USERS"
echo "Spawn rate: $SPAWN_RATE users/sec"
echo "Run time: $RUN_TIME"
echo "Job name: $JOB_NAME"
echo "=============================================="

# Create a ConfigMap with the locust file content
echo "Creating ConfigMap with Locust script..."
${KUBECTL} -n ${NAMESPACE} create configmap locust-scripts --from-file=locustfile.py=./load_tests/locustfile.py -o yaml --dry-run=client | ${KUBECTL} apply -f -

# Create the Job from the template
echo "Creating Kubernetes Job for load testing..."
cat load_tests/k8s_load_test.yaml | \
  sed "s/heart-of-news-load-test/${JOB_NAME}/g" | \
  sed "s|--host=https://api.heartofnews.com|--host=${HOST}|g" | \
  sed "s/--users=200/--users=${USERS}/g" | \
  sed "s/--spawn-rate=10/--spawn-rate=${SPAWN_RATE}/g" | \
  sed "s/--run-time=10m/--run-time=${RUN_TIME}/g" | \
  ${KUBECTL} -n ${NAMESPACE} apply -f -

# Wait for the job to start
echo "Waiting for load test job to start..."
${KUBECTL} -n ${NAMESPACE} wait --for=condition=ready pod -l job-name=${JOB_NAME} --timeout=60s || true

# Stream logs from the load test pod
echo "Streaming logs from the load test pod..."
POD_NAME=$(${KUBECTL} -n ${NAMESPACE} get pod -l job-name=${JOB_NAME} -o jsonpath="{.items[0].metadata.name}")
${KUBECTL} -n ${NAMESPACE} logs -f ${POD_NAME} || true

# Wait for the job to complete
echo "Waiting for load test job to complete..."
${KUBECTL} -n ${NAMESPACE} wait --for=condition=complete job/${JOB_NAME} --timeout=3600s || true

# Check if the job succeeded
if ${KUBECTL} -n ${NAMESPACE} get job/${JOB_NAME} -o jsonpath="{.status.succeeded}" | grep -q "1"; then
  echo "Load test completed successfully!"
else
  echo "Load test failed or was interrupted."
  ${KUBECTL} -n ${NAMESPACE} describe job/${JOB_NAME}
  ${KUBECTL} -n ${NAMESPACE} logs ${POD_NAME}
  exit 1
fi

# Create output directory
OUTPUT_DIR="./load_tests/results/${TIMESTAMP}"
mkdir -p "${OUTPUT_DIR}"

# Copy results from the pod
echo "Copying results from the pod..."
${KUBECTL} -n ${NAMESPACE} cp ${POD_NAME}:/results/results_stats.csv "${OUTPUT_DIR}/results_stats.csv"
${KUBECTL} -n ${NAMESPACE} cp ${POD_NAME}:/results/results_stats_history.csv "${OUTPUT_DIR}/results_stats_history.csv"
${KUBECTL} -n ${NAMESPACE} cp ${POD_NAME}:/results/results_failures.csv "${OUTPUT_DIR}/results_failures.csv"
${KUBECTL} -n ${NAMESPACE} cp ${POD_NAME}:/results/report.html "${OUTPUT_DIR}/report.html"

echo "=============================================="
echo "Load test completed at: $(date)"
echo "Results saved to: ${OUTPUT_DIR}"
echo "=============================================="

# Optional: Clean up
if [ "${CLEANUP:-true}" = "true" ]; then
  echo "Cleaning up resources..."
  ${KUBECTL} -n ${NAMESPACE} delete job/${JOB_NAME}
fi