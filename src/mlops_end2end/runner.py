from __future__ import annotations

import argparse
import json
import math
import os
import platform
import shutil
import subprocess
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path
from typing import Any

from mlops_end2end.config import Settings


def _tail(path: Path, line_count: int = 40) -> str:
    if not path.exists():
        return "log file was not created"
    return "\n".join(path.read_text(encoding="utf-8", errors="replace").splitlines()[-line_count:])


def _run_logged(command: list[str], log_path: Path, environment: dict[str, str]) -> None:
    with log_path.open("w", encoding="utf-8") as log:
        completed = subprocess.run(
            command,
            check=False,
            env=environment,
            stdout=log,
            stderr=subprocess.STDOUT,
            text=True,
        )
    if completed.returncode != 0:
        raise RuntimeError(
            f"command failed ({' '.join(command)}):\n{_tail(log_path)}"
        )


def _start_logged(
    command: list[str], log_path: Path, environment: dict[str, str]
) -> tuple[subprocess.Popen[str], Any]:
    log = log_path.open("w", encoding="utf-8")
    process = subprocess.Popen(
        command,
        env=environment,
        stdout=log,
        stderr=subprocess.STDOUT,
        text=True,
    )
    return process, log


def _wait_json(url: str, timeout_seconds: float) -> dict[str, Any]:
    deadline = time.monotonic() + timeout_seconds
    last_error = "no response"
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                payload = response.read().decode("utf-8")
                if response.status == 200:
                    return json.loads(payload) if payload else {}
        except Exception as exc:  # noqa: BLE001 - readiness retries all transport failures
            last_error = str(exc)
        time.sleep(0.25)
    raise TimeoutError(f"{url} was not ready after {timeout_seconds}s: {last_error}")


def _wait_ready(url: str, timeout_seconds: float) -> None:
    deadline = time.monotonic() + timeout_seconds
    last_error = "no response"
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.status == 200:
                    return
        except Exception as exc:  # noqa: BLE001 - readiness retries all transport failures
            last_error = str(exc)
        time.sleep(0.25)
    raise TimeoutError(f"{url} was not ready after {timeout_seconds}s: {last_error}")


