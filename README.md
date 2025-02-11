
## Setup Instructions

1. **Local Development:**
   - Install [Docker Desktop](https://www.docker.com/products/docker-desktop) (WSL2 backend is recommended for Windows users).
   - Clone the repository:
     ```bash
     git clone https://github.com/your-username/202502_realtime_mlops.git
     ```
   - Follow the instructions in [docs/deployment.md](docs/deployment.md) for setting up the local environment using Docker Compose.

## Running the Application

1. **Start All Services:**
   Run the following command from the project root to start all services:
   ```bash
   docker-compose up -d
   ```
   This will spin up Kafka, ZooKeeper, Prometheus, Grafana, Alertmanager, node-exporter, and JMX Exporter in the background.

2. **Run the Kafka Producer:**  
   If the Kafka Producer is not containerized, you need to run it manually:
   ```bash
   python kafka/producer/kafka_producer.py
   ```
   Ensure that it is sending data to the correct Kafka topic.

3. **Start the Spark Streaming Job:**  
   In the `spark_streaming/src/` directory, execute:
   ```bash
   python streaming_main.py
   ```
   This job reads data from Kafka, processes it, and writes it to Delta Lake.

4. **Run the Batch Data Extraction Job:**  
   Execute the extraction script to prepare training and test datasets:
   ```bash
   python data_extraction/extract_dataset.py
   ```

5. **Verify the Setup:**  
   - **Kafka:** Check that messages are flowing through Kafka topics using `kafka-console-consumer`.
   - **Spark Streaming:** View the Spark UI at [http://localhost:4040](http://localhost:4040).
   - **Delta Lake:** Use a Spark session to verify data persistence.
   - **Monitoring:**  
     - Prometheus UI: [http://localhost:9090](http://localhost:9090)  
     - Grafana UI: [http://localhost:3000](http://localhost:3000)  
     - Alertmanager UI: [http://localhost:9093](http://localhost:9093)


## Documentation

Detailed documentation covering architecture, deployment, troubleshooting, and CI/CD is maintained in the `docs/` folder. Key documents include:

- **architecture.md:** Detailed explanation of system components and design rationale.
- **deployment.md:** Instructions for local and cloud deployments.
- **README Updates:** Each submodule (e.g., `spark_streaming`, `data_extraction`, and `monitoring`) contains its own README, which is referenced in this document.

## License

This project is licensed under the MIT License.

---

For further details or to contribute, please refer to the documentation in the `docs/` folder or contact the project maintainer.
