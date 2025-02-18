# dbt

This directory contains the **dbt** project for transforming and modeling data stored in **Delta Lake** (MinIO) via **Spark Thrift Server**. When `dbt run` is executed, dbt uses **method: thrift** to connect to Spark, allowing you to write SQL models that operate on streaming/batch data ingested into Delta Lake.

---

## Overview

1. **Spark Thrift Server**  
   - Provides a JDBC endpoint (`spark-thrift:10000`) that dbt can query.  
   - The underlying data is stored in **MinIO** (`s3a://my-bucket/delta-lake/...`) as Delta Lake tables, typically populated by **Spark Streaming** from Kafka.

2. **dbt (Docker Container)**  
   - A container that runs `dbt run` or other commands, referencing a **`profiles.yml`** with `method: thrift`.  
   - Models (`.sql` files in `models/`) define transformations and views/tables in Spark.

3. **Profiles & Models**  
   - **`profiles.yml`** sets `host: spark-thrift`, `port: 10000`, etc. for `type: spark`.  
   - **`models/`** directory holds `.sql` files describing transformations (e.g., `my_first_model.sql`).  
   - The final outputs (views or tables) are created in Spark’s `default` schema or as configured in `schema:`.

---

## Directory Structure

```
dbt/
├── dbt_project.yml
├── profiles.yml
├── models/
│   └── my_first_model.sql
└── README.md   <-- (this file)
```

- **`dbt_project.yml`**  
  Defines the dbt project name, version, and `model-paths`.
- **`profiles.yml`**  
  Configures how dbt connects to Spark (method: thrift). Also sets schema, host, port, etc.  
- **`models/`**  
  Contains SQL-based transformations. For example, `my_first_model.sql`.

---

## Getting Started

### 1. Docker Compose

If you are using the repository’s main `docker-compose.yml`, **dbt** is defined as a service. For example:

```yaml
dbt:
  image: ghcr.io/dbt-labs/dbt-spark:1.9.latest
  volumes:
    - ./dbt:/dbt
  working_dir: /dbt
  command: ["run", "--profiles-dir=/dbt"]
  depends_on:
    - spark-thrift
  networks:
    - spark-network
```

1. **Up All Services**  
   ```bash
   docker-compose up -d
   ```
   This starts Spark Thrift Server, Kafka, MinIO, Spark Streaming, etc.  
2. **Check Logs**  
   ```bash
   docker-compose logs -f dbt
   ```
   If `dbt run` connects successfully, you’ll see `Completed successfully` and `PASS=1 WARN=0 ERROR=0...` messages for any models.

### 2. Manual dbt Commands

- **Open a shell in the dbt container** (instead of auto-running `dbt run`):
  ```bash
  docker-compose run --entrypoint bash dbt
  # inside container:
  dbt debug --profiles-dir=.
  dbt run --profiles-dir=.
  dbt test --profiles-dir=.
  ```
- This helps if you want to manually compile or test new models.

---

## Configuration

### `profiles.yml` Example

```yaml
realtime_mlops:
  target: dev
  outputs:
    dev:
      type: spark
      method: thrift
      host: "spark-thrift"
      port: 10000
      user: "spark"
      pass: ""
      schema: "default"
```

- **`type: spark`** + **`method: thrift`**: Uses Spark Thrift Server.  
- **`host: "spark-thrift"`** + **`port: 10000`**: Must match container/service definitions in Docker Compose.  
- **`schema: "default"`**: dbt’s default schema in Spark.  

### `dbt_project.yml` Example

```yaml
name: "realtime_mlops"
version: "1.0"
config-version: 2

profile: "realtime_mlops"
model-paths: ["models"]  # replace 'source-paths' with 'model-paths'
```

- This instructs dbt to look in the `models/` directory for `.sql` transformations.

---

## Models & Usage

- **`models/my_first_model.sql`** (example):
  ```sql
  -- This is a simple dbt model
  SELECT
    1 AS test_col
  ```
- When `dbt run` executes, it creates or replaces a view/table named `default.my_first_model` in Spark.

**Tip**: If you want to reference data in Delta Lake, you can do something like:
```sql
SELECT *
FROM delta.`s3a://my-bucket/delta-lake/stream_data`
```
Spark Thrift Server accesses the underlying **MinIO** path via `spark.hadoop.fs.s3a.*` config (set on the Thrift Server side).

---

## Troubleshooting

1. **Connection Refused (443)**  
   - If you see `Could not connect to ... 443`, you might have omitted `port: 10000`. Ensure `profiles.yml` is correct.
2. **Initial Startup Fail**  
   - dbt might fail on the first run if Spark Thrift Server isn’t fully ready. A second run often succeeds.
3. **Delta Lake Access Errors**  
   - Thrift Server needs `spark.hadoop.fs.s3a.access.key` etc. Make sure those are set in the Thrift container environment.

---

## Next Steps

- **Extend Models**  
  Create additional `.sql` files under `models/` to transform data, join with other tables, or create aggregated views.
- **`dbt test`** & Documentation  
  Add YAML tests (not_null, unique, etc.) or run `dbt docs generate` for documentation.  
- **Machine Learning**  
  Data in Delta Lake is then used for ML training (Phase 3/4). Tools like MLflow can be introduced for experiment tracking.
- **Deployment**  
  Eventually, dbt can be integrated into CI/CD pipelines or run on a schedule to keep data transformations fresh.

---

## Summary

Within **`202502_realtime_mlops`**, the **dbt** directory holds everything needed for **SQL-based transformations** on **Spark** (backed by MinIO as Delta Lake). By connecting via **Spark Thrift Server** (`method: thrift`), you can run `dbt run` in a Docker container, ensuring consistent environment and easy orchestration alongside other services (Kafka, Spark Streaming, etc.).