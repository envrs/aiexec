# AiExec IDE chart

Helm chart for AiExec as IDE with a persistent storage or an external database (for example PostgreSQL).


## Quick start

Install the chart:

```bash
helm repo add aiexec https://khulnasoft.github.io/aiexec
helm repo update
helm install aiexec-ide aiexec/aiexec-ide -n aiexec --create-namespace
```


## Examples
See more examples in the [examples directory](https://github.com/khulnasoft/aiexec/tree/main/examples/aiexec-ide).