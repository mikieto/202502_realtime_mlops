# Spark Thrift Server

This directory contains the resources (e.g., `Dockerfile`) needed to build and run a **Spark Thrift Server** container. The Thrift Server provides a **JDBC interface** so that **dbt** (and other SQL clients) can query data stored in **Delta Lake** on **MinIO**.

---

## Overview

1. **Spark Thrift Server + MinIO**  
   - The Dockerfile installs Spark, Delta Lake dependencies, and sets `spark.hadoop.fs.s3a.*` configs so Spark can read/write data on MinIO (`s3a://my-bucket/...`).

2. **dbt Integration**  
   - dbt (`method: thrift`) connects to this Thrift Server on port `10000`.  
   - SQL queries are executed on Spark’s driver, which accesses Delta tables in **MinIO**.

3. **Docker Compose**  
   - Typically, `docker-compose.yml` includes a `spark-thrift` service using the Dockerfile from this folder.  
   - The service depends on **Spark Master**, **MinIO**, etc., to ensure it can start properly.

---

## Directory Structure

```
spark_thrift/
├── Dockerfile
└── README.md   <-- this file
```

- **`Dockerfile`**  
  Builds a custom Spark Thrift Server image, pulling `bitnami/spark` as a base and installing `io.delta:delta-core`, plus Kafka packages if needed.  
  It also configures environment variables (like `MINIO_ENDPOINT`, `MINIO_ROOT_USER`, `MINIO_ROOT_PASSWORD`) so Spark can read/write `s3a://`.

---

## Dockerfile Details

An example `Dockerfile` might include:

```dockerfile
FROM bitnami/spark:3.3.2

ENV SPARK_PACKAGES="org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.2,io.delta:delta-core_2.12:2.3.0,io.delta:delta-storage:2.3.0"

# These can be overridden by docker-compose.yml environment:
ENV MINIO_ENDPOINT=http://minio:9000
ENV MINIO_ROOT_USER=admin
ENV MINIO_ROOT_PASSWORD=admin123

CMD spark-submit --packages "$SPARK_PACKAGES" \
  --class "org.apache.spark.sql.hive.thriftserver.HiveThriftServer2" \
  --conf "spark.hadoop.fs.s3a.endpoint=${MINIO_ENDPOINT}" \
  --conf "spark.hadoop.fs.s3a.access.key=${MINIO_ROOT_USER}" \
  --conf "spark.hadoop.fs.s3a.secret.key=${MINIO_ROOT_PASSWORD}" \
  --conf "spark.hadoop.fs.s3a.path.style.access=true" \
  "/opt/bitnami/spark/jars/spark-thrift-server-3.3.2.jar"
```

**Key points**:

- **`SPARK_PACKAGES`**: Includes **Delta Lake** and possibly **Kafka** dependencies.  
- **MinIO Credentials**: Passed via environment variables, then used in `spark-submit` conf.  
- **`spark.hadoop.fs.s3a.path.style.access=true`** allows MinIO path-based addressing.

---

## Usage via Docker Compose

1. **Definition in `docker-compose.yml`**  
   ```yaml
   spark-thrift:
     build:
       context: ./spark_thrift
     environment:
       - SPARK_MASTER_URL=spark://spark-master:7077
       - MINIO_ENDPOINT=http://minio:9000
       - MINIO_ROOT_USER=admin
       - MINIO_ROOT_PASSWORD=admin123
     depends_on:
       - spark-master
       - minio
     ports:
       - "10000:10000"
     networks:
       - spark-network
   ```
2. **Startup**  
   ```bash
   docker-compose up -d
   ```
   - Thrift Server container will run on port `10000`, waiting for dbt or other JDBC clients.

3. **dbt Connection**  
   - In `dbt/profiles.yml`:
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
   - dbt `run` or `debug` will contact the Thrift Server at `spark-thrift:10000`.

---

## Verifying Connectivity

- **Check Thrift Server logs**:  
  ```bash
  docker-compose logs -f spark-thrift
  ```
  Look for lines like `Starting Thrift CLIService... Listening on port 10000`.
- **dbt logs**:
  ```bash
  docker-compose logs -f dbt
  ```
  If successful, you’ll see queries like `CREATE OR REPLACE VIEW default.my_first_model` running via Thrift.

---

## Troubleshooting

1. **Connection Refused**  
   - Possibly the Thrift Server isn’t fully up when dbt tries to connect. Use `depends_on` or wait a few seconds and retry.
2. **MinIO Access Errors**  
   - Make sure `spark.hadoop.fs.s3a.endpoint`, `access.key`, and `secret.key` are set.  
   - Confirm `spark.hadoop.fs.s3a.path.style.access=true` if you’re using path-style with MinIO.
3. **Delta Not Found**  
   - Ensure `io.delta:delta-core` is specified in `SPARK_PACKAGES`, or you’ll see “Table not found or unknown format: delta.”

---

## Future Enhancements

- **Security**: TLS or Kerberos for Spark Thrift Server.  
- **Performance Tuning**: Adjust memory, CPU, or concurrency settings for high-volume queries.  
- **Cloud Migration**: Replace MinIO with real S3, or host the Thrift Server on AWS EMR/Databricks.

---

## Summary

`spark_thrift/` provides a **Dockerfile** and supporting environment to run **Spark Thrift Server** with **Delta Lake** on **MinIO**. This service is crucial for **dbt** (and other SQL tools) to query or transform data in Spark. By orchestrating all containers via Docker Compose, you have an **end-to-end** real-time data pipeline: **Kafka** → **Spark Streaming** → **Delta (MinIO)** → **Spark Thrift** → **dbt**.