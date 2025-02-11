# Monitoring

This directory contains the configuration files and setup for monitoring the system using Prometheus, Grafana, and Alertmanager.

---

## Overview

The monitoring stack includes:
- **Prometheus**: Collects and stores metrics from various components.
- **Grafana**: Visualizes the collected metrics via dashboards.
- **Alertmanager**: Sends alerts based on predefined rules.
- **Kafka JMX Exporter**: Exposes Kafka's internal metrics for Prometheus.

---

## Directory Structure

```
monitoring/
├── grafana/
│   ├── dashboards/                # Predefined Grafana dashboards
│   ├── provisioning/
│   │   ├── datasources/
│   │   │   ├── data-sources.yaml  # Grafana auto-provisioning for Prometheus
├── prometheus/
│   ├── prometheus.yaml            # Prometheus configuration
│   ├── alert.rules.yaml           # Alerting rules
├── alertmanager/
│   ├── alertmanager.yaml          # Alertmanager configuration
├── jmx_exporter/
│   ├── jmx_prometheus_javaagent-1.1.0.jar  # JMX Exporter JAR file
│   ├── kafka_jmx_exporter.yaml    # Kafka JMX Exporter config
└── README.md                      # This file
```

---

## Kafka JMX Exporter

Kafka JMX Exporter is used to expose internal Kafka metrics to Prometheus.
- It is deployed as a **Java Agent** in the Kafka container.
- It enables monitoring of Kafka broker metrics like **MessagesInPerSec**, **BytesInPerSec**, **FailedProduceRequestsPerSec**, etc.

### Configuration
- The JMX Exporter JAR file is located at:
  ```bash
  monitoring/jmx_exporter/jmx_prometheus_javaagent-1.1.0.jar
  ```
- The configuration file is located at:
  ```bash
  monitoring/jmx_exporter/kafka_jmx_exporter.yaml
  ```
- Kafka’s environment variables in `docker-compose.yml` ensure that JMX Exporter runs properly:
  ```yaml
  KAFKA_OPTS: "-javaagent:/opt/jmx_prometheus_javaagent.jar=9404:/opt/kafka_jmx_exporter.yml"
  ```

### Verification
After starting Kafka, check if metrics are exposed:
```bash
curl http://localhost:9404/metrics
```
This should return various Kafka broker metrics.

---

## Prometheus
Prometheus collects metrics from various sources, including Kafka JMX Exporter.

### Configuration
- Config file: `monitoring/prometheus/prometheus.yaml`
- Alerting rules: `monitoring/prometheus/alert.rules.yaml`

### Verification
To check if Prometheus is running:
- Open `http://localhost:9090` in a browser.
- Go to **Status → Targets** and ensure all targets are up.
- To test an alert rule:
  ```bash
  curl -X GET http://localhost:9090/api/v1/alerts | jq .
  ```

---

## Grafana
Grafana is used to visualize Prometheus data.

### Configuration
Grafana is automatically provisioned with a Prometheus data source using `data-sources.yaml`:
```yaml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
```

This file is located at:
```
monitoring/grafana/provisioning/datasources/data-sources.yaml
```
### Verification
1. Start Grafana and open `http://localhost:3000`
2. Go to **Configuration → Data Sources**
3. Ensure **Prometheus** is listed

---

## Alertmanager
Alertmanager handles alerts from Prometheus and sends notifications to Slack.

### Configuration
- Config file: `monitoring/alertmanager/alertmanager.yaml`
- Example alert rule (in `alert.rules.yaml`):
  ```yaml
  groups:
    - name: test_alerts
      rules:
        - alert: AlwaysOn
          expr: vector(1)  # Always fires
          for: 1m
          labels:
            severity: critical
          annotations:
            summary: "Test Alert"
            description: "This is a test alert to check Slack notifications."
  ```

### Slack Integration
Slack webhook URL is configured in `alertmanager.yaml`:
```yaml
receivers:
  - name: 'slack-notifications'
    slack_configs:
      - send_resolved: true
        channel: "#alerts"
        api_url: "https://hooks.slack.com/services/XXXX/YYYY/ZZZZ"
        title: "🔥 Alert: {{ .CommonLabels.alertname }}"
        text: "🚨 *{{ .CommonAnnotations.summary }}*\n{{ .CommonAnnotations.description }}"
```
### Verification
To check Alertmanager logs:
```bash
docker logs alertmanager --tail 50
```

To manually trigger a Slack alert:
```bash
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Test message from Alertmanager"}' \
  https://hooks.slack.com/services/XXXX/YYYY/ZZZZ
```

---

## Deployment
To start the full monitoring stack:
```bash
docker-compose up -d
```
To restart after configuration changes:
```bash
docker-compose down && docker-compose up -d
```

This ensures **Kafka JMX Exporter, Prometheus, Grafana, and Alertmanager** are all running correctly.

For more details, refer to `spark_streaming/README.md`. 🚀

