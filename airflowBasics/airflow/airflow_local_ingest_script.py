from time import time
import pandas as pd
from sqlalchemy import create_engine
import numpy as np

# Note we need some dependencies to make sure that this script runs on our airflow workers
# So we need to make sure that the needed dependencies are added to airflow in our custom airflow build
# In our docker file which we use to create our custom airflow build, we add the needed dependencies


def ingest(user, password, host, port, db, table_name, file):

    # create our connection engine
    engine = create_engine(
        f"postgresql://{user}:{password}@{host}:{port}/{db}")
    engine.connect()
    print("connection established ...")

    # we read parquet file no chunks
    df = pd.read_parquet(file, engine='pyarrow')

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
