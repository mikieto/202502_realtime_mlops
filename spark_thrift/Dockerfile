FROM bitnami/spark:3.3.2

ENV SPARK_PACKAGES="org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.2,io.delta:delta-core_2.12:2.3.0,io.delta:delta-storage:2.3.0"

# Run the streaming job by default
CMD spark-submit --packages "$SPARK_PACKAGES" \
  --class "org.apache.spark.sql.hive.thriftserver.HiveThriftServer2" \
  --conf "spark.hadoop.fs.s3a.endpoint=${MINIO_ENDPOINT}" \
  --conf "spark.hadoop.fs.s3a.access.key=${MINIO_ROOT_USER}" \
  --conf "spark.hadoop.fs.s3a.secret.key=${MINIO_ROOT_PASSWORD}" \
  "/opt/bitnami/spark/jars/spark-thrift-server-3.3.2.jar"