# Spark Streaming

This directory contains the code for the **real-time data processing** job using **Spark Streaming**. The job reads data from a **Kafka** topic, parses/transforms it, and writes the processed data into **Delta Lake** (stored on **MinIO**). Once data lands in Delta, it can be queried/transformed by **dbt** (through Spark Thrift Server) or used for downstream analytics and ML tasks.

---

## Overview

This **Spark Streaming** component typically runs in a **Docker container** alongside:
- **Kafka** & **ZooKeeper** (for real-time data ingestion)
- **MinIO** (as an S3-compatible storage for Delta Lake)
- **Spark Master/Worker** (to provide the cluster runtime for streaming)
- **Spark Thrift Server** (so dbt can query Spark via JDBC/Thrift)

Hence, the streaming job:

1. **Subscribes** to a Kafka topic (e.g., `dev_topic`)  
2. **Processes** incoming JSON or Protobuf-based messages  
3. **Writes** the result to a **Delta Lake** table at `s3a://my-bucket/delta-lake/...` (MinIO)  
4. **Exposes** logs that can be monitored alongside other containers (Prometheus/Grafana optional)

---

## Directory Structure

```
spark_streaming/
├── Dockerfile                  # Docker build for the Spark Streaming container
├── requirements.txt            # Python dependencies (if using custom PySpark or libraries)
├── spark_streaming.py          # Main Spark Streaming script
└── README.md                   # This file
```

- **`spark_streaming.py`**: The primary script that reads from Kafka, processes data, and writes to Delta Lake.  
- **`Dockerfile`**: Containerizes the streaming job, often including Spark + Delta dependencies.  
- **`requirements.txt`** (optional): If you install custom Python dependencies in the streaming container.

---

## Prerequisites

1. **Docker Compose**  
   Ensure Docker Compose is installed. This project uses `docker-compose.yml` in the repository root to orchestrate all services.

2. **Kafka**  
   A running Kafka service (e.g. via Docker Compose) with a topic named `dev_topic`.  
   - Check the main `docker-compose.yml` for Kafka definitions.

3. **MinIO (S3-compatible store)**  
   Provides Delta Lake storage at `s3a://my-bucket/`. Credentials (`MINIO_ROOT_USER`/`MINIO_ROOT_PASSWORD`) are usually passed as environment variables or `spark-submit --conf`.

4. **Spark Master/Worker**  
   The streaming job uses Spark’s cluster mode or client mode via `spark://spark-master:7077` (defined in Docker Compose).

5. **Delta Lake Dependencies**  
   Typically set via Dockerfile `SPARK_PACKAGES` environment variable (`io.delta:delta-core_2.12:x.x.x`).  

---

## Running the Streaming Job

### 1. Build & Start via Docker Compose

From the **project root**, run:
```bash
docker-compose up -d
```
This brings up:
- **Kafka + ZooKeeper**
- **Spark Master/Worker**
- **MinIO**  
- **Spark Thrift Server**
- **spark_streaming** container (running `spark_streaming.py`)

### 2. Check Logs

```bash
docker-compose logs -f spark_streaming
```
You should see log output indicating that the Spark job:
- Connects to Kafka at `kafka:9092`
- Subscribes to `dev_topic`
- Writes Delta files to `s3a://my-bucket/delta-lake/...` in MinIO

### 3. Verify Data in MinIO

1. **MinIO Console**: [http://localhost:9001](http://localhost:9001) (default credentials: `admin / admin123`)
2. **Check `my-bucket/delta-lake/`**:  
   You should see `_delta_log/` or partition folders for Delta Lake.

### 4. Configuration & Customization

- **Kafka Broker**: Typically set via env var `KAFKA_BROKER` or inside `spark_streaming.py`.  
- **Topic**: `KAFKA_TOPIC`, defaulting to `dev_topic`.  
- **Delta Path**: `DELTA_LAKE_PATH`, e.g. `s3a://my-bucket/delta-lake`.  
- **MinIO Credentials**: Passed to Spark as `MINIO_ROOT_USER`, `MINIO_ROOT_PASSWORD`. The Dockerfile or Compose sets `spark.hadoop.fs.s3a.*` accordingly.

---

## Monitoring & Alerting

1. **Spark Master UI**  
   Visit [http://localhost:8080](http://localhost:8080) for Spark Master details (workers, jobs, etc.).  
   Optionally, the Streaming UI might appear at `[host machine]:4040` if exposed.

2. **Prometheus & Grafana** (Optional)  
   - If your Compose file includes metrics scraping, you can see streaming metrics in Grafana dashboards.  
   - [http://localhost:3000](http://localhost:3000) for Grafana, [http://localhost:9090](http://localhost:9090) for Prometheus.

3. **Alerting**  
   If alert rules are configured (e.g., in Alertmanager), you can get Slack/email notifications on job failures or high latency.

---

## Troubleshooting

- **No Data in MinIO**: Check `docker-compose logs -f spark_streaming`. Possibly missing MinIO credentials or incorrect `s3a://...` path.  
- **Kafka Connection Issues**: Ensure `kafka` is up, and the topic exists.  
- **Delta Write Errors**: Confirm the Dockerfile includes the right Delta packages.  
- **UI Not Accessible**: Verify port mappings in `docker-compose.yml`.

---

## Future Enhancements

- **Windowed Aggregations**: Implement time-based or session-based windows in the streaming job for more complex analytics.  
- **Schema Enforcement**: Use Delta Lake’s schema evolution or enforcement if the incoming data structure changes.  
- **Stateful Operations**: Maintain state across records to enable real-time analytics like running counts or intermediate aggregates.

---

## Summary

This **Spark Streaming** module bridges **Kafka** to **Delta Lake** on **MinIO**, enabling a robust, real-time ingestion pipeline. Data can then be transformed further by **dbt** (via Spark Thrift Server) or used for machine learning. Refer to the main project README for broader architecture details (Kafka Producer, Thrift Server, dbt setup, etc.).