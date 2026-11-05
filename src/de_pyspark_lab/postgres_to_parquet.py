import argparse
import os
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--result_path",
        default="output/postgres_material_summary",
    )
    args = parser.parse_args()

    user = os.environ["POSTGRES_USER"]
    password = os.environ["POSTGRES_PASSWORD"]
    database = os.environ["POSTGRES_DB"]
    host = os.getenv("POSTGRES_HOST", "127.0.0.1")
    port = os.getenv("POSTGRES_PORT", "55432")

    spark = (
        SparkSession.builder
        .appName("postgres-to-parquet")
        .master("local[2]")
        .config("spark.sql.shuffle.partitions", "2")
        .config(
            "spark.jars.packages",
            "org.postgresql:postgresql:42.7.14",
        )
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("ERROR")

    try:
        source = (
            spark.read.format("jdbc")
            .option(
                "url",
                f"jdbc:postgresql://{host}:{port}/{database}",
            )
            .option("dbtable", "public.materialbewegungen")
            .option("user", user)
            .option("password", password)
            .option("driver", "org.postgresql.Driver")
            .option("fetchsize", "1000")
            .load()
        )

        source_count = source.count()
        if source_count == 0:
            raise ValueError("Source table is empty")

        source_total = source.agg(
            F.sum("menge")
        ).first()[0]

        result = (
            source.groupBy("werk", "buchungsdatum")
            .agg(F.sum("menge").alias("Gesamtmenge"))
            .select(
                F.col("werk").alias("Werk"),
                F.col("buchungsdatum").alias("Buchungsdatum"),
                "Gesamtmenge",
            )
            .withColumn(
                "Buchungsmonat",
                F.date_format("Buchungsdatum", "yyyy-MM"),
            )
        )

        output = str(Path(args.result_path).resolve())

        (
            result.write
            .mode("overwrite")
            .partitionBy("Buchungsmonat")
            .parquet(output)
        )

        verified = spark.read.parquet(output)

        target_total = verified.agg(
            F.sum("Gesamtmenge")
        ).first()[0]

        assert source_total == target_total, (
            "Source/target quantity mismatch"
        )
        assert verified.count() == result.count(), (
            "Aggregated row count mismatch"
        )

        verified.orderBy(
            "Werk", "Buchungsdatum"
        ).show(truncate=False)

        print(f"Source rows: {source_count}")
        print(f"Source quantity: {source_total}")
        print(f"Target quantity: {target_total}")
        print(f"Parquet location: {output}")
        print("SUCCESS: PostgreSQL to Parquet ETL passed")

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
