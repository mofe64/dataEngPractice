## Links

1. [Google airflow provider docs](https://airflow.apache.org/docs/apache-airflow-providers-google/stable/index.html)

2. [GCS to GCS docs](https://airflow.apache.org/docs/apache-airflow-providers-google/stable/_api/airflow/providers/google/cloud/transfers/gcs_to_gcs/index.html#airflow.providers.google.cloud.transfers.gcs_to_gcs.GCSToGCSOperator)

3. [External Table creator with airflow](https://stackoverflow.com/questions/69651569/how-to-create-external-table-in-google-big-query-for-parquet-file-to-run-in-airf)

We can also create big query external table operator as follows :

```python
    create_imp_external_table = BigQueryCreateExternalTableOperator(
        task_id=f"create_imp_external_table",
        bucket='my-bucket',
        source_objects=["/data/userdata1.parquet"], #pass a list
        destination_project_dataset_table=f"my-project.my_dataset.parquet_table",
        source_format='PARQUET', #use source_format instead of file_format
    )
```

## Note

When moving data to BigQuery, bigquery will automatically generate the schema based off the content in the files, however if the contents of any of the files
vary greatly or the content of any of the files conflict we might have errors as big query will not be able to determine which schema to use since the files conflict.
In this scenario we can manually set autodetect to true in the external data config options or we can manually set the schema
