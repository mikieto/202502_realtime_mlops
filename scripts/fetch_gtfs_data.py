#!/usr/bin/env python3

import os
import requests
import zipfile
import subprocess
from minio import Minio

# ====================
# Define Configurations
# ====================

# 1) GTFS download URL
GTFS_URL = "https://api-public.odpt.org/api/v4/files/Toei/data/Toei-Train-GTFS.zip"
ZIP_PATH = "toei_gtfs.zip"
LOCAL_EXTRACT_DIR = "gtfs_temp"

# 2) MinIO connection settings
MINIO_HOST = "localhost"     # Change to minio if using Docker
MINIO_PORT = 9000
MINIO_ACCESS_KEY = "admin"
MINIO_SECRET_KEY = "admin123"
MINIO_SECURE = False     # Change to True if using HTTPS

# 3) MinIO path settings
MINIO_BUCKET = "my-bucket"
STOP_TIMES_REMOTE_PATH = "bronze/gtfs_data/stop_times.txt"
STOPS_REMOTE_PATH      = "bronze/gtfs_data/stops.txt"

# 4) Local file paths
STOP_TIMES_LOCAL = os.path.join(LOCAL_EXTRACT_DIR, "stop_times.txt")
STOPS_LOCAL      = os.path.join(LOCAL_EXTRACT_DIR, "stops.txt")

# 5) dbt settings
DBT_PROJECT_DIR = "./dbt"
DBT_TARGET = "local"


def fetch_gtfs_and_update_dbt():
    """
    1) Download GTFS Zip from GTFS_URL
    2) Unzip GTFS Zip locally (ZIP_PATH -> LOCAL_EXTRACT_DIR)
    3) Upload to MinIO (MINIO_HOST, MINIO_BUCKET, etc.)
    """

    # 1) Download GTFS zip
    print(f"[INFO] Downloading GTFS from {GTFS_URL} ...")
    resp = requests.get(GTFS_URL, timeout=60)
    resp.raise_for_status()

    with open(f"{LOCAL_EXTRACT_DIR}/{ZIP_PATH}", "wb") as f:
        f.write(resp.content)
    print(f"[INFO] Saved ZIP to {LOCAL_EXTRACT_DIR}/{ZIP_PATH}")

    # 2) Unzip
    print(f"[INFO] Unzipping GTFS data into '{LOCAL_EXTRACT_DIR}' ...")
    with zipfile.ZipFile(f"{LOCAL_EXTRACT_DIR}/{ZIP_PATH}", "r") as zf:
        zf.extractall(LOCAL_EXTRACT_DIR)

    # 3) Upload to MinIO
    print(f"[INFO] Uploading extracted files to MinIO({MINIO_HOST}:{MINIO_PORT}) ...")
    client = Minio(
        f"{MINIO_HOST}:{MINIO_PORT}",
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=MINIO_SECURE
    )

    client.fput_object(MINIO_BUCKET, STOP_TIMES_REMOTE_PATH, STOP_TIMES_LOCAL)
    client.fput_object(MINIO_BUCKET, STOPS_REMOTE_PATH,      STOPS_LOCAL)
    print("[INFO] MinIO upload completed.")

def main():
    fetch_gtfs_and_update_dbt()


if __name__ == "__main__":
    main()

