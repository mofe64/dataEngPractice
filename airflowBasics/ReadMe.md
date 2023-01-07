## Setting the Airflow user:

On Linux, the quick-start needs to know your host user-id and needs to have group id set to 0.
Otherwise the files created in `dags`, `logs` and `plugins` will be created with root user.
You have to make sure to configure them for the docker-compose:

    ```bash
    mkdir -p ./dags ./logs ./plugins
    echo -e "AIRFLOW_UID=$(id -u)" > .env
    ```

On Windows you will probably also need it. If you use MINGW/GitBash, execute the same command.

To get rid of the warning ("AIRFLOW_UID is not set"), you can create `.env` file with
this content:

    ```
    AIRFLOW_UID=50000
    ```

## Official docker set up file

```shell (linux)
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/stable/docker-compose.yaml'
```

```shell (windows)
curl -O docker-compose.yaml 'https://airflow.apache.org/docs/apache-airflow/stable/docker-compose.yaml'
```


Note : Airflow version provided with official docker set up file does not work with GCP as a result we modify it to use our custom docker file, which adds
the necessary packages and requirements to ariflow to work with GCP

## Links

1. https://stackoverflow.com/questions/71500915/curl-lfo-errors-from-windows-powershell
