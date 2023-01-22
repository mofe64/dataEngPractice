from pathlib import Path
import pandas as pd
from prefect import flow, task
import os
from prefect_gcp.cloud_storage import GcsBucket
from google.cloud import storage


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
    # modify specific columns in df to change their type to datetime
    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
    return df


@task(log_prints=True)
def clean(df: pd.DataFrame) -> pd.DataFrame:
    print(
        f"pre : missing passenger count: {df['passenger_count'].isin([0]).sum()}")
    df = df[df['passenger_count'] != 0]
    print(
        f"post : missing passenger count: {df['passenger_count'].isin([0]).sum()}")
    return df


# Note this uploads our data as a file called data\filename.parquet
# figure out how to do create a path for directories
@task()
def write_local(df: pd.DataFrame, file_name: str) -> Path:
    """Write df out locally as parquet file"""
    path = Path(f"data\{file_name}.parquet")
    df.to_parquet(path, compression="gzip")
    return path


@task()
def write_gcs(path: Path) -> None:
    # WARNING; WORKAROUND to prevent timeout for files > 6 MB on 800 kbps upload link.
    storage.blob._DEFAULT_CHUNKSIZE = 5 * 1024 * 1024  # 5 MB
    storage.blob._MAX_MULTIPART_SIZE = 5 * 1024 * 1024  # 5 MB
    gcs_block = GcsBucket.load("prefect-gcs-test-block")
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


if __name__ == '__main__':
    etl_web_to_gcs()
