#!/bin/bash
# Script to run load tests for Heart of News backend

set -e

# Configuration
TARGET_URL=${TARGET_URL:-"https://api-staging.heartofnews.com"}
USERS=${USERS:-100}
SPAWN_RATE=${SPAWN_RATE:-10}
RUN_TIME=${RUN_TIME:-"5m"}
HEADLESS=${HEADLESS:-true}
OUTPUT_DIR="./load_tests/results/$(date +%Y%m%d-%H%M%S)"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Print test configuration
echo "=============================================="
echo "Heart of News - Load Testing"
echo "=============================================="
echo "Test started at: $(date)"
echo "Target URL: $TARGET_URL"
echo "Number of users: $USERS"
echo "Spawn rate: $SPAWN_RATE users/sec"
echo "Run time: $RUN_TIME"
echo "Output directory: $OUTPUT_DIR"
echo "=============================================="

# Check if Python virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo "Installing requirements..."
pip install -r load_tests/requirements.txt

# Run Locust in appropriate mode
if [ "$HEADLESS" = true ]; then
    # Headless mode
    echo "Running load test in headless mode..."
    locust -f load_tests/locustfile.py \
        --host="$TARGET_URL" \
        --users="$USERS" \
        --spawn-rate="$SPAWN_RATE" \
        --run-time="$RUN_TIME" \
        --headless \
        --csv="$OUTPUT_DIR/results" \
        --html="$OUTPUT_DIR/report.html"
else
    # Web UI mode
    echo "Starting Locust web interface..."
    locust -f load_tests/locustfile.py --host="$TARGET_URL"
fi

# Deactivate virtual environment
deactivate

echo "=============================================="
echo "Load test completed at: $(date)"
echo "Results saved to: $OUTPUT_DIR"
echo "=============================================="