## Spark Stuff

### Some sample operations

Note: We use a jupyter notebook to run the bulk of commands here

1. Read CSV file
   spark by default does not infer types when reading files, so we can provide a schem definition for a csv file
   one trick we can use is to read a subset of the data with pandas so we can get the types and use that data to create a schema eg
   Get a subset of data from original (101 rows in this instance)
   We need to do this cause the original file might have thousands of rows so we want ro reduce the size.
   Note this is a linux command

   ```bash
    !head -n 101 original.csv > head.csv
   ```

   Now we can read subset into pandas and get the types eg

   ```python
    import pandas as pd
    df_pandas = pd.read_csv('head.csv')

    df_pandas.dtypes
   ```

   we can define a schema as follows

   ```python
        from pyspark.sql import types
        schema = types.StructType([
            types.StructField('col1Name', types.StringType(), True),
            types.StructField('col2Name', types.IntegerType(), True),
            types.StructField('col3Name', types.TimestampType(), True),
        ])
   ```

   Note the true we put in each type means that the field is nullable
   Then use the schema when creating a spark dataframe

   ```python
       df = spark.read \
           .option("header", "true") \
           .schema(schema) \
           .csv('file.csv')
   ```

2. Write dataframe to parquet
   ```python
       df.write.parquet('directory')
   ```
3. read parquet files
   Note because parquet contain the information about schema, spark is able to use that to infer the type for each column
   ```python
       df = spark.read.parquet('directory')
   ```
   To view the schema for a df, we can run `df.printSchema()`

Spark comes with a bunch of executors that can be used to carry out tasks on multiple files in parrallel. If we are processing multiple files, each
file goes to a seperate executor.
However if we have a single file, only one executor will be used to work on that file.
We can break that file into multiple partititions which will be handle by individual executors to do this we use the repartition command as follows
Note our repartition command is a transformation operation and as such is lazy

```python
    df.repartition(number_of_partitions)
```

### Spark Dataframes

Spark dfs can do the same stuff as pandas df, but we can carry out some additional operations
eg to select just a few columns from df we can run

```python
    df.select('col1', 'col2')
        .filter(df.col == 'value')
        .show()
```

### Note

filter is a spark tranformation operation and is by default lazy, as a refuslt it will not be executed right away, until we carry out an action
Actions are eager

Transformations include

1. selecting columns
2. filtering columns
3. applying functions to columns
4. joins
5. group by

Spark will create a sequence of transformations and stores them until we carry out an action such as calling .show()
at this point spark will execute the sequence of transformations
Actions include

1. Show, take, head
2. write

Spark provides us with some loaded functions, to access them we import them from pyspark.sql

```python
    from pyspark.sql import functions as F
```

using our F import we can access all inbuilt functions eg

```python
    df.withColumn('new_col_name', F.to_date(df.pickup_datetime)) \
        .show()
```

Note : .withColumn adds a new column to the df, if we provide a col name which aleady exists, we will overwrite the old column

We can also define our own functions eg

```python
    def some_fn(some_param):
        perform_some_action
        return some_value

    some_udf = F.udf(some_fn, returnType=types.StringType())

    df.withColumn('new_col_name', some_udf(df.pickup_datetime)) \
        .show()
```

### Spark clusters

When we set up spark as follows

```python
spark = SparkSession.builder \
    .master("local[*]") \
    .appName('test') \
    .getOrCreate()
```

We are setting up spark to use a local cluster on the host machine
A Spark cluster is made up of a master and executors
The ideal flow, is that we have some spark code or some python script which we will send to the spark master(on our localhost:4040)
we use a special command called spark submit to send our code to the master, and we specify what kind of resources we need for this job.

In the cluster, we have machines which will execute this job and they are called executors, they are coordinated by the spark master
Ideally the executors will work on some data which is usually stored in some datalake eg s3 or GCS which are external to the system

### Group by

When we use a group by in spark the operation is carried out in multiple stages
first the group by operation is carried out in every single partition of our data individually, this will result in multiple results
next the individual group by results undergo a process called shuffling in which results with the same group by key are placed in the same partition
finally the partitions are combined to get our final result

### Joins

```python
    df_join = df1.join(df2, on=['col1', 'col2'], how='outer')
```

### Connecting spark to GCP

