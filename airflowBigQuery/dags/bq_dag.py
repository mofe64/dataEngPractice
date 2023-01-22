import os

from airflow import DAG
from airflow.utils.dates import days_ago
from google.cloud import storage
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateExternalTableOperator, BigQueryInsertJobOperator
from airflow.providers.google.cloud.transfers.gcs_to_gcs import GCSToGCSOperator


PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
BUCKET = os.environ.get("GCP_GCS_BUCKET")

path_to_local_home = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")
parquet_file = "ny_taxi.parquet"
BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET", 'ny_taxi_sample')

default_args = {
    "owner": "airflow",
    "start_date": days_ago(1),
    "depends_on_past": False,
    "retries": 1
}

with DAG(
    dag_id="bg_dag",
    schedule_interval="@daily",
    default_args=default_args,
    catchup=False,
    max_active_runs=1,
    tags=['mofe'],
) as dag:
    # rearrange data in our gcs bucket, we move data from one place to another, we set
    # move object to true if we want to move files instead of copy
    reformat_gcs_data_task = GCSToGCSOperator(
        task_id="reformat_gcs_data_task",
        source_bucket=BUCKET,
        source_object='data/ny_taxi.parquet',
        destination_bucket=BUCKET,
        destination_object='yellow/',
        # move_object=True
    )

    # Create external table with data already loaded in GCS
    gcs_to_bq_ext_task = BigQueryCreateExternalTableOperator(
        task_id="gcs_to_bq_ext_task",
        table_resource={
            "tableReference": {
                "projectId": PROJECT_ID,
                "datasetId": BIGQUERY_DATASET,
                "tableId": "external_table_name",
            },
            "externalDataConfiguration": {
                "autodetect": True,
                "sourceFormat": "PARQUET",
                # "sourceUris": [f"gs://{BUCKET}/yellows/*"], use in case we have multiple files in that directory
                # we only have one file in the yellows dir so we can have it like this
                "sourceUris": [f"gs://{BUCKET}/yellow/{parquet_file}"],
            },
        },
    )

    # This query creats a new table called tripdata_partitioned and partitions the new table by the tpep_pickup_datetime column
    # we seed this new table with data from the table we created from our GCS Bucket data in our previous task called external_table_name
    CREATE_PARTITION_TABLE_QUERY = f"CREATE OR REPLACE TABLE {BIGQUERY_DATASET}.tripdata_partitioned \
            PARTITION BY DATE(tpep_pickup_datetime) AS \
            SELECT * FROM {BIGQUERY_DATASET}.external_table_name"

    # This operator allows us to run sql queries including DDL statements
    bq_ext_table_partition = BigQueryInsertJobOperator(
        task_id='bq_ext_table_partition',
        configuration={
            "query": {
                "query": CREATE_PARTITION_TABLE_QUERY,
                "useLegacySql": False
            }
        }
    )

    reformat_gcs_data_task >> gcs_to_bq_ext_task >> bq_ext_table_partition
