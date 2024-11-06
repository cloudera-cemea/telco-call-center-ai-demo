import os

import cml.data_v1 as cmldata
from pyspark.sql.utils import AnalysisException


SPARK_DATA_LAKE_CONNECTION = os.getenv("SPARK_DATA_LAKE_CONNECTION_NAME")
DEMO_DATABASE_NAME = os.getenv("DEMO_DATABASE_NAME")
DEMO_TABLE_NAME = os.getenv("DEMO_TABLE_NAME")

data_lake_connection = cmldata.get_connection(SPARK_DATA_LAKE_CONNECTION)
spark = data_lake_connection.get_spark_session()

# Check if data exists. If not, create it from local csv.
try:
    spark.read.table(f"{DEMO_DATABASE_NAME}.{DEMO_TABLE_NAME}").show()
    print("Found existing demo data. Proceeding without creating it.")

except AnalysisException:
    print(f"Did not find existing data under {DEMO_DATABASE_NAME}.{DEMO_TABLE_NAME}. Proceeding to create it.")
    spark.sql(f"CREATE DATABASE IF NOT EXISTS {DEMO_DATABASE_NAME}")
    dataframe = spark.read.csv("data.csv", header=True, inferSchema=True)
    dataframe.write.saveAsTable(f"{DEMO_DATABASE_NAME}.{DEMO_TABLE_NAME}")
    spark.read.table(f"{DEMO_DATABASE_NAME}.{DEMO_TABLE_NAME}").show() 
    print("Finished creating demo data.")
