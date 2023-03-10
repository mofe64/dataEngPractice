## Notes

### Installation

Once you know which adapter we want to use, we can install it as dbt-<adapter>. For example, if using Postgres:

```shell
 pip install dbt-postgres
```

This will install dbt-core and dbt-postgres only

[Available dbt adapters](https://docs.getdbt.com/docs/supported-data-platforms)

To set up a new dbt project we run

```
    dbt init
```

When you invoke dbt from the command line, dbt parses our dbt_project.yml and obtains the profile name,
which dbt needs to connect to your data warehouse.
dbt then checks your profiles.yml file for a profile with the same name.

A profile contains all the details required to connect to your data warehouse.
dbt will search the current working directory for the profiles.yml file and will default to the ~/.dbt/ directory if not found.
In our profiles.yml file, you can store as many profiles as you need. Typically, you would have one profile for each warehouse you use.

A profile consists of targets, and a specified default target.

Each target specifies the type of warehouse you are connecting to, the credentials to connect to the warehouse, and some dbt-specific configurations.
You may need to surround your password in quotes if it contains special characters.

The credentials you need to provide in your target varies across warehouses — [sample profiles for each supported warehouse](https://docs.getdbt.com/docs/supported-data-platforms)

dbt supports multiple targets within one profile to encourage the use of separate development and production environments
A typical profile for using dbt locally will have a target named dev, and have this set as the default.

We may also have a prod target within your profile, which creates the objects in our production schema. However,

If we have multiple targets in your profile, and want to use a target other than the default, qw can do this using the --target option when issuing a dbt command.
In our yml file

- `target` : This is the default target your dbt project will use. It must be one of the targets you define in your profile. Commonly it is set to dev.
- `outputs` : This will contain all the targest we wish to declare as well as their configuration options

Note the schema we define in our configuration options is where all our operations will be output to. If the schema doesn't exist, dbt will create it
The dbname refers to the database that owns the schema and must exist before we run the script

### Sample

```yaml
    local-postgres:
        target: dev
            outputs:
                dev:
                    type: postgres
                    threads: 4
                    host: localhost
                    port: 5432
                    user: username
                    pass: password
                    dbname: sample_ny_data
                    schema: dbt_schema
```

VALIDATING OUR WAREHOUSE CREDENTIALS
Use the debug command to check whether you can successfully connect to your warehouse. Simply run dbt debug from within a dbt project to test your connection.

[Connection profile docs](https://docs.getdbt.com/docs/get-started/connection-profiles)

## Materialization strategies

1. Table : drops table if it already exists in data warehouse and creates the table in the schema we are working with
2. View : drops view if it already exists in data warehouse and creates the view in the schema we are working with
3. Incremental : allows us to run our model incrementally, useful for data that doesn't change frequently, running the model will insert
   only the latest data in the table
4. Ephemeral : is a derived model

The from clause of our dbt model consists of
Sources :
This is the data loaded to our dwh that we use as a source for our models
Configuration for our sources are defined in yml files in the models folder
Used with the source marcro which will resolve the name to the right schema, plus build dependencies automatically
Source freshness can be defined and tested

Seeds :
These are CSV files stored in our repository under the seeds folder
They give us the benefit of version control
Runs with a special command `seed -s file_name`
recommended for data that doesn't change frequently

Ref :
This is a macro used to reference tables or views created by dbt. we only need to provide the table or view name,
the ref resolves the schema name and database name for us

We can run models in two ways

1. dbt run -m model_file_name
2. dbt run (this will run every model we have)

### Macros

In addition to the already defined macros which dbt gives us we can define our own macros as well.
Our macros will return some code which will be applied whenever they are used.
They allow us use control structures (eg if statements, loops) in SQL
They also allow us use environment variables in our dbt project while in production
Sample macro

```sql
    {# This macro returns the description of the payment_type #}
    {% macro get_payment_type_description(payment_type) -%}
        case {{payment_type}}
            when 1 then 'Credit card'
            when 2 then 'Cash'
            when 3 then 'No Cash'
        end
    {%- endmacro %}
```

## Packages

like libs in other programming langs
standalone dbt projects with models and macros that tackle a specific area
By adding a package, the packages models and macros will be part of our project
We import packages in the packages.yml file and by running `dbt deps`
We can find useful packages [here](https://hub.getdbt.com/)

## Variables

useful for defining values that should be used across the project
with a macro dbt allows us to provide data to models for compilation
to use a variable we use the {{var('...')}} function
variables can be defined in two ways in the dbt_project.yml file or on the command line

in the dbt_project.yml file they are defined as follows

```yml
vars:
  payment_type_values: [1, 2, 3, 4, 5, 6]
```

## Seeds

We can use seeds by adding the Csv file we want to use in our seeds folder and running `dbt seed`
This will create a table from the csv file in our db. dbt will use the same data types found in the csv file as the data types
for each column.
If we do not want this in our dbt_project.yml
dbt seed by default appends the values to table if it already exists to drop and recreate the table run
`dbt seed --full-refresh`

```yml
seeds:
  project_name:
    seed_file_name:
      +column_types:
        columnname: columntype
```

### Note - DBT BUILD

dbt build is an all in command, it will run the models, seeds, and tests all at once

## Tests & Documentation

Tests are assumptions we make about our data. In dbt tests are essentially a select query.
These assumptions get compiled to sql that returns the amounts of failing records
Tests are defined in the schema.yml file where our models are located.
We run our tests by running `dbt test`
we can also add documentation to our project in the schema.yml file as seen below

```yml
- name: stg_green_tripdata
  description: >
    Trip made by green taxis, also known as boro taxis and street-hail liveries.
    Green taxis may respond to street hails,but only in the areas indicated in green on the
    map (i.e. above W 110 St/E 96th St in Manhattan and in the boroughs).
    The records were collected and provided to the NYC Taxi and Limousine Commission (TLC) by
    technology service providers.
  columns:
    - name: tripid
      description: Primary key for this table, generated with a concatenation of vendorid+pickup_datetime
      tests:
        - unique:
            severity: warn
        - not_null:
            severity: warn
    - name: VendorID
      description: >
        A code indicating the TPEP provider that provided the record.
        1= Creative Mobile Technologies, LLC;
        2= VeriFone Inc.
    - name: Pickup_locationid
      description: locationid where the meter was engaged.
      tests:
        - relationships:
            to: ref('taxi_zone_lookup')
            field: locationid
            severity: warn
```

## Deployments

### Running a DBT project in prod

dbt cloud includes a scheduler we can use to create jobs to run in production
A single job can run multiple commands
jobs can also be triggered manually or on schedule
A job can also generate documentation that can be viewed under the run information
