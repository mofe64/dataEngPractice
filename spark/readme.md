# Installatuin guides

### Spark setup on linux

Download OpenJDK 11 or Oracle JDK 11 (It's important that the version is 11 - spark requires 8 or 11)
We'll use [OpenJDK](https://jdk.java.net/archive/)

Download it (e.g. to `~/spark`):

```
mkdir spark
cd spark
wget https://download.java.net/java/GA/jdk11/9/GPL/openjdk-11.0.2_linux-x64_bin.tar.gz
```

Unpack it:

```bash
tar xzfv openjdk-11.0.2_linux-x64_bin.tar.gz
```

define `JAVA_HOME` and add it to `PATH`:

```bash
export JAVA_HOME="${HOME}/spark/jdk-11.0.2"
export PATH="${JAVA_HOME}/bin:${PATH}"
```

check that it works:

```bash
java --version
```

Output:

```
openjdk 11.0.2 2019-01-15
OpenJDK Runtime Environment 18.9 (build 11.0.2+9)
OpenJDK 64-Bit Server VM 18.9 (build 11.0.2+9, mixed mode)
```

Remove the archive:

```bash
rm openjdk-11.0.2_linux-x64_bin.tar.gz
```

### Installing Spark

Download Spark. Use 3.3.0 version:

```bash
wget https://dlcdn.apache.org/spark/spark-3.3.1/spark-3.3.1-bin-hadoop3.tgz
```

Unpack:

```bash
tar xzfv spark-3.3.0-bin-hadoop3.tgz
```

Remove the archive:

```bash
rm spark-3.3.0-bin-hadoop3.tgz
```

Add it to `PATH`:

```bash
export SPARK_HOME="${HOME}/spark/spark-3.3.0-bin-hadoop3"
export PATH="${SPARK_HOME}/bin:${PATH}"
```

### Testing Spark

Execute `spark-shell` and run the following:

```scala
val data = 1 to 10000
val distData = sc.parallelize(data)
distData.filter(_ < 10).collect()
```

### spark setup on windows

Install Java 11
Add Java to path
create directory eg in c drive tools/hadoop-3.2.0
Download hadoop binaries from [here](https://github.com/cdarlint/winutils/tree/master/hadoop-3.2.0)
or we can run this to download

```bash
    HADOOP_VERSION="3.2.0"
    PREFIX="https://raw.githubusercontent.com/cdarlint/winutils/master/hadoop-${HADOOP_VERSION}/bin/"

    FILES="hadoop.dll hadoop.exp hadoop.lib hadoop.pdb libwinutils.lib winutils.exe winutils.pdb"

    for FILE in ${FILES}; do
        wget "${PREFIX}/${FILE}"
    done
```

Add hadoop binaries to path

```bash
    export HADOOP_HOME="/c/tools/hadoop-3.2.0"
    export PATH="${HADOOP_HOME}/bin:${PATH}"
```

Next download spark
Select version 3.0.3 (3.2.0 has problems with starting the shell on Windows)

```bash
    wget https://dlcdn.apache.org/spark/spark-3.0.3/spark-3.0.3-bin-hadoop3.2.tgz
```

Unpack it in some location without spaces, e.g. c:/tools/:

```bash
    tar xzfv spark-3.0.3-bin-hadoop3.2.tgz
```

Let's also add it to PATH:

```bash
    export SPARK_HOME="/c/tools/spark-3.0.3-bin-hadoop3.2"
    export PATH="${SPARK_HOME}/bin:${PATH}"
```

Testing it
Go to this directory

```bash
    cd spark-3.0.3-bin-hadoop3.2
```

And run spark-shell:

```bash
    ./bin/spark-shell.cmd
```

At this point you may get a message from windows firewall — allow it.
Ignore any illegal reflective access operation

run this to finalize tests

```scala
    val data = 1 to 10000
    val distData = sc.parallelize(data)
    distData.filter(_ < 10).collect()
```

### pyspark

This document assumes we already have python.

To run PySpark, we first need to add it to `PYTHONPATH`:

```bash
export PYTHONPATH="${SPARK_HOME}/python/:$PYTHONPATH"
export PYTHONPATH="${SPARK_HOME}/python/lib/py4j-0.10.9-src.zip:$PYTHONPATH"
```

Make sure that the version under `${SPARK_HOME}/python/lib/` matches the filename of py4j or you will
encounter `ModuleNotFoundError: No module named 'py4j'` while executing `import pyspark`.

For example, if the file under `${SPARK_HOME}/python/lib/` is `py4j-0.10.9.3-src.zip`, then the
`export PYTHONPATH` statement above should be changed to

```bash
export PYTHONPATH="${SPARK_HOME}/python/lib/py4j-0.10.9.3-src.zip:$PYTHONPATH"
```

Now you can run Jupyter or IPython to test if things work. Go to some other directory, e.g. `~/tmp`.

Download a CSV file that we'll use for testing:

```bash
wget https://s3.amazonaws.com/nyc-tlc/misc/taxi+_zone_lookup.csv
```

Now let's run `ipython` (or `jupyter notebook`) and execute:

```python
import pyspark
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .master("local[*]") \
    .appName('test') \
    .getOrCreate()

df = spark.read \
    .option("header", "true") \
    .csv('taxi+_zone_lookup.csv')

df.show()
```

Test that writing works as well:

```python
df.write.parquet('zones')
```
