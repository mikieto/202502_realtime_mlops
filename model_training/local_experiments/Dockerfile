# model_training/local_experiments/Dockerfile.jupyter_spark

FROM bitnami/spark:3.3.0

USER root

# Python & pip & necessary packages
RUN apt-get update && apt-get install -y \
    python3 python3-pip \
    libsasl2-dev \
    libssl-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir -r /app/requirements.txt

# RUN curl -o /opt/bitnami/spark/jars/hadoop-aws-3.3.1.jar ...
# RUN curl -o /opt/bitnami/spark/jars/aws-java-sdk-bundle-1.11.874.jar ...

EXPOSE 8888

CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=''", "--notebook-dir=/app"]
