# Design: mlops-end2end

## Architecture

Pipeline architecture coordinates artifact-producing stages. A small ports-and-adapters boundary protects the promotion policy from Airflow, MLflow, FastAPI, and storage details.

```text
Airflow Dag
  -> generate + Pandera contract
  -> scikit-learn train + MLflow run/version
  -> pure quality policy -> MLflow alias
  -> FastAPI inference -> Prometheus metrics
  -> benchmark JSON
```

Dependencies point inward: adapters implement application ports; domain policy imports no framework. Stage boundaries exchange paths and identifiers, not large data frames through XCom.

## OpenSpec Self-Challenge

| Question | Answer | Consequence |
|---|---|---|
| Does Airflow solve a present force? | Yes. The claim includes dependencies, retries, stage evidence, and orchestration. | Use the stable `airflow.sdk` authoring surface and a three-task Dag. |
| Is a microservice topology required? | No. Independent deployment is not part of the benchmark. | Keep one image and one bounded runtime. |
| Are Kafka or RabbitMQ required? | No. There is no event stream, fan-out, or asynchronous load target. | Messaging is `none`. |
| Does Kumo apply? | No. The default and measured path has no AWS behavior. | Cloud mode is `none`; do not add a fake cloud boundary. |
| Should drift be included? | No. It has a separate repository and metric. | Emit serving telemetry here; consume it in #22 later. |
| Is time-to-production too broad? | It intentionally measures lifecycle friction. | Report AUC and inference p95 separately so quality and serving cost remain visible. |
| Can policy run without frameworks? | Yes. The quality gate accepts a registry port and a value object. | Unit tests prove DIP and substitutability with a recording adapter. |
| Is a notebook useful here? | Not for the operational path. | Keep the runtime script-first; notebooks are excluded. |

## Revisit Triggers

- Add a distributed Airflow executor only when parallel stage pressure is measured.
- Add Postgres only when concurrent metadata writers or durability become part of the claim.
- Add a cloud adapter only when a concrete managed-service behavior is required; use Kumo first for AWS-compatible behavior.
- Extract shared lifecycle contracts into the reuse kit only after a second repository confirms the same shape.

