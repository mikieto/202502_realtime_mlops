# Kafka Producer

This Kafka Producer is a Python-based application that fetches real-time GTFS-RT data (vehicle positions) from an external API, decodes the Protobuf payload, converts it to JSON, and sends the data to a Kafka topic.

## Overview

**Project:** 202502_realtime_mlops  
**Component:** Kafka Producer  
**Data Source:** GTFS-RT Vehicle API  
**Kafka Topic:** `dev_topic`

This component is part of the overall real-time data ingestion pipeline. It retrieves data from the GTFS-RT API at regular intervals and produces JSON messages into Kafka for downstream processing in Spark Streaming and Delta Lake.

## Features

- **Data Fetching:**  
  Retrieves GTFS-RT data from the configured API endpoint.

- **Data Decoding:**  
  Uses a compiled Protobuf module (`gtfs_realtime_pb2`) to decode the raw data.

- **Data Transformation:**  
  Converts the Protobuf message into a JSON-compatible dictionary.

- **Kafka Integration:**  
  Sends the JSON data to a Kafka topic (`dev_topic`) using the Kafka Producer API.

- **Configurable Polling Interval:**  
  The script fetches new data periodically (default is every 60 seconds).

## Prerequisites

- **Docker Environment:**  
  Ensure that Docker Desktop is installed and configured to run the Kafka, ZooKeeper, and monitoring containers using Docker Compose.  
  Refer to the project root `README.md` and `docs/deployment.md` for instructions on starting the Kafka environment.

- **Python 3:**  
  This project requires Python 3.8 or later. It is recommended to use a virtual environment.

- **Dependencies:**  
  The required Python packages are listed in the `requirements.txt` file.

## Setup Instructions

### 1. Start the Kafka Environment

Navigate to the project root and start the required services:

```bash
cd 202502_realtime_mlops
docker-compose up -d
```

Verify that the Kafka broker is running:

```bash
docker-compose ps
```

### 2. Create and Activate the Virtual Environment

Navigate to the Kafka producer directory and set up the environment:

```bash
cd kafka
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configuration

- **API Endpoint:**  
  The GTFS-RT API endpoint is defined in the source code as `VEHICLE_URL`. Modify this URL if needed.

- **Kafka Broker:**  
  The Kafka broker address is set to `localhost:9092`. Ensure this matches your Docker Compose setup.

- **Kafka Topic:**  
  The topic name (`dev_topic`) is set in the script. Update it if necessary.

## Running the Producer

With the virtual environment activated and dependencies installed, start the producer:

```bash
python3 kafka_producer.py
```

You should see console output indicating that data is being fetched and sent to Kafka. For example:

```
Sent data to Kafka: {"header": {"gtfs_realtime_version": "2.0", ... }
```

## Verifying Data Ingestion

To verify that data is being sent to Kafka, use the Kafka console consumer:

```bash
docker exec -it kafka kafka-console-consumer \
    --bootstrap-server localhost:9092 \
    --topic dev_topic \
    --from-beginning
```

This should display the JSON messages produced by the Kafka Producer.

## Monitoring Kafka with JMX Exporter

Kafka exposes metrics via JMX. The project includes a JMX Exporter for Prometheus, allowing visualization and alerting through Grafana.

1. **Ensure JMX Exporter is configured** in `docker-compose.yaml`:
   ```yaml
   environment:
     KAFKA_OPTS: "-javaagent:/opt/jmx_prometheus_javaagent.jar=9404:/opt/kafka_jmx_exporter.yml"
   ```

2. **Check JMX metrics**:
   ```bash
   curl -X GET http://localhost:9404/metrics
   ```

3. **View Kafka dashboards in Grafana** (`http://localhost:3000`).

## Troubleshooting

- **Virtual Environment Issues:**  
  Ensure that you have activated the virtual environment before running the script (`source venv/bin/activate`).

- **Dependency Errors:**  
  If you encounter module import errors, check that all packages in `requirements.txt` are installed properly. Re-run `pip install -r requirements.txt` if necessary.

- **Kafka Connection Issues:**  
  Confirm that your Kafka and ZooKeeper containers are running:
  ```bash
  docker-compose ps
  ```
  Check logs for errors:
  ```bash
  docker logs kafka
  ```

## Future Enhancements

- **Security Enhancements:**  
  Implement TLS, ACLs, or SASL authentication for Kafka.

- **Automated Topic Creation:**  
  A script to automate Kafka topic creation.

- **Enhanced Logging & Monitoring:**  
  Centralized logging for debugging and performance tracking.

## License

This component is released under the MIT License. See the LICENSE file in the project root for details.

