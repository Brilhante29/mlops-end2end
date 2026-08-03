from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import subprocess
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "benchmarks" / "results"
PUBLICATION = ROOT / "benchmarks" / "publication"
CONTAINER_RESULT = "/tmp/mlops-publication.json"


def run(
    command: list[str], *, capture: bool = True, check: bool = True
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=capture, check=False)
    if check and result.returncode != 0:
        details = (result.stdout or "") + (result.stderr or "")
        raise RuntimeError(f"command failed ({' '.join(command)}):\n{details[-4000:]}")
    return result


def combined_digest(paths: list[str]) -> str:
    lines: list[str] = []
    for relative in sorted(paths):
        content = (ROOT / relative).read_bytes()
        lines.append(f"{relative}|{hashlib.sha256(content).hexdigest()}")
    payload = ("\n".join(lines) + "\n").encode()
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def median(values: list[float]) -> float:
    return round(float(statistics.median(values)), 3)


def required_path(payload: dict[str, Any], *path: str) -> Any:
    current: Any = payload
    for part in path:
        if not isinstance(current, dict) or part not in current:
            raise ValueError(f"missing benchmark field: {'.'.join(path)}")
        current = current[part]
    return current


def validate_run(payload: dict[str, Any]) -> None:
    if payload.get("project") != "mlops-end2end":
        raise ValueError("unexpected benchmark project")
    if payload.get("failures") != 0:
        raise ValueError("failed lifecycle run cannot enter publication evidence")
    proof = payload.get("proof", {})
    expected = {
        "airflow_execution_mode": "dags-test",
        "mlflow_tracking_backend": "sqlite-direct",
        "model_alias": "champion",
        "lifecycle_completed": True,
        "readiness_payload_parsed": True,
        "prometheus_predictions_exported": True,
    }
    for name, value in expected.items():
        if proof.get(name) != value:
            raise ValueError(f"invalid proof {name}={proof.get(name)!r}")
    if float(required_path(payload, "metrics", "roc_auc")) < 0.80:
        raise ValueError("quality gate was not satisfied")


def values(runs: list[dict[str, Any]], name: str) -> list[float]:
    return [float(required_path(item, "metrics", name)) for item in runs]


