from pathlib import Path
import pandas as pd
from prefect import flow, task
import os
from prefect_gcp.cloud_storage import GcsBucket


@task(retries=3)
def fetch(dataset_url: str) -> pd.DataFrame:
    print("beginning extract task")
    file_name = 'output.parquet'
    # download the csv (if os.system is windows wget not recognized use curl instead   )
    # os.system(f"wget {url} -O {file_name}")
    os.system(f"curl -sSL {dataset_url} --ssl-no-revoke > {file_name}")

    print("download complete ...")
    # we read parquet file no chunks
    df = pd.read_parquet(file_name, engine='pyarrow')
    return df


@task(log_prints=True)
def clean(df: pd.DataFrame) -> pd.DataFrame:
    print(
        f"pre : missing passenger count: {df['passenger_count'].isin([0]).sum()}")
    df = df[df['passenger_count'] != 0]
    print(
        f"post : missing passenger count: {df['passenger_count'].isin([0]).sum()}")
    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
    return df


@task()
def write_local(df: pd.DataFrame, file_name: str) -> Path:
    """Write df out locally as parquet file"""
    path = Path(f"data/{file_name}.parquet")
    df.to_parquet(path, compression="gzip")
    return path


@task()
def write_gcs(path: Path) -> None:
    gcs_block = GcsBucket.load("bucketname")
    gcs_block.upload_from_path(
        from_path=f"{path}",
        to_path=path
    )
    return


@flow()
def etl_web_to_gcs() -> None:
    """Main ETL function"""
    url = 'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2022-01.parquet'
    df = fetch(url)
    cleaned_data = clean(df)
    path = write_local(df=cleaned_data, file_name="ny_taxi")
    write_gcs(path)
