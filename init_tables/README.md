## **init_tables/README.md**

```markdown
# init_tables

This directory contains files for **registering external tables** (CSV/Delta) in **Spark Thrift Server** before the rest of the pipeline (e.g., dbt or training). It ensures that Spark Thrift recognizes your data (e.g., CSV files, Delta Lake paths) as tables.

---

## Overview

- **`Dockerfile`**: Builds a minimal container based on `bitnami/spark:3.3.2` (which includes `beeline`).
- **`init_tables.sh`**: A shell script that runs `beeline` commands to create external tables in Spark Thrift Server.
- **`requirements.txt` (Optional)**: If you need Python packages for any additional steps. If `beeline` alone suffices, you might not need this.

### Why we need this

In our PoC, we want CSV and/or Delta data sources to be **registered** as tables in Spark Thrift. Then downstream tools (like dbt, training scripts) can `SELECT * FROM those_tables`. This step is critical for your pipeline’s data availability.

---

## Usage

### 1. Docker Build & Run

Typically, you have something like this in your `docker-compose.yml`:

```yaml
init-tables:
  build:
    context: ./init_tables
    dockerfile: Dockerfile
  container_name: init-tables
  depends_on:
    - spark-thrift
  networks:
    - spark-network
```

Then run:

```bash
docker-compose up init-tables
```

This will:

1. Build the image using `init_tables/Dockerfile`.
2. Start the container.
3. Execute `init_tables.sh` → which calls `beeline` and registers tables in Spark Thrift Server.

### 2. `init_tables.sh` Example

A snippet inside `init_tables.sh` might look like:

```bash
beeline -u "jdbc:hive2://spark-thrift:10000/default" -n spark -p "" -e "
  USE default;

  CREATE TABLE IF NOT EXISTS vehicle_positions
    USING DELTA
    LOCATION 's3a://my-bucket/delta-lake/vehicle_positions';

  CREATE TABLE IF NOT EXISTS stops
    USING CSV
    OPTIONS (
      path 's3a://my-bucket/bronze/gtfs_data/stops.txt',
      header='true',
      inferSchema='true'
    );

  -- Add more CREATE TABLE statements if needed
"
```

These statements create external tables that other services (dbt or training) can query as `SELECT * FROM stops`, etc.

---

## Notes

- You only need to run `init_tables` once at the beginning of your pipeline (unless you’re recreating tables).
- `bitnami/spark:3.3.2` includes beeline, so you can directly run the above commands.
- Adjust the `s3a://my-bucket/` paths, table names, or CSV options as needed for your environment.
- If you have extra logic (e.g., copying data to MinIO or something else), you could add it into `init_tables.sh`.