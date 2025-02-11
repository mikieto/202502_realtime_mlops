# Deployment Guide

This document explains how to set up and deploy the **202502_realtime_mlops** project, covering all major phases: data ingestion (Kafka), real-time processing (Spark Streaming & Delta Lake), and monitoring & alerting (Prometheus, Grafana, and Alertmanager).

---

## Prerequisites

Before starting, ensure you have the following installed:
- **Docker & Docker Compose** (Ensure Docker Desktop is running, WSL2 backend recommended for Windows)
- **Python 3 & Virtual Environment**
- **Git** (For cloning the repository)

---

## Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/202502_realtime_mlops.git
cd 202502_realtime_mlops
```

---

## Phase 1: Kafka-based Data Ingestion

### Step 2: Start Kafka & ZooKeeper

```bash
docker-compose up -d zookeeper kafka
```

Verify the containers are running:
```bash
docker ps
```

### Step 3: Create Kafka Topics (If Needed)

If auto-topic creation is disabled, manually create a topic:
```bash
docker exec -it kafka kafka-topics.sh --create --topic dev_topic --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1
```

### Step 4: Start Kafka Producer

Navigate to the producer directory:
```bash
cd producer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python kafka_producer.py
```

---

## Phase 2: Spark Streaming & Delta Lake

### Step 5: Start Spark Streaming

Navigate to Spark Streaming directory:
```bash
cd ../spark_streaming/src
python streaming_main.py
```

The script will:
- Read from Kafka (`dev_topic`)
- Process and transform incoming data
- Store it in Delta Lake (`delta/dev`)

Verify the data was written:
```python
from pyspark.sql import SparkSession
spark = SparkSession.builder.getOrCreate()
df = spark.read.format("delta").load("/home/<username>/projects/202502_realtime_mlops/delta/dev")
df.show()
```

---

## Phase 3: Monitoring & Alerting

### Step 6: Start Prometheus, Grafana, & Alertmanager

```bash
docker-compose up -d prometheus grafana alertmanager node-exporter kafka-exporter
```

Verify containers:
```bash
docker ps
```

### Step 7: Configure Grafana Dashboards

1. Open Grafana: [http://localhost:3000](http://localhost:3000)
2. Login (default: `admin/admin`)
3. Add Prometheus as a Data Source (`http://prometheus:9090`)
4. Import Kafka & Spark dashboards (JSON templates in `grafana/dashboards/`)

### Step 8: Verify Prometheus & Alertmanager

- Prometheus UI: [http://localhost:9090](http://localhost:9090)
- Alertmanager UI: [http://localhost:9093](http://localhost:9093)
- Check alerts:
```bash
curl -X GET http://localhost:9090/api/v1/alerts | jq .
```

---

## Summary

This guide covered:
- **Phase 1:** Kafka-based data ingestion
- **Phase 2:** Spark Streaming & Delta Lake storage
- **Phase 3:** Monitoring & alerting with Prometheus & Grafana

Next steps: Extend Delta Lake for ML model training and inference (Phase 4).

For further details, refer to `docs/architecture.md` and `docs/troubleshooting.md`. If issues arise, restart containers and verify logs:
```bash
docker-compose logs -f
```

