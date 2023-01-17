## Helpful

### Create virtualenv

```shell
    python -m venv envname
```

### activate virtualenv

```shell
     # In cmd.exe
     venv\Scripts\activate.bat
     # In PowerShell
     venv\Scripts\Activate.ps1
```

### install from requirements.txt

```shell
    pip install -r requirements.txt
```

### Prefect UI

With the venv activated run `prefect orion start`
We should also configure prefect to communicate with server by running

```shell
    prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api
```

### Blocks

Blocks are a primitive within Prefect that enable the storage of configuration and provide an interface for interacting with external systems.
Blocks are useful for configuration that needs to be shared across flow runs and between flows.
Blocks can be created using the UI as well as using code

Note when sql alchemy block don't forget to add the driver in this project we used a sync driver and (postgresql + psycopg2)

[Docs](https://docs.prefect.io/concepts/blocks/)

# Debug

If getting can't find version 1.5.2 of pandas error, update python version and recreate virtual env so it reflects new python version

## Links

1. https://stackoverflow.com/questions/54938026/curl-unknown-error-0x80092012-the-revocation-function-was-unable-to-check-r
