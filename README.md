# #21 mlops-end2end

**Status:** scaffold

**Proves:** treino, registro, deploy e monitoramento.

**Benchmark target:** time_to_production_minutes.

**Stack:** python, mlflow, fastapi, prometheus, docker.

## Next milestone

Implement the smallest Docker-runnable version and produce the first JSON benchmark under enchmarks/results/.

## Run

`ash
docker build -t mlops-end2end .
docker run --rm mlops-end2end
`

## Benchmark

`ash
docker run --rm mlops-end2end benchmark
`

| Metric | Value | Unit |
|---|---:|---|
| time_to_production_minutes | pending | pending |

## Architecture

Defined in sdd/spec.md before implementation.

## References

See REFERENCES.md.