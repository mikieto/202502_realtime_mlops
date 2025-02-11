
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder.appName("CheckDeltaLake")
    .config(
        "spark.jars.packages",
        "io.delta:delta-core_2.12:2.4.0"
    )
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
    .getOrCreate()
)

# Delta Lake の保存パス（DELTA_LAKE_PATH の値）
#DELTA_LAKE_PATH = "s3://your-bucket/delta-lake/"  # または "file:///path/to/delta-table"
DELTA_LAKE_PATH = "file:///home/mikieto/projects/202502_realtime_mlops/delta/dev"

# Delta テーブルを読み込む
df = spark.read.format("delta").load(DELTA_LAKE_PATH)

# データの表示
df.show(10, truncate=False)
