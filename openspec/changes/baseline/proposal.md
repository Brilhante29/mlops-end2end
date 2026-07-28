# Change Proposal: baseline

Project: `mlops-end2end` (#21)

## Intent

A single local-first command validates data, trains and quality-gates a model, promotes an MLflow alias, serves it with FastAPI, exports Prometheus metrics, and measures elapsed time to production.

## Why This Change Exists

Describe the smallest change that improves the measurable claim or removes a
known portfolio risk.

## Scope

- In scope: End-to-end MLOps pipeline including data validation, model training, MLflow tracking, FastAPI serving, and benchmark measurement.
- Out of scope: paid credentials, unrelated infrastructure, and unmeasured features.

## Portfolio Impact

Program: `mlops-data-platform`

This change should produce evidence, fixtures, decisions, or components that
can be reused by sibling repositories without moving project-specific behavior
into the kit.

## Acceptance Signal

The benchmark in `project.yaml` remains reproducible and its result is recorded
in `benchmarks/results/`.
