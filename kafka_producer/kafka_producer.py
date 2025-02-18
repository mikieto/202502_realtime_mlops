#!/usr/bin/env python3
import os
import json
import time
import requests
from confluent_kafka import Producer
from google.protobuf.json_format import MessageToDict
from google.protobuf.message import DecodeError

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import gtfs_realtime_pb2  # Compiled GTFS-RT Protobuf module

# ===================
# Configurable Values
# ===================
# Get environment variables from Docker Compose
VEHICLE_URL = os.getenv("VEHICLE_URL", "https://api-public.odpt.org/api/v4/gtfs/realtime/toei_odpt_train_vehicle")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "dev_topic")
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")

def fetch_vehicle_data():
    """
    Fetch and decode GTFS-RT vehicle data from the API.
    Returns a JSON-compatible dictionary if successful, or None on failure.
    """
    try:
        response = requests.get(VEHICLE_URL)
        response.raise_for_status()
        payload = response.content

        # Decode Protobuf message (FeedMessage)
        message = gtfs_realtime_pb2.FeedMessage()
        message.ParseFromString(payload)
        data = MessageToDict(message, preserving_proto_field_name=True)
        return data
    except requests.RequestException as e:
        print(f"HTTP request failed: {e}")
        return None
    except DecodeError as e:
        print(f"Protobuf decoding error: {e}")
        return None

def delivery_report(err, msg):
    """
    Callback function called once for each produced message to indicate delivery result.
    """
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

def main():
    """
    Main function to periodically fetch GTFS-RT data, append metadata, and produce messages to Kafka.
    """
    # Configure the Producer with the Kafka broker address.
    conf = {'bootstrap.servers': KAFKA_BROKER}
    producer = Producer(conf)

    try:
        while True:
            vehicle_data = fetch_vehicle_data()
            if vehicle_data:
                # Append additional metadata to the fetched data
                vehicle_data["producer_timestamp"] = time.time()  # Current timestamp from the producer
                vehicle_data["source_id"] = "toei_vehicle_api"     # Identifier for the data source
                vehicle_data["event_type"] = "gtfs_realtime_vehicle" # Classification of the event type

                # Convert data to JSON string
                data_json = json.dumps(vehicle_data)
                # Produce a message to Kafka; asynchronous send with callback.
                producer.produce(KAFKA_TOPIC, data_json.encode('utf-8'), callback=delivery_report)
                # Poll to handle delivery reports (callbacks)
                producer.poll(0)
                print(f"Sent data to Kafka topic '{KAFKA_TOPIC}': {data_json} ...")
            else:
                print("No data fetched; skipping sending.")
            # Wait for 60 seconds before fetching data again
            time.sleep(60)
    except KeyboardInterrupt:
        print("Producer interrupted by user.")
    finally:
        # Ensure all messages are delivered before shutting down.
        producer.flush()

if __name__ == '__main__':
    main()