def aggregate(runs: list[dict[str, Any]]) -> dict[str, Any]:
    for item in runs:
        validate_run(item)
    primary = values(runs, "time_to_production_seconds")
    metric_names = [
        "time_to_production_seconds",
        "airflow_migration_seconds",
        "airflow_dag_run_seconds",
        "api_startup_seconds",
        "roc_auc",
        "accuracy",
        "inference_p50_ms",
        "inference_p95_ms",
        "inference_requests_per_second",
    ]
    medians = {name: median(values(runs, name)) for name in metric_names}
    primary_median = medians["time_to_production_seconds"]
    return {
        "aggregation": "median_per_metric_across_clean_lifecycle_runs",
        "repetitions": len(runs),
        **medians,
        "minimum_time_to_production_seconds": round(min(primary), 3),
        "maximum_time_to_production_seconds": round(max(primary), 3),
        "range_seconds": round(max(primary) - min(primary), 3),
        "range_relative_to_median": round((max(primary) - min(primary)) / primary_median, 6),
        "runs": [
            {
                "run": index,
                "time_to_production_seconds": round(float(item["value"]), 3),
                "roc_auc": float(item["metrics"]["roc_auc"]),
                "inference_p95_ms": float(item["metrics"]["inference_p95_ms"]),
                "inference_requests_per_second": float(
                    item["metrics"]["inference_requests_per_second"]
                ),
            }
            for index, item in enumerate(runs, start=1)
        ],
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish three-run MLOps lifecycle evidence.")
    parser.add_argument("--image", default="mlops-end2end:benchmark")
    parser.add_argument("--repeat", type=int, default=3)
    args = parser.parse_args()
    if args.repeat < 3 or args.repeat > 9 or args.repeat % 2 == 0:
        raise SystemExit("--repeat must be an odd number from 3 through 9")

    source_commit = run(["git", "rev-parse", "HEAD"]).stdout.strip()
    if run(["git", "status", "--porcelain"]).stdout.strip():
        raise SystemExit("publication requires a clean source tree")
    started_at = datetime.now(timezone.utc)  # noqa: UP017
    timer = time.perf_counter()

    run(["docker", "build", "-t", args.image, "."], capture=False)
    image_digest = run(
        ["docker", "image", "inspect", "--format", "{{.Id}}", args.image]
    ).stdout.strip()
    image_size = int(
        run(["docker", "image", "inspect", "--format", "{{.Size}}", args.image]).stdout.strip()
    )
    if not image_digest.startswith("sha256:") or len(image_digest) != 71:
        raise RuntimeError("Docker image did not expose an immutable content digest")

    RESULTS.mkdir(parents=True, exist_ok=True)
    raw_paths: list[str] = []
    raw_runs: list[dict[str, Any]] = []
    session = uuid.uuid4().hex[:10]
    for index in range(1, args.repeat + 1):
        container = f"mlops-pub-{session}-{index}"
        relative = f"benchmarks/results/runs/lifecycle-run-{index}.json"
        destination = ROOT / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        result = run(
            [
                "docker",
                "run",
                "--name",
                container,
                "--env",
                f"BENCHMARK_OUTPUT={CONTAINER_RESULT}",
                args.image,
            ],
            check=False,
        )
        try:
            copy = run(
                ["docker", "cp", f"{container}:{CONTAINER_RESULT}", str(destination)],
                check=False,
            )
            if copy.returncode != 0:
                raise RuntimeError(f"benchmark run {index} produced no JSON")
        finally:
            run(["docker", "rm", container], check=False)
        payload = json.loads(destination.read_text(encoding="utf-8"))
        if result.returncode != 0:
            failure_path = destination.with_name(f"failed-lifecycle-run-{index}.json")
            destination.replace(failure_path)
            raise RuntimeError(f"benchmark run {index} failed; preserved {failure_path}")
        validate_run(payload)
        raw_paths.append(relative)
        raw_runs.append(payload)
        print(
            f"run={index}/{args.repeat} time_to_production_seconds={payload['value']}",
            flush=True,
        )

    summary = aggregate(raw_runs)
    command = f"python tools/publish_benchmark.py --image {args.image} --repeat {args.repeat}"
    v1 = {
        "project": "mlops-end2end",
        "metric": "time_to_production_seconds",
        "value": summary["time_to_production_seconds"],
        "unit": "seconds",
        "timestamp": datetime.now(timezone.utc).isoformat(),  # noqa: UP017
        "command": command,
        "failures": 0,
        "repeat": args.repeat,
        "measured_lifecycle_runs": args.repeat,
        "environment": raw_runs[0]["environment"],
        "metrics": summary,
        "proof": {
            **raw_runs[0]["proof"],
            "raw_artifacts": raw_paths,
            "source_commit": source_commit,
            "image_digest": image_digest,
            "image_size_bytes": image_size,
        },
    }
    summary_path = RESULTS / "summary.json"
    write_json(summary_path, v1)

    artifact_digest = combined_digest(raw_paths)
    aggregate_summary = {
        **summary,
        "image_size_bytes": image_size,
        "raw_artifact_digest": artifact_digest,
    }
    metric_specs = [
        ("time_to_production_seconds", "seconds", "lower_is_better"),
        ("roc_auc", "ratio", "higher_is_better"),
        ("inference_p95_ms", "milliseconds", "lower_is_better"),
        ("inference_requests_per_second", "requests_per_second", "higher_is_better"),
    ]
    metrics = [
        {
            "name": name,
            "value": summary[name],
            "unit": unit,
            "direction": direction,
            "samples": values(raw_runs, name),
            "failures": 0,
            "summary": aggregate_summary,
        }
        for name, unit, direction in metric_specs
    ]
    environment = raw_runs[0]["environment"]
    v2 = {
        "schema_version": 2,
        "run_id": str(uuid.uuid4()),
        "project": "mlops-end2end",
        "benchmark_id": "mlops.lifecycle.v2",
        "workload": {
            "version": "2.0.0",
            "fixture_digest": combined_digest(
                [
                    "dags/mlops_end2end.py",
                    "src/mlops_end2end/adapters/data.py",
                    "src/mlops_end2end/adapters/training.py",
                    "src/mlops_end2end/application/promotion.py",
                    "src/mlops_end2end/domain/quality.py",
                ]
            ),
            "config_digest": combined_digest(
                [
                    "Dockerfile",
                    "benchmarks/config/mlops-lifecycle-v2.json",
                    "src/mlops_end2end/config.py",
                    "src/mlops_end2end/runner.py",
                    "tools/publish_benchmark.py",
                ]
            ),
            "warmup_iterations": int(environment["warmup_requests"]),
            "measured_iterations": args.repeat,
            "concurrency": 1,
        },
        "metrics": metrics,
        "execution": {
            "command": command,
            "started_at": started_at.isoformat(),
            "duration_seconds": round(time.perf_counter() - timer, 3),
            "exit_code": 0,
            "repeat": args.repeat,
        },
        "environment": {
            "runtime": (
                f"Python {environment['python']}, Airflow {environment['airflow']}, "
                f"MLflow {environment['mlflow']}, scikit-learn {environment['scikit_learn']}"
            ),
            "architecture": f"Linux {environment['architecture']} Docker container",
            "hardware_class": "local-docker",
            "cpu_count": environment["cpu_count"],
            "mlflow_tracking_backend": "sqlite-direct",
        },
        "provenance": {
            "source_commit": source_commit,
            "clean_tree": True,
            "image_ref": args.image,
            "image_digest": image_digest,
            "dependency_lock_digest": combined_digest(["pyproject.toml", "requirements.txt"]),
            "producer": "local",
            "artifact_digest": artifact_digest,
        },
        "comparability_key": (
            f"mlops-lifecycle:2.0.0:airflow-{environment['airflow']}:"
            f"mlflow-{environment['mlflow']}:sqlite-direct:"
            f"python-{environment['python']}:{environment['architecture']}"
        ),
    }
    output = PUBLICATION / "mlops-lifecycle-v2.json"
    write_json(output, v2)
    print(f"summary={summary_path}")
    print(f"v2={output}")
    print(f"source_commit={source_commit}")
    print(f"image_digest={image_digest}")


if __name__ == "__main__":
    main()
