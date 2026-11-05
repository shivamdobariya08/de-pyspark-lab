from pathlib import Path

from pyspark.sql import SparkSession


def test_postgres_parquet_output():
    output = Path("output/postgres_material_summary")

    assert output.is_dir(), "Parquet output directory missing"
    assert (output / "Buchungsmonat=2026-11").is_dir()

    spark = (
        SparkSession.builder
        .master("local[2]")
        .appName("postgres-parquet-validation")
        .getOrCreate()
    )

    try:
        df = spark.read.parquet(str(output.resolve()))

        actual = {
            (
                row["Werk"],
                row["Buchungsdatum"].isoformat(),
                row["Gesamtmenge"],
                row["Buchungsmonat"],
            )
            for row in df.collect()
        }

        expected = {
            ("1000", "2026-11-01", 30, "2026-11"),
            ("2000", "2026-11-02", 15, "2026-11"),
        }

        assert actual == expected

    finally:
        spark.stop()