def _post_prediction(api_url: str, features: list[float]) -> float:
    request = urllib.request.Request(
        f"{api_url}/predict",
        data=json.dumps({"features": features}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    started = time.perf_counter()
    with urllib.request.urlopen(request, timeout=10) as response:
        if response.status != 200:
            raise RuntimeError(f"prediction returned HTTP {response.status}")
        json.loads(response.read().decode("utf-8"))
    return (time.perf_counter() - started) * 1_000


def _percentile(values: list[float], quantile: float) -> float:
    ordered = sorted(values)
    index = max(0, math.ceil(len(ordered) * quantile) - 1)
    return ordered[index]


def _configure_environment(settings: Settings) -> dict[str, str]:
    airflow_dir = settings.runtime_dir / "airflow"
    airflow_dir.mkdir(parents=True, exist_ok=True)
    (settings.runtime_dir / "logs").mkdir(parents=True, exist_ok=True)
    environment = os.environ.copy()
    environment.update(
        {
            "AIRFLOW_HOME": str(airflow_dir),
            "AIRFLOW__CORE__DAGS_FOLDER": "/opt/portfolio/dags",
            "AIRFLOW__CORE__EXECUTOR": "LocalExecutor",
            "AIRFLOW__CORE__LOAD_EXAMPLES": "False",
            "AIRFLOW__DATABASE__SQL_ALCHEMY_CONN": (
                f"sqlite:///{(airflow_dir / 'airflow.db').as_posix()}"
            ),
            "AIRFLOW__LOGGING__BASE_LOG_FOLDER": str(airflow_dir / "logs"),
            "AIRFLOW__API_AUTH__JWT_SECRET": "local-reproducible-demo-only",
            "MLFLOW_TRACKING_URI": settings.tracking_uri,
            "MLOPS_RUNTIME_DIR": str(settings.runtime_dir),
            "PYTHONPATH": "/opt/portfolio/src",
        }
    )
    return environment


def _benchmark_api(
    api_url: str, requests: int, concurrency: int, warmup_requests: int
) -> dict[str, float]:
    features = [0.15, -0.20, 0.75, 1.10, -0.45, 0.30, 0.90, -0.10]
    for _ in range(warmup_requests):
        _post_prediction(api_url, features)
    started = time.perf_counter()
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        latencies = list(pool.map(lambda _: _post_prediction(api_url, features), range(requests)))
    elapsed = time.perf_counter() - started
    return {
        "inference_p50_ms": round(_percentile(latencies, 0.50), 3),
        "inference_p95_ms": round(_percentile(latencies, 0.95), 3),
        "inference_requests_per_second": round(requests / elapsed, 3),
    }


def run_benchmark() -> dict[str, Any]:
    lifecycle_started = time.perf_counter()
    stage_started = lifecycle_started
    stage_timings: dict[str, float] = {}
    settings = Settings.from_env()
    output_path = Path(
        os.getenv("BENCHMARK_OUTPUT", "/tmp/mlops-end2end-benchmark.json")
    )
    requests = int(os.getenv("BENCHMARK_REQUESTS", "300"))
    concurrency = int(os.getenv("BENCHMARK_CONCURRENCY", "8"))
    warmup_requests = int(os.getenv("BENCHMARK_WARMUP_REQUESTS", "20"))

    if settings.runtime_dir.exists():
        shutil.rmtree(settings.runtime_dir)
    settings.prepare()
    log_dir = settings.runtime_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    mlflow_dir = settings.runtime_dir / "mlflow"
    artifact_dir = mlflow_dir / "artifacts"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    environment = _configure_environment(settings)

    processes: list[tuple[subprocess.Popen[str], Any, Path]] = []
    current_stage = "mlflow_startup"
    try:
        mlflow_log = log_dir / "mlflow.log"
        mlflow_process, mlflow_handle = _start_logged(
            [
                "mlflow",
                "server",
                "--host",
                "127.0.0.1",
                "--port",
                "5000",
                "--workers",
                "1",
                "--backend-store-uri",
                f"sqlite:///{(mlflow_dir / 'mlflow.db').as_posix()}",
                "--default-artifact-root",
                artifact_dir.as_uri(),
            ],
            mlflow_log,
            environment,
        )
        processes.append((mlflow_process, mlflow_handle, mlflow_log))
        _wait_ready(f"{settings.tracking_uri}/health", 90)
        stage_timings["mlflow_startup_seconds"] = time.perf_counter() - stage_started

        stage_started = time.perf_counter()
        current_stage = "airflow_migration"
        _run_logged(["airflow", "db", "migrate"], log_dir / "airflow-db.log", environment)
        stage_timings["airflow_migration_seconds"] = time.perf_counter() - stage_started

        stage_started = time.perf_counter()
        current_stage = "pipeline"
        _run_logged(
            [sys.executable, "-m", "dags.mlops_end2end"],
            log_dir / "pipeline.log",
            environment,
        )
        stage_timings["pipeline_seconds"] = time.perf_counter() - stage_started

        stage_started = time.perf_counter()
        current_stage = "api_startup"
        api_log = log_dir / "api.log"
        api_process, api_handle = _start_logged(
            [
                "uvicorn",
                "mlops_end2end.api:app",
                "--host",
                "127.0.0.1",
                "--port",
                "8000",
                "--log-level",
                "warning",
            ],
            api_log,
            environment,
        )
        processes.append((api_process, api_handle, api_log))
        api_url = "http://127.0.0.1:8000"
        health = _wait_json(f"{api_url}/health", 90)
        stage_timings["api_startup_seconds"] = time.perf_counter() - stage_started
        time_to_production = time.perf_counter() - lifecycle_started
        current_stage = "inference_benchmark"
        api_metrics = _benchmark_api(api_url, requests, concurrency, warmup_requests)

        with urllib.request.urlopen(f"{api_url}/metrics", timeout=5) as response:
            prometheus_text = response.read().decode("utf-8")
        candidate = json.loads(settings.candidate_path.read_text(encoding="utf-8"))
        result: dict[str, Any] = {
            "project": "mlops-end2end",
            "metric": "time_to_production_seconds",
            "value": round(time_to_production, 3),
            "unit": "seconds",
            "timestamp": datetime.now(UTC).isoformat(),
            "command": "docker run --rm mlops-end2end",
            "environment": {
                "os": platform.platform(),
                "architecture": platform.machine(),
                "cpu_count": os.cpu_count(),
                "python": platform.python_version(),
                "airflow": version("apache-airflow"),
                "mlflow": version("mlflow"),
                "scikit_learn": version("scikit-learn"),
                "requests": requests,
                "warmup_requests": warmup_requests,
                "concurrency": concurrency,
                "lifecycle_window": "process start through alias-backed API readiness",
                "inference_window": "after API readiness and warmup",
                "random_seed": settings.random_seed,
                "sample_count": settings.sample_count,
            },
            "failures": 0,
            "metrics": {
                "time_to_production_seconds": round(time_to_production, 3),
                "roc_auc": round(float(candidate["roc_auc"]), 6),
                "accuracy": round(float(candidate["accuracy"]), 6),
                **{name: round(value, 3) for name, value in stage_timings.items()},
                **api_metrics,
            },
            "proof": {
                "dag_id": "mlops_end2end",
                "registered_model": settings.model_name,
                "model_alias": health["alias"],
                "model_version": health["version"],
                "run_id": candidate["run_id"],
                "quality_threshold": settings.quality_threshold,
                "prometheus_predictions_exported": "mlops_predictions_total" in prometheus_text,
                "readiness_payload_parsed": True,
                "lifecycle_completed": True,
            },
        }
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
        print(json.dumps(result, indent=2, sort_keys=True))
        return result
    except Exception as exc:
        failure_result: dict[str, Any] = {
            "project": "mlops-end2end",
            "metric": "time_to_production_seconds",
            "value": round(time.perf_counter() - lifecycle_started, 3),
            "unit": "seconds",
            "timestamp": datetime.now(UTC).isoformat(),
            "command": "docker run --rm mlops-end2end",
            "environment": {
                "os": platform.platform(),
                "architecture": platform.machine(),
                "cpu_count": os.cpu_count(),
                "python": platform.python_version(),
                "requests": requests,
                "warmup_requests": warmup_requests,
                "concurrency": concurrency,
                "random_seed": settings.random_seed,
                "sample_count": settings.sample_count,
            },
            "failures": 1,
            "proof": {"lifecycle_completed": False},
            "failure": {
                "stage": current_stage,
                "type": type(exc).__name__,
                "message": str(exc),
            },
        }
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(failure_result, indent=2, sort_keys=True), encoding="utf-8"
        )
        diagnostics = [f"benchmark failed: {exc}"]
        for process, _, log_path in processes:
            diagnostics.append(
                f"\n[{log_path.name}] pid={process.pid} exit={process.poll()}\n{_tail(log_path)}"
            )
        raise RuntimeError("\n".join(diagnostics)) from exc
    finally:
        for process, handle, _ in reversed(processes):
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
            handle.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the reproducible MLOps proof.")
    parser.add_argument("mode", nargs="?", default="benchmark", choices=["benchmark"])
    parser.parse_args()
    run_benchmark()


if __name__ == "__main__":
    main()

