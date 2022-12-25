from time import time
import pandas as pd
import argparse
import os
from sqlalchemy import create_engine
import numpy as np

parser = argparse.ArgumentParser(description="Ingest csv data to postgres")

# args we want to collect include
# user
# password
# host
# port
# database name
# table name
# url of the csv


def ingest(params):
    print(f"ingest received params {params}")
    user = params.user
    password = params.password
    host = params.host
    port = params.port
    db = params.db
    table_name = params.table_name
    url = params.url

    file_name = 'output.parquet'

    # download the csv
    os.system(f"wget {url} -O {file_name}")

    # create our connection engine
    engine = create_engine(
        f"postgresql://{user}:{password}@{host}:{port}/{db}")

    # we read parquet file no chunks
    df = pd.read_parquet(file_name, engine='pyarrow')

    # modify specific columns in df to change their type to datetime
    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

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


if __name__ == '__main__':
    parser.add_argument('--user', help='user name for postgres')
    parser.add_argument('--password', help='password for postgress')
    parser.add_argument('--host', help='host for postgres')
    parser.add_argument('--port', help='port for postgres')
    parser.add_argument('--db', help='database name for postgres')
    parser.add_argument(
        '--table-name', help='name of the table we will write results to')
    parser.add_argument('--url', help='url of the csv file')

    args = parser.parse_args()

    ingest(args)
