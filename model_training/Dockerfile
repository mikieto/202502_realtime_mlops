FROM python:3.9-slim

USER root

# Python & pip & necessary packages
RUN apt-get update && apt-get install -y \
    python3 python3-pip \
    libsasl2-dev \
    libssl-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# local_experiments directory contains the requirements.txt file for the local development
COPY local_experiments/requirements.txt /app/local_experiments/requirements.txt
RUN pip install --no-cache-dir -r /app/local_experiments/requirements.txt

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . /app

# Command to run model training script
CMD ["python", "train.py"]
