# Package the flow as docker image

You can package the flow as a docker image and refer to it in the chart.

```bash
# Download the flows
wget https://raw.githubusercontent.com/datastax/aiexec-charts/main/examples/flows/basic-prompting-hello-world.json
# Build the docker image locally
docker build -t myuser/aiexec-hello-world:1.0.0 .
# Push the image to DockerHub
docker push myuser/aiexec-hello-world:1.0.0
```

The use the runtime chart to deploy the application:

```bash
helm repo add aiexec https://khulnasoft.github.io/aiexec
helm repo update
helm install aiexec-runtime aiexec/aiexec-runtime \
    --set "image.repository=myuser/aiexec-hello-world" \
    --set "image.tag=1.0.0"
```
