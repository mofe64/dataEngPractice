FROM python:3.9

RUN apt-get install wget
RUN pip install pandas sqlalchemy psycopg2 numpy pyarrow

WORKDIR /app
COPY ingest_data_script_parquet.py  ingest_data_script_parquet.py

ENTRYPOINT ["python", "ingest_data_script_parquet.py"]