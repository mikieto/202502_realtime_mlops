# Kafka Producer

This **Kafka Producer** component is responsible for fetching real-time GTFS-RT (vehicle position) data from an external API, decoding the Protobuf payload, converting it to JSON, and sending the data to a Kafka topic. It fits into the **`202502_realtime_mlops`** project as the primary **data ingestion** source for the subsequent streaming pipeline (Spark Streaming → Delta Lake (MinIO) → Spark Thrift Server → dbt).

## Overview

- **Project**: `202502_realtime_mlops`
- **Component**: `kafka_producer`
- **Data Source**: GTFS-RT Vehicle API
- **Kafka Topic**: `dev_topic` (configurable)

This producer can be **containerized via Docker Compose** or run locally using Python. It periodically polls the GTFS-RT endpoint, transforms the data into JSON, and produces messages to Kafka for **downstream Spark processing**.

---

## Features

- **Data Fetching**  
  Periodically fetches GTFS-RT data from the configured API endpoint (`VEHICLE_URL`).

- **Protobuf Decoding**  
  Uses a Protobuf module (`gtfs_realtime_pb2`) to decode raw GTFS-RT data into a Python object.

- **JSON Transformation**  
  Converts the Protobuf message into JSON for consumption by downstream services (e.g., Spark Streaming).

- **Kafka Integration**  
  Sends JSON payloads to the specified **Kafka topic** (`dev_topic`) using the Python `kafka-python` library (or any other configured library).

- **Configurable Polling Interval**  
  Can be set to fetch new data every X seconds (default is typically 60s).

---

## Running the Producer (Containerized Approach)

### 1. Docker Compose

In the main `docker-compose.yml` (project root), there is a `kafka_producer` service definition. For example:

```yaml
services:
  kafka_producer:
    build:
      context: ./kafka_producer
    environment:
      - VEHICLE_URL=https://api-public.odpt.org/api/v4/gtfs/realtime/toei_odpt_train_vehicle
      - KAFKA_BROKER=kafka:9092
      - KAFKA_TOPIC=dev_topic
    depends_on:
      - kafka
    networks:
      - spark-network
```

1. From the **project root**, start all services (including Kafka, ZooKeeper, Spark, etc.):
   ```bash
   docker-compose up -d
   ```
2. Check logs for `kafka_producer`:
   ```bash
   docker-compose logs -f kafka_producer
   ```
   You should see messages indicating data is being fetched and sent to the Kafka topic.

### 2. Verifying Data in Kafka

- **Console Consumer** (within the Kafka container or via Docker Compose):
  ```bash
  docker-compose exec kafka kafka-console-consumer \
    --bootstrap-server kafka:9092 \
    --topic dev_topic \
    --from-beginning
  ```
  This should display the JSON messages produced by the Kafka Producer.

---

## Local Development (Optional)

If you prefer **not** to run the producer in a Docker container, you can run it **locally**:

1. **Kafka Broker**  
   Ensure Kafka is running, typically via Docker Compose:
   ```bash
   docker-compose up -d
   ```
2. **Python Virtual Environment**  
   ```bash
   cd kafka_producer
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install Dependencies**  
   ```bash
   pip install -r requirements.txt
   ```
4. **Set Environment Variables**  
   - `VEHICLE_URL`: GTFS-RT API endpoint.  
   - `KAFKA_BROKER`: e.g. `localhost:9092` or `kafka:9092` if using Docker.  
   - `KAFKA_TOPIC`: e.g. `dev_topic`.
5. **Run the Producer**  
   ```bash
   python kafka_producer.py
   ```

You should see console output indicating successful sending of JSON data to Kafka.

---

## Configuration Details

- **`VEHICLE_URL`**  
  The default GTFS-RT endpoint can be specified via environment variables (in Docker Compose or local).  
- **`KAFKA_BROKER`**  
  Points to your Kafka broker, typically `kafka:9092` if using Docker Compose on the same network.  
- **`KAFKA_TOPIC`**  
  Default is `dev_topic`. Change it in code or via env variable as needed.  
- **Polling Interval**  
  If needed, edit the `time.sleep(...)` or scheduling logic in `kafka_producer.py`.

---

## Monitoring & Troubleshooting

1. **Kafka Broker Logs**  
   ```bash
   docker-compose logs -f kafka
   ```
   Watch for any broker-side errors (e.g., authentication or network issues).

2. **Producer Container Logs**  
   ```bash
   docker-compose logs -f kafka_producer
   ```
   Verify that data is fetched at intervals and successfully sent to the topic.

3. **Topic Data**  
   Use `kafka-console-consumer` as shown above to read messages from the topic. Confirm the JSON structure is valid.

4. **Prometheus & Grafana (Optional)**  
   - If you have JMX Exporter for Kafka, you can check topic metrics like messages in/out.  
   - Grafana dashboards can visualize Kafka throughput and producer rates.

---

## Future Enhancements

- **Security (TLS/SSL, SASL)**  
  Add TLS or SASL authentication between Producer and Kafka if needed.

- **Automated Topic Creation**  
  A script or config that ensures the topic (`dev_topic`) is created with desired replication/partition settings.

- **Rate Limiting & Backpressure**  
  If the API or Kafka cluster needs to handle high volume, implement more sophisticated handling logic in the producer.

---

## License

This Kafka Producer is released under the **MIT License**. See the [LICENSE](../LICENSE) file in the project root for more details.

---

**Questions or Issues?**  
Feel free to open an issue or pull request in the main repository. The `kafka_producer` component is one part of the **real-time ingestion pipeline** that also involves Spark Streaming, MinIO (Delta Lake), Spark Thrift Server, and dbt.