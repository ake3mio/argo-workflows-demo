from hera.workflows import Workflow, WorkflowsService, Container, Parameter, DAG, NoneArchiveStrategy, Artifact, \
    S3Artifact, script
from hera.workflows.models import ImagePullPolicy

START_DATE = "2020-01-01"
END_DATE = "2024-01-01"


@script(image="python:3.9.12-slim", image_pull_policy=ImagePullPolicy.if_not_present)
def get_tickerconfig(start_date, end_date):
    import json
    import sys
    json.dump([
        {
            "ticker": "MSFT",
            "start_date": start_date,
            "end_date": end_date,
        },
        {
            "ticker": "AAPL",
            "start_date": start_date,
            "end_date": end_date,
        },
        {
            "ticker": "TSLA",
            "start_date": start_date,
            "end_date": end_date,
        },
    ], sys.stdout)


get_market_data = Container(
    name="marketdata",
    inputs=[
        Parameter(name="ticker"),
        Parameter(name="start_date"),
        Parameter(name="end_date"),
    ],
    arguments=[
        Parameter(name="ticker", value="{{item.ticker}}"),
        Parameter(name="start_date", value="{{item.start_date}}"),
        Parameter(name="end_date", value="{{item.end_date}}"),
    ],
    outputs=[
        Artifact(
            name="data",
            path="/tmp/marketdata_{{inputs.parameters.ticker}}_{{inputs.parameters.start_date}}_{{inputs.parameters.end_date}}.csv",
            archive=NoneArchiveStrategy(),
        )
    ],
    image="marketdata",
    image_pull_policy=ImagePullPolicy.if_not_present,
    command=["python3", "/app/main.py"],
    args=[
        "{{inputs.parameters.ticker}}",
        "{{inputs.parameters.start_date}}",
        "{{inputs.parameters.end_date}}",
    ]
)

run_strategy = Container(
    name="strategy",
    inputs=[
        S3Artifact(name="data", path="/tmp", key="argo-runs/{{workflow.name}}/"),
        Parameter(name="ticker"),
        Parameter(name="start_date"),
        Parameter(name="end_date"),
    ],
    arguments=[
        Parameter(name="ticker", value="{{item.ticker}}"),
        Parameter(name="start_date", value="{{item.start_date}}"),
        Parameter(name="end_date", value="{{item.end_date}}"),
    ],
    outputs=[
        Artifact(
            name="results",
            path="/tmp/results_{{inputs.parameters.ticker}}_{{inputs.parameters.start_date}}_{{inputs.parameters.end_date}}.csv",
            archive=NoneArchiveStrategy(),
        )
    ],
    image="strategy",
    image_pull_policy=ImagePullPolicy.if_not_present,
    command=["python3", "/app/main.py"],
    args=[
        "{{inputs.parameters.ticker}}",
        "{{inputs.parameters.start_date}}",
        "{{inputs.parameters.end_date}}",
    ]
)

with Workflow(
        generate_name="demo-py-parallel-workflow-",
        entrypoint="steps",
        namespace="argo",
        workflows_service=WorkflowsService(host="http://localhost:32746"),
        image_pull_policy=ImagePullPolicy.if_not_present,
) as w:
    with DAG(name="steps"):
        tickerconfig = get_tickerconfig(
            arguments={
                "start_date": START_DATE,
                "end_date": END_DATE
            }
        )
        market_data = get_market_data(with_param=tickerconfig.result)
        strategy = run_strategy(with_param=tickerconfig.result)

        tickerconfig >> market_data >> strategy

w.create(wait=False)
