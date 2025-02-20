#!/bin/bash

CLASSPATH=$(ls /app/jars/*.jar 2>/dev/null | tr '\n' ':')

echo "=== [DEBUG] Computed CLASSPATH ==="
echo "${CLASSPATH}"

if [ -z "${CLASSPATH}" ]; then
  echo "Error: No JAR found in /app/jars/*.jar"
  exit 1
fi

exec spark-submit \
  --master local[*] \
  --class org.apache.spark.sql.hive.thriftserver.HiveThriftServer2 \
  --driver-class-path "${CLASSPATH}" \
  --conf spark.executor.extraClassPath="${CLASSPATH}" \
  --conf spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension \
  --conf spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog \
  --conf spark.hadoop.fs.s3a.endpoint="${MINIO_ENDPOINT}" \
  --conf spark.hadoop.fs.s3a.access.key="${MINIO_ROOT_USER}" \
  --conf spark.hadoop.fs.s3a.secret.key="${MINIO_ROOT_PASSWORD}" \
  --conf spark.hadoop.fs.s3a.path.style.access="${MINIO_PATH_STYLE_ACCESS}"
#  --conf spark.hadoop.fs.s3a.endpoint=http://minio:9000 \
#  --conf spark.hadoop.fs.s3a.access.key=admin \
#  --conf spark.hadoop.fs.s3a.secret.key=admin123
