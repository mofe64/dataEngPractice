import os
import logging

from airflow import DAG
from airflow.utils.dates import days_ago

from airflow.operators.python import PythonOperator


PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
BUCKET = os.environ.get("GCP_GCS_BUCKET")


default_args = {
    "owner": "airflow",
    "start_date": days_ago(1),
    "depends_on_past": False,
    "retries": 1,
}


def test1():
    print("testing to see stuff 1")
    print(f"project id var is {PROJECT_ID}")
    print(f"bucket var is {BUCKET}")


def test2():
    print("testing to see stuff 2")
    print(f"project id var is {PROJECT_ID}")
    print(f"bucket var is {BUCKET}")


# NOTE: DAG declaration - using a Context Manager (an implicit way)
with DAG(
    dag_id="light-weight-test",
    schedule_interval="@daily",
    default_args=default_args,
    catchup=False,
    max_active_runs=1,
    tags=['dtc-de'],
) as dag:

    test1 = PythonOperator(
        task_id="test1",
        python_callable=test1,
        op_kwargs={},
    )

    test2 = PythonOperator(
        task_id="test2",
        python_callable=test2,
        op_kwargs={},
    )

    test1 >> test2
