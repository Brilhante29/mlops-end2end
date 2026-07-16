# MLOps Lifecycle Capability

## ADDED Requirements

### Requirement: Reproducible local lifecycle

The system SHALL execute data generation, validation, training, registration, quality gating, alias promotion, serving, monitoring, and benchmarking from one Docker command without a secret.

#### Scenario: Clean runtime reaches production

- **GIVEN** an empty container runtime and no external credentials
- **WHEN** the default Docker command runs
- **THEN** the Airflow Dag completes, MLflow assigns `champion`, FastAPI becomes healthy, and a benchmark JSON is emitted

### Requirement: Promotion is quality-gated

The system SHALL assign the deployment alias only when ROC AUC meets the configured threshold.

#### Scenario: Candidate passes

- **GIVEN** a candidate whose ROC AUC is at least `0.80`
- **WHEN** promotion runs
- **THEN** the registry adapter assigns the `champion` alias to that model version

#### Scenario: Candidate fails

- **GIVEN** a candidate whose ROC AUC is below `0.80`
- **WHEN** promotion runs
- **THEN** promotion fails and the registry port is not called

### Requirement: Deployment is version-decoupled

The inference service SHALL load `models:/portfolio-risk-model@champion` instead of a hard-coded model version.

#### Scenario: Alias resolves

- **GIVEN** MLflow contains an approved aliased model
- **WHEN** FastAPI starts
- **THEN** health reports the resolved alias and concrete version

### Requirement: Evidence is numeric

The benchmark SHALL report time-to-production seconds, ROC AUC, accuracy, inference p95 milliseconds, requests per second, model version, run identifier, and Prometheus export evidence.

