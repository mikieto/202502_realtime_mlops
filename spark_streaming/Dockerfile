# spark_streaming/Dockerfile
FROM bitnami/spark:3.5.3

ENV DELTA_VERSION="3.3.0"
ENV SPARK_PACKAGES="org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.3,io.delta:delta-spark_2.12:${DELTA_VERSION}"

WORKDIR /app

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

CMD spark-submit --packages "${SPARK_PACKAGES}" /app/spark_streaming.py
