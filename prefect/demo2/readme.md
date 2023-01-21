## Note

Some blocks may not be available on prefect orion UI by default so we have to register the mocule containing those blocks first first
we can register modules as follows

```shell
    prefect block register -m prefect_gcp
```

This would add the gcp blocks to our UI

## Building deployments via CLI

```shell
    prefect deployment build path_to_file:flow_entrypoint -n name
```

this will create a yaml file which represents the deployment meta data
if our flow requries parameters we can specify them in parameters section of the yaml file
we can also specify scheduling of when our flows should run via the cron flag
we can also set the schedule after the deployment has been created with the set schedule option

```shell
    prefect deployment build path_to_file:flow_entrypoint -n name --cron "0 0 * * *"
```

scheduling can alos be done via the UI and it supports interval, cron and rule based scheduling

to apply our deployment we run

```shell
    prefect deployment apply name_of_yaml_file.yaml
```

this will send our metadata to the prefect api to be applied
After applying our deployment we can see it on our UI. From our UI we have the ability to run our flow through a quick run or a custom run
A custom run allows us modify individual parameters for each run

A deployment will send the flow to a work queue where it will wait for an agent to pick it up and execute it

### Agents

Each run requires an agent that will execute it.
An agent is a lightweight python process and it lives in our execution environment. Each agent pulls from a work queue
We can have multiple work queues and each deployment specifies which work queue to use
the default workqueue is called default
to start an agent

```shell
    prefect agent start --work-queue "workqueue name"
```

Once an agent has been started it will pick up any deployment in the specified work queue and execute, any sunsequent deployment
sent to that work queue will be executed by the agent as well

### Notifications

We can also create notifications via our UI
We set the run states on which we want to be notified. Note : crashed state refers to infrastructure failure not flow failure