1. Download cloud storage connector for hadoop 3.x
   we can download it from [here](https://cloud.google.com/dataproc/docs/concepts/connectors/cloud-storage#clusters)
   The file is also available in gogole cloud storage to we can run
   make a directory eg lib
   ```
    gsutil cp gs://hadoop-lib/gcs/gcs-connector-hadoop3-2.2.5.jar gcs-connector-hadoop3-2.2.5.jar
   ```
2. Configure

   ```python
   import pyspark
   from pyspark.sql import SparkSession
   from pyspark.conf import SparkConf
   from pyspark.context import SparkContext

   credentials_location = '~/path_to_dir/google_credentials.json'
    # The location of our spark.jars has to match where we downloaded the gcs hadoop connector to
   conf = SparkConf() \
       .setMaster('local[*]') \
       .setAppName('test') \
       .set("spark.jars", "./lib/gcs-connector-hadoop3-2.2.5.jar") \
       .set("spark.hadoop.google.cloud.auth.service.account.enable", "true") \
       .set("spark.hadoop.google.cloud.auth.service.account.json.keyfile", credentials_location)

    sc = SparkContext(conf=conf)

    # we set up hadoop config to be able to handle gs connections and also provide the location of our credentials
    hadoop_conf = sc._jsc.hadoopConfiguration()
    hadoop_conf.set("fs.AbstractFileSystem.gs.impl",  "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS")
    hadoop_conf.set("fs.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem")
    hadoop_conf.set("fs.gs.auth.service.account.json.keyfile", credentials_location)
    hadoop_conf.set("fs.gs.auth.service.account.enable", "true")

    spark = SparkSession.builder \
    .config(conf=sc.getConf()) \
    .getOrCreate()

    # Now we can read directly from the gcs bucket eg
    df_green = spark.read.parquet('gs://data_lake_de-zoomcamp-nytaxi/pq/green/*/*')
   ```

### Creating a local spark cluster manually

All our commands above have been run using a spark session builder, with `.setMaster('local[*]')`, this abstracts the creation and connection to the local spark cluster.
We can also achieve same manually by following the [docs](https://spark.apache.org/docs/latest/spark-standalone.html)

1. first go to spark home directory (where spark was installed) then we execute the following command

```
    ./sbin/start-master.sh
```

Once started, the master will print out a spark://HOST:PORT URL for itself, which you can use to connect workers to it, or pass as the “master” argument to SparkContext. You can also find this URL on the master’s web UI, which is http://localhost:8080 by default.

```
spark = SparkSession.builder \
    .master("masterUrl") \
    .appName('test') \
    .getOrCreate()
```

By default workers are not created for us

2. we can start one or more workers and connect them to the master via:

```
    ./sbin/start-worker.sh <master-spark-URL>
```

for older versions of spark

```
    ./sbin/start-slave.sh <master-spark-URL>
```

We can use a python script instead of a notebook to run our spark as well, we simply put the spark code in a python file and execute the file as normal
if we get no module named pyspark errors make sure the pyspark has been added to path

we can also paramaterize the python script by using argparse and passing in the argumens when executing the file as normal

In an instance where we have multiple clusters, hardcoding the master url like

```
spark = SparkSession.builder \
    .master("masterUrl") \
    .appName('test') \
    .getOrCreate()
```

is not scalable and practical, we might also want to specify other configuration options such as how many executors we want and hardcoding these values is also not practical. we need to specify the config options outside the python script and we can do that using a tool called spark submit

In our spark home we use th spark submit script eg

```bash
url="master_url"
spark-submit \
    --master="${url}"
    --executor-memory 1G \ #optional
    --total-executor-cores 4 \ #optional
    python_script.py \
        --param=param_value

```

# Important

After running our jobs, we need to manually stop our workers and masters
we can do so by running in our spark home

```bash
    ./sbin/stop-slave.sh # for older versions to stop workers for newer versions we use stop-worker
    ./sbin/stop-master.sh
```

## Setting up clusters on google cloud

1. On google cloud, search for dataproc, create cluster, in optional components select docker and jupyter notebook
2. click on created cluster, submit job, job type should be pyspark. we also need to specify the path to the main python file, we can upload the python code to gcs and provide the path. Note in whatever python file we are specifying we do not want to specify master in our session builder, so our session builder should look like

```python
spark = SparkSession.builder \
    .appName('test') \
    .getOrCreate()
```

3. if there are any additional python files, specify the path to them, they should also be uploaded to the code bucket
4. any arguments we want to use should be specified in the arguments tab, specify the argument in full syntax format eg `--param=param_value`
5. submit

### Using Google Cloud SDK for submitting to dataproc

([link](https://cloud.google.com/dataproc/docs/guides/submit-job#dataproc-submit-job-gcloud))

## Important our service account used in our google-credentials need to have permissions to access and use dataproc

### we can give the service account dataproc admin role to enable this

### Note we can integrate this process with airflow by using a bash operator to run the script below, there is also a spark submit operator,but the bash operator is easier

```bash
gcloud dataproc jobs submit pyspark \
    --cluster=de-zoomcamp-cluster \ # cluster name
    --region=europe-west6 \ # cluster regions
    gs://dtc_data_lake_de-zoomcamp-nytaxi/code/06_spark_sql.py \ # main python file
    -- \ # args for main pyth0n file
        --input_green=gs://dtc_data_lake_de-zoomcamp-nytaxi/pq/green/2020/*/ \
        --input_yellow=gs://dtc_data_lake_de-zoomcamp-nytaxi/pq/yellow/2020/*/ \
        --output=gs://dtc_data_lake_de-zoomcamp-nytaxi/report-2020
```

### we can also use spark to write to Big Query

Write results to big query ([docs](https://cloud.google.com/dataproc/docs/tutorials/bigquery-connector-spark-example#pyspark)):

```bash
gcloud dataproc jobs submit pyspark \
    --cluster=de-zoomcamp-cluster \
    --region=europe-west6 \
    --jars=gs://spark-lib/bigquery/spark-bigquery-latest_2.12.jar
    gs://dtc_data_lake_de-zoomcamp-nytaxi/code/06_spark_sql_big_query.py \
    -- \
        --input_green=gs://dtc_data_lake_de-zoomcamp-nytaxi/pq/green/2020/*/ \
        --input_yellow=gs://dtc_data_lake_de-zoomcamp-nytaxi/pq/yellow/2020/*/ \
        --output=trips_data_all.reports-2020
```
