### Notes

After building our image, we upload the docker image to docker hub
prefect provides a docker block which we can use to load a docker image into prefect.
We can find this block in the UI
We can use this to configure a brand new docker image with with a new prefect image or we can
sepcify the image to be the docker image we pushed to docker hub, this will ensure that we get a
docker image preloaded with our flow code
Set image pull policy to always

Alternatively we can create the docker block with code by running

```python
    from prefect.infrastructure.docker import DockerContainer

    docker_block = DockerContainer(
        image="image",
        image_pull_policy="ALWAYS"
        auto_remove=True
    )

    docker_block.save("blockname", overwrite=True)
```

Now we can deploy our docker flow via the cmd or via python code
as follows

```python
    from prefect.infrastructure.docker import DockerContainer
    from prefect.deployments import Deployment
    from flow_file import flow_func

    docker_block = DockerContainer.load("blockname")

    docker_dep = Deployment.build_from_flow(
        flow=flow_func,
        name='docker-flow',
        infrastructure=docker_block
    )

    if __name__ == "__main__":
        docker_dep.apply()
```

### Note

We shoudl make sure that our prefect api url config is set so that our docker container can interface with prefect
Next we need to make sure we have an agent that will pick up our flow

We can also run our flow manually by running

```shell
    prefect deployment run flow name - p "months=[2,1]"
```
