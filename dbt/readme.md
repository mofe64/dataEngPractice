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
