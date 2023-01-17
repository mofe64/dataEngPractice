import os
from time import time
from prefect import flow, task
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
from prefect_sqlalchemy import SqlAlchemyConnector
from prefect.tasks import task_input_hash
from datetime import timedelta


# cache_key_fn allows us efficiently reuse results of tasks that may be expensive to run with every flow run,
# or reuse cached results if the inputs to a task have not changed.
# To enable caching, specify a cache_key_fn which a function that returns a cache key — on our task.
# we may also provide a cache_expiration timedelta indicating when the cache expires.
# If you do not specify a cache_expiration, the cache key does not expire.
@task(log_prints=True, tags=['extract'], cache_key_fn=task_input_hash, cache_expiration=timedelta(days=1))
def extract_data(url: str) -> pd.DataFrame:
    print("beginning extract task")
    file_name = 'output.parquet'
    # download the csv (if os.system is windows wget not recognized use curl instead   )
    # os.system(f"wget {url} -O {file_name}")
    os.system(f"curl -sSL {url} --ssl-no-revoke > {file_name}")

    print("download complete ...")
    # we read parquet file no chunks
    df = pd.read_parquet(file_name, engine='pyarrow')
    # modify specific columns in df to change their type to datetime
    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

    return df


@task(log_prints=True)
def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    print(
        f"pre : missing passenger count: {df['passenger_count'].isin([0]).sum()}")
    df = df[df['passenger_count'] != 0]
    print(
        f"post : missing passenger count: {df['passenger_count'].isin([0]).sum()}")
    return df


@task(log_prints=True, retries=3)
def load_data(table_name, df):
    # We use our sql alchemy block to initialize the connection to our database.
    # Using this we no longer have to provide our connection credentials or params
    # in our script
    connection_block = SqlAlchemyConnector.load("sample-ny-data-connection")
    with connection_block.get_connection(begin=False) as engine:
        # create the table
        # df.head(n=0) returns just the column names for dataframe
        # we convert to sql, provide the table name, engine and if a table with such name
        # already exists we replace
        df.head(n=0).to_sql(name=table_name, con=engine, if_exists='replace')

        # read_parquet does not allow chunking, so we manually do that ourselves
        # split into 10 chunks
        for chunk in np.array_split(df, 10):
            t_start = time()
            # add chunk data to table
            chunk.to_sql(name=table_name, con=engine, if_exists='append')
            t_end = time()
            print('inserted chunk in %.3f seconds' % (t_end - t_start))

    # Without Blocks
    #     # create our connection engine
    #     engine = create_engine(
    #         f"postgresql://{user}:{password}@{host}:{port}/{db}")
    #     # create the table
    #     # df.head(n=0) returns just the column names for dataframe
    #     # we convert to sql, provide the table name, engine and if a table with such name
    #     # already exists we replace
    #     df.head(n=0).to_sql(name=table_name, con=engine, if_exists='replace')

    #    # read_parquet does not allow chunking, so we manually do that ourselves
    #    # split into 10 chunks
    #     for chunk in np.array_split(df, 10):
    #         t_start = time()
    #         # add chunk data to table
    #         chunk.to_sql(name=table_name, con=engine, if_exists='append')
    #         t_end = time()
    #         print('inserted chunk in %.3f seconds' % (t_end - t_start))


@flow(name="subflow", log_prints=True)
def log_subflow():
    print("sample flow to show that flows can call other flows...")


@flow(name="ingest_data")
def main_flow():
    table_name = 'yellow_taxi_trips'
    url = 'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2022-01.parquet'
    raw_data = extract_data(url=url)
    cleaned_data = transform_data(df=raw_data)
    # We use our sql alchemy block to initialize the connection to our database.
    # Using this we no longer have to provide our connection credentials as params
    load_data(table_name, df=cleaned_data)


if __name__ == '__main__':
    main_flow()
