from time import time
import pandas as pd
import argparse
import os
from sqlalchemy import create_engine

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

    csv_name = 'output.csv'

    # download the csv
    os.system(f"wget {url} -O {csv_name}")

    # create our connection engine
    engine = create_engine(
        f"postgresql://{user}:{password}@{host}:{port}/{db}")

    # we read a chunk outside of our while loop so that we can manually
    # create our table first before proceeding to add the data into
    # our created table in  a loop
    # read csv in chunks
    df_iter = pd.read_csv(csv_name, iterator=True, chunksize=100000)

    # get first chunk of csv
    df = next(df_iter)

    # modify specific columns in df to change their type to datetime
    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

    # create the table
    # df.head(n=0) returns just the column names for dataframe
    # we convert to sql, provide the table name, engine and if a table with such name
    # already exists we replace
    df.head(n=0).to_sql(name=table_name, con=engine, if_exists='replace')

    # convert rest of data in first chunk to sql, this time we append the data to
    # already created table
    df.to_sql(name=table_name, con=engine, if_exists='append')

    # when there are no more chunks next will raise an exception
    # effectively exiting our infinite loop
    try:
        while True:
            t_start = time()

            # get next chunk of csv
            df = next(df_iter)

            # modify specific columns in df to change their type to datetime
            df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
            df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

            # add chunk data to table
            df.to_sql(name=table_name, con=engine, if_exists='append')

            t_end = time()

            print('inserted chunk in %.3f seconds' % (t_end - t_start))

    except StopIteration:
        print("Ingestion complete ...")
    except:
        print("Som ething went wrong")


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
