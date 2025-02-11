#!/usr/bin/env python3
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from sklearn.model_selection import train_test_split
import pandas as pd

def main():
    """
    This script reads streaming data from a Delta Lake table where 'feed_timestamp' 
    and 'vehicle_timestamp_str' are strings representing Unix time in seconds. 
    We convert them to datetime in Pandas, split into train/test, and save CSV files.
    """

    # --- 1. Initialize SparkSession with Delta support ---
    spark = (
        SparkSession.builder
        .appName("ExtractDataset")
        .config("spark.jars.packages", "io.delta:delta-core_2.12:2.4.0")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        .getOrCreate()
    )

    # Set the path to your Delta Lake table
    DELTA_PATH = "file:///home/mikieto/projects/202502_realtime_mlops/delta/dev"

    # --- 2. Load data from Delta Lake (no timestamp casting in Spark) ---
    df = spark.read.format("delta").load(DELTA_PATH)
    print("[INFO] Loaded Delta table schema:")
    df.printSchema()

    df = df.withColumn("processing_timestamp_str", col("processing_timestamp").cast("string"))
    df = df.drop("processing_time")

    # Convert Spark DataFrame to Pandas DataFrame
    pandas_df = df.toPandas()

    # Debug: check some rows
    # print(pandas_df.head(5))

    # --- 3. Convert feed_timestamp and vehicle_timestamp_str to datetime in Pandas ---
    # Assuming they are Unix seconds as strings
    pandas_df["feed_timestamp"] = pd.to_datetime(pandas_df["feed_timestamp"], errors="coerce", unit="s")
    pandas_df["vehicle_timestamp"] = pd.to_datetime(pandas_df["vehicle_timestamp_str"], errors="coerce", unit="s")
    pandas_df["processing_timestamp"] = pd.to_datetime(pandas_df["processing_timestamp_str"], errors="coerce", unit="s")

    # Optional: drop rows with invalid or missing timestamps
    # pandas_df.dropna(subset=["feed_timestamp", "vehicle_timestamp"], inplace=True)

    # --- 4. Split into training and test sets ---
    train_df, test_df = train_test_split(pandas_df, test_size=0.2, random_state=42)
    print(f"[INFO] Total records: {len(pandas_df)}")
    print(f"[INFO] Train: {len(train_df)}, Test: {len(test_df)}")

    # --- 5. Save the results to CSV ---
    # Get the directory where the current script is located
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Create an output folder inside that directory
    output_dir = os.path.join(current_dir, "data_extraction_output")
    os.makedirs(output_dir, exist_ok=True)

    train_file = os.path.join(output_dir, "train_dataset.csv")
    test_file = os.path.join(output_dir, "test_dataset.csv")

    train_df.to_csv(train_file, index=False)
    test_df.to_csv(test_file, index=False)

    print(f"[INFO] Train dataset -> {train_file}")
    print(f"[INFO] Test dataset  -> {test_file}")

    # Stop Spark
    spark.stop()
    print("[INFO] Extraction completed.")

if __name__ == "__main__":
    main()
