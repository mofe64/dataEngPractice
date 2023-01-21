FROM prefecthq/prefecthq/prefect:2.7.7-python

COPY requirements.txt .

RUN pip install -r requirements.txt --trusted-host pypi.python.org --no-cache-dir
COPY ../demo1 /opt/prefect/flows
COPY ../demo2 /opt/prefect/flows


