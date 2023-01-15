## Setup Google credentials

1. For the sake of standardization across config, we renamed the gcp-service-accounts-credentials file to google_credentials.json & store it in your $HOME directory in the directory like below
   ```
   ~/.google/credentials
   ```

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

## Getting the Official docker airflow set up file

```shell (linux)
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/stable/docker-compose.yaml'
```

```shell (windows)
curl -O docker-compose.yaml 'https://airflow.apache.org/docs/apache-airflow/stable/docker-compose.yaml'
```

# Important

Airflow version provided with official docker set up file does not work with GCP as a result we modify it to use our custom docker file, which adds
the necessary packages and requirements to ariflow to work with GCP
Note : In our docker compose file, we set airflow load examples to false, to prevent the preloading of our web console with examples which might make it confusing
Back in our `docker-compose.yaml`:

- In `x-airflow-common`:

  - Remove the `image` tag, to replace it with your `build` from our custom Dockerfile, as shown
    ```
        build:
            context: .
            dockerfile: ./Dockerfile
    ```
  - Mount your `google_credentials` in `volumes` section as read-only

    ```volumes:
            - ./dags:/opt/airflow/dags
            - ./logs:/opt/airflow/logs
            - ./plugins:/opt/airflow/plugins
            - ~/.google/credentials/:/.google/credentials:ro

    ```

  - Set environment variables: `GCP_PROJECT_ID`, `GCP_GCS_BUCKET`, `GOOGLE_APPLICATION_CREDENTIALS` & `AIRFLOW_CONN_GOOGLE_CLOUD_DEFAULT`, as per your config.

  ```
    GOOGLE_APPLICATION_CREDENTIALS: /.google/credentials/google_credentials.json
    AIRFLOW_CONN_GOOGLE_CLOUD_DEFAULT: 'google-cloud-platform://?extra__google_cloud_platform__key_path=/.google/credentials/google_credentials.json'
    GCP_PROJECT_ID: 'project id'
    GCP_GCS_BUCKET: "bucket name"
  ```

- Change `AIRFLOW__CORE__LOAD_EXAMPLES` to `false` (optional)

## Execution

Build the image (only first-time, or when there's any change in the Dockerfile, takes ~15 mins for the first-time):

```
docker-compose build
```

or (for legacy versions)

```
docker build .
```

Initialize the Airflow scheduler, DB, and other config

```
docker-compose up airflow-init
```

Kick up the all the services from the container:

```
docker-compose up
```

In another terminal, run `docker-compose ps` to see which containers are up & running (there should be 7, matching with the services in your docker-compose file).

Login to Airflow web UI on ``localhost:8080` with default creds: `airflow/airflow`

Run your DAG on the Web Console.

On finishing your run or to shut down the container/s:

```
docker-compose down
```

To stop and delete containers, delete volumes with database data, and download images, run:

```
docker-compose down --volumes --rmi all
```

or

```
docker-compose down --volumes --remove-orphans
```

## Links

1. https://stackoverflow.com/questions/71500915/curl-lfo-errors-from-windows-powershell

## Debug

1. If having gcs object create forbidden error, check to see that the GCP resources(Big Query and Cloud Storage) have been created first, if they have not create them by running the terraform scripts
