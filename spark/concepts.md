## Spark Stuff

### Some sample operations

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
