import logging
import os
import re
import subprocess

import cml.data_v1 as cmldata
from pyspark.sql.utils import AnalysisException

logging.getLogger().setLevel(logging.INFO)

SPARK_DATA_LAKE_CONNECTION = os.getenv("SPARK_DATA_LAKE_CONNECTION")
DEMO_DATABASE_NAME = os.getenv("DEMO_DATABASE_NAME")
DEMO_TABLE_NAME = os.getenv("DEMO_TABLE_NAME")

data_lake_connection = cmldata.get_connection(SPARK_DATA_LAKE_CONNECTION)
spark = data_lake_connection.get_spark_session()


def _extract_storage_location_from_error(error_message: str):
    """
    Extracts the storage location from an AnalysisException error message.

    This function parses the error message contained within an AnalysisException
    to identify and return the storage location that caused the conflict. The
    storage location is typically specified within parentheses following the
    keyword 'location'.

    Example:
    >>> error_message = "Can not create the managed table('`foo`.`bar`'). The associated\
        location('s3a://bucket/data/warehouse/tablespace/external/hive/foo.db/bar')\
        already exists."
    >>> _extract_storage_location_from_error(error_message)
     's3a://bucket/data/warehouse/tablespace/external/hive/foo.db/bar'

    Args:
        error_message (str): The error message containing the location.

    Returns:
        str: The extracted storage location as a string, or None if no location
        is found.
    """

    match = re.search(r"location\('([^']+)'\)", error_message)
    if match:
        return match.group(1)
    return None


if __name__ == "__main__":

    # Check if data exists. If not, create it from local csv.
    try:
        spark.read.table(f"{DEMO_DATABASE_NAME}.{DEMO_TABLE_NAME}").show()
        logging.info("Found existing demo data. Proceeding without creating it.")

    except AnalysisException:
        logging.info(f"Did not find existing data under {DEMO_DATABASE_NAME}.{DEMO_TABLE_NAME}. Proceeding to create it.")
        spark.sql(f"CREATE DATABASE IF NOT EXISTS {DEMO_DATABASE_NAME}")
        dataframe = spark.read.csv("data.csv", header=True, inferSchema=True)

        # writing will fail if data files still exist
        try:
            dataframe.write.saveAsTable(f"{DEMO_DATABASE_NAME}.{DEMO_TABLE_NAME}")
            logging.info("Data written successfully.")

        # if data files exist remove them and try writing again
        except AnalysisException as aex:
            logging.info("Data files already exist. Attempting to remove them.")
            conflict_location = _extract_storage_location_from_error(aex.desc)
            if conflict_location:
                cmd = ["hdfs", "dfs", "-rm", "-r", conflict_location]
                subprocess.call(cmd)
                dataframe.write.saveAsTable(f"{DEMO_DATABASE_NAME}.{DEMO_TABLE_NAME}")
                logging.info("Data written successfully.")
            else:
                logging.info("Failed to extract storage location from error. Data not written.")
                raise aex

        spark.read.table(f"{DEMO_DATABASE_NAME}.{DEMO_TABLE_NAME}").show() 
        logging.info("Finished creating demo data.")
