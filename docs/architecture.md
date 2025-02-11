# Architecture Overview

## Phase 1: Real-Time Data Ingestion

### Overview

Phase 1 of the **202502_realtime_mlops** project focuses on building a real-time data ingestion pipeline using Apache Kafka. The primary goal is to demonstrate the ability to set up a robust streaming data collection system that ingests GTFS-RT data (e.g., vehicle information) and makes it available for downstream processing.

### Components

- **Kafka Cluster**  
  - **Kafka Broker:** Handles the reception, storage, and distribution of messages.  
  - **ZooKeeper:** Manages the Kafka cluster’s metadata and coordination.

- **Kafka Producer**  
  - A Python-based application that fetches GTFS-RT data from an external API (GTFS-RT feed), decodes the Protobuf payload, converts it to JSON, and sends it to a Kafka topic (e.g., `vehicle_topic` or `dev_topic`).

### Design Rationale

- **Modularity**  
  The system is designed with clear separation between data ingestion (Kafka), data processing (to be implemented in later phases), and eventual model serving.

- **Scalability**  
  Using Docker Compose for local development ensures that the setup can be easily scaled and later migrated to container orchestration platforms (e.g., Kubernetes).

- **Reproducibility**  
  A standardized environment using Docker Desktop with a WSL2 backend guarantees that the setup can be reproduced across different machines.

### Diagram (Phase 1)

```
[GTFS-RT API] --> [Kafka Producer (Python)] --> [Kafka Broker] <---> [ZooKeeper]
```

---

## Phase 2: Real-Time Data Processing (Spark Streaming & Delta Lake)

### Overview

In Phase 2, we extend the architecture to include **real-time data processing** using Spark Streaming. The data ingested by Kafka (from the Producer in Phase 1) is now read by a Spark Streaming job, transformed if necessary, and then written to **Delta Lake** for persistent storage and subsequent analytics or machine learning tasks (in Phase 3 and beyond).

### Components

- **Spark Streaming (ETL Job)**  
  - A PySpark application that continuously reads messages from a Kafka topic (e.g., `dev_topic`), parses them (JSON), and writes them to a Delta Lake table.  
  - Utilizes a **checkpoint directory** for fault tolerance and exactly-once/at-least-once semantics (depending on the configuration).

- **Delta Lake**  
  - An open-source storage layer for reliable data lakes.  
  - Stores streaming data in an append-only fashion, enabling ACID transactions, versioning, and time-travel queries.  
  - In the local development setup, Delta Lake data is written to a directory (e.g., `/home/<username>/projects/202502_realtime_mlops/delta/dev`), which can also be containerized or migrated to a cloud-based storage system in future phases.

### Data Flow

1. **Kafka Producer** fetches GTFS-RT data and sends JSON payloads to Kafka (`dev_topic`).  
2. **Spark Streaming** consumes messages from the `dev_topic`, parses them, and applies any necessary transformations (filtering, JSON parsing, schema validation, etc.).  
3. **Delta Lake** receives the processed data from Spark, stored in a specified path. A separate **checkpoint directory** ensures the streaming job can recover state upon restarts.

### Diagram (Phase 2)

```
                Phase 1 (Existing)
[GTFS-RT API] --> [Kafka Producer] --> [Kafka Broker] <---> [ZooKeeper]
                                    |       ^
                                    |       |
                                    v       |
                              Phase 2 (New)
                             [Spark Streaming]
                                    |
                                    v
                              [Delta Lake]
```

### Key Considerations

- **Version Compatibility**  
  Spark Streaming and Delta Lake must be on compatible versions. Ensuring PySpark and Delta Lake packages match the local Spark version is critical to avoid runtime errors.

- **Checkpointing & Fault Tolerance**  
  Spark Streaming uses a dedicated checkpoint directory (e.g., `/home/<username>/projects/202502_realtime_mlops/delta_checkpoints/dev`) to maintain progress and enable seamless recovery if the job restarts.

- **Windows + WSL2 Environment**  
  - Spark Streaming and Delta Lake run inside WSL2 or Docker containers.  
  - The Kafka cluster can also run in Docker on Windows.  
  - Both local file paths and Docker volumes need to be carefully managed to avoid path-mismatch issues (`/mnt/...` vs. `C:/...`).

### Next Steps

- **Phase 3: Machine Learning Model Training & Management**  
  Phase 3 will leverage the Delta Lake data to train ML models. This includes setting up MLflow (or equivalent) for experiment tracking, hyperparameter tuning, and model versioning in a reproducible fashion.

---

## Phase 3: Monitoring and Alerting (Prometheus, Grafana, and Alertmanager)

### Overview

Phase 3 introduces system observability by integrating **Prometheus**, **Grafana**, and **Alertmanager** to monitor Kafka, Spark Streaming, and overall system health.

### Components

- **Prometheus**  
  - Collects metrics from Kafka, Spark, and system resources (via Node Exporter and JMX Exporter).
  - Stores time-series data for performance analysis and anomaly detection.

- **Grafana**  
  - Visualizes Prometheus metrics in real-time dashboards.
  - Configured with prebuilt dashboards for Kafka, Spark, and system metrics.

- **Alertmanager**  
  - Sends alerts (e.g., high error rates, low throughput) to Slack.
  - Uses predefined alert rules stored in `alert.rules.yml`.

### Diagram (Phase 3)

```
[Prometheus] <-- [Kafka JMX Exporter]  
            |  
            v  
       [Grafana] --> [User Dashboard]  
            |  
            v  
   [Alertmanager] --> [Slack Alerts]
```

### Summary

- **Phase 1** established a Kafka-based data ingestion pipeline.  
- **Phase 2** introduced Spark Streaming and Delta Lake for real-time data processing and persistent storage.  
- **Phase 3** implemented monitoring and alerting using Prometheus, Grafana, and Alertmanager.  
- **Next steps:** Leverage Delta Lake for ML training and API-based model inference.

By incrementally building out these components, the **202502_realtime_mlops** project demonstrates end-to-end skills in real-time data ingestion, processing, monitoring, and MLOps orchestration.

