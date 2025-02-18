# 202502_realtime_mlops

This repository demonstrates a **real-time data pipeline** using **Kafka**, **Spark Streaming**, **Delta Lake (MinIO)**, **Spark Thrift Server**, and **dbt**. The PoC is designed to highlight **streaming data ingestion**, **data transformations** (via Spark/dbt), and **Delta Lake** persistence on an S3-compatible store (MinIO). 

Future steps (MLflow, FastAPI, monitoring, etc.) can be easily integrated on top of this setup.

---

## Table of Contents

1. [Overview](#overview)  
2. [Setup Instructions](#setup-instructions)  
3. [Running the Application](#running-the-application)  
4. [Architecture at a Glance](#architecture-at-a-glance)  
5. [Documentation](#documentation)  
6. [License](#license)

---

## Overview

- **Kafka/ZooKeeper**: Ingest real-time data (e.g., vehicle location updates).  
- **Spark Master/Worker**: Provides distributed compute for streaming/batch jobs.  
- **Spark Streaming**: Reads from Kafka, writes to **Delta Lake** (on MinIO).  
- **MinIO**: An S3-compatible object store for Delta Lake data.  
- **Spark Thrift Server**: Exposes a JDBC interface so dbt can query data in Spark.  
- **dbt**: Executes SQL models (`method: thrift`) to transform/query Delta Lake data via Spark Thrift Server.  

This PoC is primarily container-based (Docker Compose), allowing you to spin up the entire environment locally for demonstration and testing.

---

## Setup Instructions

1. **Local Development Environment**  
   - Install [Docker Desktop](https://www.docker.com/products/docker-desktop) (WSL2 backend is recommended for Windows users).
   - Clone the repository:
     ```bash
     git clone https://github.com/your-username/202502_realtime_mlops.git
     cd 202502_realtime_mlops
     ```
   - Ensure Docker Compose is available (either Docker Compose v2 or v1).  
   - (Optional) Customize environment variables in `.env` or in `docker-compose.yml` if you want to change MinIO credentials, etc.

2. **Directory Structure** (simplified)
   ```
   202502_realtime_mlops/
   ├── docker-compose.yml
   ├── dbt/
   │   ├── dbt_project.yml
   │   ├── profiles.yml
   │   └── models/
   ├── kafka_producer/
   │   └── kafka_producer.py
   ├── spark_streaming/
   │   ├── Dockerfile
   │   └── spark_streaming.py
   ├── spark_thrift/
   │   └── Dockerfile
   └── ...
   ```

3. **Updating the Configs**  
   - `spark_thrift/Dockerfile` contains the Spark packages for **Delta** and **Kafka** plus `spark.hadoop.fs.s3a.*` for MinIO.  
   - `dbt/profiles.yml` uses `method: thrift` to connect to `spark-thrift:10000`.  
   - `spark_streaming.py` writes to `s3a://my-bucket/delta-lake`.  
   - Kafka, ZooKeeper, and MinIO ports are mapped in `docker-compose.yml`.  

---

## Running the Application

1. **Start All Services**  
   ```bash
   docker-compose up -d
   ```
   This spins up ZooKeeper, Kafka, Spark Master/Worker, **MinIO**, **Spark Thrift Server**, **dbt**, and any other containers defined.  
   - **Note**: The `dbt` container may attempt to run `dbt run` on startup, which can fail if the Spark Thrift Server is not fully ready. Subsequent attempts will succeed.

2. **Check Logs**  
   - **Kafka**: `docker-compose logs -f kafka`  
   - **Spark Streaming**: `docker-compose logs -f spark_streaming`  
   - **Spark Thrift**: `docker-compose logs -f spark-thrift`  
   - **dbt**: `docker-compose logs -f dbt`  

   You should see `PASS=1 WARN=0 ERROR=0` if `dbt run` completes successfully after Spark Thrift Server is ready.

3. **Kafka Producer**  
   - A containerized or manual script that sends data to Kafka on `kafka:9092`.  
   - Example: `kafka_producer/kafka_producer.py` for streaming location data into `dev_topic`.

4. **Spark Streaming**  
   - The `spark_streaming` container runs `spark_streaming.py` automatically, reading from Kafka `dev_topic` and writing to `Delta Lake` (`s3a://my-bucket/delta-lake`) on MinIO.

5. **Delta Lake on MinIO**  
   - Visit the MinIO console at [http://localhost:9001](http://localhost:9001) (default creds `admin:admin123`).
   - Check that `my-bucket` has the `delta-lake/` path with `_delta_log/`.

6. **dbt (method: thrift)**  
   - `dbt` queries and transforms data in Spark via the Thrift Server. On first run, it creates or replaces a model (e.g., `my_first_model`).  
   - If you need to manually run additional commands:
     ```bash
     # One-off approach (starts a container with bash instead of dbt run):
     docker-compose run --entrypoint bash dbt

     # Then inside the container:
     dbt debug --profiles-dir=.
     dbt run --profiles-dir=.
     dbt test --profiles-dir=.
     ```

---

## Architecture at a Glance

```
               +-------------+
               |  Kafka      |
  Producer --> |  (9092)     |
               +-----+-------+
                     |
             Spark Streaming
                   +----> Writes to Delta Lake (s3a://my-bucket/delta-lake)
                     |
             +-------v-------+
             |  MinIO (S3)   |
             |  (9000,9001)  |
             +-------+-------+
                     |
   dbt + Thrift -> +---+--+---+  
   [method: thrift]    |  Spark Master/Worker
                       +----------------------> Query data
```

1. **Kafka** for streaming ingestion.  
2. **Spark Streaming** reads from Kafka, writes Delta to MinIO.  
3. **MinIO** simulates S3 for Delta Lake storage.  
4. **Spark Thrift Server** provides a JDBC interface so dbt can run SQL transformations.  

---

## Documentation

Further details about architecture, deployment, and component-level info can be found in the `docs/` folder (if present). Key documents might include:

- **architecture.md:** Detailed design of components.  
- **deployment.md:** Additional instructions for local vs. cloud.  
- **spark_streaming/README.md:** Specifics on the streaming job.  
- **dbt/README.md:** Info on models, profiles, and usage.  

---

## License

This project is licensed under the MIT License. For details, see [LICENSE](LICENSE).

---

**For questions or to contribute,** please open an Issue or Pull Request. Updates to the PoC—such as MLflow integration, FastAPI services, or monitoring (Prometheus, Grafana)—will be tracked in future commits.
