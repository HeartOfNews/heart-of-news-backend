#!/bin/bash
# Initialize monitoring directory structure and required permissions

# Create logs directory
mkdir -p logs
chmod 755 logs

# Create prometheus multiproc directory
mkdir -p /tmp/prometheus_multiproc
chmod 777 /tmp/prometheus_multiproc

# Create directories for OpenTelemetry
mkdir -p .otel
chmod 755 .otel

# Create a placeholder for Sentry DSN in .env if not already set
if ! grep -q "SENTRY_DSN" .env 2>/dev/null; then
    echo "# Add your Sentry DSN here to enable error tracking" >> .env
    echo "SENTRY_DSN=" >> .env
fi

# Create placeholder for APM and monitoring settings
if ! grep -q "ENABLE_METRICS" .env 2>/dev/null; then
    cat << EOF >> .env

# Monitoring settings
LOG_LEVEL=INFO
ENABLE_METRICS=true
PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus_multiproc
ENABLE_PERFORMANCE_TRACKING=true
METRICS_EXPORT_INTERVAL=15

# APM Settings
# ELASTIC_APM_SERVER_URL=
# DATADOG_API_KEY=
# DATADOG_APP_KEY=
EOF
fi

echo "Monitoring environment initialized successfully!"