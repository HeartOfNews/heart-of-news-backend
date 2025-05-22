#!/bin/bash
# Initialize and start monitoring for staging environment

set -e

# Create required directories
mkdir -p monitoring/prometheus/rules
mkdir -p monitoring/grafana/{provisioning/{datasources,dashboards},dashboards}
mkdir -p monitoring/alertmanager
mkdir -p logs

# Create Prometheus configuration for staging if it doesn't exist
if [ ! -f "monitoring/prometheus/prometheus.staging.yml" ]; then
  echo "Creating Prometheus configuration for staging..."
  cat > monitoring/prometheus/prometheus.staging.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    environment: staging

# Alertmanager configuration
alerting:
  alertmanagers:
  - static_configs:
    - targets:
      - alertmanager:9093

# Load and evaluate rules
rule_files:
  - "rules/*.yml"

# Scrape configurations
scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'heart-of-news-api'
    metrics_path: '/api/v1/metrics'
    static_configs:
      - targets: ['api:8000']
    
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']

  - job_name: 'redis-exporter'
    static_configs:
      - targets: ['redis-exporter:9121']

  - job_name: 'postgres-exporter'
    static_configs:
      - targets: ['postgres-exporter:9187']
EOF
fi

# Create Alertmanager configuration for staging if it doesn't exist
if [ ! -f "monitoring/alertmanager/alertmanager.staging.yml" ]; then
  echo "Creating Alertmanager configuration for staging..."
  cat > monitoring/alertmanager/alertmanager.staging.yml << 'EOF'
global:
  resolve_timeout: 5m
  slack_api_url: 'https://hooks.slack.com/services/YOUR_SLACK_WEBHOOK'

route:
  group_by: ['alertname', 'job']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  receiver: 'slack-notifications'
  routes:
  - match:
      severity: critical
    receiver: 'slack-notifications'
    continue: true

receivers:
- name: 'slack-notifications'
  slack_configs:
  - channel: '#heart-of-news-alerts'
    send_resolved: true
    title: '[{{ .Status | toUpper }}{{ if eq .Status "firing" }}:{{ .Alerts.Firing | len }}{{ end }}] Heart of News Staging Alert'
    text: >-
      {{ range .Alerts }}
        *Alert:* {{ .Labels.alertname }}{{ if .Labels.severity }} - `{{ .Labels.severity }}`{{ end }}
        *Description:* {{ .Annotations.description }}
        *Details:*
        {{ range .Labels.SortedPairs }} • *{{ .Name }}:* `{{ .Value }}`
        {{ end }}
      {{ end }}
EOF
fi

# Create Grafana dashboard provisioning for staging if it doesn't exist
if [ ! -d "monitoring/grafana/provisioning/dashboards" ]; then
  echo "Creating Grafana dashboard provisioning for staging..."
  mkdir -p monitoring/grafana/provisioning/dashboards
  
  cat > monitoring/grafana/provisioning/dashboards/dashboards.yml << 'EOF'
apiVersion: 1

providers:
  - name: 'Heart of News Staging'
    orgId: 1
    folder: 'Heart of News'
    type: file
    disableDeletion: false
    editable: true
    options:
      path: /var/lib/grafana/dashboards
EOF
fi

# Create Grafana datasource provisioning for staging if it doesn't exist
if [ ! -d "monitoring/grafana/provisioning/datasources" ]; then
  echo "Creating Grafana datasource provisioning for staging..."
  mkdir -p monitoring/grafana/provisioning/datasources
  
  cat > monitoring/grafana/provisioning/datasources/datasources.yml << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: false
EOF
fi

# Create Prometheus multiproc directory
mkdir -p /tmp/prometheus_multiproc
chmod 777 /tmp/prometheus_multiproc

# Start the monitoring stack
echo "Starting monitoring stack for staging..."
docker-compose -f docker-compose.staging.yml up -d prometheus grafana alertmanager

echo "Monitoring for staging environment initialized and started!"
echo "Grafana: https://grafana-staging.heartofnews.com"