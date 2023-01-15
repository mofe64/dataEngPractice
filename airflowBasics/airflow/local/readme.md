## Explanation

This folder contains the docker compose file which sets up our local postgres db. We will ingest some data from the web, to our local postgres via airflow
We connect this database to our airflow by making sure it is on the same network as airflow this is done via an external network.
Note - airflow also has an internal postgres service that it uses to store metadata however, it does not expose any ports since it is an internal service and as such will not conflict with our local postgres
