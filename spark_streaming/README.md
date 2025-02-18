---

# Spark Streaming

This directory contains the code for our real-time data processing job. The job reads data from a Kafka topic, processes it, and writes the processed data into Delta Lake. Additionally, monitoring and alerting mechanisms are in place to ensure system reliability.

---

## Overview

The system consists of three main parts:

1. **Data Ingestion (Phase 1):**
   - A Kafka Producer collects real-time data (e.g., from a GTFS-RT API) and sends it to a Kafka topic (e.g., `dev_topic`).

2. **Data Processing (Phase 2):**
   - A Spark Streaming job reads data from Kafka, processes it (e.g., parsing JSON), and writes it into Delta Lake.
   - Delta Lake ensures reliable storage with support for ACID transactions and versioning.

3. **Monitoring and Alerting (Phase 3):**
   - Metrics such as processing latency and errors are monitored via **Prometheus** and visualized in **Grafana**.
   - Alert rules trigger **Slack notifications** when anomalies (e.g., processing failures) are detected.

---

## Directory Structure

```
spark_streaming/
├── src/
│   ├── streaming_main.py         # The main Spark Streaming application.
│   ├── streaming_config.py       # Reads settings from environment and YAML files.
│   ├── config_dev.yaml           # Example configuration file for the development environment.
│   ├── config_prod.yaml          # Example configuration file for production (if needed).
├── monitoring/
│   ├── prometheus.yaml           # Prometheus configuration for monitoring Spark Streaming.
│   ├── alert.rules.yaml          # Alert rules for detecting processing failures.
│   ├── grafana_dashboards/       # Preconfigured Grafana dashboards.
├── requirements.txt              # Python package dependencies.
├── Dockerfile                    # Dockerfile for containerizing the Spark job.
└── README.md                     # This file.
```

---

## Prerequisites

Before running the Spark Streaming job, ensure that:

### **1. Python and PySpark**
   - A Python virtual environment is set up and activated.
   - PySpark (version 3.4.1 recommended) is installed.
   - Delta Lake (e.g., `delta-spark 2.4.0`) is installed and compatible with your PySpark version.

### **2. Kafka Cluster**
   - Kafka and ZooKeeper are running (e.g., via Docker Compose).
   - A Kafka topic named `dev_topic` has been created (if auto-topic creation is disabled, create it manually).

### **3. Monitoring Stack**
   - Prometheus, Alertmanager, and Grafana are running (via Docker Compose).
   - `prometheus.yaml` includes the necessary scrape job for Spark Streaming metrics.
   - Alert rules in `alert.rules.yaml` are configured to detect failures.
   - Grafana dashboards are configured for visualization.

---

## How to Run

### **1. Start Kafka Producer**
Run the Kafka Producer to send messages to the `dev_topic`.

### **2. Start the Spark Streaming Job**
Navigate to `spark_streaming/src` and run:
```bash
python streaming_main.py
```
This starts the Spark job, which:
   - Reads settings from `.env` and `config_dev.yaml`
   - Connects to Kafka on `localhost:9092`
   - Subscribes to `dev_topic`
   - Processes incoming JSON data
   - Writes the processed data to Delta Lake
   - Exposes metrics for Prometheus monitoring

### **3. Monitor Spark Streaming Metrics**
#### **View Metrics in Prometheus**
Access Prometheus at:
```
http://localhost:9090
```
Run the following query to check processing status:
```promql
rate(spark_streaming_processed_records_total[5m])
```

#### **View Metrics in Grafana**
Access Grafana at:
```
http://localhost:3000
```
Dashboards for Spark Streaming metrics should be preloaded.

### **4. Trigger and Test Alerts**
Alert rules are configured in `alert.rules.yaml`. To test Slack notifications:
1. Introduce an error in `streaming_main.py` (e.g., wrong Kafka topic).
2. Restart the job and monitor Prometheus for alert triggers.
3. Slack notifications should be sent upon failure.

---

## Troubleshooting

- **Kafka Connection Errors:** Ensure Kafka is running and `KAFKA_BROKER` in `config_dev.yaml` is correctly set.
- **Delta Lake Write Issues:** Verify the output directory exists and has proper permissions.
- **Prometheus Not Scraping Metrics:** Check `prometheus.yaml` to confirm Spark Streaming is included in the scrape jobs.
- **Slack Alerts Not Triggering:** Confirm Alertmanager is running and the `alert.rules.yaml` contains valid alert conditions.

---

## Summary

This component of the project enables real-time data processing using Kafka and Spark Streaming. Monitoring and alerting ensure system reliability, making it easier to detect and respond to failures. This sets the foundation for machine learning and further data processing stages.

For any questions or further troubleshooting, refer to the documentation or seek additional support.

