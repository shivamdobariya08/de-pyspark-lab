from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = (
    SparkSession.builder.appName("local-data-engineering-lab")
    .master("local[2]")
    .config("spark.sql.shuffle.partitions", "2")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")

try:
    # Synthetic example records; no real customer data.
    records = [
        ("1000", "MAT001", 10),
        ("1000", "MAT002", 20),
        ("2000", "MAT003", 15),
    ]

    df = spark.createDataFrame(
        records,
        ["Werk", "Materialnummer", "Menge"],
    )

    result = df.groupBy("Werk").agg(F.sum("Menge").alias("Gesamtmenge"))

    result.show()

    output_path = Path("output/material_summary").resolve()

    result.write.mode("overwrite").parquet(str(output_path))

    verified = spark.read.parquet(str(output_path))

    assert verified.count() == 2
    assert verified.agg(F.sum("Gesamtmenge")).first()[0] == 45

    print("SUCCESS: PySpark ETL and Parquet validation passed")

finally:
    spark.stop()
