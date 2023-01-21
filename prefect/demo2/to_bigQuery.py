from pathlib import Path
import pandas as pd
from prefect import flow, task
import os
from prefect_gcp.cloud_storage import GcsBucket
from prefect_gcp import GcpCredentials
from google.cloud import storage


@task(retries=3)
def extractFromGcs(filename: str):
    gcs_path = f"data\{filename}.parquet"
    gcs_block = GcsBucket.load("prefect-gcs-test-block")
    gcs_block.get_directory(from_path=gcs_path, local_path=f"/data")
    return Path(f"/data/{gcs_path}")


@task
def sampleTransform(path: Path) -> pd.DataFrame:
    df = pd.read_parquet(path)
    print("doing some sample transforms")
    return df


@task
def write_to_bigQuery(df: pd.DataFrame):
    gcp_credentials_block = GcpCredentials.load(
        "booming-edge-372615-first-user-service-account-creds")

    df.to_gbq(
        destination_table="ny_taxi_sample.yellow_taxi",
        project_id="booming-edge-372615",
        credentials=gcp_credentials_block.get_credentials_from_service_account(),
        chunksize=500_000,
        if_exists="append"
    )


@flow()
def to_bigQuery():
    path = extractFromGcs(filename="ny_taxi")
    df = sampleTransform(path)
    write_to_bigQuery(df)


if __name__ == '__main__':
    to_bigQuery()
