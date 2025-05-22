#!/bin/bash
# Start the monitoring stack for Heart of News

# Create required directories if they don't exist
mkdir -p monitoring/prometheus/rules
mkdir -p monitoring/grafana/{provisioning/{datasources,dashboards},dashboards}
mkdir -p monitoring/alertmanager
mkdir -p logs

# Ensure Prometheus rules directory exists
if [ ! -d "monitoring/prometheus/rules" ]; then
    echo "Creating Prometheus rules directory..."
    mkdir -p monitoring/prometheus/rules
fi

# Create Prometheus multiproc directory
if [ ! -d "/tmp/prometheus_multiproc" ]; then
    echo "Creating Prometheus multiproc directory..."
    mkdir -p /tmp/prometheus_multiproc
    chmod 777 /tmp/prometheus_multiproc
fi

# Start the monitoring stack
echo "Starting monitoring stack..."
docker-compose -f docker-compose.monitoring.yml up -d

# Check if services are running
echo "Checking services..."
docker-compose -f docker-compose.monitoring.yml ps

echo ""
echo "Monitoring stack is now running"
echo "- Prometheus: http://localhost:9090"
echo "- Grafana: http://localhost:3000 (admin/heartofnews)"
echo "- Alertmanager: http://localhost:9093"
echo "- Kibana: http://localhost:5601"
echo ""
echo "To stop the monitoring stack:"
echo "docker-compose -f docker-compose.monitoring.yml down"