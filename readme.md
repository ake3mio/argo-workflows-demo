# argo workflows demo

This repo contains a quick dirty demo setup and usage of [argo workflows](https://argo-workflows.readthedocs.io/en/stable/) for data processing pipelines.

# Requirements

- Docker desktop with kubernetes enabled
- Terraform
- Python 3
- Argo cli (follow the instructions here: https://github.com/argoproj/argo-workflows/releases/)


## Setup argo workflows

This repo has terraform to deploy argo on to a docker desktop kubernetes cluster for a demo setup.
The terraform can be found in the [tf](tf) directory.

Run the terraform by executing the following in a shell from the [tf](tf) directory:

```shell
terraform init
terraform apply -auto-approve 
```

After the terraform apply completes, wait about 30-60 seconds and then you can visit the following urls:

- Argo UI at http://localhost:32746: Visualise and UI submission of workflows
- Minio: http://localhost:30091: A S3 compliant store which is configured to store the artifact from workflow runs.


## Demos

You can execute workflows in several ways on argo, including via:

- argo cli pointing to a kubernetes manifest
- triggering rest apis on the argo server
- using the [hera](https://hera.readthedocs.io/en/stable/) python framework


### [simple-workflow.yaml](manifest-workflows%2Fsimple-workflow.yaml)
This is a simple sequential workflow.

Parameters are provided to a download-marketdata step.
The download-marketdata step saves market to a file which through argo is automatically saved to an s3 bucket as an artifact.
The strategy step uses the artifact as an input and saves results as an output artifact

Run:
```shell
argo submit -n argo --watch ./manifest-workflows/simple-workflow.yaml
```


![Screenshot 2024-04-01 at 15.27.52.png](docs%2FScreenshot%202024-04-01%20at%2015.27.52.png)
![Screenshot 2024-04-01 at 15.28.15.png](docs%2FScreenshot%202024-04-01%20at%2015.28.15.png)


### [parallel-workflow.yaml](manifest-workflows%2Fparallel-workflow.yaml)

This demos dynamic fanout dependent on the outputs from a previous task.
In the context of the demo - multiple tickers are returned from the initial step, which result in market downloads being executed in parallel per ticker and then a strategy per ticker run in parallel.

Run:
```shell
argo submit -n argo --watch ./manifest-workflows/parallel-workflow.yaml
```

![Screenshot 2024-04-01 at 15.34.57.png](docs%2FScreenshot%202024-04-01%20at%2015.34.57.png)

### [parallel-workflow-supplied-values.yaml](manifest-workflows%2Fparallel-workflow-supplied-values.yaml)
This is the same as parallel-workflow.yaml, but the workflow can be saved as a workflow template. The parameters need to be manually supplied to run the workflow.
This could be supplied via, the UI, the cli or as in this demo - a rest call.

Run:

```shell
kubectl apply -f ./manifest-workflows/parallel-workflow-supplied-values.yaml 
kubectl apply -f ./manifest-workflows/parallel-workflow-supplied-values-event-binding.yaml

ARGO_TOKEN="Bearer $(kubectl -n argo get secret argo-api-token -o=jsonpath='{.data.token}' | base64 --decode)"

curl  http://localhost:32746/api/v1/events/argo/parallel-workflow-supplied-values \
    -H "Authorization: $ARGO_TOKEN" \
    -d '{"start_date": "2022-01-01", "end_date": "2024-01-01"}'

```

![Screenshot 2024-04-01 at 15.47.15.png](docs%2FScreenshot%202024-04-01%20at%2015.47.15.png)


### [main.py](src%2Fworkflow%2Fmain.py)

This is an example of how to use the [hera](https://hera.readthedocs.io/en/stable/) python framework to create workflows.

Run:

```shell
python ./src/workflow/main.py
```

![Screenshot 2024-04-01 at 15.57.11.png](docs%2FScreenshot%202024-04-01%20at%2015.57.11.png)


## Untested but useful functionality

- [Daemon Containers](https://argo-workflows.readthedocs.io/en/stable/walk-through/daemon-containers/) - These are pods that can be span up for the duration of the workflow. Example use-cases: shared database, message broker etc.
- [Sidecars](https://argo-workflows.readthedocs.io/en/stable/walk-through/sidecars/) - Extra containers that can run in the same pod as a task. These will also share the same networking and volume.
- [Cron Workflows](https://argo-workflows.readthedocs.io/en/stable/cron-workflows/) - workflows that will execute on a predefines schedule.
- [Argo events](https://argoproj.github.io/argo-events/) integration - Can be used to do task such as trigger a workflow when code is pushed to a branch, a s3 bucket is updated, (etc.) orr even trigger another workflow, a slack message, a email (etc.) when a work flow is completed.

## Clean up

```shell
kubectl -n argo delete workflow --all 

cd ./tf

terraform destroy -auto-approve
```