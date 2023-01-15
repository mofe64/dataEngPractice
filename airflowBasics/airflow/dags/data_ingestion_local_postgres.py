import os
from datetime import datetime
from airflow import DAG

from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow_local_ingest_script import ingest

# Note this current implementation will download only one version of the dataset, which is 2022-01 monthly
# As a result of the current implementation the table created in postgres will be destroyed and recreated every month
# Ideally we want this to be dynamic and download the dataset for the current month stored in a seperate table but we cannot
# currently do that as the provider does not have datasets for 2023.
# If the data existed we would create our data set file as follows
# instead of hardcoding the year and month like we did above we can use the get the current year and month from airflow
# we use the jinja templating engine to extract the execution date and format it to extract the year and month and then use that to format the file name
# dataset_file = "yellow_tripdata_{{execution_date.strftime(\'%Y-%m'\)}}.parquet"
# we could also use some other logic to ensure that we get the dataset for the current month
# This would ensure that we that our url is formatted to the url for the current month, and that
# the file we download is dynamically named to represent the current month
# next we would also make our table name dynamic so that the dataset for each month is stored in a brand new table
# or we would implement some logic to ensure that the new data is merged with the already existing one
# formatting the table name can be achieved by
# TABLE_NAME_TEMPLATE = yellow_tripdata_{{execution_date.strftime(\'%Y-%m'\)}}


# we save file to airflow home cause temp folders are deleted are task finsihes,
# if we use airflow home, other tasks will still have access to this file
AIRFLOW_HOME = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")
dataset_file = "yellow_tripdata_2022-01.parquet"

url = f"https://d37ci6vzurychx.cloudfront.net/trip-data/{dataset_file}"


PG_HOST = os.getenv('PG_HOST')
PG_USER = os.getenv('PG_USER')
PG_PASSWORD = os.getenv('PG_PASSWORD')
PG_PORT = os.getenv('PG_PORT')
PG_DATABASE = os.getenv('PG_DATABASE')

local_workflow = DAG(
    "LocalIngestionDag",
    # cron translates to second day of every month at 6 am
    schedule_interval="0 6 2 * *",
    start_date=datetime(2023, 1, 1)
)

with local_workflow:
    wget_task = BashOperator(
        task_id='wget',
        bash_command=f"curl -sSL {url} > {AIRFLOW_HOME}/{dataset_file}"
    )

    ingest_task = PythonOperator(
        task_id="ingest_to_local_postgres",
        python_callable=ingest,
        op_kwargs=dict(
            user=PG_USER,
            password=PG_PASSWORD,
            host=PG_HOST,
            port=PG_PORT,
            db=PG_DATABASE,
            table_name="sample_ny_taxi_data",
            file_name=f"{AIRFLOW_HOME}/{dataset_file}"
        )
    )

    wget_task >> ingest_task
